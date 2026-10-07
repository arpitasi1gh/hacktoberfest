from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from .. import database as db
from ..dependencies import require_user, verify_csrf
from ..web import render

router = APIRouter()


def dashboard_context(user: dict, pending_action: dict | None = None) -> dict:
    user_id = user["id"]
    context = {
        "user": user,
        "tasks": db.list_tasks(user_id, include_completed=True),
        "stats": db.get_progress_stats(user_id),
        "actions": db.list_recent_actions(user_id),
    }
    if pending_action is not None:
        context["action"] = pending_action
    return context


def render_dashboard(request: Request, user: dict, status_code: int = 200):
    pending_action = request.session.get("pending_action")
    if not isinstance(pending_action, dict):
        pending_action = None
    elif isinstance(pending_action.get("task_id"), int):
        task = db.get_task(user["id"], pending_action["task_id"])
        if task is None:
            pending_action = {**pending_action, "task_id": None, "progress": None}
        else:
            pending_action = {**pending_action, "progress": task["progress"]}
        request.session["pending_action"] = pending_action
    return render(
        request,
        "index.html",
        dashboard_context(user, pending_action),
        status_code=status_code,
    )


@router.get("/")
def dashboard(request: Request, user: dict = Depends(require_user)):
    return render_dashboard(request, user)


@router.post("/theme", dependencies=[Depends(verify_csrf)])
def toggle_theme(request: Request):
    current_theme = request.session.get("theme", "light")
    request.session["theme"] = "dark" if current_theme != "dark" else "light"
    if request.headers.get("X-Requested-With") == "fetch":
        if request.session.get("user_id"):
            user = db.get_user_by_id(request.session["user_id"])
            if user is not None:
                return render_dashboard(request, user)
        return render(request, "auth.html", {"auth_mode": "login"})
    destination = "/" if request.session.get("user_id") else "/login"
    return RedirectResponse(destination, status_code=303)


@router.post(
    "/history/delete",
    dependencies=[Depends(require_user), Depends(verify_csrf)],
)
def delete_history(request: Request, user: dict = Depends(require_user)):
    db.delete_all_history(user["id"])
    request.session.pop("pending_action", None)
    if request.headers.get("X-Requested-With") == "fetch":
        return render_dashboard(request, user)
    return RedirectResponse("/#history", status_code=303)
