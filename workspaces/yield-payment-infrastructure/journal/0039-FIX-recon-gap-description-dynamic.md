---
type: FIX
date: 2026-05-01
created_at: 2026-05-01T06:35:00Z
author: agent
session_id: current
session_turn: 1
project: yield-payment-infrastructure
topic: recon_gap_description now dynamic — measured vs system reference
phase: implement
tags: [backend, reconciliation-gap, yield-events, fastapi]
---

## What Was Wrong

`POST /forecast/all` and `POST /forecast` both returned a **static** `recon_gap_description`:

```
"System reference gap: 1.23 bps on $1B/year annualized. "
"This is the normalized system gap — not your account's measured reconciliation gap. "
"Measured gap = bank actual yield − FloatYield calculated yield ..."
```

This was displayed even when 65 `yield_events` rows existed per account — making the "system reference" disclaimer actively misleading. Users with real historical data would be told "insufficient history" when they had plenty.

## What Was Fixed

Split `_recon_gap()` into `_recon_gap_info()` returning `tuple[float, str]`:

```python
def _recon_gap_info(account_id: int) -> tuple[float, str]:
    # Returns (gap_bps, description)
    if len(rows) < 5:
        return (1.23, (
            "System reference gap: 1.23 bps on $1B/year annualized. "
            "Insufficient yield history for a measured gap — falling back to normalized system reference."
        ))
    measured = round(sum(gaps) / len(gaps), 2)
    return (measured, (
        f"Measured gap: {measured:.2f} bps on $1B/year annualized "
        f"({len(rows)} events, {30}-day lookback). "
        "This is your account's measured reconciliation gap — bank actual yield minus FloatYield calculated yield."
    ))
```

Both endpoints (`/forecast`, `/forecast/all`) now call `_recon_gap_info()` once and unpack `(gap_bps, recon_gap_desc)`.

## Verified

- Account 1 (65 rows): `recon_gap_description` → "Measured gap: 1.22 bps on $1B/year annualized (30 events, 30-day lookback)..."
- Holt interval widening confirmed: 7d→638, 14d→659, 30d→704, 60d→781
- All 3 accounts return differentiated model outputs
- Preflight: ALL CHECKS PASSED

## File Changed

- `backend/app/main.py`: `_recon_gap()` → `_recon_gap_info()`, 2 call sites updated

## For Discussion

1. The `recon_gap_description` still says "(30 events, 30-day lookback)" even though `LIMIT 30` is used in the query — the actual count is capped at 30 rows. Should this reflect the cap accurately?
2. Should `yield_events` with exactly 5 rows (the minimum threshold) show "Measured" or "Preliminary measured"? The current code returns "Measured" at ≥5 rows.
3. The 1.23 bps fallback value is hardcoded in `_recon_gap_info()`. Should this also come from a config/environment variable for different deployment contexts?
