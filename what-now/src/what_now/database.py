from collections.abc import Iterator
from contextlib import contextmanager
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "whatnow.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    notes TEXT,
    deadline TEXT,
    estimated_minutes INTEGER NOT NULL,
    energy_cost TEXT NOT NULL CHECK (energy_cost IN ('low', 'medium', 'high')),
    importance INTEGER NOT NULL CHECK (importance BETWEEN 1 AND 5),
    progress INTEGER NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
    task_title TEXT,
    action TEXT NOT NULL,
    why TEXT NOT NULL,
    first_step TEXT NOT NULL,
    timebox_minutes INTEGER NOT NULL,
    fallback TEXT NOT NULL,
    outcome TEXT CHECK (outcome IN ('done', 'skip', 'blocked')),
    feedback_note TEXT,
    progress_before INTEGER,
    progress_after INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Yield a named-column connection and always close it after the transaction."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _add_column_if_missing(
    connection: sqlite3.Connection,
    table: str,
    column: str,
    definition: str,
) -> None:
    columns = {
        row["name"]
        for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
    }
    if column not in columns:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db() -> None:
    """Create current tables and safely migrate databases from earlier versions."""
    with get_connection() as connection:
        connection.executescript(SCHEMA)
        user_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(users)").fetchall()
        }
        if "full_name" not in user_columns and "display_name" in user_columns:
            connection.execute("ALTER TABLE users RENAME COLUMN display_name TO full_name")
        else:
            _add_column_if_missing(connection, "users", "full_name", "TEXT")
            if "display_name" in user_columns:
                connection.execute(
                    "UPDATE users SET full_name = display_name WHERE full_name IS NULL"
                )
            if "username" in user_columns:
                connection.execute(
                    "UPDATE users SET full_name = username "
                    "WHERE full_name IS NULL OR trim(full_name) = ''"
                )
        _add_column_if_missing(connection, "users", "email", "TEXT")
        connection.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email "
            "ON users(email COLLATE NOCASE)"
        )
        _add_column_if_missing(connection, "tasks", "notes", "TEXT")
        _add_column_if_missing(
            connection,
            "tasks",
            "progress",
            "INTEGER NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100)",
        )
        _add_column_if_missing(
            connection,
            "tasks",
            "user_id",
            "INTEGER REFERENCES users(id) ON DELETE CASCADE",
        )
        _add_column_if_missing(
            connection,
            "actions",
            "user_id",
            "INTEGER REFERENCES users(id) ON DELETE CASCADE",
        )
        _add_column_if_missing(connection, "actions", "task_title", "TEXT")
        _add_column_if_missing(connection, "actions", "feedback_note", "TEXT")
        _add_column_if_missing(connection, "actions", "progress_before", "INTEGER")
        _add_column_if_missing(connection, "actions", "progress_after", "INTEGER")
        connection.execute(
            "UPDATE tasks SET progress = 100 "
            "WHERE completed_at IS NOT NULL AND progress = 0"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_tasks_user_active "
            "ON tasks(user_id, completed_at, deadline)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_actions_user_created "
            "ON actions(user_id, created_at)"
        )
        user_count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if user_count == 1:
            sole_user_id = connection.execute("SELECT id FROM users").fetchone()["id"]
            connection.execute(
                "UPDATE tasks SET user_id = ? WHERE user_id IS NULL",
                (sole_user_id,),
            )
            connection.execute(
                "UPDATE actions SET user_id = ? WHERE user_id IS NULL",
                (sole_user_id,),
            )


def get_user_by_email(email: str) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE email = ? COLLATE NOCASE",
            (email,),
        ).fetchone()
    return dict(row) if row else None


def get_user_for_login(identifier: str) -> dict | None:
    with get_connection() as connection:
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(users)").fetchall()
        }
        if "username" in columns:
            row = connection.execute(
                "SELECT * FROM users WHERE email = ? COLLATE NOCASE "
                "OR username = ? COLLATE NOCASE",
                (identifier, identifier),
            ).fetchone()
        else:
            row = connection.execute(
                "SELECT * FROM users WHERE email = ? COLLATE NOCASE",
                (identifier,),
            ).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, full_name, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def create_user(full_name: str, email: str, password_hash: str) -> int:
    with get_connection() as connection:
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(users)").fetchall()
        }
        if "username" in columns:
            cursor = connection.execute(
                "INSERT INTO users (full_name, email, username, password_hash) "
                "VALUES (?, ?, ?, ?)",
                (full_name, email, email, password_hash),
            )
        else:
            cursor = connection.execute(
                "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
                (full_name, email, password_hash),
            )
        user_id = int(cursor.lastrowid)
        user_count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if user_count == 1:
            connection.execute(
                "UPDATE tasks SET user_id = ? WHERE user_id IS NULL",
                (user_id,),
            )
            connection.execute(
                "UPDATE actions SET user_id = ? WHERE user_id IS NULL",
                (user_id,),
            )
        return user_id


def list_tasks(user_id: int, include_completed: bool = False) -> list[dict]:
    query = "SELECT * FROM tasks WHERE user_id = ?"
    if not include_completed:
        query += " AND completed_at IS NULL"
    query += " ORDER BY completed_at IS NOT NULL, deadline IS NULL, deadline ASC, id DESC"
    with get_connection() as connection:
        rows = connection.execute(query, (user_id,)).fetchall()
    return [dict(row) for row in rows]


def get_task(user_id: int, task_id: int) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id),
        ).fetchone()
    return dict(row) if row else None


def add_task(
    user_id: int,
    title: str,
    notes: str,
    deadline: str,
    daily_minutes: int,
    energy_cost: str,
    importance: int,
) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """INSERT INTO tasks
               (user_id, title, notes, deadline, estimated_minutes, energy_cost, importance)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
               (user_id, title, notes, deadline, daily_minutes, energy_cost, importance),
        )
        return int(cursor.lastrowid)


def update_task(
    user_id: int,
    task_id: int,
    title: str,
    notes: str,
    deadline: str,
    daily_minutes: int,
    energy_cost: str,
    importance: int,
    progress: int,
) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            """UPDATE tasks
               SET title = ?, notes = ?, deadline = ?, estimated_minutes = ?,
                   energy_cost = ?, importance = ?, progress = ?,
                   completed_at = CASE
                       WHEN ? = 100 THEN COALESCE(completed_at, datetime('now'))
                       ELSE NULL
                   END
               WHERE id = ? AND user_id = ?""",
            (
                title,
                notes,
                deadline,
                daily_minutes,
                energy_cost,
                importance,
                progress,
                progress,
                task_id,
                user_id,
            ),
        )
    return cursor.rowcount > 0


def set_task_completed(user_id: int, task_id: int, completed: bool) -> bool:
    with get_connection() as connection:
        if completed:
            cursor = connection.execute(
                """UPDATE tasks SET completed_at = datetime('now')
                   WHERE id = ? AND user_id = ? AND progress = 100""",
                (task_id, user_id),
            )
        else:
            cursor = connection.execute(
                """UPDATE tasks SET completed_at = NULL,
                   progress = CASE WHEN progress = 100 THEN 99 ELSE progress END
                   WHERE id = ? AND user_id = ?""",
                (task_id, user_id),
            )
    return cursor.rowcount > 0


def delete_task(user_id: int, task_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id),
        )
    return cursor.rowcount > 0


def record_action_outcome(
    user_id: int,
    task_id: int | None,
    action: dict,
    outcome: str,
    feedback_note: str | None = None,
    progress_after: int | None = None,
) -> int | None:
    with get_connection() as connection:
        task = (
            connection.execute(
                "SELECT title, progress FROM tasks WHERE id = ? AND user_id = ?",
                (task_id, user_id),
            ).fetchone()
            if task_id is not None
            else None
        )
        progress_before = task["progress"] if task else action.get("progress")
        if task is not None and outcome == "done":
            if progress_after is None or not progress_before < progress_after <= 100:
                return None
            connection.execute(
                """UPDATE tasks SET progress = ?,
                   completed_at = CASE
                       WHEN ? = 100 THEN datetime('now')
                       ELSE NULL
                   END
                   WHERE id = ? AND user_id = ?""",
                (progress_after, progress_after, task_id, user_id),
            )
        elif task_id is not None and task is None and outcome == "done":
            if (
                not isinstance(progress_before, int)
                or progress_after is None
                or not progress_before < progress_after <= 100
            ):
                return None
        elif task is not None:
            progress_after = progress_before

        if task is None:
            task_id = None
        cursor = connection.execute(
            """INSERT INTO actions
               (user_id, task_id, task_title, action, why, first_step,
                timebox_minutes, fallback, outcome, feedback_note,
                progress_before, progress_after)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                task_id,
                task["title"] if task else action.get("task_title"),
                action["action"],
                action["why"],
                action["first_step"],
                action["timebox_minutes"],
                action["fallback"],
                outcome,
                feedback_note,
                progress_before,
                progress_after,
            ),
        )
        return int(cursor.lastrowid)


def list_recent_suggestions(user_id: int, limit: int = 5) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """SELECT task_title, action, why, first_step, timebox_minutes, fallback,
                      outcome, feedback_note, progress_before, progress_after
               FROM actions
               WHERE user_id = ? AND outcome IS NOT NULL
               ORDER BY id DESC
               LIMIT ?""",
            (user_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def get_progress_stats(user_id: int) -> dict:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
              (SELECT COUNT(*) FROM tasks
               WHERE user_id = ? AND completed_at IS NOT NULL) AS done,
              (SELECT COUNT(*) FROM tasks
               WHERE user_id = ? AND completed_at IS NULL) AS open,
              (SELECT COUNT(*) FROM actions
               WHERE user_id = ? AND outcome = 'skip'
                 AND date(created_at, 'localtime') = date('now', 'localtime')) AS skip_today,
              (SELECT COUNT(*) FROM actions
               WHERE user_id = ? AND outcome = 'blocked'
                 AND date(created_at, 'localtime') = date('now', 'localtime')) AS blocked_today,
              (SELECT COUNT(*) FROM actions
               WHERE user_id = ? AND outcome = 'done'
                 AND date(created_at, 'localtime') = date('now', 'localtime'))
              +
              (SELECT COUNT(*) FROM tasks t
               WHERE t.user_id = ? AND t.completed_at IS NOT NULL
                 AND date(t.completed_at, 'localtime') = date('now', 'localtime')
                 AND NOT EXISTS (
                   SELECT 1 FROM actions a
                   WHERE a.task_id = t.id AND a.user_id = t.user_id
                     AND a.outcome = 'done'
                     AND date(a.created_at, 'localtime') = date('now', 'localtime')
                 )) AS done_today
            """,
            (user_id, user_id, user_id, user_id, user_id, user_id),
        ).fetchone()
    return {
        "done": row["done"] or 0,
        "open": row["open"] or 0,
        "done_today": row["done_today"] or 0,
        "skip_today": row["skip_today"] or 0,
        "blocked_today": row["blocked_today"] or 0,
    }


def list_recent_actions(user_id: int, limit: int = 20) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT a.id, a.action, a.outcome, a.created_at,
                   a.feedback_note, a.progress_before, a.progress_after,
                   COALESCE(a.task_title, t.title) AS task_title
            FROM actions a
            LEFT JOIN tasks t ON t.id = a.task_id
            WHERE a.user_id = ?
            ORDER BY a.id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def delete_all_history(user_id: int) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM actions WHERE user_id = ?", (user_id,))
