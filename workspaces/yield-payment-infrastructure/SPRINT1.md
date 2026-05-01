# FloatYield — Sprint 1: Forecast

**Workspace:** `workspaces/yield-payment-infrastructure/`
**Sprint Focus:** Yield forecast engine + partner dashboard

---

## Pre-Flight Setup

Run these three commands in order. Fix anything that fails before proceeding.

```bash
# 1. Start backend (in background terminal, or &)
./scripts/run_backend.sh

# 2. Start frontend (separate terminal)
cd apps/web && npm run dev

# 3. Run preflight
uv run python scripts/preflight.py
```

Expected preflight output:
```
=== FloatYield Preflight ===
  [OK] Backend health: {'status': 'ok', 'version': '0.1.0', 'feature_store': True, 'database': '...'}
  [OK] Accounts endpoint: 3 account(s) seeded
  [OK] Frontend serves on :3000
ALL CHECKS PASSED — environment is green
```

---

## What We Are Shipping Today

**FloatYield Forecast** — a yield projection engine that:
- Shows all partner accounts and their current balances / rates
- Projects daily yield for configurable horizons (7 / 14 / 30 / 60 / 90 days)
- Runs three scenarios: Base, Stress (−15%), Upside (+10%)
- Displays reconciliation gap in basis points
- Shows aggregate portfolio summary across all partners

---

## The Three Decisions You Drive

| Phase | What You Decide | What I Build |
|-------|----------------|--------------|
| **1. Account Scope** | Which partners / balances / rates to model | Forecast engine seeded with your inputs |
| **2. Scenario Weights** | How to distribute Base / Stress / Upside across partners | Scenario-adjusted yield projections |
| **3. Output Format** | Table? Chart? CSV export? PDF memo? | Chosen format rendered in the dashboard |

---

## What I Produce vs. What You Produce

| | Agent (me) | Human (you) |
|--|-----------|-------------|
| **Decisions** | — | Account scope, scenario weights, output format |
| **Backend API** | FastAPI + SQLite yield engine | — |
| **Frontend** | React dashboard with forecast table | — |
| **Analysis** | — | Go-to-market commentary, risk flags |
| **Validation** | preflight, tsc, live smoke test | — |

---

## Scaffolds Already Built

- `backend/app/main.py` — FastAPI app with `/health`, `/accounts`, `/forecast`, `/forecast/summary`
- `backend/requirements.txt` — fastapi, uvicorn, pydantic
- `scripts/run_backend.sh` — starts uvicorn on :8000
- `scripts/preflight.py` — health + seed validation
- `apps/web/` — Next.js 15 (App Router, TypeScript)
- `apps/web/app/page.tsx` — dashboard (accounts, forecast, summary)
- `yield_engine.py` (existing) — stdlib simulation engine from prior session

---

## Backend Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | `{"status": "ok", "feature_store": true, ...}` |
| GET | `/accounts` | All partner accounts |
| POST | `/forecast` | Yield forecast for one account + scenario |
| GET | `/forecast/summary` | Aggregate across all accounts |

## Next

Once preflight is green — tell me your first decision: **which partners and balances to model in Sprint 1?**
