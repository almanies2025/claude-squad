"""
Synthetic daily yield history generator for FloatYield forecast models.
Realistic yield variance: signal-to-noise ratio ~1:1.
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta


def generate_yield_series(
    balance: float,
    nominal_rate: float,
    start_date: date,
    days: int = 730,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate synthetic daily yield data.

    Key ratios (per $1M balance):
    - Base daily yield @ 4.5%: ~$123/day
    - Realistic daily variance: ±0.8 bps on balance = ±$80/day per $1M
      (driven by: actual/actual day-count effects, intraday balance swings,
       Treasury price fluctuations)
    - Monthly/quarterly regime shifts: ±3–5 bps shifts that persist weeks

    Components added to base_yield:
    - White noise: σ = 0.5 bps/day (daily operational variance)
    - Regime shifts: 2–3 interest rate events per year (±5 bps, persist 2–6 weeks)
    - Slow drift: ±0.01 bps/day (yield curve normalization)

    Net signal-to-noise ratio: ~1:1.5 — hard to forecast, realistic.
    """
    np.random.seed(seed)
    dates = [start_date + timedelta(days=i) for i in range(days)]

    # 1 basis point = 0.01% = 0.0001
    bps = 0.0001
    base_daily = balance * (nominal_rate / 365)  # e.g. $50M × 4.5%/365 = $6,164/day
    daily_noise_bps = 0.5 * bps * balance  # σ = 0.5 bps on balance

    # White noise (irreducible daily variance)
    white_noise = np.random.normal(0, daily_noise_bps, days)

    # Slow trend drift (±0.01 bps/day = ±$5/day per $50M)
    trend = np.linspace(0, 0.0001 * balance * (days / 365) * 0.5, days)
    trend = trend * (2 * np.random.choice([-1, 1]) * (seed % 2 or 1))

    # Regime shifts (interest rate events)
    # Simulate 2-3 rate events per year: ±5 bps shifts that decay over 2-6 weeks
    regime = np.zeros(days)
    rate_events = [
        (120, -0.0005, 35),  # day 120: -5 bps, lasts 35 days (e.g. rate cut)
        (220, +0.0003, 21),  # day 220: +3 bps, lasts 21 days (rate hike)
        (340, -0.0004, 42),  # day 340: -4 bps, lasts 42 days (economic slowdown)
        (460, +0.0005, 28),  # day 460: +5 bps, lasts 28 days (hot economy)
        (570, -0.0003, 25),  # day 570: -3 bps, lasts 25 days
    ]
    for event_day, delta_bps, duration_days in rate_events:
        if event_day < days:
            for i in range(event_day, min(event_day + duration_days, days)):
                regime[i] = delta_bps * balance * (1 - (i - event_day) / duration_days)

    daily_yield = base_daily + white_noise + trend + regime

    return pd.DataFrame(
        {
            "date": dates,
            "daily_yield": daily_yield,
            "balance": balance,
            "rate": nominal_rate,
            "base_yield": base_daily,
            "noise_bps": white_noise / balance / bps,
            "regime_bps": regime / balance / bps,
        }
    )


def generate_portfolio_history(accounts: list[dict], days: int = 730) -> pd.DataFrame:
    """Generate combined yield history for all accounts."""
    frames = []
    for acct in accounts:
        df = generate_yield_series(
            balance=acct["balance"],
            nominal_rate=acct["rate"],
            start_date=date(2024, 1, 1),
            days=days,
            seed=acct.get("seed", 42),
        )
        df["partner_name"] = acct["name"]
        frames.append(df)
    return pd.concat(frames, ignore_index=True)
