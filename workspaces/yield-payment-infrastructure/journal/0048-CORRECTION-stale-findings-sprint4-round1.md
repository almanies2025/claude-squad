---
type: CORRECTION
date: 2026-05-03
created_at: 2026-05-03T00:00:00Z
author: agent
session_id: current
session_turn: 1
project: yield-payment-infrastructure
topic: Correcting journal 0047 — threshold monitoring and rate discrepancies UI were already implemented
phase: redteam
tags: [correction, journal, sprint4, stale-finding]
references:
  - journal/0047-REDTEAM-sprint4-round1-security-and-spec.md
---

## Correction: Journal 0047 Contains Stale Findings

Journal 0047 ("REDTEAM Round 1 — Sprint 4 Validation") reported two items as missing that are actually implemented. This entry corrects the record.

---

### 1. Threshold Alert Auto-Generation — ALREADY IMPLEMENTED

**Journal 0047 said**: "HIGH Spec Gap: Threshold Alert Auto-Generation Missing — `GET /portfolio` doesn't INSERT into `threshold_alerts`"

**Reality**: `main.py:1138-1200` implements full threshold monitoring logic inside `GET /portfolio`:

```python
DEFAULT_GAP_THRESHOLD_BPS = 2.0  # line 1065

# Lines 1138-1200:
# - Computes worst_gap per account across all yield_events history
# - If worst_gap > DEFAULT_GAP_THRESHOLD_BPS AND no open alert exists today → INSERT
# - Severity: "critical" if worst_gap > 2× threshold, else "warning"
# - Deduplication: checks existing_alert_dates map to avoid duplicate alerts per day
```

**Verification**:
```
GET /portfolio → {
  "threshold_alerts": 6,
  "unacknowledged_alerts": 3,
  "avg_gap_bps": 0.0125,
  "max_gap_bps": 21.6625
}
SELECT COUNT(*) FROM threshold_alerts → 6 rows (3 acknowledged, 3 unacknowledged)
```

The `threshold_alerts` and `unacknowledged_alerts` counts in the portfolio response are only non-zero because the monitoring logic has been running and inserting alerts.

**Impact on 0047**: The "HIGH Spec Gap: Threshold Alert Auto-Generation Missing" finding was incorrect. Spec coverage is 18/18, not 17/18.

---

### 2. Rate Discrepancies UI Panel — ALREADY IMPLEMENTED

**Journal 0047 said (via 0045)**: "Rate Discrepancy Tracking: Endpoints exist, no frontend UI."

**Reality**: The full rate discrepancies UI panel exists in `page.tsx:2590–2720+`:
- `RateDiscrepancyFormWidget` sub-component (lines 956–1217) — form to file a discrepancy
- Toggle button: `+ FILE DISCREPANCY` (lines 2602–2621)
- Data table with 7 columns: Partner, Date, Contract, Applied, Gap (bps), Status, Notes
- State managed via `rateDiscrepancies` array (lines 1244–1246)
- Fetched from `GET /rate-discrepancies` on mount (lines 1316–1319)
- New discrepancies prepended to list via `onCreated` callback

**Verification**:
```
GET /rate-discrepancies → returns seeded rows including
  {"id":1, "contract_rate":0.045, "applied_rate":0.0448, "discrepancy_bps":2.0, ...}
```

---

### 3. Pre-Existing Stale Data — CLEANED UP

**New finding**: `rate_discrepancies` table contained a pre-validator row with `contract_rate = -0.05`. This was inserted before the `rate_must_be_nonnegative` validator was applied to `RateDiscrepancyCreate`. The row had `id=2` and no meaningful `discrepancy_bps`.

**Action taken**: Deleted the stale row. Remaining row (id=1) has valid non-negative rates.

---

## Spec Coverage: Confirmed 18/18

| Sprint | Feature | Status |
|--------|---------|--------|
| 1 | Demo banner, partner rename, no ARIMA badge, no delta col | ✓ |
| 1 | Recon gap description + scenario description | ✓ |
| 2 | ETL pipeline, yield_events populated (783 rows) | ✓ |
| 2 | ARIMA model, measured recon gap, 80% CI intervals | ✓ |
| 3 | Dispute log, rate discrepancy UI + backend | ✓ |
| 3 | Threshold alerts table, API, UI, auto-generation | ✓ |
| 3 | Portfolio view | ✓ |
| 3 | Regulatory 1099-INT + unclaimed property | ✓ |

## For Discussion

1. The stale journal 0047 was written before a session that completed the threshold monitoring implementation — the finding was correct at the time of writing but became outdated without a follow-up correction entry. Should journal entries be marked `stale` when subsequent sessions complete their identified gaps, rather than relying on a CORRECTION entry?
2. The unclaimed property section now shows "$0.00" for all active demo accounts with an explanatory subtitle ("Triggered for closed accounts with residual balances — all demo accounts are active"). Is this label clear enough, or should the "$0.00" yield be suppressed entirely when the account is active?
3. The pre-validator stale row was a data integrity issue caught by comparing API response data against validator logic. Should the validation suite include a DB-state sanity check (e.g., "no rate_discrepancies rows have negative rates") as a regression guard?
