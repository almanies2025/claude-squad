---
name: redteam-sprint4-round1
description: Red team Round 1 security + spec coverage — 3 HIGH security issues fixed, 1 HIGH gap (threshold monitoring)
type: REDTEAM
date: 2026-05-03
created_at: 2026-05-03T00:00:00Z
author: co-authored
session_id: current
project: yield-payment-infrastructure
topic: Sprint 4 red team round 1 — security fixes applied, threshold monitoring gap identified
phase: redteam
tags: [security, validation, spec-coverage, sprint-4]
---

# REDTEAM Round 1 — Sprint 4 Validation

## Security Audit Results

### HIGH Issues Found (All Fixed)

1. **contract_rate/applied_rate — no non-negative validation** (`main.py:299-305`)
   - Attack: negative rate injected → corrupts financial calculations
   - Fix: `@field_validator("contract_rate", "applied_rate")` enforcing ≥ 0
   - Verified: `curl -X POST /rate-discrepancies -d '{"contract_rate":-0.05}'` → 422

2. **DisputeUpdate.notes — no length cap** (`main.py:270-272`)
   - Attack: unbounded notes payload → DoS/storage risk
   - Fix: `@field_validator("notes")` with max 2000 chars
   - Verified: backend rejects notes > 2000 chars

3. **Dynamic column interpolation in dispute PATCH** (`main.py:865`)
   - Fragile pattern: f-string column interpolation could become injection vector if schema evolves
   - Fix: explicit `if/elif` branches for status + notes combinations
   - Verified: `PATCH /disputes/2` with status + notes works correctly

### Pre-Existing Security Posture (PASS)

- SQL injection: all queries use `?` parameter binding ✓
- Account ID validation on forecast endpoints ✓
- `DisputeCreate` validators comprehensive ✓
- DB_PATH safe — no path traversal risk ✓
- Error handling: no stack traces exposed ✓
- Frontend XSS: React auto-escapes, no `dangerouslySetInnerHTML` ✓
- CORS: explicit origins, not wildcards ✓
- No hardcoded secrets ✓

### Residual (MEDIUM/LOW — Not Fixed)

- `account_id` path param on `/regulatory/...` endpoints not validated positive — minor for demo
- Date validators check format but not temporal range — acceptable for demo

## Spec Coverage Results

### Sprint 1: 6/6 IMPLEMENTED + WIRED
- Demo banner ✓, Demo Partner A/B/C ✓, no winner badge ✓, no delta column ✓, recon_gap_description ✓, scenario_description ✓

### Sprint 2: 5/5 IMPLEMENTED + WIRED
- ETL pipeline ✓, yield_events populated (783 rows) ✓, measured recon gap ✓, ARIMA validation ✓, 80% CI intervals ✓

### Sprint 3: 5/6 IMPLEMENTED + WIRED
- Dispute log ✓, rate discrepancy UI + backend ✓, threshold alerts table/API/UI ✓, portfolio view ✓, regulatory 1099-INT ✓
- **Gap**: Unclaimed property shows $0 (balance ≠ 0 in demo → correct behaviour, looks broken)

### HIGH Spec Gap: Threshold Alert Auto-Generation Missing

**File**: `main.py:1045-1112` (`/portfolio`)
**Issue**: No background process computes gap vs. threshold and inserts into `threshold_alerts`.
**Impact**: Alerts tab always empty. No automated gap breach detection.
**Fix needed**: Add monitoring logic to `/portfolio` — after computing gap stats, INSERT into `threshold_alerts` when `avg_gap_bps > threshold`.

## Convergence Status

| Criterion | Status |
|-----------|--------|
| 0 CRITICAL findings | ✓ |
| 0 HIGH findings (post-fix) | ✓ |
| Spec coverage | 17/18 items wired; 1 HIGH gap |
| Round 2 needed | Yes — threshold monitoring job not implemented |

## For Discussion

1. **Threshold monitoring**: Should the gap-check INSERT live in `GET /portfolio` (simplest, computed on-demand) or in a dedicated background worker (more robust, runs on schedule)?
2. **Unclaimed property demo**: Should we add a zero-balance demo account to show non-trivial unclaimed output, or is $0 accurate behaviour that just needs better labelling?
3. **Alert threshold**: Should the gap threshold be per-account (stored in accounts table) or a global constant in config?
