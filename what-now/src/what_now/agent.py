"""Calls the local Ollama server to generate one next action."""

import json
import os
import re
from difflib import SequenceMatcher

import httpx

from .prompts import SYSTEM_PROMPT, build_user_prompt
from .web_context import add_web_references, extract_progress_context

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
FILE_TYPE_CLAIM_PATTERN = re.compile(r"\bpdfs?\b|\.pdf\b", re.IGNORECASE)


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
    context = await add_web_references(context)
    prompt = build_user_prompt(context)

    tasks = context.get("tasks", [])
    task_titles = {
        task["title"].casefold(): task["title"]
        for task in tasks
        if isinstance(task.get("title"), str)
    }

    def has_valid_task(candidate: dict) -> bool:
        title = candidate["task_title"]
        if not tasks:
            return title is None
        return isinstance(title, str) and title.casefold() in task_titles

    def canonicalize_task(candidate: dict) -> dict:
        if candidate["task_title"] is None:
            return candidate
        task = next(
            task
            for task in tasks
            if task["title"].casefold() == candidate["task_title"].casefold()
        )
        references = [
            {
                "title": (reference.get("title") or reference["url"])[:120],
                "url": reference["url"] if len(reference["url"]) <= 800 else "",
                "text": reference["text"][:280],
            }
            for reference in task.get("web_references", [])
            if isinstance(reference.get("url"), str)
            and isinstance(reference.get("text"), str)
            and reference["text"].strip()
            and not reference["text"].startswith(("Page not read:", "Page not fetched:"))
        ][:1]
        return {
            **candidate,
            "task_title": task_titles[candidate["task_title"].casefold()],
            "source_references": references,
        }

    recent_suggestions = context.get("recent_suggestions", [])
    progress_contexts = {
        task["title"].casefold(): task.get("progress_context")
        or extract_progress_context(task.get("notes", ""))
        for task in tasks
        if isinstance(task.get("title"), str)
    }

    def addresses_next_step_options(candidate: dict) -> bool:
        title = candidate.get("task_title")
        progress_context = (
            progress_contexts.get(title.casefold())
            if isinstance(title, str)
            else None
        )
        options = (
            progress_context.get("next_step_options")
            if isinstance(progress_context, dict)
            else None
        )
        if not isinstance(options, list) or len(options) < 2:
            return True

        decision_terms = {"choose", "select", "compare", "decide", "pick"}
        for field in ("action", "why"):
            words = set(re.findall(r"[a-z0-9]+(?:\+\+|#)?", candidate[field].casefold()))
            if words & decision_terms:
                continue
            if not any(
                set(re.findall(r"[a-z0-9]+(?:\+\+|#)?", option.casefold())) & words
                for option in options
            ):
                return False
        return True

    def build_choice_fallback(candidate: dict) -> dict:
        title = candidate["task_title"]
        progress_context = progress_contexts[title.casefold()]
        options = progress_context["next_step_options"]
        completed = progress_context.get("completed_milestones", [])
        completed_text = ", ".join(completed) if completed else "the earlier milestone"
        options_text = ", ".join(options[:-1]) + f" or {options[-1]}"
        fallback = {
            **candidate,
            "action": (
                f"Choose between {options_text} based on the language used in your "
                "target interviews and the one you can practice most comfortably."
            ),
            "why": (
                f"Your notes mark {completed_text} as covered and list {options_text} "
                "as the next tracks, so resolve that choice before repeating earlier material."
            ),
            "first_step": (
                "Write down the language used in your target interview roles and the "
                "language you can practice most comfortably."
            ),
            "fallback": (
                "If the choice is still unclear, compare one beginner exercise from "
                "each listed track."
            ),
        }
        return fallback

    def has_unsupported_file_type(candidate: dict) -> bool:
        task = next(
            (
                task
                for task in tasks
                if isinstance(candidate.get("task_title"), str)
                and task["title"].casefold() == candidate["task_title"].casefold()
            ),
            None,
        )
        if task is None:
            return False
        grounded_text = " ".join(
            [
                task.get("title", ""),
                task.get("notes", ""),
                *(
                    f"{reference.get('title', '')} {reference.get('text', '')}"
                    for reference in task.get("web_references", [])
                ),
            ]
        )
        if FILE_TYPE_CLAIM_PATTERN.search(grounded_text):
            return False
        return any(
            FILE_TYPE_CLAIM_PATTERN.search(candidate.get(field, ""))
            for field in ("action", "why", "first_step", "fallback")
        )

    def normalized(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()

    def repeats_recent_action(candidate: dict) -> bool:
        return any(
            previous.get("outcome") in {"skip", "blocked"}
            and (previous.get("task_title") or "").casefold()
            == (candidate.get("task_title") or "").casefold()
            and SequenceMatcher(
                None,
                normalized(candidate["action"]),
                normalized(previous["action"]),
            ).ratio()
            >= 0.9
            for previous in recent_suggestions
        )

    action = await _request_action(prompt)
    for attempt in range(2):
        invalid_file_type = has_unsupported_file_type(action)
        if (
            has_valid_task(action)
            and not repeats_recent_action(action)
            and not invalid_file_type
            and addresses_next_step_options(action)
        ):
            result = canonicalize_task(action)
            available_minutes = context.get("available_minutes")
            if isinstance(available_minutes, int) and not isinstance(
                available_minutes, bool
            ):
                result["timebox_minutes"] = available_minutes
            return result

        if not has_valid_task(action):
            constraint = (
                "Your previous response selected a task that is not in this user's task "
                "list. Select exactly one task using its exact title from the current prompt."
            )
        elif invalid_file_type:
            constraint = (
                "Your previous response invented a file format that is not present in "
                "the selected task title, notes, or retrieved source. Do not infer PDF, "
                "document, video, or other formats or assets. Base the next action only "
                "on the exact task details and readable source content in the prompt."
            )
        elif not addresses_next_step_options(action):
            constraint = (
                "The selected task notes explicitly separate completed work from "
                "multiple next-step options. Do not describe the completed milestone "
                "as the recommendation. Your action AND why must move forward by "
                "naming one listed next option or asking the user to choose/compare "
                "the listed options. Do not imply the completed section still needs work."
            )
        else:
            rejected = {
                "task_title": action["task_title"],
                "action": action["action"],
                "first_step": action["first_step"],
            }
            constraint = (
                "Your previous suggestion repeats an action the user skipped or was blocked "
                f"on. Do not repeat or lightly rephrase it: {json.dumps(rejected)}. "
                "Use that suggestion's outcome and feedback_note in recent_suggestions to "
                "change the approach. Select a different unfinished work unit grounded in "
                "the task notes or readable linked-page content. Avoid generic actions such "
                "as opening or navigating to a URL."
            )
        action = await _request_action(
            f"{prompt}\n\nRevision {attempt + 1}: {constraint}"
        )

    if not has_valid_task(action):
        raise AgentError(
            "The model selected a task that is not in your task list. Please try again."
        )
    if has_unsupported_file_type(action):
        raise AgentError(
            "The model suggested a file type not present in your task or its sources. "
            "Please try again."
        )
    if not addresses_next_step_options(action):
        action = build_choice_fallback(action)
    result = canonicalize_task(action)
    available_minutes = context.get("available_minutes")
    if isinstance(available_minutes, int) and not isinstance(available_minutes, bool):
        result["timebox_minutes"] = available_minutes
    return result