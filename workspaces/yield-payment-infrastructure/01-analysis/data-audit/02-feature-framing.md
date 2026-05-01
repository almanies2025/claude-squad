# FloatYield — Feature Framing (Trust Plane)

**Date:** 2026-05-01
**Phase:** 02 + 03 — Data Audit + Feature Framing
**Purpose:** Map every feature to its trust-plane classification. Define what to build, what to delay, what to disclose.

---

## Feature Trust Taxonomy

Every feature in FloatYield maps to exactly one trust category:

| Category | Definition | Build? | Example |
|----------|------------|--------|---------|
| **Safe** | Available at prediction time with real data; no leakage; no ethical risk | ✅ Build now | Balance, yield_rate, forecast_days |
| **Latent** | Schema exists, correct shape, awaiting real data feed | ⏳ Build scaffold, wait for data | `yield_events` table, ETL pipeline |
| **Broken** | Appears to work but produces misleading output | 🔧 Fix or suppress | Flat synthetic history, "vs ARIMA" column |
| **Leaky** | Uses information not available at prediction time | ❌ Remove | None currently active (flat history is broken, not leaky) |
| **Ethically Loaded** | Creates misrepresentation risk if deployed without disclosure | ⚠️ Deploy with banner | `recon_gap_bps = 1.23`, demo partner names |

---

## 1. Core Forecast Features

### F-01: Single-Account Yield Forecast (`POST /forecast`)

| Property | Value |
|----------|-------|
| **Category** | 🟡 Latent (Broken) |
| **Available @ T** | ✅ `balance`, `yield_rate`, `account_id`, `days`, `scenario` |
| **What it computes** | Daily yield = `balance × (rate_scenario × yield_rate / 365)`, cumulative over N days |
| **Output** | Daily rows + `total_projected_yield` + `recon_gap_bps` |
| **Broken because** | `recon_gap_bps` is hardcoded constant 1.23 — not measured from yield data |
| **Leakage** | None detected |
| **Ethically loaded** | `recon_gap_bps` misrepresented as measured; no uncertainty interval |
| **Fix** | Sprint 2: compute gap from `yield_events` actual vs. calculated |

### F-02: Multi-Model Comparison (`POST /forecast/all`)

| Property | Value |
|----------|-------|
| **Category** | 🔴 Broken |
| **Available @ T** | ✅ All inputs are request-time parameters |
| **Models** | Naive, Holt, ARIMA(1,1,1) |
| **Output** | Three `ModelResult` objects with `total_projected_yield`, `avg_daily`, `recon_gap_bps` |
| **Broken because** | Flat synthetic history (60 identical values) → all three models return identical output |
| **Leakage** | None (synthetic, not real data) |
| **Ethically loaded** | "★ ARIMA winner" badge is misleading; "vs ARIMA" delta is always $0 |
| **Fix** | Sprint 2: replace with real yield history → models differentiate naturally |

### F-03: Portfolio Summary (`GET /forecast/summary`)

| Property | Value |
|----------|-------|
| **Category** | 🟡 Latent |
| **Available @ T** | ✅ All inputs from `accounts` table (seeded demo data) |
| **What it computes** | Total balance, weighted avg rate, annualized yield, projected N-day yield |
| **Broken because** | Account data is demo-only; not live partner balances |
| **Leakage** | None |
| **Ethically loaded** | Partner names imply false partnerships |
| **Fix** | Sprint 1: rename partners to "Demo A/B/C"; Sprint 2: connect live account feed |

### F-04: Reconciliation Gap Display

| Property | Value |
|----------|-------|
| **Category** | ⚠️ Ethically Loaded |
| **Current value** | `recon_gap_bps = 1.23` (hardcoded constant, all accounts) |
| **What it means** | Reference system gap: 1.23 bps on $1B/year annualized |
| **In production** | Would be: `bank_actual_yield − FloatYield_calculated_yield` per account, measured daily |
| **Misrepresentation risk** | Partner sees 1.23 bps and interprets as their specific measured gap — it is not |
| **Disclosure requirement** | Must show: "Reference gap (system-wide, not account-specific). Actual gap = measured bank yield − calculated yield." |
| **Fix** | Sprint 2: measured from `yield_events`; Sprint 1: add explicit reference label |

---

## 2. Data Pipeline Features

### F-05: Yield Events Table (`yield_events`)

| Property | Value |
|----------|-------|
| **Category** | 🟡 Latent |
| **Schema** | ✅ Correct — `account_id`, `event_date`, `balance_snapshot`, `rate_snapshot`, `daily_yield`, `accrued_yield` |
| **Population** | ❌ Empty — never received a row |
| **Sprint 2 requirement** | T+1 ETL pipeline from sponsor bank Treasury statements |
| **Required for** | Real ARIMA history, measured recon gap, model validation |
| **Build** | ETL scaffold now; data connection Sprint 2 |

### F-06: Synthetic Data Generator (`scripts/forecast_models/data_generator.py`)

| Property | Value |
|----------|-------|
| **Category** | ✅ Safe (for model development only) |
| **Purpose** | Offline model validation — NOT for production forecast API |
| **Signal-to-noise** | ~1:1.5 — honest about yield being hard to forecast |
| **Used by** | `scripts/forecast_models/validate.py` — walk-forward ARIMA comparison |
| **NOT used by** | Production `POST /forecast/all` — which uses flat in-memory history |
| **Disclosure** | Must not appear in production UI |

### F-07: Account Seeding

| Property | Value |
|----------|-------|
| **Category** | ⚠️ Ethically Loaded |
| **Seed data** | Celtic Bank ($50M, 4.5%), BlueRidge CU ($120M, 4.75%), Coastal Community Bank ($78M, 4.4%) |
| **Implied risk** | Real bank names imply active partnerships |
| **Fix** | Rename to "Demo Partner A/B/C" before any external demo |

---

## 3. Scenario Features

### F-08: Rate Scenario Modifiers

| Property | Value |
|----------|-------|
| **Category** | 🟡 Latent (Missing definitions) |
| **Base** | `yield_rate × 1.0` |
| **Stress** | `yield_rate × 0.85` (−15%) |
| **Upside** | `yield_rate × 1.10` (+10%) |
| **Missing** | Economic definitions — what economic event produces −15% or +10%? |
| **Contract risk** | Partner asks: "What does 'stress' mean?" — cannot answer from current API |
| **Fix** | Add `scenario_metadata` to response: description, Fed rate delta, historical analog |
| **Build** | Sprint 2 |

---

## 4. Trust-Plane Feature Priority Matrix

```
                    ETHICAL RISK
                    Low ◄───────────────────► High
                    │                         │
                    │  F-01 (Latent)    F-04 (Eth Loaded)
                    │  F-02 (Broken)    F-07 (Eth Loaded)
    LEAKAGE  LOW ◄──┼─────────────────────────────────────
                    │  F-03 (Latent)    F-08 (Missing defs)
                    │  F-05 (Latent)
   LEAKAGE  HIGH ◄──┼─────────────────────────────────────
                    │              None active
                    │
                    └─────────────────────────────────────►
                              DATA QUALITY
                         Low ◄──────────────► High
```

**Quadrant map:**
- 🟢 Safe / High Quality: F-06 (synthetic generator — offline only)
- 🟡 Latent / Good Schema: F-01, F-03, F-05 — awaiting real data
- 🔴 Broken / Misleading: F-02 (model comparison — suppress or disclose)
- ⚠️ Ethically Loaded / Needs Disclosure: F-04, F-07, F-08

---

## 5. What to Build Next

### Sprint 1 (This Week — Demo Integrity)

| # | Feature | Action | Rationale |
|---|---------|--------|-----------|
| 1 | Demo data disclosure banner | Add to dashboard | Legal/ethical minimum for external demo |
| 2 | Rename demo partners | A/B/C naming | Remove false partnership implication |
| 3 | Remove "★ ARIMA winner" badge | Suppress from UI | Misleading on flat history |
| 4 | Remove "vs ARIMA" delta column | Suppress from UI | Always $0 — misleading |
| 5 | Label `recon_gap_bps` as "Reference gap" | Update label text | Prevents misinterpretation as measured |
| 6 | Scenario metadata | Add descriptions to API response | Contractual clarity |

### Sprint 2 (Data Feed Integration — 2–3 weeks)

| # | Feature | Action | Rationale |
|---|---------|--------|-----------|
| 1 | `yield_events` ETL pipeline | Build T+1 batch loader | Unblocks all downstream features |
| 2 | Replace flat history with real lookback | Update `POST /forecast/all` | Models differentiate; comparison meaningful |
| 3 | Measured recon gap | Compute from `yield_events` actual vs. calculated | Replaces hardcoded constant |
| 4 | ARIMA model re-validation | Walk-forward on real data | Confirms or retracts ARIMA selection |
| 5 | Uncertainty intervals | ±1σ forecast bands | Partners need range, not point estimate |
| 6 | Live account balance feed | Webhook or polling from partner bank | Real-time forecast accuracy |

### Sprint 3 (Production Hardening — 4–6 weeks)

| # | Feature | Action | Rationale |
|---|---------|--------|-----------|
| 1 | Reconciliation dispute log | New `recon_disputes` table + API | Track gap disputes per partner |
| 2 | Rate discrepancy tracking | Contract rate vs. applied rate flag | Detects bank billing errors |
| 3 | Tolerance threshold breach alerts | Alert when measured gap exceeds contract threshold | Proactive partner communication |
| 4 | Multi-partner portfolio view | Aggregate across all partner accounts | Single source of truth for FloatYield ops |
| 5 | Regulatory reporting module | 1099-INT generation, state unclaimed property | Compliance requirement |

---

## 6. ADRs

### ADR-06: Flat Synthetic History — Suppress Model Comparison in Sprint 1

**Status:** PROPOSED
**Scope:** `POST /forecast/all`, dashboard model comparison UI

**Problem:** Flat in-memory synthetic history (`history = [base_yield_daily] * 60`) produces identical outputs from all three forecast models. The "★ ARIMA winner" badge and "vs ARIMA" delta columns are therefore misleading — they show differentiation that does not exist in the live system.

**Decision:** Remove the "★ ARIMA winner" badge and "vs ARIMA" delta column from the dashboard for Sprint 1. Retain the three-model structure for future use when real yield history is connected. Add a disclosure: "Model structure shown for preview — comparison requires live yield data."

**Consequences:** Partners cannot evaluate model quality from Sprint 1 demo. This is honest about the current state.

---

### ADR-07: Reconciliation Gap — Reference Value With Mandatory Disclosure

**Status:** PROPOSED
**Scope:** `POST /forecast`, `POST /forecast/all`, dashboard display

**Problem:** `recon_gap_bps = 1.23` is displayed identically for all accounts regardless of balance or rate. It is a system-wide reference value, not a per-account measured value. Partners may misinterpret it as their specific reconciliation risk.

**Decision:** Keep the 1.23 bps value (it is the correct system reference) but:
1. Rename field/label to `reference_recon_gap_bps` in API response
2. Add `recon_gap_description: "System reference gap (1.23 bps on $1B/year annualized) — not your account's measured gap"
3. Remove per-account recon gap from detail display; show only in aggregate summary

**Consequences:** Per-account reconciliation gap cannot be shown until `yield_events` is populated (Sprint 2).

---

### ADR-08: Demo Partner Names Must Not Imply Live Partnerships

**Status:** PROPOSED
**Scope:** Seed data in `init_db()`, dashboard partner labels

**Problem:** Celtic Bank, BlueRidge Credit Union, Coastal Community Bank are real-sounding institution names used as demo archetypes. External demos imply active partnerships that do not exist.

**Decision:** Rename all seeded demo partners to clearly fictional names: "Demo Partner A", "Demo Partner B", "Demo Partner C". Add persistent "DEMO DATA" watermark to dashboard header.

**Consequences:** Internal demos look less realistic. Acceptable tradeoff for avoiding false partnership implication.

---

_Phase 02+03 complete. Feature framing delivers a priority matrix, three ADRs, and a sprint-by-sprint build plan grounded in the data audit findings._
