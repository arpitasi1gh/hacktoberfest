"""Interviewer brain: local Ollama or cloud Google AI Studio (Gemma)."""

import json
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "local")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemma-4-26b-a4b-it")
GOOGLE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GOOGLE_MODEL}:generateContent"


def build_system_prompt(role: str, focus: str, difficulty: str, job_desc: str, tone: str) -> str:
    """TCCo & DO-AVOID-INCLUDE-RETURN framework for the interviewer."""
    jd_context = job_desc if job_desc.strip() else "No specific job description provided. Assume standard industry expectations."
    
    tone_rule = ""
    if tone == "Stress":
        tone_rule = "- TONE: You are a hostile, impatient interviewer. Interrupt vague answers, sigh audibly (use text like '*sigh*'), and push hard. Do not give them a moment to relax. Do not say 'great' or 'okay'."
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
- Ask exactly ONE question per turn. Never ask multi-part questions.
- Ground your questions in the Job Description and Focus. Do not hallucinate irrelevant topics.
- Do NOT answer your own question.
- Stay in character. Never mention you are an AI.
- Do not state outdated facts as current (e.g., "React class components are the standard").

# ADVANCED INTERVIEWER TACTICS (DO THESE)
1. **The "We vs I" Test:** If they hide behind "we" (e.g., "We built a system"), force them to isolate their contribution: "What was *your* specific contribution to that?"
2. **The Trade-off Test:** If they make a technical or strategic choice, ask what they sacrificed: "What was the trade-off there? What did you give up?"
3. **The Edge Case / Failure Test:** Ask how their solution handles failure: "What happens if this scales 10x?" or "What was the biggest risk with that approach?"
4. **Interruption:** If their answer is rambling for more than 3 sentences, cut them off with a direct follow-up.
5. **STAR / CARL Method Enforcement:** If they don't state the *Result*, ask: "What was the measurable outcome?" If they don't state the *Learning*, ask: "Looking back, what would you do differently next time?" or "What did you learn from that?"

# DO-AVOID-INCLUDE
- DO: Push for specifics. If they mention a result or an optimization, ask for metrics. If they mention a tool, ask why they chose it.
- AVOID: Softening language. Never say: "great", "good", "I understand", "let's try", "interesting", "that makes sense".
- INCLUDE: A concise follow-up that drills into the weakest part of their previous answer.

# CRITICAL OUTPUT FORMAT
You must output your response as a JSON object. Do not output any thinking or planning outside the JSON.
{{
  "question": "Your spoken question here."
}}

# FALLBACK INSTRUCTION
If the candidate says "I don't know" or gives a highly vague answer, do not switch topics. Pick one keyword they used and ask them to define it or provide a concrete example.

# MODEL LIMITATIONS & PRIVACY
- If the candidate shares sensitive personal info (health, family), pivot immediately back to the interview question.
"""


async def interviewer_turn(history: list[dict], role: str, focus: str, difficulty: str, job_desc: str, tone: str = "Standard") -> str:
    system_prompt = build_system_prompt(role, focus, difficulty, job_desc, tone)
    
    if not history:
        user_message = "Start the interview. Greet briefly, then ask your opening question."
    else:
        user_message = "Continue the interview. Respond with your next line."

    context = {"history": history, "instruction": user_message}

    # 1. If explicitly set to API, skip local entirely
    if AI_PROVIDER == "api":
        return await _call_google(system_prompt, context)
        
    # 2. Try local first. If it fails (Ollama not running), fallback to API.
    try:
        return await _call_ollama(system_prompt, context)
    except Exception as exc:
        print(f"Ollama failed ({exc}). Falling back to Google API...")
        return await _call_google(system_prompt, context)


async def generate_feedback(transcript: str, role: str, focus: str) -> dict:
    """Analyze the transcript and return a generic, role-agnostic JSON report."""
    
    prompt = f"""You are a Senior Hiring Manager at a top-tier company. 
You just finished interviewing a candidate for the role of '{role}' with a focus on '{focus}'.

Review the transcript below. Adapt your evaluation to the specific domain (e.g., if the role is a Chef, evaluate culinary depth; if a Developer, evaluate technical architecture; if a Marketer, evaluate strategy).

Transcript:
{transcript}

Return ONLY a JSON object with exactly these fields:
{{
  "overall_score": integer (1 to 10),
  "summary": "one paragraph of direct, honest feedback on their overall performance",
  "score_structure": integer (1 to 10, how well they structured their answers using CARL/STAR),
  "score_depth": integer (1 to 10, how specific, metric-driven, and deep their answers were),
  "score_clarity": integer (1 to 10, how clear and concise their communication was),
  "weakest_moment": "Quote the weakest thing they actually said in the interview.",
  "ideal_response": "How a 10/10 candidate would have answered that exact same question.",
  "improvement_1": "the single most important thing they need to fix",
  "improvement_2": "second most important thing"
}}
Do not use markdown. Return only the JSON. First character must be {{, last must be }}.
"""

    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2}}
    
    # 1. If explicitly set to API, skip local
    if AI_PROVIDER == "api":
        headers = {"x-goog-api-key": GOOGLE_API_KEY, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(GOOGLE_URL, json=payload, headers=headers)
            r.raise_for_status()
        raw = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        
    # 2. Try local first, fallback to API
    else:
        try:
            payload_ollama = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json"}
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(OLLAMA_URL, json=payload_ollama)
                r.raise_for_status()
            raw = r.json()["response"].strip()
        except Exception as exc:
            print(f"Ollama failed for feedback ({exc}). Falling back to Google API...")
            headers = {"x-goog-api-key": GOOGLE_API_KEY, "Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(GOOGLE_URL, json=payload, headers=headers)
                r.raise_for_status()
            raw = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Clean up JSON if the model wrapped it in markdown
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


def clean_model_output(text: str) -> str:
    """Extract the final question, ignoring all hallucinated thinking."""
    import re
    import json
    
    # 1. Clean markdown
    text = text.replace("```json", "").replace("```", "").strip()
    
    # 2. Find all JSON objects in the text, and check them from bottom to top
    # (The real answer is almost always the last one it generates)
    matches = re.findall(r'\{.*?\}', text, re.DOTALL)
    for match in reversed(matches):
        try:
            data = json.loads(match)
            if "question" in data:
                return data["question"].strip()
        except Exception:
            pass
            
    # 3. If JSON completely fails, find the last thing inside double quotes
    quotes = re.findall(r'"([^"]{10,})"', text)
    if quotes:
        return quotes[-1].strip()

    # 4. Last resort: find the last line that ends in a question mark or period
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for line in reversed(lines):
        if line.endswith('?') or line.endswith('.'):
            # Clean up leading bullets or asterisks
            return re.sub(r'^[\*\-\s]+', '', line)

    return text


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
    raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    
    # Clean up the output before sending to the browser
    return clean_model_output(raw)