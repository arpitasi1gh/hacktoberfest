from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from .. import database as db
from ..dependencies import require_user, verify_csrf
from ..web import render_fragment
from .pages import dashboard_context

router = APIRouter(prefix="/tasks", tags=["tasks"])
EnergyCost = Literal["low", "medium", "high"]


def _deadline_value(deadline: str) -> str | None:
    if not deadline:
        return None
    try:
        datetime.fromisoformat(deadline)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Enter a valid task deadline.") from exc
    return deadline


@router.post(
    "",
    dependencies=[Depends(require_user), Depends(verify_csrf)],
)
def create_task(
    user: dict = Depends(require_user),
    title: str = Form(..., min_length=1, max_length=200),
    notes: str = Form("", max_length=2000),
    deadline: str = Form(""),
    estimated_minutes: int = Form(..., ge=5, le=600),
    energy_cost: EnergyCost = Form("medium"),
    importance: int = Form(3, ge=1, le=5),
):
    title = title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="A task title is required.")
    db.add_task(
        user["id"],
        title,
        notes.strip() or None,
        _deadline_value(deadline),
        estimated_minutes,
        energy_cost,
        importance,
    )
    return RedirectResponse("/#tasks", status_code=303)


@router.post(
    "/{task_id}/edit",
    dependencies=[Depends(require_user), Depends(verify_csrf)],
)
def update_task(
    task_id: int,
    user: dict = Depends(require_user),
    title: str = Form(..., min_length=1, max_length=200),
    notes: str = Form("", max_length=2000),
    deadline: str = Form(""),
    estimated_minutes: int = Form(..., ge=5, le=600),
    energy_cost: EnergyCost = Form("medium"),
    importance: int = Form(3, ge=1, le=5),
):
    title = title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="A task title is required.")
    updated = db.update_task(
        user["id"],
        task_id,
        title,
        notes.strip() or None,
        _deadline_value(deadline),
        estimated_minutes,
        energy_cost,
        importance,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found.")
    return RedirectResponse("/#tasks", status_code=303)


@router.post(
    "/{task_id}/complete",
    dependencies=[Depends(require_user), Depends(verify_csrf)],
)
def complete_task(task_id: int, user: dict = Depends(require_user)):
    if not db.set_task_completed(user["id"], task_id, completed=True):
        raise HTTPException(status_code=404, detail="Task not found.")
    return RedirectResponse("/#tasks", status_code=303)


@router.post(
    "/{task_id}/reopen",
    dependencies=[Depends(require_user), Depends(verify_csrf)],
)
def reopen_task(task_id: int, user: dict = Depends(require_user)):
    if not db.set_task_completed(user["id"], task_id, completed=False):
        raise HTTPException(status_code=404, detail="Task not found.")
    return RedirectResponse("/#tasks", status_code=303)


@router.post(
    "/{task_id}/delete",
    dependencies=[Depends(require_user), Depends(verify_csrf)],
)
def delete_task(
    request: Request,
    task_id: int,
    user: dict = Depends(require_user),
):
    if not db.delete_task(user["id"], task_id):
        raise HTTPException(status_code=404, detail="Task not found.")
    if request.headers.get("X-Requested-With") == "fetch":
        return HTMLResponse(
            render_fragment(request, "_task_updates.html", dashboard_context(user))
        )
    return RedirectResponse("/#tasks", status_code=303)
