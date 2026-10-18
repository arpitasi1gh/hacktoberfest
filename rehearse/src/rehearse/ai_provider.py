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
GOOGLE_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GOOGLE_MODEL}:generateContent"
)

SYSTEM_PROMPT = """You are a senior engineer conducting a job interview. You are direct, unimpressed by vague answers, and you do not comfort the candidate.

You ask one question at a time. You follow up when an answer is vague.

Rules:
- Ask ONE question per turn. Never ask two.
- Never answer your own question.
- Never say "great answer", "good job", "I understand", "it sounds like", "let's try this", or anything that softens the pressure. You are not a therapist.
- If the candidate says "I can't remember" or gives a vague answer, do NOT switch topics. Pick one concrete element they mentioned and demand detail: "You said folder structure. What was the structure before, and what was it after?"
- If the candidate gives a strong answer with specifics, move to the next topic.
- Keep each turn under 3 sentences. You are not lecturing.
- Never break character. Never mention you are an AI.

The conversation history is provided. Continue it. Stay in role.
"""

async def interviewer_turn(history: list[dict], role: str, difficulty: str) -> str:
    """Given the conversation so far, return the interviewer's next line."""
    if not history:
        user_message = (
            f"Start the interview. Role: {role}. Difficulty: {difficulty}. "
            f"Greet briefly, then ask your opening question."
        )
    else:
        user_message = "Continue the interview. Respond with your next line."

    context = {
        "role": role,
        "difficulty": difficulty,
        "history": history,
        "instruction": user_message,
    }

    if AI_PROVIDER == "api":
        return await _call_google(context)
    return await _call_ollama(context)


async def _call_ollama(context: dict) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": json.dumps(context),
        "stream": False,
        "options": {"temperature": 0.7},
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(OLLAMA_URL, json=payload)
        r.raise_for_status()
    return r.json()["response"].strip()


async def _call_google(context: dict) -> str:
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY not set")

    combined = (
        SYSTEM_PROMPT
        + "\n\nContext:\n"
        + json.dumps(context, separators=(",", ":"))
    )

    payload = {
        "contents": [{"role": "user", "parts": [{"text": combined}]}],
        "generationConfig": {"temperature": 0.7},
    }
    headers = {
        "x-goog-api-key": GOOGLE_API_KEY,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(GOOGLE_URL, json=payload, headers=headers)

    if r.status_code != 200:
        raise RuntimeError(f"Google API {r.status_code}: {r.text[:200]}")

    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()

async def generate_feedback(transcript: str, role: str) -> dict:
    """Analyze the transcript and return a JSON report card."""
    
    prompt = f"""You are a strict but fair senior engineering manager.
Review this interview transcript for a {role} position.

Transcript:
{transcript}

Return ONLY a JSON object with exactly these fields:
{{
  "score": integer (1 to 10, no decimals),
  "summary": "one paragraph of direct feedback on their overall performance",
  "improvement_1": "the single most important thing they need to fix",
  "improvement_2": "second most important thing",
  "improvement_3": "third most important thing"
}}
Do not use markdown. Return only the JSON.
"""

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2},
    }
    
    # Use whichever provider is active
    if AI_PROVIDER == "api":
        headers = {"x-goog-api-key": GOOGLE_API_KEY, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(GOOGLE_URL, json=payload, headers=headers)
            r.raise_for_status()
        raw = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    else:
        # Local Ollama fallback
        payload_ollama = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(OLLAMA_URL, json=payload_ollama)
            r.raise_for_status()
        raw = r.json()["response"].strip()

    import json
    # Clean up any potential markdown fences
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    
    return json.loads(raw.strip())