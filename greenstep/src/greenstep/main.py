"""Greenstep: predict when to go outside."""

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from .ai_provider import write_action
from .weather import geocode, fetch_weather

from .places import find_places

app = FastAPI(title="Greenstep")


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
      <head>
        <title>Greenstep</title>
        <style>
          body { font-family: system-ui; max-width: 480px; margin: 3rem auto; padding: 1rem; }
          label { display: block; margin: 1rem 0 0.25rem; font-size: 0.9rem; }
          input { width: 100%; padding: 0.5rem; font: inherit; box-sizing: border-box; }
          button { margin-top: 1.5rem; padding: 0.75rem 1rem; width: 100%; font: inherit;
                   background: #2d5a3d; color: white; border: none; border-radius: 8px; }
          .hint { font-size: 0.8rem; color: #888; margin-top: 0.25rem; }
        </style>
      </head>
      <body>
        <h1>🌿 Greenstep</h1>
        <p>Three inputs. Then we predict.</p>

        <form method="post" action="/predict">
          <label>Where are you?
            <input type="text" name="location" value="Delhi" required>
            <div class="hint">City or area name. We'll look up the weather.</div>
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

          <button type="submit">Predict my window</button>
        </form>
      </body>
    </html>
    """


@app.post("/predict", response_class=HTMLResponse)
async def predict(
    location: str = Form(...),
    sleep_hours: float = Form(...),
    screen_hours: float = Form(...),
    mood: int = Form(...),
):
    try:
        place = await geocode(location)
        weather = await fetch_weather(place["lat"], place["lon"])

        # Find real places near the user
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
        return f"""
        <!DOCTYPE html>
        <html><body style="font-family: system-ui; max-width: 480px; margin: 3rem auto; padding: 1rem;">
          <h1>Could not generate</h1>
          <pre>{type(exc).__name__}: {exc}</pre>
          <p><a href="/">← Back</a></p>
        </body></html>
        """

    place_line = ""
    if top_place:
        place_line = f"📍 {top_place['name']}"
        if top_place.get("rating"):
            place_line += f" · ★ {top_place['rating']}"
        if top_place.get("type"):
            place_line += f" · {top_place['type']}"

    return f"""
    <!DOCTYPE html>
    <html>
      <body style="font-family: system-ui; max-width: 480px; margin: 3rem auto; padding: 1rem;">
        <h1>🌿 Greenstep</h1>
        {f'<p style="color: #2d5a3d; font-weight: 600;">{place_line}</p>' if place_line else ''}
        <p style="font-size: 1.15rem; font-weight: 600;">{action['action']}</p>
        <p style="color: #555;">{action['why']}</p>
        <div style="background: #f0f5f1; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
          <p style="margin: 0;"><strong>First step:</strong> {action['first_step']}</p>
          <p style="margin: 0.5rem 0 0;"><strong>Timebox:</strong> {action['duration_minutes']} min</p>
        </div>
        <p style="color: #888; font-style: italic;">{action['fallback']}</p>
        <p style="font-size: 0.8rem; color: #888;">
          {place['name']} · {weather['temperature_c']}°C · {weather['label']}
        </p>
        <p><a href="/">← Back</a></p>
      </body>
    </html>
    """