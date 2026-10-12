"""Greenstep: predict when to go outside."""

from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .ai_provider import write_action
from .weather import geocode, fetch_weather
from .places import find_places
from . import cache

app = FastAPI(title="Greenstep")

BASE = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")


def _page(body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Greenstep</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <main class="container">
    {body}
  </main>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def home():
    return _page(_form_body())


def _form_body() -> str:
    return """
    <header>
      <h1>🌿 Greenstep</h1>
      <p class="tagline">Your window is predicted, not asked for.</p>
    </header>

    <section class="card">
      <form method="post" action="/predict">
        <label>Where are you?
          <input type="text" name="location" value="Delhi" required>
          <span class="hint">City or area. We'll look up the weather and find real places nearby.</span>
        </label>
        <label>Sleep last night (hours)
          <input type="number" name="sleep_hours" step="0.1" value="7.0" required>
        </label>
        <label>Screen time so far today (hours)
          <input type="number" name="screen_hours" step="0.1" value="5.0" required>
        </label>
        <label>Mood (1–5)
          <input type="number" name="mood" min="1" max="5" value="3" required>
        </label>
        <button type="submit" class="primary">Predict my window</button>
      </form>
    </section>
    """


@app.post("/predict", response_class=HTMLResponse)
async def predict(
    location: str = Form(...),
    sleep_hours: float = Form(...),
    screen_hours: float = Form(...),
    mood: int = Form(...),
):
    cached = cache.get(location, sleep_hours, screen_hours, mood)
    if cached:
        return _page(_result_body(cached))

    try:
        place = await geocode(location)
        weather = await fetch_weather(place["lat"], place["lon"])
        real_places = find_places(place["lat"], place["lon"])
        top_place = real_places[0] if real_places else None

        action = await write_action(
            sleep_hours=sleep_hours,
            screen_hours=screen_hours,
            mood=mood,
            location=place["name"],
            weather_label=weather["label"],
            temperature_c=weather["temperature_c"],
            top_place=top_place,
        )
    except Exception as exc:
        body = f"""
        <header><h1>🌿 Greenstep</h1></header>
        <div class="error">
          <h2>Could not generate</h2>
          <pre>{type(exc).__name__}: {exc}</pre>
        </div>
        <a href="/" class="back-link">← Back</a>
        """
        return _page(body)

    payload = {
        "action": action,
        "place": place,
        "top_place": top_place,
        "weather": weather,
    }
    cache.set(location, sleep_hours, screen_hours, mood, payload)
    return _page(_result_body(payload))


def _result_body(payload: dict) -> str:
    action = payload["action"]
    place = payload["place"]
    top_place = payload["top_place"]
    weather = payload["weather"]

    place_html = ""
    if top_place:
        rating = f'<span class="rating">★ {top_place["rating"]}</span>' if top_place.get("rating") else ""
        place_html = f"""
        <div class="place-chip">
          <span class="icon">📍</span>
          <span class="name">{top_place['name']}</span>
          <span class="dot">·</span>
          <span>{top_place.get('type', 'place')}</span>
          {rating}
        </div>
        """

    return f"""
    <header><h1>🌿 Greenstep</h1></header>

    <section class="card action-card">
      {place_html}
      <p class="action-text">{action['action']}</p>
      <p class="action-why">{action['why']}</p>
      <div class="action-meta">
        <span class="first-step">First step: {action['first_step']}</span>
        <span class="timebox">{action['duration_minutes']} min</span>
      </div>
      <p class="fallback">{action['fallback']}</p>
    </section>

    <p class="meta-footer">
      {place['name']} · {weather['temperature_c']}°C · {weather['label']}
    </p>

    <a href="/" class="back-link" style="margin-top: 2rem;">← Try different inputs</a>
    """