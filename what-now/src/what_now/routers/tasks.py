from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from .. import database as db
from ..dependencies import require_user, verify_csrf
from ..web import is_async_request
from .pages import render_dashboard

router = APIRouter(prefix="/tasks", tags=["tasks"])
EnergyCost = Literal["low", "medium", "high"]


def _deadline_value(deadline: str) -> str:
    deadline = deadline.strip()
    if not deadline:
        raise HTTPException(status_code=422, detail="A task deadline is required.")
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
    request: Request,
    user: dict = Depends(require_user),
    title: str = Form(..., min_length=1, max_length=200),
    notes: str = Form(..., min_length=1, max_length=2000),
    deadline: str = Form(..., min_length=1),
    daily_minutes: int = Form(..., ge=5, le=600),
    energy_cost: EnergyCost = Form("medium"),
    importance: int = Form(3, ge=1, le=5),
):
    title = title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="A task title is required.")
    notes = notes.strip()
    if not notes:
        raise HTTPException(status_code=422, detail="Task notes are required.")
    db.add_task(
        user["id"],
        title,
        notes,
        _deadline_value(deadline),
        daily_minutes,
        energy_cost,
        importance,
    )
    if is_async_request(request):
        return render_dashboard(request, user)
    return RedirectResponse("/#tasks", status_code=303)


@router.post(
    "/{task_id}/edit",
    dependencies=[Depends(require_user), Depends(verify_csrf)],
)
def update_task(
    request: Request,
    task_id: int,
    user: dict = Depends(require_user),
    title: str = Form(..., min_length=1, max_length=200),
    notes: str = Form(..., min_length=1, max_length=2000),
    deadline: str = Form(..., min_length=1),
    daily_minutes: int = Form(..., ge=5, le=600),
    energy_cost: EnergyCost = Form("medium"),
    importance: int = Form(3, ge=1, le=5),
    progress: int = Form(0, ge=0, le=100),
):
    title = title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="A task title is required.")
    notes = notes.strip()
    if not notes:
        raise HTTPException(status_code=422, detail="Task notes are required.")
    updated = db.update_task(
        user["id"],
        task_id,
        title,
        notes,
        _deadline_value(deadline),
        daily_minutes,
        energy_cost,
        importance,
        progress,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found.")
    if is_async_request(request):
        return render_dashboard(request, user)
    return RedirectResponse("/#tasks", status_code=303)


@router.post(
    "/{task_id}/complete",
    dependencies=[Depends(require_user), Depends(verify_csrf)],
)
def complete_task(
    request: Request,
    task_id: int,
    user: dict = Depends(require_user),
):
    if not db.set_task_completed(user["id"], task_id, completed=True):
        task = db.get_task(user["id"], task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found.")
        raise HTTPException(status_code=409, detail="Set task progress to 100% first.")
    if is_async_request(request):
        return render_dashboard(request, user)
    return RedirectResponse("/#tasks", status_code=303)


@router.post(
    "/{task_id}/reopen",
    dependencies=[Depends(require_user), Depends(verify_csrf)],
)
def reopen_task(
    request: Request,
    task_id: int,
    user: dict = Depends(require_user),
):
    if not db.set_task_completed(user["id"], task_id, completed=False):
        raise HTTPException(status_code=404, detail="Task not found.")
    if is_async_request(request):
        return render_dashboard(request, user)
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
    if is_async_request(request):
        return render_dashboard(request, user)
    return RedirectResponse("/#tasks", status_code=303)
