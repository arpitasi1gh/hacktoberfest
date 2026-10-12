"""TabPFN-based outdoor window predictor."""

import os
from datetime import date
from dotenv import load_dotenv

from tabpfn_client import TabPFNClassifier, set_access_token
from .history import load_history

load_dotenv()

# Set TabPFN API token once at import
_token = os.getenv("TABPFN_API_KEY")
if _token:
    set_access_token(_token)


def _encode_row(row: dict) -> list[float]:
    """Encode a history row into numeric features for TabPFN."""
    weather_map = {"mild": 2, "hot": 1, "cold": 0, "rainy": 0}
    return [
        float(row["hour"]),
        float(row["sleep_hours"]),
        float(row["screen_time_hours"]),
        float(row["mood"]),
        float(weather_map.get(row["weather"], 1)),
        float(date.fromisoformat(row["date"]).weekday()),
    ]


def predict_best_window(
    sleep_hours: float,
    screen_time_hours: float,
    mood: int,
    weather: str,
) -> dict:
    """Predict the best 30-min window for going outside today.

    Returns:
        {
            "hour": int,
            "probability": float,
            "all_windows": list[dict],
        }
    """
    history = load_history()

    # Fallback if no history yet
    if len(history) < 5:
        return {"hour": 18, "probability": 0.5, "all_windows": []}

    X = [_encode_row(r) for r in history]
    y = [int(r["went_outside"]) for r in history]

    model = TabPFNClassifier()
    model.fit(X, y)

    # Candidate windows: 4 PM to 9 PM
    candidates = []
    for hour in [16, 17, 18, 19, 20, 21]:
        row = {
            "hour": hour,
            "sleep_hours": sleep_hours,
            "screen_time_hours": screen_time_hours,
            "mood": mood,
            "weather": weather,
            "date": date.today().isoformat(),
        }
        candidates.append((hour, _encode_row(row)))

    X_test = [c[1] for c in candidates]
    probs = model.predict_proba(X_test)

    # predict_proba returns shape (n_samples, n_classes)
    # Column 1 = probability of class 1 (went outside)
    results = []
    for i, (hour, _) in enumerate(candidates):
        p = float(probs[i][1]) if len(probs[i]) > 1 else float(probs[i][0])
        results.append({"hour": hour, "probability": round(p, 3)})

    best = max(results, key=lambda r: r["probability"])
    return {
        "hour": best["hour"],
        "probability": best["probability"],
        "all_windows": results,
    }