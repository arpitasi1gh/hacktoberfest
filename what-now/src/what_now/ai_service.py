import json
import os
import httpx
from dotenv import load_dotenv
from .prompts import SYSTEM_PROMPT

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "local")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_MODEL = "gemini-2.5-flash"
GOOGLE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GOOGLE_MODEL}:generateContent"

async def get_next_action(context: dict) -> dict:
    prompt = json.dumps(context)
    
    if AI_PROVIDER == "local":
        try:
            payload = {"model": OLLAMA_MODEL, "system": SYSTEM_PROMPT, "prompt": prompt, "stream": False, "format": "json"}
            async with httpx.AsyncClient(timeout=120.0) as client:
                r = await client.post(OLLAMA_URL, json=payload)
                r.raise_for_status()
                return json.loads(r.json()["response"])
        except Exception:
            pass # Fallback to Google

    # Cloud Fallback
    full_prompt = SYSTEM_PROMPT + "\n\nContext:\n" + prompt
    payload = {"contents": [{"role": "user", "parts": [{"text": full_prompt}]}], "generationConfig": {"responseMimeType": "application/json"}}
    headers = {"x-goog-api-key": GOOGLE_API_KEY}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(GOOGLE_URL, json=payload, headers=headers)
        r.raise_for_status()
        raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(raw)