from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from datetime import datetime

from . import db
from .ai_service import get_next_action

app = FastAPI()
BASE = Path(__file__).resolve().parent.parent.parent
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE / "templates"))

@app.on_event("startup")
def startup():
    db.init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    all_tasks = db.get_all_tasks()
    active_tasks = db.get_active_tasks()
    stats = db.get_today_stats()
    return templates.TemplateResponse(request, "index.html", {"tasks": all_tasks, "active_count": len(active_tasks), "stats": stats})

@app.post("/tasks", response_class=HTMLResponse)
def create_task(request: Request, title: str = Form(...), notes: str = Form(""), deadline: str = Form(""), estimated_minutes: int = Form(...), energy_cost: str = Form(...), importance: int = Form(...)):
    db.add_task(title, notes, deadline, estimated_minutes, energy_cost, importance)
    return RedirectResponse(url="/", status_code=303)

@app.post("/tasks/{task_id}/delete", response_class=HTMLResponse)
def delete_task(request: Request, task_id: int):
    db.delete_task(task_id)
    return RedirectResponse(url="/", status_code=303)

@app.get("/tasks/{task_id}/edit", response_class=HTMLResponse)
def edit_task_form(request: Request, task_id: int):
    task = db.get_task(task_id)
    return templates.TemplateResponse(request, "_edit_task.html", {"task": task})

@app.post("/tasks/{task_id}/edit", response_class=HTMLResponse)
def cancel_edit(request: Request):
    return RedirectResponse(url="/", status_code=303)

@app.post("/tasks/{task_id}/update", response_class=HTMLResponse)
def update_task(request: Request, task_id: int, title: str = Form(...), notes: str = Form(""), deadline: str = Form(""), estimated_minutes: int = Form(...), energy_cost: str = Form(...), importance: int = Form(...), progress: int = Form(...)):
    db.update_task(task_id, title, notes, deadline, estimated_minutes, energy_cost, importance, progress)
    return RedirectResponse(url="/", status_code=303)

@app.post("/tasks/{task_id}/progress")
def update_progress(request: Request, task_id: int, progress: int = Form(...)):
    db.update_task_progress(task_id, progress)
    return Response(status_code=200)

@app.post("/checkin", response_class=HTMLResponse)
async def checkin(request: Request, energy: int = Form(...), minutes: int = Form(...)):
    active_tasks = db.get_active_tasks()
    context = {
        "time": datetime.now().strftime("%H:%M"),
        "energy": energy,
        "available_minutes": minutes,
        "tasks": [{"title": t["title"], "notes": t["notes"], "deadline": t["deadline"], "estimated_minutes": t["estimated_minutes"], "energy_cost": t["energy_cost"], "importance": t["importance"]} for t in active_tasks]
    }
    
    try:
        action = await get_next_action(context)
    except Exception as e:
        return f"<div class='error'>AI Error: {e}</div>"

    task_id = None
    task_progress = 0
    chosen_title = action.get("task_title", "").strip().lower()
    
    for t in active_tasks:
        if t["title"].strip().lower() == chosen_title:
            task_id = t["id"]
            task_progress = t["progress"] or 0
            break
            
    if not task_id and active_tasks:
        task_id = active_tasks[0]["id"]
        task_progress = active_tasks[0]["progress"] or 0

    action_id = db.log_action(task_id, action)
    return templates.TemplateResponse(request, "_action_card.html", {"action": action, "action_id": action_id, "task_id": task_id, "task_progress": task_progress})

@app.post("/feedback/{action_id}", response_class=HTMLResponse)
def feedback(request: Request, action_id: int, outcome: str = Form(...)):
    db.record_feedback(action_id, outcome)
    
    if outcome == "done":
        action_data = db.get_action(action_id)
        if action_data and action_data["task_id"]:
            db.increment_task_progress(action_data["task_id"], amount=10)
            
    # Use HX-Redirect to force a clean page reload
    response = Response(status_code=200)
    response.headers["HX-Redirect"] = "/"
    return response