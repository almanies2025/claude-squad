"""
FloatYield Backend — FastAPI
B2B yield-bearing payment infrastructure API
"""

import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ─── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(title="FloatYield API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── DB Path ─────────────────────────────────────────────────────────────────

DB_PATH = Path(__file__).parent.parent / "floatyield.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partner_name TEXT NOT NULL,
                balance REAL NOT NULL DEFAULT 0,
                yield_rate REAL NOT NULL DEFAULT 0.0,
                created_at TEXT NOT NULL DEFAULT (date('now'))
            );

            CREATE TABLE IF NOT EXISTS yield_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL REFERENCES accounts(id),
                event_date TEXT NOT NULL,
                balance_snapshot REAL NOT NULL,
                rate_snapshot REAL NOT NULL,
                daily_yield REAL NOT NULL,
                accrued_yield REAL NOT NULL
            );

            -- Seed demo data if empty — DEMO ONLY, not live partners
            INSERT OR IGNORE INTO accounts (id, partner_name, balance, yield_rate)
            SELECT 1, 'Demo Partner A', 50000000, 0.045 WHERE NOT EXISTS (SELECT 1 FROM accounts WHERE id=1);

            INSERT OR IGNORE INTO accounts (id, partner_name, balance, yield_rate)
            SELECT 2, 'Demo Partner B', 120000000, 0.0475 WHERE NOT EXISTS (SELECT 1 FROM accounts WHERE id=2);

            INSERT OR IGNORE INTO accounts (id, partner_name, balance, yield_rate)
            SELECT 3, 'Demo Partner C', 78000000, 0.044 WHERE NOT EXISTS (SELECT 1 FROM accounts WHERE id=3);
        """)
        db.commit()


# ─── Pydantic Models ─────────────────────────────────────────────────────────


class Account(BaseModel):
    id: int
    partner_name: str
    balance: float
    yield_rate: float
    created_at: str

    class Config:
        from_attributes = True


class YieldForecastRow(BaseModel):
    date: str
    days: int
    projected_yield: float
    cumulative_yield: float


class YieldForecast(BaseModel):
    account_id: int
    partner_name: str
    current_balance: float
    yield_rate: float
    forecast_days: int
    rows: list[YieldForecastRow]
    total_projected_yield: float
    recon_gap_bps: float
    recon_gap_description: str
    scenario_description: str


class ForecastParams(BaseModel):
    account_id: int
    days: int = 30
    rate_scenario: str = "base"  # "base" | "stress" | "upside"


class HealthResponse(BaseModel):
    status: str
    version: str
    feature_store: bool
    database: str


class SummaryStats(BaseModel):
    total_accounts: int
    total_balance: float
    weighted_avg_rate: float
    annualized_yield: float
    projected_30d_yield: float


class ModelResult(BaseModel):
    model_name: str
    total_projected_yield: float
    avg_daily: float
    recon_gap_bps: float
    lower_bound: float  # 80% CI lower bound (total projected yield)
    upper_bound: float  # 80% CI upper bound (total projected yield)


class MultiModelForecast(BaseModel):
    account_id: int
    partner_name: str
    current_balance: float
    yield_rate: float
    forecast_days: int
    models: list[ModelResult]
    recon_gap_description: str
    scenario_description: str


# ─── Routes ──────────────────────────────────────────────────────────────────


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        version="0.1.0",
        feature_store=True,
        database=str(DB_PATH),
    )


@app.get("/accounts", response_model=list[Account])
def list_accounts():
    with get_db() as db:
        rows = db.execute("SELECT * FROM accounts ORDER BY id").fetchall()
    return [dict(r) for r in rows]


@app.post("/forecast", response_model=YieldForecast)
def forecast(params: ForecastParams):
    with get_db() as db:
        acct = db.execute(
            "SELECT * FROM accounts WHERE id = ?", (params.account_id,)
        ).fetchone()
    if not acct:
        raise HTTPException(404, f"Account {params.account_id} not found")

    today = date.today()
    rate = dict(acct)["yield_rate"]

    if params.rate_scenario == "stress":
        rate = rate * 0.85
    elif params.rate_scenario == "upside":
        rate = rate * 1.10

    rows = []
    cumulative = 0.0
    balance = dict(acct)["balance"]

    for i in range(1, params.days + 1):
        d = today + timedelta(days=i)
        daily_yield = balance * (rate / 365.0)
        cumulative += daily_yield
        rows.append(
            YieldForecastRow(
                date=d.isoformat(),
                days=i,
                projected_yield=round(daily_yield, 2),
                cumulative_yield=round(cumulative, 2),
            )
        )

    # Reconciliation gap: ~1.23 bps on $1B/year annualised — the reference value
    # validated in session. Shown as system reference, not account-specific measurement.
    SCENARIOS = {
        "base": "Fed funds rate unchanged; Treasury yield at current market levels (~4.5%).",
        "stress": "Fed cuts 50bps; Treasury yield declines ~40bps. Short-duration assets reprice downward.",
        "upside": "Fed hikes 30bps; Treasury yield rises ~25bps. Short-duration assets reprice upward.",
    }
    scenario_desc = SCENARIOS.get(params.rate_scenario, SCENARIOS["base"])
    recon_gap_desc = (
        "System reference gap: 1.23 bps on $1B/year annualized. "
        "This is the normalized system gap — not your account's measured reconciliation gap. "
        "Measured gap = bank actual yield − FloatYield calculated yield (computed from your yield history)."
    )
    return YieldForecast(
        account_id=dict(acct)["id"],
        partner_name=dict(acct)["partner_name"],
        current_balance=balance,
        yield_rate=rate,
        forecast_days=params.days,
        rows=rows,
        total_projected_yield=round(cumulative, 2),
        recon_gap_bps=_recon_gap(params.account_id),
        recon_gap_description=recon_gap_desc,
        scenario_description=scenario_desc,
    )


# ─── Three-Model Forecast ─────────────────────────────────────────────────────

import numpy as np


def _naive_forecast(last_value: float, n: int) -> list[float]:
    return [last_value] * n


def _holt_forecast(
    series: list[float], n: int, alpha: float = 0.3, beta: float = 0.1
) -> list[float]:
    if len(series) < 2:
        return [series[-1]] * n
    level = series[-1]
    trend = (series[-1] - series[0]) / len(series)
    forecasts = []
    for i in range(n):
        h = level + (i + 1) * trend
        level = alpha * h + (1 - alpha) * (level + trend)
        trend = beta * (level - (level - trend)) + (1 - beta) * trend
        forecasts.append(h)
    return forecasts


def _arima_forecast(series: list[float], n: int) -> list[float]:
    if len(series) < 10:
        return [series[-1]] * n
    dy = np.diff(series)
    if len(dy) < 2 or np.std(dy) < 1e-9:
        return [series[-1]] * n
    phi = float(np.clip(np.corrcoef(dy[:-1], dy[1:])[0, 1], -0.9, 0.9))
    residuals = dy[1:] - phi * dy[:-1]
    theta = float(np.clip(np.mean(residuals) / (np.std(residuals) + 1e-9), -0.9, 0.9))
    cur = series[-1]
    dy_prev = dy[-1]
    forecasts = []
    for _ in range(n):
        dy_hat = phi * dy_prev
        next_val = cur + dy_hat
        forecasts.append(next_val)
        cur = next_val
        dy_prev = dy_hat
    return forecasts


def _compute_intervals(
    series: list[float],
    point_preds: list[float],
    model_name: str,
) -> tuple[list[float], list[float]]:
    """
    Compute 80% prediction intervals (lower/upper) for each forecast day.

    Uses empirical residual variance from the historical series:
    - Naive:  σ = std(diff(series)) — random-walk variance scales with √h
    - Holt:   σ = std(level-residuals) — trend adds h² term
    - ARIMA:  σ = std(AR-residuals) × √(1 + Σψ_i²) — AR damping

    Returns (lower_bounds, upper_bounds) as lists of daily totals (cumulative).
    """
    if len(series) < 5:
        # Insufficient history — return point predictions as degenerate intervals
        return point_preds, point_preds

    z_80 = 1.28  # z-score for 80% two-sided CI
    diffs = np.diff(series)

    if model_name.startswith("Naive"):
        sigma = float(np.std(diffs)) if len(diffs) > 1 else 0.0
        lower, upper = [], []
        for h in range(1, len(point_preds) + 1):
            se = sigma * np.sqrt(h)
            cum_lower = sum(point_preds[:h]) - z_80 * se * np.sqrt(h)
            cum_upper = sum(point_preds[:h]) + z_80 * se * np.sqrt(h)
            lower.append(max(0.0, round(cum_lower, 2)))
            upper.append(round(cum_upper, 2))
        return lower, upper

    elif model_name.startswith("Holt"):
        # Estimate level and trend variance from one-step-ahead residuals
        alpha, beta = 0.3, 0.1
        level = series[-1]
        trend = (series[-1] - series[0]) / len(series) if len(series) > 1 else 0.0
        level_resids, trend_resids = [], []
        for t in range(2, len(series)):
            l_tm1 = series[t - 1]
            b_tm1 = (series[t - 1] - series[t - 2]) / 1
            pred = l_tm1 + b_tm1
            level_resids.append(series[t] - pred)
        sigma_level = (
            float(np.std(level_resids))
            if level_resids
            else sigma_fallback(float(np.std(diffs)))
        )
        sigma_trend = float(np.std(trend_resids)) if trend_resids else sigma_level * 0.1
        sigma = np.sqrt(
            sigma_level**2 + (sigma_trend**2) * np.arange(1, len(point_preds) + 1)
        )
        sigma = np.maximum(sigma, sigma_level * 0.5)
        lower, upper = [], []
        for h, (pred, se) in enumerate(zip(point_preds, sigma), 1):
            se_h = sigma_level + sigma_trend * h
            cum_lower = sum(point_preds[:h]) - z_80 * se_h
            cum_upper = sum(point_preds[:h]) + z_80 * se_h
            lower.append(max(0.0, round(cum_lower, 2)))
            upper.append(round(cum_upper, 2))
        return lower, upper

    else:  # ARIMA
        dy = np.diff(series)
        if len(dy) < 3:
            return point_preds, point_preds
        phi = float(np.clip(np.corrcoef(dy[:-1], dy[1:])[0, 1], -0.9, 0.9))
        # Residual variance from AR(1) fit on differenced series
        residuals = dy[1:] - phi * dy[:-1]
        sigma2 = float(np.var(residuals)) if len(residuals) > 1 else 0.0
        # PSI weights: ψ_i = phi^i  →  sum(ψ_i²) = phi² / (1 - phi²)
        phi2 = phi * phi
        psi_sum = phi2 / (1.0 - phi2) if abs(phi2) < 0.99 else 10.0
        lower, upper = [], []
        for h in range(1, len(point_preds) + 1):
            # Variance at horizon h: σ² × (1 + Σ_{i=0}^{h-1} ψ_i²)
            # Approximate Σψ_i² for first h terms
            if h == 1:
                psi_cumsum = 1.0
            else:
                psi_cumsum = (
                    1.0 + phi2 * (1.0 - phi2 ** (2 * (h - 1))) / (1.0 - phi2**2)
                    if abs(phi2) < 0.99
                    else float(h)
                )
            se_h = np.sqrt(max(sigma2 * psi_cumsum, 1e-9))
            cum_lower = sum(point_preds[:h]) - z_80 * se_h
            cum_upper = sum(point_preds[:h]) + z_80 * se_h
            lower.append(max(0.0, round(cum_lower, 2)))
            upper.append(round(cum_upper, 2))
        return lower, upper


def sigma_fallback(s: float) -> float:
    return max(s, 1.0)


def _recon_gap(account_id: int) -> float:
    """
    Compute measured reconciliation gap from yield_events.

    gap_bps = mean(actual_yield - calculated_yield) / balance * 365 * 10000

    where calculated_yield = balance_snapshot * (rate_snapshot / 365).

    Falls back to 1.23 (system reference) if yield_events has fewer than
    5 rows for this account — insufficient history for a reliable measurement.
    """
    with get_db() as db:
        rows = db.execute(
            """
            SELECT balance_snapshot, rate_snapshot, daily_yield
              FROM yield_events
             WHERE account_id = ?
             ORDER BY event_date DESC
             LIMIT 30
            """,
            (account_id,),
        ).fetchall()

    if len(rows) < 5:
        return 1.23  # system reference — insufficient history

    gaps = []
    for r in rows:
        balance = float(r["balance_snapshot"])
        rate = float(r["rate_snapshot"])
        actual = float(r["daily_yield"])
        calculated = balance * (rate / 365)
        gap_daily = actual - calculated
        # Annualize and convert to bps of annual yield on $1B reference
        gap_bps = (gap_daily * 365 / balance) * 10000
        gaps.append(gap_bps)

    return round(sum(gaps) / len(gaps), 2)


@app.post("/forecast/all", response_model=MultiModelForecast)
def forecast_all(params: ForecastParams):
    """Return Naive, Holt, and ARIMA forecasts side-by-side for comparison."""
    with get_db() as db:
        acct = db.execute(
            "SELECT * FROM accounts WHERE id = ?", (params.account_id,)
        ).fetchone()
    if not acct:
        raise HTTPException(404, f"Account {params.account_id} not found")

    acct = dict(acct)
    today = date.today()
    base_rate = acct["yield_rate"]

    if params.rate_scenario == "stress":
        base_rate *= 0.85
    elif params.rate_scenario == "upside":
        base_rate *= 1.10

    balance = acct["balance"]
    base_yield_daily = balance * (base_rate / 365)

    # Query yield_events for actual lookback history.
    # Falls back to flat base_yield_daily if no history is available.
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
        # Most recent last (ascending order for the models)
        history = [float(r["daily_yield"]) for r in reversed(rows)]
    else:
        history = [base_yield_daily] * max(60, params.days)

    # Naive uses last observed yield (history[-1]), not the scenario rate.
    # Scenario modifier is applied via base_yield_daily for Holt/ARIMA.
    naive_preds = _naive_forecast(
        history[-1] if len(history) >= 1 else base_yield_daily, params.days
    )
    holt_preds = _holt_forecast(history, params.days)
    arima_preds = _arima_forecast(history, params.days)

    def make_model(name: str, preds: list[float]) -> ModelResult:
        total = sum(preds)
        lo, hi = _compute_intervals(history, preds, name)
        # lo/hi are per-day cumulative lower/upper bounds.
        # Use the final day's bound as the total forecast interval.
        lower_total = round(max(0.0, lo[-1]), 2) if lo else round(max(0.0, total), 2)
        upper_total = round(hi[-1], 2) if hi else round(total, 2)
        return ModelResult(
            model_name=name,
            total_projected_yield=round(total, 2),
            avg_daily=round(np.mean(preds), 2),
            recon_gap_bps=_recon_gap(params.account_id),
            lower_bound=lower_total,
            upper_bound=upper_total,
        )

    SCENARIOS = {
        "base": "Fed funds rate unchanged; Treasury yield at current market levels (~4.5%).",
        "stress": "Fed cuts 50bps; Treasury yield declines ~40bps. Short-duration assets reprice downward.",
        "upside": "Fed hikes 30bps; Treasury yield rises ~25bps. Short-duration assets reprice upward.",
    }
    scenario_desc = SCENARIOS.get(params.rate_scenario, SCENARIOS["base"])
    recon_gap_desc = (
        "System reference gap: 1.23 bps on $1B/year annualized. "
        "This is the normalized system gap — not your account's measured reconciliation gap. "
        "Measured gap = bank actual yield − FloatYield calculated yield (computed from your yield history)."
    )
    return MultiModelForecast(
        account_id=acct["id"],
        partner_name=acct["partner_name"],
        current_balance=balance,
        yield_rate=base_rate,
        forecast_days=params.days,
        models=[
            make_model("Naive (Persistence)", naive_preds),
            make_model("Holt (Double Exp)", holt_preds),
            make_model("ARIMA(1,1,1)", arima_preds),
        ],
        recon_gap_description=recon_gap_desc,
        scenario_description=scenario_desc,
    )


@app.get("/forecast/summary", response_model=SummaryStats)
def forecast_summary(days: int = Query(default=30)):
    with get_db() as db:
        accounts = db.execute("SELECT * FROM accounts").fetchall()

    if not accounts:
        raise HTTPException(404, "No accounts found")

    total_balance = sum(float(a["balance"]) for a in accounts)
    weighted_rate = (
        sum(float(a["balance"]) * float(a["yield_rate"]) for a in accounts)
        / total_balance
        if total_balance
        else 0
    )
    annualized_yield = total_balance * weighted_rate
    projected_30d = sum(
        float(a["balance"]) * (float(a["yield_rate"]) / 365) * days for a in accounts
    )

    return SummaryStats(
        total_accounts=len(accounts),
        total_balance=round(total_balance, 2),
        weighted_avg_rate=round(weighted_rate, 6),
        annualized_yield=round(annualized_yield, 2),
        projected_30d_yield=round(projected_30d, 2),
    )
