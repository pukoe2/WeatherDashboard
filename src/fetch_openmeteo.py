import requests

def fetch_hourly_daily(lat: float, lon: float, past_days: int = 30, timezone: str = "UTC"):
    """
    Fetch hourly shortwave radiation and daily sum for past N days + today.
    Returns two JSON payloads: (hourly_json, daily_json).
    """
    base = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "shortwave_radiation",
        "daily": "shortwave_radiation_sum",
        "past_days": past_days,
        "forecast_days": 1,
        "timezone": timezone,
    }
    r = requests.get(base, params=params, timeout=30)
    r.raise_for_status()
    js = r.json()
    hourly_json = {
        "time": js.get("hourly", {}).get("time", []),
        "shortwave_radiation": js.get("hourly", {}).get("shortwave_radiation", []),
        "units": {"shortwave_radiation": js.get("hourly_units", {}).get("shortwave_radiation", "W/m²")},
    }
    daily_json = {
        "time": js.get("daily", {}).get("time", []),
        "shortwave_radiation_sum": js.get("daily", {}).get("shortwave_radiation_sum", []),
        "units": {"shortwave_radiation_sum": js.get("daily_units", {}).get("shortwave_radiation_sum", "Wh/m²")},
    }
    return hourly_json, daily_json

