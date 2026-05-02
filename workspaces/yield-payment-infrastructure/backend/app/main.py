"""
FloatYield Backend — FastAPI
B2B yield-bearing payment infrastructure API
"""

import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from app.core.config import settings

# ─── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(title="FloatYield API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
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

            CREATE UNIQUE INDEX IF NOT EXISTS idx_yield_events_account_date
                ON yield_events(account_id, event_date);

            CREATE TABLE IF NOT EXISTS recon_disputes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL REFERENCES accounts(id),
                dispute_date TEXT NOT NULL,
                filed_by TEXT NOT NULL,
                gap_bps REAL NOT NULL,
                gap_dollar_amount REAL NOT NULL,
                dispute_type TEXT NOT NULL DEFAULT 'recon_gap',
                reason TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT (date('now'))
            );

            CREATE TABLE IF NOT EXISTS threshold_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL REFERENCES accounts(id),
                alert_date TEXT NOT NULL,
                gap_bps REAL NOT NULL,
                threshold_bps REAL NOT NULL,
                severity TEXT NOT NULL DEFAULT 'warning',
                acknowledged INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (date('now'))
            );

            CREATE TABLE IF NOT EXISTS rate_discrepancies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL REFERENCES accounts(id),
                discrepancy_date TEXT NOT NULL,
                contract_rate REAL NOT NULL,
                applied_rate REAL NOT NULL,
                discrepancy_bps REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT (date('now'))
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

    @field_validator("account_id")
    @classmethod
    def account_id_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("account_id must be a positive integer")
        return v

    @field_validator("days")
    @classmethod
    def days_range(cls, v: int) -> int:
        if not (1 <= v <= 365):
            raise ValueError("days must be between 1 and 365")
        return v

    @field_validator("rate_scenario")
    @classmethod
    def valid_scenario(cls, v: str) -> str:
        if v not in ("base", "stress", "upside"):
            raise ValueError("rate_scenario must be 'base', 'stress', or 'upside'")
        return v


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


class Dispute(BaseModel):
    id: int
    account_id: int
    partner_name: str
    dispute_date: str
    filed_by: str
    gap_bps: float
    gap_dollar_amount: float
    dispute_type: str
    reason: str
    status: str
    notes: str | None
    created_at: str

    class Config:
        from_attributes = True


class DisputeCreate(BaseModel):
    account_id: int
    dispute_date: str
    filed_by: str
    gap_bps: float
    gap_dollar_amount: float
    dispute_type: str = "recon_gap"
    reason: str
    notes: str | None = None

    @field_validator("gap_bps", "gap_dollar_amount")
    @classmethod
    def gap_must_be_nonnegative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("gap_bps and gap_dollar_amount must be non-negative")
        return v

    @field_validator("dispute_date")
    @classmethod
    def dispute_date_must_be_valid_iso(cls, v: str) -> str:
        from datetime import datetime

        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("dispute_date must be in YYYY-MM-DD format")
        return v

    @field_validator("filed_by")
    @classmethod
    def filed_by_max_length(cls, v: str) -> str:
        if len(v) > 200:
            raise ValueError("filed_by must be 200 characters or fewer")
        return v

    @field_validator("reason")
    @classmethod
    def reason_max_length(cls, v: str) -> str:
        if len(v) > 2000:
            raise ValueError("reason must be 2000 characters or fewer")
        return v


class DisputeUpdate(BaseModel):
    status: Literal["open", "resolved", "escalated"] | None = None
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def notes_max_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 2000:
            raise ValueError("notes must be 2000 characters or fewer")
        return v


class DisputeSummary(BaseModel):
    total_disputes: int
    open_disputes: int
    resolved_disputes: int
    escalated_disputes: int
    total_disputed_amount: float


class RateDiscrepancy(BaseModel):
    id: int
    account_id: int
    partner_name: str
    discrepancy_date: str
    contract_rate: float
    applied_rate: float
    discrepancy_bps: float
    status: str
    notes: str | None
    created_at: str

    class Config:
        from_attributes = True


class RateDiscrepancyCreate(BaseModel):
    account_id: int
    discrepancy_date: str
    contract_rate: float
    applied_rate: float
    discrepancy_bps: float
    notes: str | None = None

    @field_validator("discrepancy_date")
    @classmethod
    def discrepancy_date_must_be_valid_iso(cls, v: str) -> str:
        from datetime import datetime

        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("discrepancy_date must be in YYYY-MM-DD format")
        return v

    @field_validator("discrepancy_bps")
    @classmethod
    def discrepancy_bps_must_be_nonnegative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("discrepancy_bps must be non-negative")
        return v

    @field_validator("contract_rate", "applied_rate")
    @classmethod
    def rate_must_be_nonnegative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("rate must be non-negative")
        return v


class ThresholdAlert(BaseModel):
    id: int
    account_id: int
    partner_name: str
    alert_date: str
    gap_bps: float
    threshold_bps: float
    severity: str
    acknowledged: bool
    created_at: str

    class Config:
        from_attributes = True


class PortfolioStats(BaseModel):
    total_accounts: int
    total_balance: float
    total_disputes: int
    open_disputes: int
    threshold_alerts: int
    unacknowledged_alerts: int
    avg_gap_bps: float
    max_gap_bps: float
    annualized_yield: float
    projected_30d_yield: float


class RegulatoryReport(BaseModel):
    account_id: int
    partner_name: str
    report_type: str
    tax_year: int
    total_yield: float
    account_balance: float
    yield_rate: float
    generated_at: str


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
    gap_bps, recon_gap_desc = _recon_gap_info(params.account_id)
    return YieldForecast(
        account_id=dict(acct)["id"],
        partner_name=dict(acct)["partner_name"],
        current_balance=balance,
        yield_rate=rate,
        forecast_days=params.days,
        rows=rows,
        total_projected_yield=round(cumulative, 2),
        recon_gap_bps=gap_bps,
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
            cum_lower = sum(point_preds[:h]) - z_80 * se
            cum_upper = sum(point_preds[:h]) + z_80 * se
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
            # sigma[h-1] = sqrt(sigma_level² + sigma_trend² * h²) — widens with horizon
            se_h = sigma[h - 1]
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
        # PSI weights: ψ_i = phi^i.  Σ_{i=0}^{h-1} ψ_i² = Σ_{i=0}^{h-1} phi^{2i}
        # = 1 + phi² + phi⁴ + ... + phi^{2(h-1)} = (1 - phi^{2h}) / (1 - phi²)
        phi2 = phi * phi
        lower, upper = [], []
        for h in range(1, len(point_preds) + 1):
            if abs(phi2) < 0.99:
                # Geometric series: (1 - phi^{2h}) / (1 - phi²)
                psi_cumsum = (1.0 - phi2**h) / (1.0 - phi2)
            else:
                psi_cumsum = float(h)
            se_h = np.sqrt(max(sigma2 * psi_cumsum, 1e-9))
            cum_lower = sum(point_preds[:h]) - z_80 * se_h
            cum_upper = sum(point_preds[:h]) + z_80 * se_h
            lower.append(max(0.0, round(cum_lower, 2)))
            upper.append(round(cum_upper, 2))
        return lower, upper


def sigma_fallback(s: float) -> float:
    return max(s, 1.0)


def _recon_gap_info(account_id: int) -> tuple[float, str]:
    """
    Compute measured reconciliation gap from yield_events.

    gap_bps = mean(actual_yield - calculated_yield) / balance * 365 * 10000

    where calculated_yield = balance_snapshot * (rate_snapshot / 365).

    Returns (gap_bps, description). Falls back to (1.23, system_reference_desc)
    if yield_events has fewer than 5 rows for this account.
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
        return (
            1.23,
            (
                "System reference gap: 1.23 bps on $1B/year annualized. "
                "Insufficient yield history for a measured gap — falling back to normalized system reference."
            ),
        )

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

    measured = round(sum(gaps) / len(gaps), 2)
    return (
        measured,
        (
            f"Measured gap: {measured:.2f} bps on $1B/year annualized "
            f"({len(rows)} events, {30}-day lookback). "
            "This is your account's measured reconciliation gap — bank actual yield minus FloatYield calculated yield."
        ),
    )


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

    # Scenario rate adjustment — a parallel shift applied to the yield curve.
    # Stress: -15% (Fed cuts 50bps, Treasuries reprice down ~40bps).
    # Upside: +10% (Fed hikes 30bps, Treasuries reprice up ~25bps).
    scenario_multiplier = 1.0
    if params.rate_scenario == "stress":
        scenario_multiplier = 0.85
    elif params.rate_scenario == "upside":
        scenario_multiplier = 1.10

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

    # Scenario adjustment is applied as a parallel shift to model outputs.
    # The historical series was generated at base_rate; scenario rates shift
    # the entire projected yield curve proportionally.
    naive_preds = _naive_forecast(
        history[-1] if len(history) >= 1 else base_yield_daily, params.days
    )
    holt_preds = _holt_forecast(history, params.days)
    arima_preds = _arima_forecast(history, params.days)

    # Apply scenario parallel shift to all model outputs (dollar terms).
    # Holt/ARIMA forecast in daily yield $; multiply by scenario_multiplier.
    # Naive is already a flat forecast at history[-1] — shift it too.
    if scenario_multiplier != 1.0:
        naive_preds = [p * scenario_multiplier for p in naive_preds]
        holt_preds = [p * scenario_multiplier for p in holt_preds]
        arima_preds = [p * scenario_multiplier for p in arima_preds]

    gap_bps, recon_gap_desc = _recon_gap_info(params.account_id)

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
            recon_gap_bps=gap_bps,
            lower_bound=lower_total,
            upper_bound=upper_total,
        )

    scenario_rate = base_rate * scenario_multiplier
    SCENARIOS = {
        "base": "Fed funds rate unchanged; Treasury yield at current market levels (~4.5%).",
        "stress": "Fed cuts 50bps; Treasury yield declines ~40bps. Short-duration assets reprice downward.",
        "upside": "Fed hikes 30bps; Treasury yield rises ~25bps. Short-duration assets reprice upward.",
    }
    scenario_desc = SCENARIOS.get(params.rate_scenario, SCENARIOS["base"])
    return MultiModelForecast(
        account_id=acct["id"],
        partner_name=acct["partner_name"],
        current_balance=balance,
        yield_rate=scenario_rate,
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


# ─── Reconciliation Disputes ─────────────────────────────────────────────────


@app.get("/disputes", response_model=list[Dispute])
def list_disputes(account_id: int | None = Query(default=None)):
    """List all recon disputes, optionally filtered by account."""
    with get_db() as db:
        if account_id is not None:
            rows = db.execute(
                """
                SELECT d.*, a.partner_name
                  FROM recon_disputes d
                  JOIN accounts a ON d.account_id = a.id
                 WHERE d.account_id = ?
                 ORDER BY d.created_at DESC
                """,
                (account_id,),
            ).fetchall()
        else:
            rows = db.execute(
                """
                SELECT d.*, a.partner_name
                  FROM recon_disputes d
                  JOIN accounts a ON d.account_id = a.id
                 ORDER BY d.created_at DESC
                """,
            ).fetchall()
    return [dict(r) for r in rows]


@app.post("/disputes", response_model=Dispute)
def create_dispute(data: DisputeCreate):
    """File a new reconciliation dispute."""
    with get_db() as db:
        acct = db.execute(
            "SELECT partner_name FROM accounts WHERE id = ?", (data.account_id,)
        ).fetchone()
    if not acct:
        raise HTTPException(404, f"Account {data.account_id} not found")
    with get_db() as db:
        cur = db.execute(
            """
            INSERT INTO recon_disputes
                (account_id, dispute_date, filed_by, gap_bps, gap_dollar_amount,
                 dispute_type, reason, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'open', ?)
            """,
            (
                data.account_id,
                data.dispute_date,
                data.filed_by,
                data.gap_bps,
                data.gap_dollar_amount,
                data.dispute_type,
                data.reason,
                data.notes,
            ),
        )
        db.commit()
        row = db.execute(
            """
            SELECT d.*, a.partner_name
              FROM recon_disputes d
              JOIN accounts a ON d.account_id = a.id
             WHERE d.id = ?
            """,
            (cur.lastrowid,),
        ).fetchone()
    return dict(row)


@app.patch("/disputes/{dispute_id}", response_model=Dispute)
def update_dispute(dispute_id: int, data: DisputeUpdate):
    """Update dispute status or notes."""
    with get_db() as db:
        existing = db.execute(
            "SELECT * FROM recon_disputes WHERE id = ?", (dispute_id,)
        ).fetchone()
    if not existing:
        raise HTTPException(404, f"Dispute {dispute_id} not found")
    with get_db() as db:
        if data.status is not None and data.notes is not None:
            db.execute(
                "UPDATE recon_disputes SET status = ?, notes = ? WHERE id = ?",
                (data.status, data.notes, dispute_id),
            )
        elif data.status is not None:
            db.execute(
                "UPDATE recon_disputes SET status = ? WHERE id = ?",
                (data.status, dispute_id),
            )
        elif data.notes is not None:
            db.execute(
                "UPDATE recon_disputes SET notes = ? WHERE id = ?",
                (data.notes, dispute_id),
            )
        else:
            raise HTTPException(400, "No fields to update")
        db.commit()
        row = db.execute(
            """
            SELECT d.*, a.partner_name
              FROM recon_disputes d
              JOIN accounts a ON d.account_id = a.id
             WHERE d.id = ?
            """,
            (dispute_id,),
        ).fetchone()
    return dict(row)


@app.get("/disputes/summary", response_model=DisputeSummary)
def disputes_summary():
    """Aggregate dispute counts and totals."""
    with get_db() as db:
        rows = db.execute(
            "SELECT status, gap_dollar_amount FROM recon_disputes"
        ).fetchall()
    total = len(rows)
    open_d = sum(1 for r in rows if r["status"] == "open")
    resolved = sum(1 for r in rows if r["status"] == "resolved")
    escalated = sum(1 for r in rows if r["status"] == "escalated")
    total_amt = sum(float(r["gap_dollar_amount"]) for r in rows)
    return DisputeSummary(
        total_disputes=total,
        open_disputes=open_d,
        resolved_disputes=resolved,
        escalated_disputes=escalated,
        total_disputed_amount=round(total_amt, 2),
    )


# ─── Rate Discrepancies ─────────────────────────────────────────────────────


@app.get("/rate-discrepancies", response_model=list[RateDiscrepancy])
def list_rate_discrepancies(account_id: int | None = Query(default=None)):
    with get_db() as db:
        if account_id is not None:
            rows = db.execute(
                """
                SELECT r.*, a.partner_name
                  FROM rate_discrepancies r
                  JOIN accounts a ON r.account_id = a.id
                 WHERE r.account_id = ?
                 ORDER BY r.created_at DESC
                """,
                (account_id,),
            ).fetchall()
        else:
            rows = db.execute(
                """
                SELECT r.*, a.partner_name
                  FROM rate_discrepancies r
                  JOIN accounts a ON r.account_id = a.id
                 ORDER BY r.created_at DESC
                """,
            ).fetchall()
    return [dict(r) for r in rows]


@app.post("/rate-discrepancies", response_model=RateDiscrepancy)
def create_rate_discrepancy(data: RateDiscrepancyCreate):
    with get_db() as db:
        acct = db.execute(
            "SELECT partner_name FROM accounts WHERE id = ?", (data.account_id,)
        ).fetchone()
    if not acct:
        raise HTTPException(404, f"Account {data.account_id} not found")
    with get_db() as db:
        cur = db.execute(
            """
            INSERT INTO rate_discrepancies
                (account_id, discrepancy_date, contract_rate, applied_rate,
                 discrepancy_bps, status, notes)
            VALUES (?, ?, ?, ?, ?, 'open', ?)
            """,
            (
                data.account_id,
                data.discrepancy_date,
                data.contract_rate,
                data.applied_rate,
                data.discrepancy_bps,
                data.notes,
            ),
        )
        db.commit()
        row = db.execute(
            """
            SELECT r.*, a.partner_name
              FROM rate_discrepancies r
              JOIN accounts a ON r.account_id = a.id
             WHERE r.id = ?
            """,
            (cur.lastrowid,),
        ).fetchone()
    return dict(row)


# ─── Threshold Alerts ────────────────────────────────────────────────────────


@app.get("/alerts", response_model=list[ThresholdAlert])
def list_alerts(
    account_id: int | None = Query(default=None),
    acknowledged: bool | None = Query(default=None),
):
    """
    List threshold breach alerts.
    - account_id: filter by partner account
    - acknowledged: true = acknowledged only, false = unacknowledged only, omitted = all
    """
    with get_db() as db:
        if account_id is not None:
            base = """
                SELECT t.*, a.partner_name
                  FROM threshold_alerts t
                  JOIN accounts a ON t.account_id = a.id
                 WHERE t.account_id = ?
            """
            params = [account_id]
            if acknowledged is not None:
                base += " AND t.acknowledged = ?"
                params.append(1 if acknowledged else 0)
            rows = db.execute(base + " ORDER BY t.created_at DESC", params).fetchall()
        else:
            if acknowledged is not None:
                rows = db.execute(
                    """
                    SELECT t.*, a.partner_name
                      FROM threshold_alerts t
                      JOIN accounts a ON t.account_id = a.id
                     WHERE t.acknowledged = ?
                     ORDER BY t.created_at DESC
                    """,
                    (1 if acknowledged else 0,),
                ).fetchall()
            else:
                rows = db.execute(
                    """
                    SELECT t.*, a.partner_name
                      FROM threshold_alerts t
                      JOIN accounts a ON t.account_id = a.id
                     ORDER BY t.created_at DESC
                    """,
                ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["acknowledged"] = bool(d["acknowledged"])
        result.append(d)
    return result


@app.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int):
    """Acknowledge a threshold alert."""
    with get_db() as db:
        existing = db.execute(
            "SELECT * FROM threshold_alerts WHERE id = ?", (alert_id,)
        ).fetchone()
    if not existing:
        raise HTTPException(404, f"Alert {alert_id} not found")
    with get_db() as db:
        db.execute(
            "UPDATE threshold_alerts SET acknowledged = 1 WHERE id = ?",
            (alert_id,),
        )
        db.commit()
    return {"status": "acknowledged", "alert_id": alert_id}


# ─── Portfolio View ─────────────────────────────────────────────────────────

# Default gap threshold in bps — triggers an alert when measured gap exceeds this.
# In production this would be per-account, stored in the accounts table.
DEFAULT_GAP_THRESHOLD_BPS = 2.0


@app.get("/portfolio", response_model=PortfolioStats)
def portfolio_stats():
    """Aggregate stats across all partner accounts — single source of truth for FloatYield ops."""
    today = date.today().isoformat()

    with get_db() as db:
        accounts = db.execute("SELECT * FROM accounts").fetchall()
        dispute_counts = db.execute(
            "SELECT account_id, status, COUNT(*) as cnt FROM recon_disputes GROUP BY account_id, status"
        ).fetchall()
        alert_counts = db.execute(
            "SELECT account_id, acknowledged, COUNT(*) as cnt FROM threshold_alerts GROUP BY account_id, acknowledged"
        ).fetchall()
        gap_rows = db.execute(
            """
            SELECT account_id, balance_snapshot, rate_snapshot, daily_yield
              FROM yield_events
             ORDER BY event_date DESC
            """,
        ).fetchall()
        # Existing unacknowledged alert dates per account — for deduplication
        existing_alerts = db.execute(
            """
            SELECT account_id, alert_date FROM threshold_alerts
             WHERE acknowledged = 0
            """,
        ).fetchall()

    # Deduplication map: account_id → set of alert dates with open alerts
    existing_alert_dates: dict[int, set[str]] = {}
    for row in existing_alerts:
        existing_alert_dates.setdefault(row["account_id"], set()).add(row["alert_date"])

    total_balance = sum(float(a["balance"]) for a in accounts)
    weighted_rate = (
        sum(float(a["balance"]) * float(a["yield_rate"]) for a in accounts)
        / total_balance
        if total_balance
        else 0
    )
    annualized_yield = total_balance * weighted_rate

    # Dispute summary
    total_disputes = sum(d["cnt"] for d in dispute_counts)
    open_count = sum(d["cnt"] for d in dispute_counts if d["status"] == "open")

    # Alert summary
    unack_count = sum(a["cnt"] for a in alert_counts if not a["acknowledged"])
    total_alerts = sum(a["cnt"] for a in alert_counts)

    # Gap stats from yield_events
    if gap_rows:
        by_acct: dict[int, list] = {}
        for r in gap_rows:
            by_acct.setdefault(r["account_id"], []).append(r)
        gaps = []
        for acct_id, rows in by_acct.items():
            for r in rows:
                balance = float(r["balance_snapshot"])
                rate = float(r["rate_snapshot"])
                actual = float(r["daily_yield"])
                calculated = balance * (rate / 365)
                gap_bps = ((actual - calculated) * 365 / balance) * 10000
                gaps.append(gap_bps)
        avg_gap = sum(gaps) / len(gaps) if gaps else 1.23
        max_gap = max(gaps) if gaps else 1.23
    else:
        avg_gap = 1.23
        max_gap = 1.23

    # ── Threshold Monitoring ────────────────────────────────────────────────
    # Check each account's worst (max) gap across all historical days.
    # Insert an alert if: worst gap exceeds threshold AND no open alert already exists today.
    if gap_rows:
        by_acct_gaps: dict[int, list] = {}
        for r in gap_rows:
            by_acct_gaps.setdefault(r["account_id"], []).append(r)
        new_alerts = []
        for acct_id, rows in by_acct_gaps.items():
            # Find worst gap across all historical days for this account
            worst_gap = None
            for r in rows:
                balance = float(r["balance_snapshot"])
                rate = float(r["rate_snapshot"])
                actual = float(r["daily_yield"])
                calculated = balance * (rate / 365)
                gap_bps = ((actual - calculated) * 365 / balance) * 10000
                if worst_gap is None or gap_bps > worst_gap:
                    worst_gap = gap_bps
            if worst_gap is not None and worst_gap > DEFAULT_GAP_THRESHOLD_BPS:
                already_alerted_today = today in existing_alert_dates.get(
                    acct_id, set()
                )
                if not already_alerted_today:
                    severity = (
                        "critical"
                        if worst_gap > DEFAULT_GAP_THRESHOLD_BPS * 2
                        else "warning"
                    )
                    new_alerts.append(
                        {
                            "account_id": acct_id,
                            "alert_date": today,
                            "gap_bps": round(worst_gap, 4),
                            "threshold_bps": DEFAULT_GAP_THRESHOLD_BPS,
                            "severity": severity,
                        }
                    )
        if new_alerts:
            with get_db() as db:
                for alert in new_alerts:
                    db.execute(
                        """
                        INSERT INTO threshold_alerts
                            (account_id, alert_date, gap_bps, threshold_bps, severity, acknowledged)
                        VALUES (?, ?, ?, ?, ?, 0)
                        """,
                        (
                            alert["account_id"],
                            alert["alert_date"],
                            alert["gap_bps"],
                            alert["threshold_bps"],
                            alert["severity"],
                        ),
                    )
                db.commit()
            # Refresh alert counts after inserting
            with get_db() as db:
                alert_counts = db.execute(
                    "SELECT account_id, acknowledged, COUNT(*) as cnt FROM threshold_alerts GROUP BY account_id, acknowledged"
                ).fetchall()
            unack_count = sum(a["cnt"] for a in alert_counts if not a["acknowledged"])
            total_alerts = sum(a["cnt"] for a in alert_counts)

    return PortfolioStats(
        total_accounts=len(accounts),
        total_balance=round(total_balance, 2),
        total_disputes=total_disputes,
        open_disputes=open_count,
        threshold_alerts=total_alerts,
        unacknowledged_alerts=unack_count,
        avg_gap_bps=round(avg_gap, 4),
        max_gap_bps=round(max_gap, 4),
        annualized_yield=round(annualized_yield, 2),
        projected_30d_yield=round(total_balance * (weighted_rate / 365) * 30, 2),
    )


# ─── Regulatory Reporting ───────────────────────────────────────────────────


@app.get("/regulatory/1099-int/{account_id}", response_model=RegulatoryReport)
def report_1099_int(account_id: int, tax_year: int = Query(default=2025)):
    if not (2000 <= tax_year <= 2100):
        raise HTTPException(400, "tax_year must be between 2000 and 2100")
    """Generate mock 1099-INT for a partner account."""
    with get_db() as db:
        acct = db.execute(
            "SELECT * FROM accounts WHERE id = ?", (account_id,)
        ).fetchone()
    if not acct:
        raise HTTPException(404, f"Account {account_id} not found")
    acct = dict(acct)
    # Use yield_events to compute actual yield paid
    with get_db() as db:
        rows = db.execute(
            """
            SELECT SUM(daily_yield) as total_yield
              FROM yield_events
             WHERE account_id = ?
               AND event_date LIKE ?
            """,
            (account_id, f"{tax_year}%"),
        ).fetchone()
    total_yield = float(rows["total_yield"]) if rows and rows["total_yield"] else 0.0
    return RegulatoryReport(
        account_id=account_id,
        partner_name=acct["partner_name"],
        report_type="1099-INT",
        tax_year=tax_year,
        total_yield=round(total_yield, 2),
        account_balance=acct["balance"],
        yield_rate=acct["yield_rate"],
        generated_at=date.today().isoformat(),
    )


@app.get("/regulatory/unclaimed-property/{account_id}", response_model=RegulatoryReport)
def report_unclaimed_property(account_id: int, tax_year: int = Query(default=2025)):
    if not (2000 <= tax_year <= 2100):
        raise HTTPException(400, "tax_year must be between 2000 and 2100")
    """
    Generate mock unclaimed property notice.
    Triggered when account has unclaimed yield (e.g., closed account with residual balance).
    """
    with get_db() as db:
        acct = db.execute(
            "SELECT * FROM accounts WHERE id = ?", (account_id,)
        ).fetchone()
    if not acct:
        raise HTTPException(404, f"Account {account_id} not found")
    acct = dict(acct)
    # Mock: no unclaimed property unless balance is zero and disputes exist
    unclaimed = 0.0
    if acct["balance"] == 0:
        with get_db() as db:
            rows = db.execute(
                "SELECT SUM(gap_dollar_amount) as total FROM recon_disputes WHERE account_id = ? AND status = 'resolved'",
                (account_id,),
            ).fetchone()
            unclaimed = float(rows["total"]) if rows and rows["total"] else 0.0
    return RegulatoryReport(
        account_id=account_id,
        partner_name=acct["partner_name"],
        report_type="Unclaimed Property Notice",
        tax_year=tax_year,
        total_yield=round(unclaimed, 2),
        account_balance=acct["balance"],
        yield_rate=acct["yield_rate"],
        generated_at=date.today().isoformat(),
    )
