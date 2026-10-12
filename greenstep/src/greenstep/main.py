"""Greenstep: passive outdoor prediction + real places."""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .predictor import predict_best_window
from .places import find_places
from .ai_provider import write_action
from .history import append_row

app = FastAPI(title="Greenstep")

BASE = Path(__file__).resolve().parent.parent.parent
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE / "templates"))

# Track the last prediction so "I did it" can log it
_last_prediction: dict = {}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Home page: run prediction and show one action."""
    global _last_prediction

    # Today's conditions (you can wire these to real sensors later)
    today = {
        "sleep_hours": 7.2,
        "screen_time_hours": 4.5,
        "mood": 4,
        "weather": "mild",
    }

    # 1. TabPFN predicts best window
    prediction = predict_best_window(**today)

    # 2. SerpApi finds real places
    places = find_places()
    top_place = places[0] if places else {"title": "a nearby park", "type": "Park"}

    # 3. Gemma writes the action
    action = write_action(
        window_hour=prediction["hour"],
        window_probability=prediction["probability"],
        place=top_place,
        **today,
    )

    _last_prediction = {
        **today,
        "hour": prediction["hour"],
        "places": places,
    }

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "action": action,
            "prediction": prediction,
            "place": top_place,
            "places": places,
            "today": today,
        },
    )


@app.post("/done")
async def mark_done():
    """User clicked 'I did it' — append to history for tomorrow's prediction."""
    if _last_prediction:
        append_row(
            hour=_last_prediction.get("hour", 18),
            sleep_hours=_last_prediction.get("sleep_hours", 7.0),
            screen_time_hours=_last_prediction.get("screen_time_hours", 5.0),
            mood=_last_prediction.get("mood", 3),
            weather=_last_prediction.get("weather", "mild"),
            went_outside=1,
        )
    return RedirectResponse(url="/", status_code=303)