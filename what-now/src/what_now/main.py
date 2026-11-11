from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
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

def render_dashboard_update(request: Request) -> HTMLResponse:
    """Renders the task list and uses HTMX OOB swaps for the count and button."""
    tasks = db.get_active_tasks()
    
    # 1. Main list
    list_html = templates.get_template("_task_list.html").render(tasks=tasks, request=request)
    
    # 2. OOB Counter
    count_html = f'<span id="task-count-badge" class="task-count" hx-swap-oob="true">{len(tasks)} OPEN</span>'
    
    # 3. OOB Submit Button
    disabled = 'disabled title="Add a task first"' if len(tasks) == 0 else ''
    btn_html = f'<button type="submit" id="submit-btn" style="margin-top: 1.5rem;" hx-swap-oob="true" {disabled}>What should I do?</button>'
    
    return HTMLResponse(list_html + count_html + btn_html)

@app.on_event("startup")
def startup():
    db.init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    tasks = db.get_active_tasks()
    stats = db.get_today_stats()
    return templates.TemplateResponse(request, "index.html", {"tasks": tasks, "stats": stats})

@app.post("/tasks", response_class=HTMLResponse)
def create_task(request: Request, title: str = Form(...), notes: str = Form(""), deadline: str = Form(""), estimated_minutes: int = Form(...), energy_cost: str = Form(...), importance: int = Form(...)):
    db.add_task(title, notes, deadline, estimated_minutes, energy_cost, importance)
    return render_dashboard_update(request)

@app.post("/tasks/{task_id}/delete", response_class=HTMLResponse)
def delete_task(request: Request, task_id: int):
    db.delete_task(task_id)
    return render_dashboard_update(request)

@app.post("/tasks/{task_id}/complete", response_class=HTMLResponse)
def complete_task(request: Request, task_id: int):
    db.complete_task(task_id)
    return render_dashboard_update(request)

@app.get("/tasks/{task_id}/edit", response_class=HTMLResponse)
def edit_task_form(request: Request, task_id: int):
    task = db.get_task(task_id)
    return templates.TemplateResponse(request, "_edit_task.html", {"task": task})

@app.post("/tasks/{task_id}/edit", response_class=HTMLResponse)
def cancel_edit(request: Request):
    return render_dashboard_update(request)

@app.post("/tasks/{task_id}/update", response_class=HTMLResponse)
def update_task(request: Request, task_id: int, title: str = Form(...), notes: str = Form(""), deadline: str = Form(""), estimated_minutes: int = Form(...), energy_cost: str = Form(...), importance: int = Form(...), progress: int = Form(...)):
    db.update_task(task_id, title, notes, deadline, estimated_minutes, energy_cost, importance, progress)
    return render_dashboard_update(request)

@app.post("/checkin", response_class=HTMLResponse)
async def checkin(request: Request, energy: int = Form(...), minutes: int = Form(...)):
    tasks = db.get_active_tasks()
    context = {
        "time": datetime.now().strftime("%H:%M"),
        "energy": energy,
        "available_minutes": minutes,
        "tasks": [{"title": t["title"], "notes": t["notes"], "deadline": t["deadline"], "estimated_minutes": t["estimated_minutes"], "energy_cost": t["energy_cost"], "importance": t["importance"]} for t in tasks]
    }
    
    try:
        action = await get_next_action(context)
    except Exception as e:
        return f"<div class='error'>AI Error: {e}</div>"

    task_id = None
    for t in tasks:
        if t["title"].lower() in action["action"].lower():
            task_id = t["id"]
            break

    action_id = db.log_action(task_id, action)
    return templates.TemplateResponse(request, "_action_card.html", {"action": action, "action_id": action_id})

@app.post("/feedback/{action_id}", response_class=HTMLResponse)
def feedback(request: Request, action_id: int, outcome: str = Form(...)):
    db.record_feedback(action_id, outcome)
    
    # If Done, increment task progress
    if outcome == "done":
        action_data = db.get_action(action_id)
        if action_data and action_data["task_id"]:
            db.increment_task_progress(action_data["task_id"], amount=10)
            
    # Must update dashboard (list, counter, button) because progress changed
    stats = db.get_today_stats()
    stats_html = templates.get_template("_stats.html").render(stats=stats, request=request)
    
    tasks = db.get_active_tasks()
    list_html = templates.get_template("_task_list.html").render(tasks=tasks, request=request)
    count_html = f'<span id="task-count-badge" class="task-count" hx-swap-oob="true">{len(tasks)} OPEN</span>'
    disabled = 'disabled title="Add a task first"' if len(tasks) == 0 else ''
    btn_html = f'<button type="submit" id="submit-btn" style="margin-top: 1.5rem;" hx-swap-oob="true" {disabled}>What should I do?</button>'
    
    # We also need to OOB swap the task list back in.
    list_oob = list_html.replace('<ul class="task-items">', '<ul id="task-list-inner" class="task-items" hx-swap-oob="innerHTML:#task-list-container">')
    
    return HTMLResponse(stats_html + count_html + btn_html + list_oob)