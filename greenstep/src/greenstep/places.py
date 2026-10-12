"""Find real places near a location using SerpApi's Google Maps engine."""

import os

from dotenv import load_dotenv
load_dotenv()

import serpapi

SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")


def find_places(lat: float, lon: float, query: str = "cafes and parks", limit: int = 3):
    """Search Google Maps for real places near coordinates.

    Uses `ll` (GPS origin) instead of `location` — `location` requires a
    companion zoom parameter and is rejected by SerpApi without one.
    """
    if not SERPAPI_KEY:
        raise RuntimeError("SERPAPI_KEY not set. Add it to your .env file.")

    client = serpapi.Client(api_key=SERPAPI_KEY)
    results = client.search({
        "engine": "google_maps",
        "q": query,
        "ll": f"@{lat},{lon},14z",
        "type": "search",
    })

    places = []
    for r in results.get("local_results", [])[:limit]:
        places.append({
            "name": r.get("title", "a nearby place"),
            "address": r.get("address"),
            "rating": r.get("rating"),
            "type": r.get("type", "place"),
            "reviews": r.get("reviews"),
        })
    return places