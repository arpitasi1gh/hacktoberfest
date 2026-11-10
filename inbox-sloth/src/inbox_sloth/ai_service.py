import json
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "local")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
GOOGLE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GOOGLE_MODEL}:generateContent"

async def generate_replies(email: str, tone_context: str) -> dict:
    prompt = f"""You are a ghostwriter. Draft replies in the user's exact tone.
Past examples of user's tone:
{tone_context if tone_context else "Standard professional tone."}

Incoming email: "{email}"

Return ONLY a JSON object with exactly these keys:
{{"short": "1 sentence reply", "polite": "standard corporate reply", "pushback": "firm decline"}}
Do not use markdown. Return only the JSON.
"""

    if AI_PROVIDER == "api":
        payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.3, "responseMimeType": "application/json"}}
        headers = {"x-goog-api-key": GOOGLE_API_KEY}
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(GOOGLE_URL, json=payload, headers=headers)
            r.raise_for_status()
            raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        try:
            payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json", "options": {"temperature": 0.3}}
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(OLLAMA_URL, json=payload)
                r.raise_for_status()
                raw = r.json()["response"]
        except Exception:
            # Fallback to Google
            payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.3, "responseMimeType": "application/json"}}
            headers = {"x-goog-api-key": GOOGLE_API_KEY}
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(GOOGLE_URL, json=payload, headers=headers)
                r.raise_for_status()
                raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]

    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    
    return json.loads(raw.strip())