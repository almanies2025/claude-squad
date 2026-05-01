---
type: DISCOVERY
date: 2026-05-01
author: agent
session_id: current
project: yield-payment-infrastructure
topic: yield_events table schema is correct but table is empty — no production data pathway exists
phase: analyze
tags: [data-audit, yield-events, etl-pipeline, sprint-2]
---

## Discovery

The `yield_events` table exists in the SQLite schema with all correct columns (`account_id`, `event_date`, `balance_snapshot`, `rate_snapshot`, `daily_yield`, `accrued_yield`) — but has never received a single row. The entire forecast engine runs on in-memory formulas, not database records.

## Why This Matters

In production, the yield data flow is:
1. Sponsor bank sends end-of-day Treasury yield statement (T+1)
2. Statement contains: account ID, date, balance snapshot, rate snapshot, actual daily yield, accrued yield
3. FloatYield ETL pipeline ingests statement → validates totals → inserts into `yield_events`
4. `POST /forecast/all` reads last N days from `yield_events` as ARIMA input history
5. Reconciliation API compares `yield_events.daily_yield_actual` against `SUM(forecast rows)` for the month

**Step 3 — the ETL pipeline — does not exist in the codebase.** Without it, the forecast API cannot use real historical yield data, ARIMA has no signal to work on, and the reconciliation gap cannot be measured.

## What This Causes

| Symptom | Location | Root Cause |
|---------|---------|-----------|
| All three models return identical output | `main.py:293` flat history | No real yield history in `yield_events` |
| `recon_gap_bps = 1.23` hardcoded | `main.py:266` | No measured gap data to compute from |
| "★ ARIMA winner" misleading | `page.tsx:540` | Model never validated on real data in this system |
| "vs ARIMA" delta always $0 | `page.tsx:490` | Models produce same constant output |

## The Path Forward

Sprint 2's primary technical deliverable must be the yield_events ETL pipeline. Without it, all downstream features (real ARIMA comparison, measured recon gap, partner billing) are blocked.

## For Discussion

- Should the Sprint 2 data feed use a mock bank statement generator (for demo continuity) while the real ETL is built?
- What is the expected format of bank Treasury statements — CSV, SWIFT MT9xx, ISO 20022, custom API?
- Who owns the ETL pipeline — FloatYield engineering or the partner bank's integration team?
