import sqlite3
from pathlib import Path
from datetime import date

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "whatnow.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    notes TEXT,
    deadline TEXT,
    estimated_minutes INTEGER,
    energy_cost TEXT CHECK (energy_cost IN ('low', 'medium', 'high')),
    importance INTEGER DEFAULT 3,
    progress INTEGER DEFAULT 0,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    why TEXT NOT NULL,
    first_step TEXT NOT NULL,
    timebox_minutes INTEGER NOT NULL,
    fallback TEXT NOT NULL,
    outcome TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
"""

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)

def get_active_tasks():
    with get_conn() as conn:
        # Only return tasks that are not completed and progress is under 100
        return [dict(r) for r in conn.execute("SELECT * FROM tasks WHERE completed_at IS NULL AND (progress IS NULL OR progress < 100)").fetchall()]

def get_task(task_id):
    with get_conn() as conn:
        return dict(conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone())

def add_task(title, notes, deadline, estimated_minutes, energy_cost, importance):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO tasks (title, notes, deadline, estimated_minutes, energy_cost, importance) VALUES (?, ?, ?, ?, ?, ?)",
            (title, notes, deadline, estimated_minutes, energy_cost, importance)
        )

def update_task(task_id, title, notes, deadline, estimated_minutes, energy_cost, importance, progress):
    with get_conn() as conn:
        # If progress hits 100, auto-complete the task
        if progress >= 100:
            conn.execute(
                "UPDATE tasks SET title=?, notes=?, deadline=?, estimated_minutes=?, energy_cost=?, importance=?, progress=?, completed_at=datetime('now') WHERE id=?",
                (title, notes, deadline, estimated_minutes, energy_cost, importance, progress, task_id)
            )
        else:
            conn.execute(
                "UPDATE tasks SET title=?, notes=?, deadline=?, estimated_minutes=?, energy_cost=?, importance=?, progress=?, completed_at=NULL WHERE id=?",
                (title, notes, deadline, estimated_minutes, energy_cost, importance, progress, task_id)
            )

def delete_task(task_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

def complete_task(task_id):
    with get_conn() as conn:
        conn.execute("UPDATE tasks SET completed_at = datetime('now'), progress = 100 WHERE id = ?", (task_id,))

def increment_task_progress(task_id, amount=10):
    with get_conn() as conn:
        task = conn.execute("SELECT progress FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if task:
            new_prog = min(100, (task["progress"] or 0) + amount)
            if new_prog >= 100:
                conn.execute("UPDATE tasks SET progress = 100, completed_at = datetime('now') WHERE id = ?", (task_id,))
            else:
                conn.execute("UPDATE tasks SET progress = ? WHERE id = ?", (new_prog, task_id))

def log_action(task_id, action_data):
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO actions (task_id, action, why, first_step, timebox_minutes, fallback) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (task_id, action_data["action"], action_data["why"], action_data["first_step"], action_data["timebox_minutes"], action_data["fallback"])
        )
        return cur.lastrowid

def get_action(action_id):
    with get_conn() as conn:
        return dict(conn.execute("SELECT * FROM actions WHERE id = ?", (action_id,)).fetchone())

def record_feedback(action_id, outcome):
    with get_conn() as conn:
        conn.execute("UPDATE actions SET outcome = ? WHERE id = ?", (outcome, action_id))

def get_today_stats():
    with get_conn() as conn:
        today = date.today().isoformat()
        row = conn.execute("""
            SELECT 
                SUM(CASE WHEN outcome = 'done' THEN 1 ELSE 0 END) as done,
                SUM(CASE WHEN outcome = 'skip' THEN 1 ELSE 0 END) as skip,
                SUM(CASE WHEN outcome = 'blocked' THEN 1 ELSE 0 END) as blocked
            FROM actions WHERE date(created_at) = ?
        """, (today,)).fetchone()
        return {"done": row["done"] or 0, "skip": row["skip"] or 0, "blocked": row["blocked"] or 0}