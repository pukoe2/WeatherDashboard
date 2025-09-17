#!/usr/bin/env python3
import argparse
from pathlib import Path
import pandas as pd
from src.geocode import geocode_city
from src.fetch_openmeteo import fetch_hourly_daily
from src.transform import make_tidy_frames, compute_rolling
from src.plots import plot_lines, plot_weekly_bars

def parse_args():
    p = argparse.ArgumentParser(description="WeatherDashboard – Solar Irradiance (Open-Meteo)")
    p.add_argument("--cities", nargs="+", required=True, help="City names (e.g., 'Montreal,CA' 'Teresina,BR')")
    p.add_argument("--days", type=int, default=30, help="How many past days (max ~92)")
    p.add_argument("--timezone", type=str, default="auto", help="IANA timezone (e.g., America/Toronto) or 'auto'")
    p.add_argument("--outdir", type=str, default=".", help="Output base directory")
    p.add_argument("--verbose", action="store_true", help="Print progress")
    return p.parse_args()

def main():
    args = parse_args()
    if args.verbose:
        print(f"[ARGS] {args}")

    outdir = Path(args.outdir)
    data_dir = outdir / "data"
    charts_dir = outdir / "charts"
    data_dir.mkdir(parents=True, exist_ok=True)
    charts_dir.mkdir(parents=True, exist_ok=True)

    all_hourly, all_daily = [], []

    for city in args.cities:
        if args.verbose:
            print(f"[STEP] Geocoding: {city}")
        loc = geocode_city(city)
        if loc is None:
            print(f"[WARN] Could not geocode: {city}")
            continue

        lat, lon, tz = loc["latitude"], loc["longitude"], loc.get("timezone")
        tz_to_use = args.timezone if args.timezone.lower() != "auto" else (tz or "UTC")
        if args.verbose:
            print(f"[OK] {city} -> ({lat:.4f}, {lon:.4f}) tz={tz_to_use}")

        if args.verbose:
            print(f"[STEP] Fetching Open-Meteo for {city}")
        hourly_json, daily_json = fetch_hourly_daily(lat, lon, past_days=args.days, timezone=tz_to_use)
        if args.verbose:
            print(f"[OK] Received hourly={len(hourly_json.get('time', []))} daily={len(daily_json.get('time', []))}")

        hourly_df, daily_df = make_tidy_frames(city, hourly_json, daily_json)
        all_hourly.append(hourly_df)
        all_daily.append(daily_df)

    if not all_hourly:
        print("[EXIT] No data fetched. Exiting.")
        return

    hourly = pd.concat(all_hourly, ignore_index=True)
    daily  = pd.concat(all_daily,  ignore_index=True)

    if args.verbose:
        print(f"[STEP] Computing rolling means on {len(daily)} daily rows")
    hourly, daily = compute_rolling(hourly, daily)

    # Save CSVs
    hourly_csv = data_dir / "hourly_shortwave_radiation.csv"
    daily_csv  = data_dir / "daily_shortwave_radiation_sum.csv"
    hourly.to_csv(hourly_csv, index=False)
    daily.to_csv(daily_csv, index=False)
    if args.verbose:
        print(f"[OK] Saved CSVs: {hourly_csv} , {daily_csv}")

    # Charts
    if args.verbose:
        print("[STEP] Creating plots")
    plot_lines(daily, charts_dir / "daily_radiation_sum_lines.png")
    plot_weekly_bars(daily, charts_dir / "weekly_best_worst.png")

    print(f"[DONE] CSVs in {data_dir} ; charts in {charts_dir}")

if __name__ == "__main__":
    main()

