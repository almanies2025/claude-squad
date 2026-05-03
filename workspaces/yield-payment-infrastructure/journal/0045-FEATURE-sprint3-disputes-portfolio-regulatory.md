---
type: FEATURE
date: 2026-05-03
created_at: 2026-05-03T00:00:00Z
author: co-authored
session_id: current
session_turn: 1
project: yield-payment-infrastructure
topic: Sprint 3 — disputes, threshold alerts, portfolio view, regulatory reports
phase: implement
tags: [sprint3, disputes, alerts, portfolio, regulatory, backend, frontend]
---

## Sprint 3 — Production Hardening Features

### What Was Built

Five Sprint 3 features from the feature-framing.md roadmap:

**1. Reconciliation Dispute Log**
- New `recon_disputes` table: id, account_id, dispute_date, filed_by, gap_bps, gap_dollar_amount, dispute_type, reason, status, notes, created_at
- Endpoints: `GET /disputes`, `POST /disputes`, `PATCH /disputes/{id}`, `GET /disputes/summary`
- Frontend: disputes tab with full table, status badges, and file-dispute form

**2. Threshold Breach Alerts**
- New `threshold_alerts` table: id, account_id, alert_date, gap_bps, threshold_bps, severity, acknowledged
- Endpoints: `GET /alerts`, `POST /alerts/{id}/acknowledge`
- Frontend: 🔔 alert badge in header (visible when unacknowledged alerts exist), acknowledge button per alert

**3. Rate Discrepancy Tracking**
- New `rate_discrepancies` table: id, account_id, discrepancy_date, contract_rate, applied_rate, discrepancy_bps, status, notes
- Endpoints: `GET /rate-discrepancies`, `POST /rate-discrepancies`

**4. Multi-Partner Portfolio View**
- Endpoint: `GET /portfolio` — aggregate stats across all partner accounts
- Returns: total_balance, total_disputes, open_disputes, threshold_alerts, unacknowledged_alerts, avg_gap_bps, max_gap_bps, annualized_yield, projected_30d_yield
- Frontend: dedicated "PORTFOLIO" tab with 6 stat cards + per-account breakdown table

**5. Regulatory Reporting Module**
- Endpoints: `GET /regulatory/1099-int/{account_id}`, `GET /regulatory/unclaimed-property/{account_id}`
- 1099-INT: computed from yield_events for the specified tax year
- Unclaimed Property: shown for zero-balance accounts with resolved disputes
- Frontend: "REGULATORY" tab showing 1099-INT for all 3 demo partners

### Files Changed

- `backend/app/main.py`: 3 new tables (DDL), 14 new Pydantic models, 9 new endpoints
- `apps/web/app/page.tsx`: 4 new types, 5 new state vars, 2 new sub-components (StatusBadge, DisputeFormWidget), 3 new tab panels, header alert badge, tab switcher

### Backend Verification

```
GET /portfolio → {total_accounts:3, total_balance:248000000.0, open_disputes:0, threshold_alerts:0, avg_gap_bps:0.0125, max_gap_bps:21.6625}
GET /disputes → []
GET /alerts → []
GET /regulatory/1099-int/1 → {total_yield:1067089.62, account_balance:50000000.0, yield_rate:0.045}
```

### Outstanding

- `rate_discrepancies` table is seeded but no UI to file a rate discrepancy — disputes form only handles recon_gap type
- Threshold alerts are not auto-generated; table is seeded but empty until a monitoring job populates it
- Unclaimed property report is entirely mock (no real trigger condition)
- Capital sequencing problem (journal 0040) still unresolved

### For Discussion

1. The `rate_discrepancies` table has no frontend form — should the dispute form be extended to support `dispute_type: "rate_discrepancy"`?
2. Threshold alerts currently require a monitoring job to populate the table. Should FloatYield itself generate alerts when measured gap exceeds a threshold, or is this partner-side logic?
3. The portfolio `avg_gap_bps` of 0.0125 vs `max_gap_bps` of 21.66 — should the max trigger an automatic alert insertion?
