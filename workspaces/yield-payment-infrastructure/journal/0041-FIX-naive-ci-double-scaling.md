---
type: FIX
date: 2026-05-01
created_at: 2026-05-01T07:45:00Z
author: agent
session_id: current
session_turn: 1
project: yield-payment-infrastructure
topic: Naive CI double-scaling — was σ√h·√h, should be σ√h
phase: implement
tags: [intervals, naive, ci, bug, leaderboard]
---

## What Was Wrong

In `_compute_intervals`, the Naive model branch computed 80% CI bounds as:

```python
se = sigma * np.sqrt(h)
cum_lower = sum(point_preds[:h]) - z_80 * se * np.sqrt(h)   # BUG
cum_upper = sum(point_preds[:h]) + z_80 * se * np.sqrt(h)   # BUG
```

`se = σ√h` is the standard error at horizon h. The cumulative CI bound then multiplied by `√h` again — `z_80 * σ√h * √h = z_80 * σ * h` — double-scaling the interval width by an additional √h factor.

**Effect**: Naive CI spans were `h`-proportional instead of `√h`-proportional:

| Horizon | Correct span | Bug span | Ratio |
|---------|-------------|---------|-------|
| 7-day   | $989        | $2,616  | 2.6× |
| 14-day  | $1,399      | $5,233  | 3.7× |
| 30-day  | $2,047      | $11,213 | 5.5× |
| 60-day  | $2,895      | $22,427 | 7.7× |

At 60 days, the Naive model appeared 7.7× more uncertain than it actually was — making the leaderboard comparison between Naive and Holt/ARIMA structurally misleading.

## What Was Fixed

```python
# BEFORE (bug)
cum_lower = sum(point_preds[:h]) - z_80 * se * np.sqrt(h)
cum_upper = sum(point_preds[:h]) + z_80 * se * np.sqrt(h)

# AFTER (correct)
cum_lower = sum(point_preds[:h]) - z_80 * se
cum_upper = sum(point_preds[:h]) + z_80 * se
```

`z_80 * se` = `z_80 * σ√h` — the correct cumulative 80% CI bound. Verified: h=60/h=7 ratio = 2.93× = √60/√7 ✓

## File Changed

- `backend/app/main.py:328-329`

## Verified

```
Account 1 (h=7):  Naive CI span = $989    (was $2,616)
Account 1 (h=60): Naive CI span = $2,895  (was $22,427)
Ratio h=60/h=7: 2.93× = √60/√7 ✓
```

## For Discussion

1. Should the Naive model comparison bar chart label explicitly note it represents the "zero-skill floor" — the yield if the model had no predictive power beyond last observed rate?
2. The leaderboard now shows Naive ±0.8%, Holt ±0.2%, ARIMA ±0.1% relative width at 30 days. Is this the right signal to give partners — or should the UI explicitly label the Naive result as "reference only"?
