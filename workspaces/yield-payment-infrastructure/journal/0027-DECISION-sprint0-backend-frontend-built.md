---
type: DECISION
date: 2026-05-01
author: co-authored
session_id: current
project: yield-payment-infrastructure
topic: Sprint 0 built — FastAPI backend + React dashboard
phase: implement
tags: [sprint0, backend, frontend, fastapi, react]
---

## Decision

Built Sprint 0 scaffold for FloatYield: FastAPI backend + Next.js frontend.

## What Was Built

**Backend** (`backend/app/main.py`):
- `GET /health` — health check with `feature_store: true`
- `GET /accounts` — list 3 seeded partner accounts
- `POST /forecast` — single-model yield projection (simple flat yield)
- `POST /forecast/all` — all 3 models side by side (Naive, Holt, ARIMA)
- `GET /forecast/summary` — aggregate portfolio stats
- SQLite database seeded with 3 demo accounts: Celtic Bank ($50M @ 4.5%), BlueRidge Credit Union ($120M @ 4.75%), Coastal Community Bank ($78M @ 4.4%)

**Scripts**:
- `scripts/run_backend.sh` — uv pip install + uvicorn :8000
- `scripts/preflight.py` — health + seed + frontend validation
- `scripts/forecast_models/` — data_generator.py, models.py, validate.py, report.py

**Frontend** (`apps/web/`):
- Next.js 15 (App Router, TypeScript)
- Partner account selector
- Days + scenario controls (base/stress/upside)
- Bar chart comparing all 3 models
- Detail table: 30d yield, avg/day, recon gap bps, vs ARIMA delta
- ARIMA marked ★ winner

**Sprint 1 prompt** (`SPRINT1.md`): adapted from metis supply-chain prompt

## Why

User requested to build a real web backend + frontend for FloatYield.
Adapted the metis Sprint 1 setup prompt to FloatYield context.
Built Sprint 0 so user can run preflight and begin Sprint 1 decisions.

## Dependencies

- Python 3 with `fastapi`, `uvicorn`, `pydantic` in `backend/requirements.txt`
- Node.js with Next.js 15 in `apps/web/`
- `uv` for Python package management

## Outstanding

- Backend and frontend not yet started together (user must run `run_backend.sh` and `npm run dev`)
- SQLite database created on first backend startup
- `forecast/all` uses flat history for model inputs (real history from `yield_events` table is a future Sprint 2+ item)
