---
type: GAP
date: 2026-05-01
author: co-authored
session_id: current
project: yield-payment-infrastructure
topic: Forecast vs reconciliation gap — two distinct problems conflated in Sprint 1
phase: implement
tags: [reconciliation-gap, forecast-vs-actuals, dashboard]
---

## Gap

Sprint 1 Forecast currently conflates two separate problems:

1. **Yield forecasting** — predicting what FloatYield calculates as daily yield
2. **Reconciliation gap** — FloatYield's simple interest (/365) diverging from the bank's actual Treasury returns

## Why This Is a Problem

The dashboard shows projected yield and a "recon gap in bps" — but that bps is calculated from a fixed formula (1.23 bps on $1B/year annualised), not from actual bank yield data.

In production:
- The bank provides daily Treasury yield statements (actual/actual day-count)
- FloatYield calculates simple interest (/365)
- The gap is real, measured, and negotiated

Currently Sprint 1 shows:
```
Projected yield: $6,164/day
Recon gap: 1.23 bps (estimated, not measured)
```

What it should show (Sprint 2):
```
FloatYield calculated: $6,164/day
Bank actual yield: $6,198/day (from bank's statement)
Measured gap: $34/day (0.55 bps)
```

## What Is Missing

The `yield_events` table exists in the schema but is not populated with actual yield data. The bank yield feed (actual Treasury statements) is not yet integrated.

This is not a Sprint 1 gap — it is a known Phase 2 item. But the dashboard should be honest about what is estimated vs. measured.

## For Discussion

- Should Sprint 1 dashboard label the recon gap as "estimated" vs "measured"?
- Should we show the estimated gap alongside the forecast so partners understand it's a contractual allowance, not a measurement?
