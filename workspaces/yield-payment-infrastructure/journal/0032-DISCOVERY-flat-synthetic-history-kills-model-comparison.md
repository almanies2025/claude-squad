---
type: DISCOVERY
date: 2026-05-01
author: agent
session_id: current
project: yield-payment-infrastructure
topic: Flat synthetic history causes all three forecast models to return identical output — model comparison is broken
phase: analyze
tags: [data-audit, arima, holt, naive, synthetic-history, model-comparison]
---

## Discovery

`POST /forecast/all` generates 60 days of flat in-memory history:
```python
history = [base_yield_daily] * max(60, params.days)  # main.py:293
```

This is 60 identical values. All three models (Naive, Holt, ARIMA) return the same constant output. The model comparison UI — "★ ARIMA winner" and "vs ARIMA" delta — is therefore decorative, not informational.

## Why All Three Models Converge

| Model | On Flat Input | Output |
|-------|--------------|--------|
| Naive | Last value repeated | `base_yield_daily` |
| Holt | Level = last value, trend ≈ 0 | `base_yield_daily` (no trend to apply) |
| ARIMA | Differencing on constant series | No differenced signal → returns last value |

The models are working correctly. The data has no signal. ARIMA's OLS fit on a constant differenced series returns φ ≈ 0, which collapses the AR(1) to a naive forecast.

## What Real Yield History Looks Like

`scripts/forecast_models/data_generator.py` produces realistic history with:
- White noise (σ = 0.5 bps/day)
- Regime shifts (±3–5 bps, decaying over weeks)
- Slow drift

On that data, ARIMA genuinely outperformed naive by +$1,745/day in the offline validation (journal 0028). The model selection is valid — it just cannot be demonstrated in the live API without real `yield_events` data.

## The ADR This Demands

**Proposed ADR-06**: Suppress the "★ ARIMA winner" badge and "vs ARIMA" delta column in Sprint 1. Keep the three-model structure for when real history is connected. Add disclosure: "Model comparison requires live yield data — currently showing synthetic baseline."

## For Discussion

- Is the three-model display valuable as a structural preview even without real differentiation? (Partners see the concept.)
- Should we build a mock yield_events populator for Sprint 2 demo continuity — generating plausible synthetic rows that look like real bank statements?
