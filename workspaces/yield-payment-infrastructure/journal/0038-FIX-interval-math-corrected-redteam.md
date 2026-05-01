---
type: DECISION
date: 2026-05-01
created_at: 2026-05-01T00:00:00Z
author: agent
session_id: yield-payment-infrastructure
session_turn: 1
project: FloatYield
topic: Redteam caught two interval math bugs — Holt intervals flat, ARIMA systematically over-wide
phase: implement
tags: [redteam, intervals, holt, arima, math-fix]
---

## What Was Fixed

**Holt intervals were flat** — `trend_resids` was never populated (empty list), so `sigma_trend = sigma_level * 0.1 = 0`. The loop then computed `se_h = sigma_level + 0 * h = sigma_level` for all horizons — a constant width regardless of forecast distance. Corrected to use the pre-computed `sigma[h-1]` array which widens as `sqrt(sigma_level² + sigma_trend² * h²)`.

**ARIMA psi_cumsum formula was wrong** — implemented `(1 + phi² * (1 - phi^{2(h-1)}) / (1 - phi²))` which doubles the exponent. Correct is `(1 - phi^{2h}) / (1 - phi²)` — a clean geometric series where Σψ_i² from i=0 to h-1 = (1 - phi^{2h}) / (1 - phi²).

## For Discussion

1. The Holt fix means Holt intervals are now wider than before (correctly). Does this change how partners should interpret the "range" in a way that needs disclosure?
2. The ARIMA fix narrows ARIMA intervals compared to before — does this affect the "narrowest = most confident" signal that the UI currently implies?
