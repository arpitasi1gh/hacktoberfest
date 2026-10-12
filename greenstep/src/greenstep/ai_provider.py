"""Gemma-powered action writer for Greenstep."""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client()
    return _client


def write_action(
    window_hour: int,
    window_probability: float,
    place: dict,
    sleep_hours: float,
    screen_time_hours: float,
    mood: int,
    weather: str,
) -> str:
    """Generate a specific, actionable outdoor action using Gemma."""
    hour_label = f"{window_hour}:00"
    place_name = place.get("title", "a nearby spot")
    place_type = place.get("type", "place")

    prompt = f"""You are Greenstep, a quiet outdoor habit coach.

Your job: write ONE specific, gentle action for the user.

Context:
- Best predicted outdoor window: {hour_label} ({int(window_probability * 100)}% chance they'll go out)
- Nearest place: {place_name} ({place_type})
- Their sleep: {sleep_hours}h, screen time: {screen_time_hours}h, mood: {mood}/5
- Weather: {weather}

Rules:
- Exactly one sentence. No preamble.
- Name the place and the time.
- Be warm, not preachy. No exclamation marks.
- Never say "you should" or "try to".

Write the action now:"""

    try:
        client = _get_client()
        response = client.models.generate_content(
            model="gemma-4-26b-a4b-it",
            contents=prompt,
        )
        return response.text.strip()
    except Exception:
        # Fallback if Gemma call fails
        return (
            f"Head to {place_name} around {hour_label} for a quiet walk. "
            f"The evening air is mild right now."
        )