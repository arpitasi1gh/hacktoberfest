"""Inference provider: local Ollama or cloud Google AI Studio (Gemma)."""

import json
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "local")

# Local (Ollama)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

# Cloud (Google AI Studio)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemma-4-26b-a4b-it")
GOOGLE_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GOOGLE_MODEL}:generateContent"
)

SYSTEM_PROMPT = """You are a direct, practical outdoor coach. You do not motivate. You state one action.

Return ONLY a JSON object. No markdown fences. No text before or after.

Exactly these five fields:
{
  "action": "One imperative sentence. Start with a verb. Name the place and what to do there.",
  "why": "One sentence. Reference the weather or mood. Plain words. No metaphors.",
  "first_step": "What you do BEFORE leaving. Shoes, keys, water. Under 2 minutes.",
  "duration_minutes": 25,
  "fallback": "A smaller OUTDOOR action. Never indoor."
}

Rules:
1. NEVER use vague references. Not "a nearby trail", "the river". Be concrete enough to act on.
2. NEVER make the user decide. Bad: "Choose a trail". Good: "Walk to the nearest cafe and order a filter coffee."
3. NEVER use these words: might, could, perhaps, simply, just, opportunity, movement, wellness, mindful, conducive, stillness.
4. duration_minutes between 10 and 45. Default 25.
5. Tone: peer, not coach. No "let's", no exclamation marks.
6. Do NOT repeat the input. Output the JSON object only.
7. You are given "nearest_place" with a real name. Use it. Say "Walk to <name>".
8. If "nearest_place" is null, describe a specific generic place type instead.

Example of a GOOD response:
{"action":"Walk to Tartinery and order a filter coffee, sit outside for 20 minutes.","why":"Mild weather and low energy — a short change of scene fits.","first_step":"Put on your shoes.","duration_minutes":25,"fallback":"Stand outside your building for 5 minutes."}

Example of a BAD response (do NOT do this):
{"action":"Consider taking a walk or finding a nice trail nearby.","why":"It's a pleasant opportunity for movement.","first_step":"Think about where to go.","duration_minutes":60,"fallback":"Just relax."}
"""


async def write_action(sleep_hours, screen_hours, mood, location, weather_label, temperature_c, top_place=None):
    """Return a parsed action dict. Local Ollama by default, cloud if AI_PROVIDER=api."""
    context = {
        "location": location,
        "weather": weather_label,
        "temperature_c": temperature_c,
        "sleep_hours": sleep_hours,
        "screen_hours": screen_hours,
        "mood": mood,
        "starting_point": "at home, about to leave",
        "nearest_place": top_place,
    }

    if AI_PROVIDER == "api":
        raw = await _call_google(context)
    else:
        raw = await _call_ollama(context)

    parsed = _parse_json(raw)

    return {
        "action": parsed.get("action", "Walk outside for 15 minutes."),
        "why": parsed.get("why", "Fresh air helps focus."),
        "first_step": parsed.get("first_step", "Put on your shoes."),
        "duration_minutes": parsed.get("duration_minutes", 25),
        "fallback": parsed.get("fallback", "Stand outside for 2 minutes."),
    }


async def _call_ollama(context: dict) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": json.dumps(context),
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.4},
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(OLLAMA_URL, json=payload)
        r.raise_for_status()
    return r.json()["response"]


async def _call_google(context: dict) -> str:
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY not set")

    combined = (
        SYSTEM_PROMPT
        + "\n\nReturn ONLY valid JSON. No markdown fences.\n\nContext:\n"
        + json.dumps(context, separators=(",", ":"))
    )

    payload = {
        "contents": [{"role": "user", "parts": [{"text": combined}]}],
        "generationConfig": {"temperature": 0.4},
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
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Unexpected response shape: {json.dumps(data)[:300]}") from exc


def _parse_json(raw: str) -> dict:
    """Strip markdown fences and any preamble/trailing text before parsing."""
    original = raw
    raw = raw.strip()

    if "```" in raw:
        for part in raw.split("```"):
            cleaned = part.strip()
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
            if cleaned.startswith("{"):
                raw = cleaned
                break

    brace = raw.find("{")
    if brace > 0:
        raw = raw[brace:]

    last = raw.rfind("}")
    if last != -1 and last < len(raw) - 1:
        raw = raw[: last + 1]

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        print("=== RAW OUTPUT ===")
        print(original)
        raise RuntimeError(f"Invalid JSON. First 200 chars: {original[:200]!r}") from exc