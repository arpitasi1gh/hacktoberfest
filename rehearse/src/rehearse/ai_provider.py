"""Interviewer brain: local Ollama or cloud Google AI Studio (Gemma)."""

import json
import os
import re
import httpx
from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "local")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
# NOTE: Google changes model names frequently. If you get a 404 error on Render, 
# change this to "gemini-1.5-flash" or "gemini-2.5-flash".
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-1.5-flash") 
GOOGLE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GOOGLE_MODEL}:generateContent"

def extract_clean_text(raw_text: str) -> str:
    """Bulletproof parser to strip markdown and extract the 'question' field."""
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
    
    # 1. Look for JSON objects from bottom to top
    matches = re.findall(r'\{.*\}', raw_text, re.DOTALL)
    for match in reversed(matches):
        try:
            data = json.loads(match)
            if "question" in data:
                return data["question"].strip()
        except Exception:
            pass
            
    # 2. Look for the last string in double quotes
    quotes = re.findall(r'"([^"]{10,})"', raw_text)
    if quotes:
        return quotes[-1].strip()

    # 3. Fallback: just return the cleaned text
    return raw_text

def build_system_prompt(role: str, focus: str, difficulty: str, job_desc: str, tone: str) -> str:
    """TCCo & DO-AVOID-INCLUDE-RETURN framework for the interviewer."""
    jd_context = job_desc if job_desc.strip() else "No specific job description provided. Assume standard industry expectations."
    
    tone_rule = ""
    if tone == "Stress":
        tone_rule = "- TONE: You are a hostile, impatient interviewer. Interrupt vague answers, sigh audibly (use text like '*sigh*'), and push hard. Do not give them a moment to relax."
    else:
        tone_rule = "- TONE: Professional, direct, but respectful. You are evaluating them, not torturing them."

    return f"""# ROLE
You are a Senior {role} Manager at a top-tier company conducting a {focus} interview.

# TASK
Conduct a realistic, high-stakes interview. You ask one question, wait for the candidate's answer, and then follow up based on what they said.

# CONTEXT
- Role: {role}
- Focus: {focus}
- Difficulty: {difficulty}
- Job Description: {jd_context}

# CONSTRAINTS & GROUNDING RULES
{tone_rule}
- Ask exactly ONE question per turn.
- Ground your questions in the Job Description and Focus. Do not hallucinate irrelevant topics.
- Do NOT answer your own question.
- Stay in character. Never mention you are an AI.

# ADVANCED INTERVIEWER TACTICS
1. **The "We vs I" Test:** If they hide behind "we", force them to isolate their contribution.
2. **The Trade-off Test:** Ask what they sacrificed for a choice.
3. **The Edge Case Test:** Ask how their solution handles failure.
4. **STAR / CARL Enforcement:** If they don't state the Result, ask "What was the measurable outcome?" If they don't state the Learning, ask "What would you do differently next time?"

# DO-AVOID-INCLUDE
- DO: Push for specifics. Ask for metrics and tools.
- AVOID: Softening language. Never say: "great", "good", "I understand", "let's try", "interesting", "that makes sense".
- INCLUDE: A concise follow-up that drills into the weakest part of their previous answer.

# CRITICAL OUTPUT FORMAT
You must output your response as a JSON object. Do not output any thinking outside the JSON.
{{
  "question": "Your spoken question here."
}}
"""

async def interviewer_turn(history: list[dict], role: str, focus: str, difficulty: str, job_desc: str, tone: str = "Standard") -> str:
    system_prompt = build_system_prompt(role, focus, difficulty, job_desc, tone)
    
    if not history:
        user_message = "Start the interview. Greet briefly, then ask your opening question."
    else:
        user_message = "Continue the interview. Respond with your next line."

    context = {"history": history, "instruction": user_message}
    raw_response = ""

    if AI_PROVIDER == "api":
        raw_response = await _call_google(system_prompt, context)
    else:
        try:
            raw_response = await _call_ollama(system_prompt, context)
        except Exception:
            raw_response = await _call_google(system_prompt, context)
            
    return extract_clean_text(raw_response)


async def generate_feedback(transcript: str, role: str, focus: str) -> dict:
    prompt = f"""You are a Senior Hiring Manager reviewing a {focus} interview for a {role} role.
Transcript:
{transcript}

Return ONLY a JSON object with exactly these fields:
{{
  "overall_score": integer (1 to 10),
  "summary": "one paragraph of direct, honest feedback",
  "score_structure": integer (1 to 10),
  "score_depth": integer (1 to 10),
  "score_clarity": integer (1 to 10),
  "weakest_moment": "Quote the weakest thing they said.",
  "ideal_response": "How a 10/10 candidate would have answered that exact question.",
  "improvement_1": "most important fix",
  "improvement_2": "second most important fix"
}}
Do not use markdown. Return only the JSON. First character must be {{, last must be }}.
"""

    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2}}
    
    if AI_PROVIDER == "api":
        headers = {"x-goog-api-key": GOOGLE_API_KEY, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(GOOGLE_URL, json=payload, headers=headers)
            r.raise_for_status()
        raw = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    else:
        try:
            payload_ollama = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json"}
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(OLLAMA_URL, json=payload_ollama)
                r.raise_for_status()
            raw = r.json()["response"].strip()
        except Exception as exc:
            headers = {"x-goog-api-key": GOOGLE_API_KEY, "Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(GOOGLE_URL, json=payload, headers=headers)
                r.raise_for_status()
            raw = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    
    return json.loads(raw.strip())


async def _call_ollama(system: str, context: dict) -> str:
    payload = {
        "model": OLLAMA_MODEL, "system": system, "prompt": json.dumps(context),
        "stream": False, "options": {"temperature": 0.7},
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(OLLAMA_URL, json=payload)
        r.raise_for_status()
    return r.json()["response"].strip()

async def _call_google(system: str, context: dict) -> str:
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY not set")

    combined = system + "\n\nContext:\n" + json.dumps(context, separators=(",", ":"))
    payload = {"contents": [{"role": "user", "parts": [{"text": combined}]}], "generationConfig": {"temperature": 0.3}}
    headers = {"x-goog-api-key": GOOGLE_API_KEY, "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(GOOGLE_URL, json=payload, headers=headers)

    if r.status_code != 200:
        raise RuntimeError(f"Google API {r.status_code}: {r.text[:200]}")

    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()