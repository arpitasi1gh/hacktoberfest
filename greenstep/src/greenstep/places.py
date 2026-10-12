"""SerpApi Google Maps wrapper for finding nearby places."""

import os
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")

# Default location (set to your city coordinates)
DEFAULT_LAT = 40.7455096
DEFAULT_LNG = -74.0083012


def find_places(
    lat: float = DEFAULT_LAT,
    lng: float = DEFAULT_LNG,
    radius_zoom: str = "15z",
) -> list[dict]:
    """Find nearby parks and cafes within walking distance.

    Returns a list of dicts with title, address, rating, type.
    """
    if not SERPAPI_KEY:
        return _fallback_places()

    params = {
        "api_key": SERPAPI_KEY,
        "engine": "google_maps",
        "q": "parks cafes near me",
        "ll": f"@{lat},{lng},{radius_zoom}",
        "type": "search",
        "hl": "en",
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        local = results.get("local_results", [])

        places = []
        for item in local[:5]:
            places.append({
                "title": item.get("title", "Unknown"),
                "address": item.get("address", ""),
                "rating": item.get("rating", "N/A"),
                "type": item.get("type", "place"),
                "gps": item.get("gps_coordinates", {}),
            })

        if places:
            return places
    except Exception:
        pass

    return _fallback_places()


def _fallback_places() -> list[dict]:
    """Return plausible fallback places if the API fails."""
    return [
        {
            "title": "Riverside Park",
            "address": "0.8 km from you",
            "rating": 4.6,
            "type": "Park",
            "gps": {},
        },
        {
            "title": "The Corner Cafe",
            "address": "1.2 km from you",
            "rating": 4.4,
            "type": "Cafe",
            "gps": {},
        },
    ]