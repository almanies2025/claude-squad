---
type: DECISION
date: 2026-05-01
author: agent
session_id: current
project: yield-payment-infrastructure
topic: ADR-07: Reconciliation gap shown as system reference with mandatory disclosure
phase: implement
tags: [adr-07, reconciliation-gap, hardcoded-value, sprint-1, disclosure]
---

## Decision

`recon_gap_bps = 1.23` is retained as the system reference value, but the API and UI now include explicit disclosure that it is: (a) a system-wide reference, not account-specific; (b) normalized to $1B/year, not measured from any account's actual yield data.

## Why

A partner seeing "1.23 bps" for their $120M account might interpret it as their specific reconciliation risk. In reality it is a normalized system constant — the same value shown for a $50M account. The dollar amount of the gap scales with balance, but the bps rate does not. Without disclosure, this is misleading.

## Implementation

**API** (`backend/app/main.py`):
- `POST /forecast` now returns `recon_gap_description: str` alongside `recon_gap_bps: float`
- `POST /forecast/all` now returns `recon_gap_description: str` on the top-level response
- Description text: "System reference gap: 1.23 bps on $1B/year annualized. This is the normalized system gap — not your account's measured reconciliation gap. Measured gap = bank actual yield − FloatYield calculated yield (available Sprint 2)."

**UI** (`apps/web/app/page.tsx`):
- Yellow description box below bar chart: displays `forecast.recon_gap_description`
- Text explains the reference vs. measured distinction
- Per-account gap in forecast card header still shows "Est. recon gap: 1.23 bps" — context comes from the description box below

## Future (Sprint 2)

Once `yield_events` is populated, the API will return `measured_recon_gap_bps` computed from actual bank yield statements. At that point, per-account measured gaps replace the reference value.

## For Discussion

- Should per-account recon gap display be entirely suppressed until Sprint 2 (when it can show a real measured value)?
- Should the API return both `reference_recon_gap_bps` and `measured_recon_gap_bps` when available?
