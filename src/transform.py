import pandas as pd

def make_tidy_frames(city_label: str, hourly_json: dict, daily_json: dict):
    # Hourly tidy
    h = pd.DataFrame({
        "timestamp": pd.to_datetime(hourly_json.get("time", []), utc=False, errors="coerce"),
        "shortwave_radiation": hourly_json.get("shortwave_radiation", []),
    })
    h["city"] = city_label

    # Daily tidy
    d = pd.DataFrame({
        "date": pd.to_datetime(daily_json.get("time", []), utc=False, errors="coerce").dt.date,
        "shortwave_radiation_sum": daily_json.get("shortwave_radiation_sum", []),
    })
    d["city"] = city_label
    return h, d

def compute_rolling(hourly: pd.DataFrame, daily: pd.DataFrame):
    hourly = hourly.dropna(subset=["timestamp"]).copy()
    daily = daily.dropna(subset=["date"]).copy()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values(["city", "date"])
    daily["sum_7d_mean"] = daily.groupby("city")["shortwave_radiation_sum"]\
                               .transform(lambda s: s.rolling(7, min_periods=3).mean())
    return hourly, daily

