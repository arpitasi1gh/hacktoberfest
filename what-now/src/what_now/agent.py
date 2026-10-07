"""Calls the local Ollama server to generate one next action."""

import json
import os

import httpx

from .prompts import SYSTEM_PROMPT, build_user_prompt

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.getenv("WHATNOW_MODEL", "gemma3:4b")
TIMEOUT_SECONDS = 30.0

REQUIRED_FIELDS = {
    "task_title",
    "action",
    "why",
    "first_step",
    "timebox_minutes",
    "fallback",
}


class AgentError(Exception):
    """Raised when the agent cannot produce a valid action."""


async def _request_action(prompt: str) -> dict:
    payload = {
        "model": MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": prompt,
        "stream": False,
        "format": "json",          # Ollama constrains output to valid JSON
        "options": {
            "temperature": 0.8,
            "top_p": 0.95,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
    except httpx.ConnectError as exc:
        raise AgentError("Ollama is not running. Start it with `ollama serve`.") from exc
    except httpx.TimeoutException as exc:
        raise AgentError("Ollama took too long to respond. Try again.") from exc
    except httpx.HTTPStatusError as exc:
        raise AgentError(f"Ollama returned an error: {exc.response.status_code}") from exc

    raw = response.json().get("response", "").strip()
    if not raw:
        raise AgentError("Model returned an empty response.")

    try:
        action = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AgentError(f"Model returned invalid JSON: {raw[:200]}") from exc

    if not isinstance(action, dict):
        raise AgentError("Model response must be a JSON object.")

    missing = REQUIRED_FIELDS - action.keys()
    if missing:
        raise AgentError(f"Model response missing fields: {sorted(missing)}")

    for field in REQUIRED_FIELDS - {"timebox_minutes", "task_title"}:
        if not isinstance(action[field], str) or not action[field].strip():
            raise AgentError(f"Model response contains an invalid {field} value.")

    if action["task_title"] is not None and (
        not isinstance(action["task_title"], str) or not action["task_title"].strip()
    ):
        raise AgentError("Model response contains an invalid task_title value.")

    timebox = action["timebox_minutes"]
    if isinstance(timebox, bool) or not isinstance(timebox, int) or not 1 <= timebox <= 600:
        raise AgentError("Model response contains an invalid timebox_minutes value.")

    return action


async def get_next_action(context: dict) -> dict:
    """Ask Ollama for one varied next action. Returns a dict matching the schema."""
    prompt = build_user_prompt(context)
    action = await _request_action(prompt)

    recent_suggestions = context.get("recent_suggestions", [])

    def repeats_recent_action(candidate: dict) -> bool:
        return any(
            candidate["action"] == previous["action"]
            or candidate["first_step"] == previous["first_step"]
            for previous in recent_suggestions
        )

    if repeats_recent_action(action):
        action = await _request_action(
            f"{prompt}\n\nYour last response repeated a recent action or first step. "
            "Generate a different concrete action or first step for the same suitable "
            "task; do not reuse the previous response."
        )
        if repeats_recent_action(action):
            raise AgentError(
                "The model repeated a recent suggestion. Please try again."
            )

    return action