---
type: DECISION
date: 2026-05-01
author: co-authored
session_id: current
project: yield-payment-infrastructure
topic: ARIMA(1,1,1) wins forecast model bake-off
phase: implement
tags: [forecasting, arima, naive, holt-winters, model-selection]
---

## Decision

Selected ARIMA(1,1,1) as the default forecast model for all partner accounts.

## Validation Results

Walk-forward time-series validation: 5 windows × 30-day test, 180-day training minimum.

**Portfolio ($248M combined, 3 accounts):**

| Model | Portfolio MAE/day | vs Naive |
|-------|-------------------|----------|
| ARIMA(1,1,1) | $11,106 | +$1,745/day better |
| Naive (Persistence) | $12,851 | baseline |
| Holt-Winters | $31,713 | −$18,862/day worse |

**Per-account winners:** ARIMA(1,1,1) won on all 3 accounts.

## Why ARIMA Wins

- Daily yield has ~1:1 signal-to-noise ratio — hard but not impossible to forecast
- ARIMA(1,1,1) captures momentum after rate regime shifts without overfitting
- Naive is competitive but ARIMA edges it out on all accounts
- Holt-Winters adds trend estimation which amplifies noise on daily data

## Why Holt-Winters Loses Badly

Daily yield has no reliable directional trend — it oscillates around a mean. Adding trend estimation on top of noisy daily data means the model chases noise, resulting in forecasts that are systematically worse than naive.

## Why This Matters for the Reconciliation Problem

The reconciliation gap (~1.23 bps) is the core operational risk.
Better forecast accuracy means FloatYield can predict the gap before month-end,
not just explain it after. This is what makes the contract-level tolerance
threshold negotiation possible.

## Model Selection Policy

- Default: ARIMA(1,1,1) for all accounts
- Naive (Persistence): fallback if ARIMA overfits on small accounts
- Holt-Winters: NOT recommended for daily yield forecasting

## Files

- `scripts/forecast_models/data_generator.py` — synthetic yield history generator
- `scripts/forecast_models/models.py` — NaiveYield, HoltYield, ARIMAYield classes
- `scripts/forecast_models/validate.py` — walk-forward validation engine
- `scripts/forecast_models/report.py` — full comparison report
- `backend/model_comparison.json` — serialized validation results
