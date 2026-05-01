---
type: DISCOVERY
date: 2026-05-01
author: agent
session_id: current
project: yield-payment-infrastructure
topic: Signal-to-noise ratio ~1:1 makes yield genuinely hard to forecast
phase: implement
tags: [yield-forecasting, signal-to-noise, reconciliation-gap]
---

## Discovery

Daily yield data has approximately 1:1 signal-to-noise ratio.

## What This Means

For a $50M account @ 4.5%:
- Base daily yield: ~$6,164/day
- Daily volatility (σ): ~$6,827/day
- Signal-to-noise: 0.90x

The noise is almost as large as the signal. This is realistic for actual yield data:
- Actual/actual day-count effects cause ~$80/day variance per $1M balance
- Intraday balance swings add more
- Treasury price fluctuations add regime shifts

## Implications for the Forecast Module

1. **No model will be highly accurate** — MAPE of 15-20% is realistic, not a failure
2. **Walk-forward validation is essential** — simple train/test split would overfit
3. **The reconciliation gap dominates** — even a perfect yield forecast is off by ~1.23 bps/day due to the bank's actual Treasury returns differing from FloatYield's simple interest calculation
4. **The value of forecasting is not accuracy — it's bounded confidence** — knowing the range, not the exact number

## The Core Problem Is the Reconciliation Gap

The yield forecast tells partners what FloatYield *calculates* they'll earn.
The reconciliation gap is what FloatYield's calculation *diverges from*
what the bank actually earned on the same balance.

These are two different problems:
1. Yield forecasting (hard, ~1:1 S/N)
2. Reconciliation gap prediction (structural, deterministic given bank returns)

They should be shown separately in the dashboard, not conflated.

## For Discussion

- Should the dashboard show "forecast yield" vs "reconciled yield" vs "bank actual yield" as three separate lines?
- The gap between forecast and bank actual is the operational risk — should it be highlighted as a separate risk metric?
