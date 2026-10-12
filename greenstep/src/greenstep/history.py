"""Read and append to the outdoor history CSV."""

import csv
from pathlib import Path
from datetime import date

HISTORY_PATH = Path("data/history.csv")
FIELDNAMES = [
    "date", "hour", "sleep_hours", "screen_time_hours",
    "mood", "weather", "went_outside",
]


def load_history() -> list[dict]:
    """Load all rows from the history CSV."""
    if not HISTORY_PATH.exists():
        return []
    with HISTORY_PATH.open(newline="") as f:
        return list(csv.DictReader(f))


def append_row(
    hour: int,
    sleep_hours: float,
    screen_time_hours: float,
    mood: int,
    weather: str,
    went_outside: int,
):
    """Append a new row for today's outcome."""
    row = {
        "date": date.today().isoformat(),
        "hour": hour,
        "sleep_hours": sleep_hours,
        "screen_time_hours": screen_time_hours,
        "mood": mood,
        "weather": weather,
        "went_outside": went_outside,
    }
    file_exists = HISTORY_PATH.exists()
    with HISTORY_PATH.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)