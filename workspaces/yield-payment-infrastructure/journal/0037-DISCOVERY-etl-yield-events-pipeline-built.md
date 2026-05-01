---
type: DISCOVERY
date: 2026-05-01
created_at: 2026-05-01T12:00:00Z
author: agent
session_id: yield-payment-infrastructure
session_turn: 1
project: FloatYield
topic: ETL pipeline built and verified — yield_events populated, but API still uses flat history
phase: implement
tags: [etl, yield-events, synthetic-history, data-pipeline]
---

## What Was Found

**ETL pipeline is greenfield — built from scratch.**

`scripts/etl/load_yield_events.py` implements:

- **Synthetic path**: Random-walk generator with Gaussian noise (~2% daily std) and slight downward drift. Produces 65 business-day rows per account (90 calendar days). Models now have non-flat history.
- **CSV path**: Parses sponsor bank Treasury statement exports. Header must match: `account_id, event_date, balance_snapshot, rate_snapshot, daily_yield, accrued_yield`.
- **Deduplication**: `INSERT OR IGNORE`-style check on `(account_id, event_date)`. Re-running is safe — 0 re-inserted, 195 deduplicated on second run.
- **Verified**: 195 rows loaded across 3 demo accounts (2026-02-02 → 2026-05-01).

## Fixed — `POST /forecast/all` Now Queries yield_events

**Applied**: `main.py` updated to query `yield_events` as lookback source:

```python
with get_db() as db:
    rows = db.execute(
        """
        SELECT daily_yield
          FROM yield_events
         WHERE account_id = ?
         ORDER BY event_date DESC
         LIMIT 60
        """,
        (params.account_id,),
    ).fetchall()

if rows:
    history = [float(r["daily_yield"]) for r in reversed(rows)]
else:
    history = [base_yield_daily] * max(60, params.days)
```

**Verified** — all three accounts return differentiated model outputs:

| Account        | Naive      | Holt       | ARIMA      |
| -------------- | ---------- | ---------- | ---------- |
| Demo Partner A | 43,150.68  | 44,208.92  | 43,547.01  |
| Demo Partner B | 109,315.07 | 111,996.04 | 110,319.15 |
| Demo Partner C | 65,819.18  | 67,433.37  | 66,423.72  |

195 synthetic rows loaded (3 accounts × 65 business days, 2026-02-02 → 2026-05-01).

## Sprint 2 — Uncertainty Intervals Added

**Applied**: `_compute_intervals(history, preds, model_name)` added to `main.py`. Returns per-day cumulative lower/upper bounds at 80% CI. `ModelResult` now has `lower_bound` and `upper_bound` fields.

**Interval model per method**:
- **Naive (Persistence)**: σ = std(diff(series)); se_h = σ√h; random-walk variance grows with horizon
- **Holt (Double Exp)**: level + trend residual variance; se_h = σ_level + σ_trend × h
- **ARIMA(1,1,1)**: σ² × (1 + Σψ_i²) where ψ_i = phi^i; AR damping reduces variance contribution from distant terms

**Verified — all 3 accounts**:

| Account | Model | Point | 80% CI | Width |
|---------|-------|-------|--------|-------|
| Demo Partner A | Naive | 43,917 | [42,609, 45,225] | 6.0% |
| Demo Partner A | Holt | 44,209 | [43,684, 44,734] | 2.4% |
| Demo Partner A | ARIMA | 43,547 | [43,364, 43,730] | 0.8% |
| Demo Partner B | Naive | 111,256 | [107,942, 114,570] | 6.0% |
| Demo Partner B | Holt | 111,996 | [110,667, 113,325] | 2.4% |
| Demo Partner B | ARIMA | 110,319 | [109,856, 110,783] | 0.8% |

Pattern is consistent: ARIMA narrows fastest (AR damping), Holt intermediate, Naive widest.

---

## For Discussion

1. The synthetic noise model (`gauss(0, 0.02)`) was seeded with `_r.seed(42)` for reproducibility. Is a fixed seed acceptable for a demo, or should each ETL run produce different noise (removing the seed)?
2. The ETL generates exactly 65 rows per account (business days only, skipping weekends). Sponsor bank settlement typically skips weekends too — is this alignment correct, or should the pipeline insert weekend rows with zero yield?
3. The CSV path requires exact column names. Should the parser be more lenient (case-insensitive, extra whitespace stripped), or keep strict matching to catch format errors early?
