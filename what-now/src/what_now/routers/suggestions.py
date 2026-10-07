from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from .. import agent, database as db
from ..dependencies import require_user, verify_csrf
from ..web import render
from .pages import dashboard_context

router = APIRouter()
Outcome = Literal["done", "skip", "blocked"]


@router.post(
    "/checkin",
    response_class=HTMLResponse,
    dependencies=[Depends(require_user), Depends(verify_csrf)],
)
async def checkin(
    request: Request,
    energy: int = Form(..., ge=1, le=5),
    available_minutes: int = Form(..., ge=5, le=240),
    user: dict = Depends(require_user),
):
    tasks = db.list_tasks(user["id"])
    context = {
        "time": datetime.now().strftime("%H:%M"),
        "energy": energy,
        "available_minutes": available_minutes,
        "recent_suggestions": db.list_recent_suggestions(user["id"]),
        "tasks": [
            {
                key: task[key]
                for key in (
                    "title",
                    "notes",
                    "deadline",
                    "estimated_minutes",
                    "energy_cost",
                    "importance",
                )
            }
            for task in tasks
        ],
    }

    if isinstance(request.session.get("pending_action"), dict):
        return RedirectResponse("/", status_code=303)

    page_context = dashboard_context(user)
    try:
        action = await agent.get_next_action(context)
    except agent.AgentError as exc:
        page_context["error"] = f"Could not get a suggestion: {exc}"
        return render(request, "index.html", page_context, status_code=502)

    selected_title = action["task_title"]
    selected_task = next(
        (
            task for task in tasks
            if selected_title is not None
            and task["title"].casefold() == selected_title.casefold()
        ),
        None,
    )
    if tasks and selected_task is None and not (energy == 1 and available_minutes < 10):
        page_context["error"] = (
            "Could not match the suggestion to one of your tasks. Please try again."
        )
        return render(request, "index.html", page_context, status_code=502)
    request.session["pending_action"] = {
        **action,
        "task_title": selected_task["title"] if selected_task else None,
        "task_id": selected_task["id"] if selected_task else None,
    }
    return RedirectResponse("/", status_code=303)


@router.post(
    "/feedback",
    dependencies=[Depends(require_user), Depends(verify_csrf)],
)
def feedback(
    request: Request,
    outcome: Outcome = Form(...),
    user: dict = Depends(require_user),
):
    action = request.session.get("pending_action")
    if not isinstance(action, dict):
        raise HTTPException(status_code=409, detail="There is no pending suggestion.")

    task_id = action.get("task_id")
    if not isinstance(task_id, int):
        task_id = None
    db.record_action_outcome(user["id"], task_id, action, outcome)
    if outcome == "done" and task_id is not None:
        db.set_task_completed(user["id"], task_id, completed=True)
    request.session.pop("pending_action", None)
    return RedirectResponse("/", status_code=303)
