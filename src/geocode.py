import requests

def geocode_city(query: str, count: int = 1):
    """
    Use Open-Meteo Geocoding API to resolve a city string to lat/lon.
    Returns dict with latitude, longitude, name, country, timezone.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": query, "count": count, "language": "en", "format": "json"}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    results = data.get("results", [])
    if not results:
        return None
    top = results[0]
    return {
        "name": top.get("name"),
        "country": top.get("country_code"),
        "latitude": top.get("latitude"),
        "longitude": top.get("longitude"),
        "timezone": top.get("timezone"),
    }

