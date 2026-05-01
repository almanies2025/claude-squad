---
type: GAP
date: 2026-05-01
author: agent
session_id: current
project: yield-payment-infrastructure
topic: recon_gap_bps is hardcoded constant — not computed, not measured, same for all accounts
phase: analyze
tags: [data-audit, reconciliation-gap, hardcoded-value, ethicially-loaded]
---

## Gap

`recon_gap_bps = 1.23` is returned identically for every account regardless of balance, rate, or partner — because it is a hardcoded constant, not a computed value.

## What 1.23 bps Actually Represents

From the session-validated math: the reconciliation gap is ~1.23 bps on $1B/year annualized — a system-wide reference value derived from the day-count mismatch between FloatYield's simple interest (/365) and the bank's actual/actual Treasury returns.

**Key properties:**
- It is the same number for all accounts (normalization to $1B book)
- It has no variance — no uncertainty interval
- It is not measured from any account's actual yield data
- It is a contractual reference value, not a billing value

## The Misrepresentation Risk

A BlueRidge Credit Union ($120M) seeing "1.23 bps" might interpret it as their specific reconciliation risk. In reality:
- For $120M @ 4.75%: annual yield = $5.7M; 1.23 bps of that = ~$700/year
- This is shown identically to Celtic Bank ($50M): annual yield = $2.25M; 1.23 bps = ~$277/year

The dollar gap scales with balance, but the bps is constant. A partner could reasonably ask: "Why is my reconciliation gap the same as a $50M partner when I have 2.4× more deposits?"

The answer: it's a system reference, not their specific measured gap. But the current UI doesn't say that.

## What Production Looks Like

In Sprint 2+, measured recon gap per account:
```
bank_actual_yield (from yield_events) − FloatYield_calculated_yield = measured_gap
measured_gap_bps = measured_gap / (balance × rate) × 10000
```

This varies by account, by month, and by day. It has variance. It can breach the contractually agreed tolerance threshold. It is what partners actually care about.

## The Fix

**Sprint 1 (disclosure):**
- Rename to `reference_recon_gap_bps` in API response
- Add `recon_gap_description` field: "System reference gap (1.23 bps on $1B/year) — not your account's measured gap"
- Remove per-account display; show only in aggregate summary

**Sprint 2 (measurement):**
- Compute from `yield_events`: `measured_gap = daily_yield_actual − daily_yield_calculated`
- Show per-account with timestamp: "Measured gap (T-1): 0.89 bps"

## For Discussion

- Should the API return both `reference_recon_gap_bps` (system reference) AND `measured_recon_gap_bps` (when available)?
- Should the dashboard show the reference gap at all in Sprint 1, or defer until measured data exists?
- What tolerance threshold should trigger a partner alert? (Contractually defined in Program Manager Agreement.)
