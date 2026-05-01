---
type: FIX
date: 2026-05-01
created_at: 2026-05-01T15:30:00Z
author: agent
session_id: current
session_turn: 1
project: yield-payment-infrastructure
topic: Rate environment integration — scenario parameter now affects model predictions
phase: implement
tags: [rate-scenario, holt, arima, naive, parallel-shift, scenario-multiplier]
---

## Problem

`rate_scenario` was a label only. The `POST /forecast/all` endpoint computed a scenario-adjusted `base_rate` (lines 463-466 before fix) but then never used it. All three models — Naive, Holt, and ARIMA —forecast from the historical `daily_yield` series generated at the **base** yield rate, unaffected by the requested scenario.

Pattern 4 in journal 0042 ("Rate environment blindness") documented this gap.

## Fix

**`backend/app/main.py:463-510`**

Introduced `scenario_multiplier` as an explicit parallel-shift coefficient:

```python
scenario_multiplier = 1.0
if params.rate_scenario == "stress":
    scenario_multiplier = 0.85   # Fed cuts 50bps → -15%
elif params.rate_scenario == "upside":
    scenario_multiplier = 1.10   # Fed hikes 30bps → +10%

# ... history loaded ...

# Apply scenario parallel shift to all model outputs (dollar terms).
if scenario_multiplier != 1.0:
    naive_preds = [p * scenario_multiplier for p in naive_preds]
    holt_preds  = [p * scenario_multiplier for p in holt_preds]
    arima_preds = [p * scenario_multiplier for p in arima_preds]
```

The `yield_rate` in the API response now returns `base_rate * scenario_multiplier` (e.g., 4.5% base → 3.825% stress → 4.95% upside).

## Verification

Account 1, 30-day forecast:

| Scenario | Naive total | Holt total | ARIMA total | yield_rate |
| -------- | ----------- | ---------- | ----------- | ---------- |
| Base     | $188,215    | $198,615   | $186,677    | 4.500%     |
| Stress   | $159,982    | $168,823   | $158,675    | 3.825%     |
| Upside   | $207,036    | $218,477   | $205,344    | 4.950%     |

- base→stress ratio: 159,982 / 188,215 = **0.850×** ✓
- base→upside ratio: 207,036 / 188,215 = **1.100×** ✓
- yield_rate: stress=0.85×, upside=1.10× ✓

## What Was Already Working

`POST /forecast` (single-model) already applied scenario to the rate correctly — the rate was used directly in the daily yield calculation loop. Only `POST /forecast/all` (three-model comparison) was broken.

## Pattern Preserved

This is a **parallel shift** assumption — same multiplier applied to all horizons. Appropriate for short-duration yield products where Fed moves affect the entire yield curve uniformly. More sophisticated products (e.g., with duration mismatch) would need term-structure modeling.
