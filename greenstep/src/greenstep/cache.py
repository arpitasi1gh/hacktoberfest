"""Cache predictions keyed on the inputs that produced them."""

import hashlib
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "greenstep.db"


def _key(location: str, sleep: float, screen: float, mood: int) -> str:
    raw = f"{location}|{sleep}|{screen}|{mood}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            key TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    return c


def get(location: str, sleep: float, screen: float, mood: int) -> dict | None:
    with _conn() as c:
        row = c.execute(
            "SELECT payload FROM predictions WHERE key = ?",
            (_key(location, sleep, screen, mood),),
        ).fetchone()
    return json.loads(row["payload"]) if row else None


def set(location: str, sleep: float, screen: float, mood: int, payload: dict) -> None:
    with _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO predictions (key, payload) VALUES (?, ?)",
            (_key(location, sleep, screen, mood), json.dumps(payload)),
        )