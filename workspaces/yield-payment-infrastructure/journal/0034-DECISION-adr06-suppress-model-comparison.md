---
type: DECISION
date: 2026-05-01
author: agent
session_id: current
project: yield-payment-infrastructure
topic: ADR-06: Suppress model comparison UI on flat synthetic history
phase: implement
tags: [adr-06, model-comparison, flat-history, sprint-1, demo]
---

## Decision

Suppressed the "★ ARIMA winner" badge and "vs ARIMA" delta column from the dashboard. Retained the three-model structure for future use when real yield history is connected.

## Why

`POST /forecast/all` generates 60 days of flat in-memory synthetic history (`history = [base_yield_daily] * 60`). All three models return identical output on flat input. The "★ winner" badge and delta columns were therefore decorative — they implied differentiation that does not exist in the live system. This is misleading in a demo.

## What Was Removed

1. "★ ARIMA winner" badge from bar chart model labels
2. "★ ARIMA winner" badge from table rows
3. "vs ARIMA" delta column from model detail table
4. Validation legend ("★ ARIMA(1,1,1) — Best on walk-forward validation")

## What Was Added Instead

- Scenario description box (green): "Fed funds rate unchanged...", "Fed cuts 50bps...", "Fed hikes 30bps..." — provides real economic context
- Recon gap description box (yellow): explains the 1.23 bps is a system reference, not account-specific measurement
- Demo disclosure banner (amber): "DEMO MODE — All data is synthetic. Model comparison requires live yield history."

## Consequences

Partners cannot evaluate model quality from Sprint 1 demo. This is honest about the current state. Real comparison requires `yield_events` population (Sprint 2).

## Files Changed

- `apps/web/app/page.tsx` — removed ARIMA badge, delta column, validation legend
- `apps/web/app/page.tsx` — added scenario + recon gap description boxes
- `apps/web/app/page.tsx` — added demo disclosure banner

## For Discussion

- Should the three-model structure be hidden entirely until real data is connected, or does the structural preview provide value even with identical outputs?
