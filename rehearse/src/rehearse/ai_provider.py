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
        tone_rule = "- TONE: You are a hostile, impatient interviewer. Interrupt vague answers, sigh audibly (use text like '*sigh*'), and push hard for metrics. Do not give them a moment to relax. Do not say 'great' or 'okay'."
    else:
        tone_rule = "- TONE: Professional, direct, but respectful. You are evaluating them, not torturing them."

    return f"""# ROLE
You are a Senior Engineering Manager at a top tech company conducting a {focus} interview for a {role} position.

# TASK
Conduct a realistic, high-stakes interview. You ask one question, wait for the candidate's answer, and then follow up.

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

# DO-AVOID-INCLUDE-RETURN
- DO: Push for specifics. If they mention an optimization, ask for metrics. If they mention a tool, ask why they chose it.
- AVOID: Softening language. Never say: "great", "good", "I understand", "let's try", "interesting", "that makes sense".
- INCLUDE: A concise follow-up that drills into the weakest part of their previous answer.
- RETURN: ONLY the spoken question. No meta-text, no markdown, no quotes.

# FALLBACK INSTRUCTION
If the candidate says "I don't know" or gives a highly vague answer, do not switch topics. Pick one keyword they used and ask them to define it or provide a concrete example.

# MODEL LIMITATIONS & PRIVACY
- Do not state outdated facts as current (e.g., "React class components are the standard").
- If the candidate shares sensitive personal info (health, family), pivot immediately back to the technical/behavioral question.
"""


async def interviewer_turn(history: list[dict], role: str, focus: str, difficulty: str, job_desc: str, tone: str = "Standard") -> str:
    system_prompt = build_system_prompt(role, focus, difficulty, job_desc, tone)
    
    if not history:
        user_message = "Start the interview. Greet briefly, then ask your opening question."
    else:
        user_message = "Continue the interview. Respond with your next line."

    context = {
        "history": history,
        "instruction": user_message,
    }

    if AI_PROVIDER == "api":
        return await _call_google(system_prompt, context)
    return await _call_ollama(system_prompt, context)


async def generate_feedback(transcript: str, role: str, focus: str) -> dict:
    """Analyze the transcript and return a JSON report card."""
    prompt = f"""You are a strict senior engineering manager reviewing a {focus} interview for a {role} position.

Transcript:
{transcript}

Return ONLY a JSON object with exactly these fields:
{{
  "score": integer (1 to 10),
  "summary": "one paragraph of direct, honest feedback on their overall performance",
  "improvement_1": "the single most important thing they need to fix",
  "improvement_2": "second most important thing",
  "improvement_3": "third most important thing"
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
        payload_ollama = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(OLLAMA_URL, json=payload_ollama)
            r.raise_for_status()
        raw = r.json()["response"].strip()

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
    payload = {"contents": [{"role": "user", "parts": [{"text": combined}]}], "generationConfig": {"temperature": 0.7}}
    headers = {"x-goog-api-key": GOOGLE_API_KEY, "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(GOOGLE_URL, json=payload, headers=headers)

    if r.status_code != 200:
        raise RuntimeError(f"Google API {r.status_code}: {r.text[:200]}")

    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()