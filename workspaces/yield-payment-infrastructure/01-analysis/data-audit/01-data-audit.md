# FloatYield — Phase 02 Data Audit

**Date:** 2026-05-01
**Phase:** 02 — Data Audit (Trust Plane)
**Verdict:** AMBER — Data is fit for demo; not fit for production partner billing

---

## Trust-Plane Question

> **Is this data trustworthy? Which features are available at prediction time, leaky, or ethically loaded?**

Short answer: The data infrastructure is structurally sound (schema correct, API routes clean, no obvious injection surfaces), but the *content* is empty. Every number the dashboard shows — yield forecasts, model comparisons, reconciliation gaps — is either synthetic, hardcoded, or derived from seeded constants. A partner seeing this dashboard in demo is seeing a simulation, not a live system. This is acceptable for Sprint 1 demos. It is **not** acceptable for production billing or contract negotiation.

---

## 1. Data Inventory — What Exists, What's Missing

### 1.1 Accounts Table (`accounts`)

| Column | Type | Source | Status |
|--------|------|--------|--------|
| `id` | INTEGER | Auto-increment | ✅ Real |
| `partner_name` | TEXT | Seeded constants | ⚠️ Demo values (Celtic Bank, BlueRidge, Coastal Community) |
| `balance` | REAL | Seeded constants | ⚠️ Demo values ($50M, $120M, $78M) — not live account data |
| `yield_rate` | REAL | Seeded constants | ⚠️ Demo values — do not reflect actual negotiated rates |
| `created_at` | TEXT | `date('now')` | ✅ Functional |

**Trust verdict:** Seeded demo constants. These represent plausible partner archetypes but are not tied to actual bank relationships or live balances. Safe for internal demo. Unsafe for any externally visible document that implies active partnerships.

### 1.2 Yield Events Table (`yield_events`)

| Column | Type | Schema | Status |
|--------|------|--------|--------|
| `id` | INTEGER | ✅ Correct | ❌ **EMPTY — no rows ever inserted** |
| `account_id` | INTEGER | ✅ FK to accounts | ❌ No data |
| `event_date` | TEXT | ✅ Correct | ❌ No data |
| `balance_snapshot` | REAL | ✅ Correct | ❌ No data |
| `rate_snapshot` | REAL | ✅ Correct | ❌ No data |
| `daily_yield` | REAL | ✅ Correct | ❌ No data |
| `accrued_yield` | REAL | ✅ Correct | ❌ No data |

**Trust verdict:** Schema is correct. The table is the right shape. It has never received a single row. All yield calculations in the forecast engine are derived from in-memory formulas, not this table. This is the single largest data gap in the system.

### 1.3 Synthetic Data Generator (`scripts/forecast_models/data_generator.py`)

Generates synthetic yield series for model training/validation. Key characteristics:

- **Base yield:** `balance × (nominal_rate / 365)` — deterministic, no variance
- **White noise:** σ = 0.5 bps/day — simulates operational variance
- **Regime shifts:** 2–3 interest rate events/year (±3–5 bps, decaying over 2–6 weeks)
- **Signal-to-noise ratio:** ~1:1.5 (noise larger than signal)
- **Seed:** Fixed at 42 — reproducible across runs

**Trust verdict:** The synthetic data is well-designed for model development — realistic variance, proper regime shifts, and honest about the ~1:1 S/N. However:
- It is **never used in the production forecast API** — the backend generates flat synthetic history in-memory
- It was used only for offline model validation (journal 0028)
- The fixed seed (42) means every model comparison run produces identical results — not a flaw, but not disclosed

---

## 2. Feature Audit — Available, Leaky, Ethically Loaded

### 2.1 Available at Prediction Time (Safe)

These features are legitimately available when the forecast API is called and can be used without leakage:

| Feature | Location | Availability | Notes |
|---------|---------|-------------|-------|
| `balance` | `POST /forecast` params, `accounts` table | ✅ Request-time | Real-time partner balance |
| `yield_rate` | `POST /forecast` params, `accounts` table | ✅ Request-time | Negotiated rate — partner-specific |
| `forecast_days` | `POST /forecast` params | ✅ Request-time | Configurable horizon (7/14/30/60/90) |
| `rate_scenario` | `POST /forecast` params | ✅ Request-time | base/stress/upside — contractually defined |
| `account_id` | `POST /forecast` params | ✅ Request-time | Partner identifier |

All four inputs are available at prediction time. No future information leaks into these features.

### 2.2 Leaky Features (Do Not Use at Prediction Time)

A feature is **leaky** if it contains information that would not be available at the time of the prediction in a real deployment:

| Feature | Location | Leaky? | Evidence |
|---------|----------|---------|----------|
| `daily_yield` in `yield_events` | Database | ⚠️ **NOT YET** — table is empty | In production, this would be the target variable (what we're predicting). It is not yet populated, so no leakage exists today. But the schema is designed for batch明日 yield posting, which means the model would need to predict *forward* from T-1 data — a valid setup. |
| `accrued_yield` in `yield_events` | Database | ⚠️ **NOT YET** — table is empty | Same as above. |
| Synthetic history length (60 days) | `main.py:293` | ✅ **LEAKY** | The backend generates 60 days of flat synthetic history for model input. In production, this should be real historical yield data pulled from `yield_events`. Using flat synthetic data means ARIMA sees no signal — and defaults to the naive prediction. This masks model quality in the demo. |
| `balance` used in `_recon_gap` formula | `main.py:201` | ⚠️ **MARGINAL** | The recon_gap formula scales with balance, which is available at prediction time. However, the formula (`gap_bps = 1.23`) is a hardcoded constant — the balance dependency was removed in the fix. No temporal leakage. |

**Critical leaky feature: flat synthetic history.**

`main.py:293`:
```python
history = [base_yield_daily] * max(60, params.days)
```

This is 60 identical values. ARIMA's differencing operator on constant input produces a constant. The Holt model's trend estimator on constant input produces a constant. **All three models return identical output because the history contains zero signal.** This is not a model failure — it's a data quality failure. The models are working correctly on bad data.

In production with real `yield_events` data, the history would contain actual yield values with genuine variance — regime shifts, noise, slow drift. The model comparison (ARIMA vs Naive vs Holt) would then show real differentiation. Today it cannot, because the history is flat.

### 2.3 Ethically Loaded Features (Require Disclosure or Restriction)

A feature is **ethically loaded** if its use creates misrepresentation risk, discriminatory potential, or contractual harm:

| Feature | Location | Risk | Assessment |
|---------|----------|------|------------|
| `recon_gap_bps = 1.23` (hardcoded) | `main.py:266`, `main.py:214` | **Misrepresentation** | The number 1.23 bps is presented as a validated reference value. It was session-validated against the $1B/year reconciliation gap math (journal 0029). However: (a) it is hardcoded, not computed; (b) it represents a total system gap, not a per-account gap; (c) it has no variance — it is the same for all accounts regardless of size, rate, or partner. A partner seeing "1.23 bps" might interpret it as an empirically measured figure for their specific account. It is not. |
| `ARIMA(1,1,1)` marked "★ winner" | `page.tsx:540` | **Misrepresentation** | ARIMA is marked the winner because it was validated against synthetic data. In the production forecast, all three models return identical results because the history is flat. The "★ winner" label is therefore misleading — it implies ARIMA provides differentiated value in the live system, when it currently does not. |
| Demo partner names | `accounts` table | **Reputational** | Celtic Bank, BlueRidge Credit Union, Coastal Community Bank are plausible fictional archetypes. They are not actual FloatYield partners. If this dashboard is shown to real prospects, there is a risk of implied false partnership. |
| Scenario rates (0.85× / 1.10×) | `main.py:179-181` | **Contractual** | Stress (−15%) and upside (+10%) are reasonable scenario brackets. However, these are not tied to any defined economic scenario (e.g., "Fed cuts 50bps"). Presenting them as named scenarios without the underlying assumptions may create contractual ambiguity. |
| "vs ARIMA" delta column | `page.tsx:490` | **Misleading** | Shows the difference between each model's 30d yield and ARIMA's. Since all three models return identical values, every delta is $0. This column adds no information but implies a comparison exists. |

---

## 3. Data Flow Map

```
Partner Dashboard (browser)
    │
    ▼
GET /accounts ────────────────────────────────────────────────────────────────
    │                                                                   │
    │  ✅ Real-time from SQLite (seeded demo data)                      │
    │  ⚠️ 3 partner names, balances, rates — not live                  │
    ▼                                                                   │
POST /forecast/all ──────────────────────────────────────────────────────────
    │                                                                   │
    ├─── GET account from SQLite: balance, yield_rate ──────────────────►│ ✅
    │                                                                   │
    ├─── Generate 60-day synthetic history (FLAT — no signal) ──────────►│ ⚠️ LEAKED
    │   "history = [base_yield_daily] * 60"                             │
    │                                                                   │
    ├─── Run Naive: returns base_yield_daily (constant) ────────────────►│ ✅
    ├─── Run Holt: returns base_yield_daily (constant) ────────────────►│ ⚠️ No trend in flat history
    └─── Run ARIMA: returns base_yield_daily (constant) ────────────────►│ ⚠️ No differencing signal

    │
    ▼
yield_events table ──────────────────────────────────────────────────────────
    │
    │  ❌ EMPTY — no rows ever inserted
    │  In production: batch-loaded by bank yield feed (T+1)
    │  Would provide real historical daily_yield for ARIMA training
    ▼
Reconciliation Gap ────────────────────────────────────────────────────────────
    │
    ├─── Formula: hardcoded 1.23 bps (was: broken formula returning 0.0)
    │   Represents: total system gap on $1B/year, per session-validated math
    │   Shown identically for all accounts regardless of size/rate
    │
    └─── In production: calculated as (bank_actual_yield − FloatYield_calculated_yield)
        Bank provides daily Treasury statement (actual/actual day-count)
        FloatYield calculates simple interest (/365)
        Gap is measured, not estimated
        Tolerance threshold agreed in contract
```

---

## 4. Gap Analysis

### G-01: `yield_events` table is empty — no production data pathway

**Severity:** CRITICAL
**Phase:** Sprint 2 (Data Feed Integration)

The production forecast engine has no real yield data. The `yield_events` table schema is correct but has never received a row. The data flow for real bank yield statements (T+1 batch load from sponsor bank Treasury statements) does not exist in the codebase.

**What a real data feed looks like:**
1. Sponsor bank sends daily Treasury yield statement (end of business T+1)
2. Statement contains: account_id, date, balance_snapshot, rate_snapshot, daily_yield_actual, accrued_yield
3. FloatYield ETL pipeline ingests statement, validates totals, inserts into `yield_events`
4. Forecast API reads last N days from `yield_events` for model input
5. Reconciliation API compares `yield_events.daily_yield` vs `SUM(forecast rows)` for the month

**No ETL pipeline exists.** This is the primary technical gap.

### G-02: Synthetic history is flat — model comparison is meaningless in live system

**Severity:** HIGH
**Phase:** Sprint 1 (immediate — already deployed)

`main.py:293`: `history = [base_yield_daily] * max(60, params.days)`

This generates 60 identical values. All three models return identical outputs. The "★ ARIMA winner" badge and "vs ARIMA" delta columns are decorative — they show $0 differences. Partners cannot evaluate model quality from this display.

**Fix:** Replace flat synthetic history with real historical yield from `yield_events`. Until that table is populated, either:
- Remove the model comparison UI entirely, OR
- Show a disclosure banner: "Model comparison requires live yield history — currently showing synthetic baseline"

### G-03: `recon_gap_bps = 1.23` is hardcoded and misrepresented

**Severity:** MEDIUM
**Phase:** Sprint 1 (immediate — already deployed)

The constant 1.23 is presented without context:
- It is the same for all accounts regardless of balance or rate
- It has no variance — no uncertainty interval is shown
- It is described as "bps on $1B/year" but displayed for accounts of all sizes

**Partner misinterpretation risk:** A $50M partner seeing "1.23 bps" might assume this is their specific reconciliation risk. In reality, 1.23 bps is the system-wide reference gap on a $1B normalized book. For a $50M account, the actual dollar gap would be proportionally smaller.

**Fix options:**
1. Show `recon_gap_bps` with explicit label: "Reference system gap (1.23 bps on $1B/year annualized) — not your account's measured gap"
2. Remove from per-account display; show only in aggregate summary
3. Compute per-account gap from actual `yield_events` data in Sprint 2

### G-04: Demo partner names imply false partnerships

**Severity:** MEDIUM
**Phase:** Sprint 1 (immediate — display layer)

Celtic Bank, BlueRidge Credit Union, Coastal Community Bank are used as demo archetypes. If the dashboard is shown to real prospects, these names imply existing bank partnerships that do not exist.

**Fix:** Replace with obviously fictional names (e.g., "Demo Partner A", "Demo Bank 1") or clearly label all displays with "DEMO DATA — NOT LIVE ACCOUNTS" watermark.

### G-05: Scenario rates lack economic definition

**Severity:** LOW-MEDIUM
**Phase:** Sprint 2

Stress (−15%) and upside (+10%) are labeled as scenarios but have no underlying economic assumptions attached (e.g., "Fed funds rate cut 50bps," "300bps yield curve inversion"). In a contract negotiation, a partner might ask "what exactly does stress mean?" The current API cannot answer that.

**Fix:** Add scenario definitions as a configuration object:
```python
SCENARIOS = {
    "stress": {"fed_delta": -0.005, "description": "Fed cuts 50bps"},
    "upside": {"fed_delta": +0.003, "description": "Fed hikes 30bps"},
}
```

---

## 5. Feature Classification Summary

| Feature | Available @ T | Leaky | Ethically Loaded | Status |
|---------|--------------|-------|-----------------|--------|
| `balance` | ✅ | No | No | Demo only — needs live feed |
| `yield_rate` | ✅ | No | No | Demo rates — needs actual contract rates |
| `forecast_days` | ✅ | No | No | Clean |
| `rate_scenario` | ✅ | No | ⚠️ Undefined scenarios | Sprint 2 |
| Account ID | ✅ | No | No | Clean |
| Synthetic 60-day history | ⚠️ Generated | ⚠️ **YES — flat** | No | Sprint 2 (replace with real) |
| `recon_gap_bps` | ✅ Computed | No | ⚠️ **YES — hardcoded, no variance** | Sprint 2 (replace with measured) |
| `yield_events` rows | ❌ Empty | N/A | No | Sprint 2 |
| Model comparison delta | N/A | No | ⚠️ **YES — always $0** | Sprint 1 (remove or disclose) |
| ARIMA "★ winner" | N/A | No | ⚠️ **YES — misleading** | Sprint 1 (remove or disclose) |
| Partner names | Seeded | No | ⚠️ **YES — implies false partnerships** | Sprint 1 (rename) |

---

## 6. Sprint 1 Data Disclosures (What to Show / What to Hide)

For the Sprint 1 demo to be honest:

**✅ CAN show:**
- Account balances, yield rates, partner names (clearly labeled as DEMO)
- Forecast yield calculations (mathematically correct, even on flat history)
- Aggregate portfolio summary ($248M total, weighted avg rate 4.59%)
- The three-model comparison as a structural preview (not as validated results)
- The reconciliation gap reference value (with clear disclosure it's a system reference, not measured)

**⚠️ Show with disclosure banner:**
- Model comparison results: "Model comparison requires live yield history. Currently showing synthetic baseline."
- "Est. recon gap": "Estimated based on system reference of 1.23 bps on $1B/year — not measured from account statements."

**❌ Should NOT show (or must hide behind auth):**
- Any implication of actual bank partnerships
- "vs ARIMA" delta column (always $0 in current state — misleading)
- "★ ARIMA winner" badge (model has not been validated on live data in this system)

---

## 7. Recommendations

### Immediate (Sprint 1)

1. **Add data disclosure banner** to dashboard: "DEMO MODE — All data shown is synthetic. No live bank accounts or yield data are connected."
2. **Remove "★ ARIMA winner" badge** from model comparison — misleading in flat-history environment
3. **Remove "vs ARIMA" delta column** — always $0, adds no value
4. **Rename demo partners**: "Demo Partner A/B/C" or "Seed Bank 1/2/3" — removes false partnership implication
5. **Add scenario descriptions**: attach economic definitions to stress/upside rate modifiers

### Sprint 2 (Data Feed Integration)

1. **Build yield_events ETL pipeline**: T+1 batch load from sponsor bank Treasury statements
2. **Replace flat synthetic history** with real N-day lookback from `yield_events`
3. **Compute measured recon_gap** as `bank_actual_yield − FloatYield_calculated_yield` per account
4. **Validate ARIMA on real data**: re-run walk-forward comparison with actual yield history
5. **Add uncertainty intervals** to forecast: ±1σ band around point estimate

### Sprint 3+ (Production)

1. **Real-time balance feed**: webhook from partner bank when balance changes materially
2. **Rate negotiation tracking**: contract rates vs. applied rates — flag discrepancies
3. **Reconciliation dispute log**: track gap disputes, resolution history, tolerance threshold breaches
4. **Partner-level recon gap**: measured gap per partner, not system-wide constant

---

## 8. ADR Candidates

**ADR-06: Flat synthetic history must not be used for live model comparison**
- Status: Must be raised
- Decision: Remove or suppress model comparison UI until real `yield_events` data is available

**ADR-07: Reconciliation gap is a reference constant until measured data exists**
- Status: Must be raised
- Decision: Display `recon_gap_bps` only in aggregate summary with explicit reference to the $1B/year normalization; suppress per-account display

**ADR-08: Demo data must not imply live partnerships**
- Status: Must be raised
- Decision: Rename all seeded partners to clearly fictional names; add DEMO watermark to all dashboard views

---

_Phase 02 Data Audit complete. Sprint 1 deliverables are structurally sound but data content is demo-only. Production readiness requires Sprint 2 data feed integration._
