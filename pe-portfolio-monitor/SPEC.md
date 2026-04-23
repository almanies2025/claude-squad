# PE Portfolio Monitor — SPEC

**Frozen at prototype start**: 2026-04-20
**Last updated**: 2026-04-20 (backend implementation complete)

## Context

SaaS product for US mid-market PE firms ($500M–$5B AUM) owning 10–20 portfolio companies. Monitors operational health between quarterly board meetings via live ERP-connected anomaly detection.

## Scope

See approved plan: `.claude/plans/majestic-doodling-reef.md`

## Key Design Decisions

| Decision             | Choice                                           |
| -------------------- | ------------------------------------------------ |
| Anomaly detection v1 | Rule-based (ML deferred — data volume too small) |
| ERP v1               | QuickBooks Online, NetSuite, Sage Intacct, CSV   |
| LP reporting         | Human-authored only (no LLM hallucination risk)  |
| Tenant isolation     | PostgreSQL RLS + per-tenant CMK encryption       |
| Auth                 | Email + TOTP 2FA + SSO (SAML/OIDC)               |

---

## What Was Built (MVP Backend — 2026-04-20)

### Backend (`backend/app/`)

| Layer                         | Status      | Notes                                                    |
| ----------------------------- | ----------- | -------------------------------------------------------- |
| **Auth**                      | ✅          | Email + bcrypt + TOTP 2FA                                |
| **API endpoints**             | ✅          | All CRUD + upload + heatmap + alerts                     |
| **Data model**                | ✅          | 13 PostgreSQL tables via Alembic                         |
| **CSV ingestion**             | ✅          | Upload → RawStaging → KPI computation                    |
| **KPI engine**                | ✅          | 14 metrics computed (out of 18 spec; 4 are v2)           |
| **Alert engine**              | ✅          | All 5 rule types implemented                             |
| **Alert lifecycle**           | ✅          | open → acknowledged → resolved/false_positive/suppressed |
| **RBAC**                      | ✅          | Role guards on company create/delete and alert mutation  |
| **QuickBooks connector**      | 🔶 Scaffold | OAuth stub — returns mock tokens                         |
| **SSO (SAML/OIDC)**           | ❌          | Schema exists; not implemented                           |
| **Email/Slack notifications** | ❌          | Subscription + delivery tables exist; no delivery logic  |
| **6 of 18 KPIs**              | ❌          | YoY%, MoM%, ARR, NRR, logo churn%, FTE — v2 features     |

### API Endpoints

| Method | Path                              | Role required                                     |
| ------ | --------------------------------- | ------------------------------------------------- |
| POST   | `/auth/register`                  | —                                                 |
| POST   | `/auth/login`                     | —                                                 |
| POST   | `/auth/totp/setup`                | authenticated                                     |
| POST   | `/auth/totp/verify`               | authenticated                                     |
| GET    | `/companies`                      | any authenticated                                 |
| POST   | `/companies`                      | `pe_admin`, `pe_ops`                              |
| GET    | `/companies/{id}`                 | any authenticated                                 |
| PATCH  | `/companies/{id}`                 | any authenticated                                 |
| DELETE | `/companies/{id}`                 | `pe_admin`                                        |
| POST   | `/companies/{id}/upload-csv`      | any authenticated                                 |
| GET    | `/companies/{id}/metrics`         | any authenticated                                 |
| GET    | `/companies/{id}/metrics/history` | any authenticated                                 |
| GET    | `/companies/{id}/heatmap`         | any authenticated                                 |
| GET    | `/alerts`                         | any authenticated                                 |
| GET    | `/alerts/{id}`                    | any authenticated                                 |
| PATCH  | `/alerts/{id}`                    | `pe_admin`, `pe_ops`, `pe_operator`, `pe_partner` |
| POST   | `/alerts/evaluate`                | `pe_admin`, `pe_ops`, `pe_operator`, `pe_partner` |
| GET    | `/heatmap`                        | any authenticated                                 |

### Unit Tests (`backend/tests/`)

- `test_alert_engine.py` — 27 tests: all 5 rule types, async await chain, recovery, deduplication
- `test_csv_processor.py` — 8 tests: helpers, CSV parsing, metric supersession

## Out of Scope

ML anomaly detection, SAP connector, predictive forecasting, covenant tracking, valuation/carry calculations, fund-level reporting, LLM commentary, SMS notifications, QuickBooks OAuth (scaffold only), SSO, notification delivery.

---

## Running the Prototype

```bash
cd backend
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/pe_monitor"
export SECRET_KEY="your-32-char-minimum-secret-key-here"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Test CSV format**: `account_id, account_name, amount, [currency]`
