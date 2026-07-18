"""Generate reproducible mock Google Search Console data for the Salomon case.

Daily brand vs non-brand search demand for Salomon running-shoe queries over
the same March 1 - July 20, 2026 window as the other mock files. Branded
search steps up during the Vestal Pro campaign and stays persistently
elevated afterwards; non-brand demand sees only a small, fading bump.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20260714
START_DATE = pd.Timestamp("2026-03-01")
END_DATE = pd.Timestamp("2026-07-20")
CAMPAIGN_START = pd.Timestamp("2026-06-01")
CAMPAIGN_END = pd.Timestamp("2026-06-20")
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "mock"

BRAND_BASE_CLICKS = 820.0
NONBRAND_BASE_CLICKS = 1450.0
BRAND_CTR = 0.29
NONBRAND_CTR = 0.055


def campaign_phase(date: pd.Timestamp) -> str:
    if date < CAMPAIGN_START:
        return "Pre-campaign"
    if date <= CAMPAIGN_END:
        return "Active campaign"
    return "Post-campaign"


def brand_multiplier(date: pd.Timestamp) -> float:
    """Campaign effect on branded queries: ramps during the flight, then
    settles onto a persistently elevated plateau that decays only slowly."""
    if date < CAMPAIGN_START:
        return 1.0
    if date <= CAMPAIGN_END:
        ramp = (date - CAMPAIGN_START).days / (CAMPAIGN_END - CAMPAIGN_START).days
        return 1.0 + 0.21 * (1 - np.exp(-3.2 * ramp)) / (1 - np.exp(-3.2))
    days_after = (date - CAMPAIGN_END).days
    return 1.0 + 0.13 + 0.07 * np.exp(-days_after / 12.0)


def nonbrand_multiplier(date: pd.Timestamp) -> float:
    """Small awareness spillover on generic queries that fades quickly."""
    if date < CAMPAIGN_START:
        return 1.0
    if date <= CAMPAIGN_END:
        return 1.04
    return 1.0 + 0.04 * np.exp(-(date - CAMPAIGN_END).days / 6.0)


def build_search_console(rng: np.random.Generator) -> pd.DataFrame:
    weekday_factors = np.array([1.04, 1.06, 1.05, 1.03, 1.00, 0.93, 0.91])
    rows = []
    for date in pd.date_range(START_DATE, END_DATE, freq="D"):
        t = (date - START_DATE).days
        trend = 1.0 + 0.0006 * t  # gentle seasonal build into summer
        weekday = weekday_factors[date.dayofweek]

        brand_clicks = (BRAND_BASE_CLICKS * trend * weekday * brand_multiplier(date)
                        * rng.lognormal(0.0, 0.045))
        nonbrand_clicks = (NONBRAND_BASE_CLICKS * trend * weekday * nonbrand_multiplier(date)
                           * rng.lognormal(0.0, 0.04))
        brand_ctr = np.clip(rng.normal(BRAND_CTR, 0.012), 0.24, 0.34)
        nonbrand_ctr = np.clip(rng.normal(NONBRAND_CTR, 0.004), 0.045, 0.068)

        rows.append({
            "date": date,
            "campaign_phase": campaign_phase(date),
            "brand_clicks": int(round(brand_clicks)),
            "brand_impressions": int(round(brand_clicks / brand_ctr)),
            "nonbrand_clicks": int(round(nonbrand_clicks)),
            "nonbrand_impressions": int(round(nonbrand_clicks / nonbrand_ctr)),
        })
    return pd.DataFrame(rows)


def main() -> None:
    rng = np.random.default_rng(SEED)
    frame = build_search_console(rng)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "search_console_daily.csv"
    frame.to_csv(path, index=False)
    print(f"Wrote {path} ({len(frame)} rows, {frame['date'].min():%b %d} - {frame['date'].max():%b %d})")


if __name__ == "__main__":
    main()
