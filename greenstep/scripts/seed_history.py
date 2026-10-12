"""Generate plausible outdoor history for TabPFN training.
Run: uv run python scripts/seed_history.py
Writes: data/history.csv
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

WEATHER = ["mild", "mild", "mild", "hot", "cold", "rainy"]
HOURS = [16, 17, 18, 19, 20]

rows = []
start = date.today() - timedelta(days=30)

for day_offset in range(30):
    d = start + timedelta(days=day_offset)
    is_weekend = d.weekday() >= 5

    sleep = round(random.uniform(5.5, 9.0), 1)
    screen = round(random.uniform(2.0, 10.0), 1)
    mood = random.choices([1, 2, 3, 4, 5], weights=[1, 2, 4, 4, 2])[0]
    weather = random.choice(WEATHER)

    for hour in HOURS:
        p = 0.15
        if sleep >= 7.0: p += 0.15
        if screen <= 4.0: p += 0.15
        if mood >= 4: p += 0.20
        if weather == "mild": p += 0.15
        if is_weekend: p += 0.10
        if hour in (17, 18, 19): p += 0.20
        if hour >= 20: p -= 0.15
        p = max(0.02, min(0.95, p))
        went = 1 if random.random() < p else 0

        rows.append({
            "date": d.isoformat(),
            "hour": hour,
            "sleep_hours": sleep,
            "screen_time_hours": screen,
            "mood": mood,
            "weather": weather,
            "went_outside": went,
        })

out = Path("data/history.csv")
out.parent.mkdir(exist_ok=True)
with out.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to {out}")