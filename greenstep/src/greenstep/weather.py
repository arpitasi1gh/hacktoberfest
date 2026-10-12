"""Geocode a city name and fetch current weather. No API keys required."""

import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Nominatim's usage policy requires an identifying User-Agent
HEADERS = {"User-Agent": "Greenstep/0.1 (personal project)"}


async def geocode(city: str) -> dict:
    """Return {'name': ..., 'lat': ..., 'lon': ...} for a city name."""
    params = {"q": city, "format": "json", "limit": 1}
    async with httpx.AsyncClient(timeout=15.0, headers=HEADERS) as client:
        r = await client.get(NOMINATIM_URL, params=params)
        r.raise_for_status()
        results = r.json()

    if not results:
        raise ValueError(f"Could not find a place called '{city}'.")

    top = results[0]

    # Nominatim returns names like "SubCentre, Delhi, India".
    # Prefer the city-level fragment (usually third-from-last in the list),
    # falling back to the first fragment if the list is short.
    parts = [p.strip() for p in top["display_name"].split(",")]
    if len(parts) >= 3:
        name = parts[-3]
    elif len(parts) == 2:
        name = parts[0]
    else:
        name = parts[0]

    return {
        "name": name,
        "full_name": top["display_name"],
        "lat": float(top["lat"]),
        "lon": float(top["lon"]),
    }


async def fetch_weather(lat: float, lon: float) -> dict:
    """Return current weather for coordinates. Includes a simplified label."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weather_code,wind_speed_10m",
        "timezone": "auto",
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(OPEN_METEO_URL, params=params)
        r.raise_for_status()
        data = r.json()

    current = data["current"]
    temp = current["temperature_2m"]
    code = current["weather_code"]

    return {
        "temperature_c": temp,
        "wind_kmh": current["wind_speed_10m"],
        "label": _label(temp, code),
        "raw_code": code,
    }


def _label(temp: float, code: int) -> str:
    """Map Open-Meteo weather code + temperature to a simple label."""
    if code in (51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99):
        return "rainy"
    if temp >= 32:
        return "hot"
    if temp <= 12:
        return "cold"
    return "mild"