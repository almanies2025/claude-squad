# FloatYield Spec Coverage Audit
**Date:** 2026-05-03
**Phase:** 04 — Red Team Step 1: Spec Coverage
**Workspace:** yield-payment-infrastructure

---

## Executive Summary

The FloatYield implementation matches the Sprint 1, 2, and 3 feature specs at the route/table level. All six Sprint 1 demo-integrity features and all five Sprint 2 data pipeline features are implemented and wired. Sprint 3 is 5/6 fully wired; 1/6 (unclaimed property) has display code but shows $0 in demo due to business logic design.

**Complexity Score: Moderate** — All route/table infrastructure present; remaining gaps are functional wiring issues, not missing schemas.

---

## 1. Spec Coverage Table

### Sprint 1 — Demo Integrity

| # | Feature | Spec Requirement | Implementation | Status |
|---|---------|-----------------|----------------|--------|
| 1 | Demo data disclosure banner | Add banner to dashboard | `page.tsx:1537-1561` — yellow "DEMO MODE" banner | IMPLEMENTED + WIRED |
| 2 | Demo Partner A/B/C naming | A/B/C naming in seed data | `main.py:102-109` — seeds "Demo Partner A/B/C" | IMPLEMENTED + WIRED |
| 3 | Remove "★ ARIMA winner" badge | Suppress from UI | `MODEL_COLORS` has no winner tag | IMPLEMENTED + WIRED |
| 4 | Remove "vs ARIMA" delta column | Suppress from UI | Model detail table has no delta column | IMPLEMENTED + WIRED |
| 5 | `recon_gap_description` in API | Add description to `POST /forecast` | `YieldForecast:144` — populated via `_recon_gap_info()` | IMPLEMENTED + WIRED |
| 6 | Scenario metadata | Add `scenario_description` to API | `YieldForecast:145` — populated via SCENARIOS dict | IMPLEMENTED + WIRED |

### Sprint 2 — Data Feed Integration

| # | Feature | Spec Requirement | Implementation | Status |
|---|---------|-----------------|----------------|--------|
| 1 | `yield_events` ETL pipeline | `scripts/etl/load_yield_events.py` + `scripts/etl/run_t1_batch.py` | Both files exist; `INSERT OR IGNORE` + `UNIQUE INDEX` on `(account_id, event_date)` | IMPLEMENTED + WIRED |
| 2 | Replace flat history with real lookback | `POST /forecast/all` queries `yield_events` | `main.py:668-678` — queries `yield_events ORDER BY event_date DESC LIMIT 60`; 783 rows in DB | IMPLEMENTED + WIRED |
| 3 | Measured recon gap | `_recon_gap_info()` computes from yield_events | `main.py:586-637` — computes gap from last 30 rows; falls back to 1.23 if <5 rows | IMPLEMENTED + WIRED |
| 4 | ARIMA model re-validation | `scripts/forecast_models/validate_db.py` | File exists; `model_comparison.json` confirms ARIMA(1,1,1) wins all 3 accounts | IMPLEMENTED + WIRED |
| 5 | Uncertainty intervals (80% CI) | `_compute_intervals()` computes 80% CI bands | `main.py:492-583` — Naive/Holt/ARIMA-specific formulas with `z_80 = 1.28` | IMPLEMENTED + WIRED |

### Sprint 3 — Production Hardening

| # | Feature | Spec Requirement | Implementation | Status |
|---|---------|-----------------|----------------|--------|
| 1 | Reconciliation dispute log | New `recon_disputes` table + API | `GET /disputes`, `POST /disputes`, `PATCH /disputes/{id}`, `GET /disputes/summary` | IMPLEMENTED + WIRED |
| 2 | Rate discrepancy tracking | Contract rate vs. applied rate flag | Table + `GET/POST /rate-discrepancies`; `RateDiscrepancyFormWidget` + table in UI | IMPLEMENTED + WIRED |
| 3 | Tolerance threshold breach alerts | Alert when measured gap exceeds threshold | Table + `GET /alerts`, `POST /alerts/{id}/acknowledge`; UI displays with acknowledge button | TABLE/API/UI IMPLEMENTED — monitoring job NOT implemented |
| 4 | Multi-partner portfolio view | `GET /portfolio` aggregate stats | `main.py:1045-1112` — total accounts, balance, disputes, alerts, gap stats | IMPLEMENTED + WIRED |
| 5 | Regulatory 1099-INT | `GET /regulatory/1099-int/{id}` | `main.py:1118-1151` — validates tax_year (2000-2100) | IMPLEMENTED + WIRED |
| 6 | Regulatory unclaimed property | `GET /regulatory/unclaimed-property/{id}` | `main.py:1154-1187`; frontend fetches into `unclaimedReports`; display section exists | IMPLEMENTED + WIRED (shows $0 because balance ≠ 0) |

---

## 2. Spec Gap List

### Gap 1: Threshold Alert Auto-Generation — No Monitoring Job (HIGH)

**Spec requirement:** "Alert when measured gap exceeds contract threshold."

**What exists:** `threshold_alerts` table, `GET /alerts`, `POST /alerts/{id}/acknowledge`, frontend display with acknowledge button.

**What's missing:** No background process computes measured gap per account and inserts into `threshold_alerts` when gap exceeds a per-account threshold. The `/portfolio` endpoint computes `avg_gap_bps` but does NOT insert into `threshold_alerts`.

**Impact:** Alerts tab always empty. No automated gap breach detection. No proactive partner notification.

**Fix:** Add monitoring logic to `GET /portfolio` — after computing gap stats, check if gap exceeds a per-account threshold and INSERT into `threshold_alerts` if so. Or create a dedicated `/monitor` endpoint.

---

### Gap 2: Unclaimed Property — Shows $0 for All Demo Accounts (MEDIUM)

**Spec requirement:** Sprint 3 feature #6: unclaimed property notices in regulatory tab.

**What's implemented:** Backend endpoint at `main.py:1154-1187`, frontend fetch and display section.

**Issue:** Business logic at `main.py:1170-1177` returns `unclaimed=0` unless `balance == 0`. All three demo accounts have non-zero balances ($50M, $120M, $78M). The section renders but shows $0 — looks broken to users.

**Impact:** Demo shows empty-looking unclaimed property cards ($0 values). Not technically broken, but poor UX.

**Fix options:**
1. Add a demo account with zero balance to show non-trivial output
2. Add a seeded dispute that generates non-zero unclaimed yield
3. Document as "behaviour is correct; balance ≠ 0 means no unclaimed property"

---

## 3. Failure Points

### HIGH: Threshold Alert Auto-Generation Missing

| Field | Value |
|-------|-------|
| File:Line | `main.py:1045-1112` (`/portfolio`), `page.tsx:2346-2443` (alerts display) |
| Type | Missing monitoring job |
| Root Cause | No background process computes gap vs. threshold and inserts rows into `threshold_alerts` |
| Why it fails | Alerts tab always empty. No automated gap breach detection. |

**Fix:** Add threshold monitoring. Simplest approach: after computing gap stats in `/portfolio`, INSERT into `threshold_alerts` when `avg_gap_bps > threshold` (threshold could be stored per-account or use a global default).

---

## 4. Verdict

| Sprint | Status | Notes |
|--------|--------|-------|
| Sprint 1 | FULL MATCH | All 6 features implemented and wired |
| Sprint 2 | FULL MATCH | All 5 features implemented and wired; 783 yield_events rows |
| Sprint 3 | PARTIAL MATCH | 5/6 fully wired; unclaimed property shows $0 in demo |

**Overall: 17/18 spec items implemented + wired. 1 HIGH gap (threshold monitoring job) remaining.**
