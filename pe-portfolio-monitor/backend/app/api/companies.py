"""Companies API: CRUD + CSV upload."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Alert, Company, Metric, Period, User
from app.dependencies import get_current_user, require_role
from app.domain.entities import (
    Company as CompanySchema,
    CompanyCreate,
    CompanyUpdate,
    CSVUploadResponse,
    HeatmapCell,
    HeatmapResponse,
    MappingConfidence,
    Metric as MetricSchema,
    MetricHistory,
)
from app.integrations.csv_processor import process_csv

router = APIRouter()


def _company_to_schema(c: Company) -> CompanySchema:
    """Convert ORM model to Pydantic schema, stripping OAuth tokens."""
    return CompanySchema(
        id=c.id,
        firm_id=c.firm_id,
        legal_name=c.legal_name,
        display_name=c.display_name,
        classification=c.classification,
        base_currency=c.base_currency,
        fiscal_year_end_month=c.fiscal_year_end_month,
        reporting_timezone=c.reporting_timezone,
        erp_vendor=c.erp_vendor,
        erp_instance_id=c.erp_instance_id,
        status=c.status,
        onboarded_at=c.onboarded_at,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


# ── GET /companies ─────────────────────────────────────────────────────────────


@router.get("", response_model=list[CompanySchema])
async def list_companies(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """
    List all companies belonging to the current user's firm.

    Results are ordered by display_name.
    """
    result = await session.execute(
        select(Company).where(Company.firm_id == user.firm_id).order_by(Company.display_name)
    )
    companies = result.scalars().all()
    return [_company_to_schema(c) for c in companies]


# ── POST /companies ─────────────────────────────────────────────────────────────


@router.post("", response_model=CompanySchema, status_code=status.HTTP_201_CREATED)
async def create_company(
    data: CompanyCreate,
    _: User = Depends(require_role(["pe_admin", "pe_ops"])),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Create a new company under the current user's firm.

    The firm's tier determines how many companies can be created.
    """
    company = Company(
        id=uuid.uuid4(),
        firm_id=user.firm_id,
        legal_name=data.legal_name,
        display_name=data.display_name,
        classification=data.classification,
        base_currency=data.base_currency,
        fiscal_year_end_month=data.fiscal_year_end_month,
        reporting_timezone=data.reporting_timezone,
        erp_vendor=data.erp_vendor,
        erp_instance_id=data.erp_instance_id,
        status="onboarding",
    )
    session.add(company)
    await session.flush()
    await session.commit()
    await session.refresh(company)
    return _company_to_schema(company)


# ── GET /companies/{id} ─────────────────────────────────────────────────────────


@router.get("/{company_id}", response_model=CompanySchema)
async def get_company(
    company_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a single company by ID, scoped to the current user's firm."""
    result = await session.execute(
        select(Company).where(Company.id == company_id, Company.firm_id == user.firm_id)
    )
    company: Company | None = result.scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return _company_to_schema(company)


# ── PATCH /companies/{id} ───────────────────────────────────────────────────────


@router.patch("/{company_id}", response_model=CompanySchema)
async def update_company(
    company_id: uuid.UUID,
    data: CompanyUpdate = Body(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Update one or more fields on a company."""
    result = await session.execute(
        select(Company).where(Company.id == company_id, Company.firm_id == user.firm_id)
    )
    company: Company | None = result.scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(company, field, value)

    company.updated_at = datetime.now(timezone.utc)
    await session.flush()
    await session.refresh(company)
    return _company_to_schema(company)


# ── DELETE /companies/{id} ─────────────────────────────────────────────────────


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: uuid.UUID,
    _: User = Depends(require_role(["pe_admin"])),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Soft-offboard a company: sets status to 'offboarded'.

    The company's historical data is preserved.
    """
    result = await session.execute(
        select(Company).where(Company.id == company_id, Company.firm_id == user.firm_id)
    )
    company: Company | None = result.scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    company.status = "offboarded"
    company.updated_at = datetime.now(timezone.utc)
    await session.flush()


# ── POST /companies/{id}/upload-csv ─────────────────────────────────────────────


@router.post("/{company_id}/upload-csv", response_model=CSVUploadResponse)
async def upload_csv(
    company_id: uuid.UUID,
    file: UploadFile = File(...),
    period_label: str = Form(...),
    start_date: date = Form(...),
    end_date: date = Form(...),
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Upload a CSV file containing account-level financial data for a period.

    CSV format:
        account_id, account_name, amount, [currency]

    The file is processed by csv_processor.process_csv() which:
    1. Upserts raw staging rows
    2. Upserts the Period record
    3. Computes canonical KPIs and writes Metric rows

    Returns a CSVUploadResponse with processing statistics.
    """
    # Verify company belongs to the user's firm
    result = await session.execute(
        select(Company).where(Company.id == company_id, Company.firm_id == user.firm_id)
    )
    company: Company | None = result.scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    if company.status.value == "offboarded":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upload to an offboarded company",
        )

    # Read and validate CSV content
    MAX_CSV_SIZE = 10 * 1024 * 1024  # 10 MB
    content = await file.read()
    if len(content) > MAX_CSV_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="CSV file exceeds 10 MB limit",
        )
    try:
        csv_text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file must be UTF-8 encoded",
        )

    if not csv_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file is empty",
        )

    response = await process_csv(
        session=session,
        company_id=company_id,
        csv_content=csv_text,
        period_label=period_label,
        start_date=start_date,
        end_date=end_date,
    )

    return response


# ── Metric helpers (used by endpoints below) ───────────────────────────────────

HEATMAP_METRIC_KEYS = (
    "revenue_net",
    "gross_profit",
    "ebitda",
    "ebitda_margin_pct",
    "dso",
    "working_capital",
    "cash_balance",
    "net_debt",
    "operating_cash_flow",
)


def _metric_to_schema(m: Metric) -> MetricSchema:
    """Convert ORM Metric to Pydantic schema."""
    return MetricSchema(
        id=m.id,
        company_id=m.company_id,
        metric_key=m.metric_key,
        period_id=m.period_id,
        value=float(m.value),
        currency=m.currency,
        computation_version=m.computation_version,
        confidence=m.confidence,
        confidence_reason=m.confidence_reason,
        source_lineage=m.source_lineage,
        computed_at=m.computed_at,
        superseded_by=m.superseded_by,
    )


def _compute_heatmap_status(
    latest: Metric | None,
    prior: Metric | None,
    has_open_alert: bool,
) -> str | None:
    """Compute traffic-light status: green (<5%), amber (5-15%), red (>15% or alert open)."""
    if has_open_alert:
        return "red"
    if latest is None:
        return None
    if prior is None:
        return None
    prior_value = float(prior.value)
    latest_value = float(latest.value)
    if prior_value == 0:
        return "red" if latest_value != 0 else None
    pct_change = abs((latest_value - prior_value) / prior_value)
    if pct_change <= 0.05:
        return "green"
    if pct_change <= 0.15:
        return "amber"
    return "red"


# ── GET /companies/{id}/metrics ──────────────────────────────────────────────────


@router.get("/{company_id}/metrics", response_model=list[MetricSchema])
async def list_company_metrics(
    company_id: uuid.UUID,
    period_id: uuid.UUID | None = Query(None, description="Filter by period ID"),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    List all metrics for a company, optionally filtered to a specific period.

    Metrics are returned in metric_key alphabetical order.
    """
    company_result = await session.execute(
        select(Company).where(Company.id == company_id, Company.firm_id == user.firm_id)
    )
    if company_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    query = (
        select(Metric)
        .where(Metric.company_id == company_id, Metric.superseded_by.is_(None))
        .order_by(Metric.metric_key)
    )
    if period_id is not None:
        query = query.where(Metric.period_id == period_id)

    result = await session.execute(query)
    return [_metric_to_schema(m) for m in result.scalars().all()]


# ── GET /companies/{id}/metrics/history ─────────────────────────────────────────


@router.get("/{company_id}/metrics/history", response_model=MetricHistory)
async def get_metric_history(
    company_id: uuid.UUID,
    metric_key: str = Query(..., description="e.g. ebitda, revenue_net"),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Return the 13-month time-series for a specific metric on a company.

    Each entry contains period_id, calendar_label, value, and a computed
    'status' (higher/lower/neutral vs the prior period).
    """
    company_result = await session.execute(
        select(Company).where(Company.id == company_id, Company.firm_id == user.firm_id)
    )
    company: Company | None = company_result.scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    periods_result = await session.execute(
        select(Period)
        .where(Period.company_id == company_id)
        .order_by(Period.end_date.desc())
        .limit(13)
    )
    periods = list(periods_result.scalars().all())
    if not periods:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No period data found for this company",
        )

    period_ids = [p.id for p in periods]
    metrics_result = await session.execute(
        select(Metric).where(
            Metric.company_id == company_id,
            Metric.metric_key == metric_key,
            Metric.period_id.in_(period_ids),
            Metric.superseded_by.is_(None),
        )
    )
    metrics_by_period: dict[uuid.UUID, Metric] = {
        m.period_id: m for m in metrics_result.scalars().all()
    }

    sparkline_periods = []
    prev_value: float | None = None
    for p in reversed(periods):
        metric = metrics_by_period.get(p.id)
        value = float(metric.value) if metric else None
        if prev_value is not None and value is not None:
            delta = value - prev_value
            status_str = "higher" if delta > 0.01 else "lower" if delta < -0.01 else "neutral"
        else:
            status_str = "neutral"
        sparkline_periods.append(
            {
                "period_id": str(p.id),
                "calendar_label": p.calendar_period_label,
                "value": value,
                "status": status_str,
            }
        )
        prev_value = value

    return MetricHistory(
        company_id=company_id,
        display_name=company.display_name,
        metric_key=metric_key,
        periods=sparkline_periods,
    )


# ── GET /companies/{id}/heatmap-cell ────────────────────────────────────────────


@router.get("/{company_id}/heatmap", response_model=HeatmapResponse)
async def get_company_heatmap(
    company_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Build a single-company heatmap (alias for the heatmap endpoint filtered to one company).

    Returns the same HeatmapCell structure scoped to one company.
    """
    # Verify company belongs to the user's firm
    company_result = await session.execute(
        select(Company).where(Company.id == company_id, Company.firm_id == user.firm_id)
    )
    company: Company | None = company_result.scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    latest_period_result = await session.execute(
        select(Period)
        .where(Period.company_id == company_id)
        .order_by(Period.end_date.desc())
        .limit(1)
    )
    latest_period = latest_period_result.scalar_one_or_none()
    if latest_period is None:
        return HeatmapResponse(
            period_label="",
            cells=[],
            generated_at=datetime.now(timezone.utc),
        )

    # Open alerts for this company
    alerts_result = await session.execute(
        select(Alert).where(Alert.company_id == company_id, Alert.status == "open")
    )
    open_alerts = {a.metric_key for a in alerts_result.scalars().all()}

    metrics_result = await session.execute(
        select(Metric).where(
            Metric.company_id == company_id,
            Metric.period_id == latest_period.id,
            Metric.superseded_by.is_(None),
        )
    )
    latest_metrics: dict[str, Metric] = {m.metric_key: m for m in metrics_result.scalars().all()}

    prior_period_result = await session.execute(
        select(Period)
        .where(Period.company_id == company_id, Period.end_date < latest_period.end_date)
        .order_by(Period.end_date.desc())
        .limit(1)
    )
    prior_period = prior_period_result.scalar_one_or_none()
    prior_metrics: dict[str, Metric] = {}
    if prior_period:
        prior_result = await session.execute(
            select(Metric).where(
                Metric.company_id == company_id,
                Metric.period_id == prior_period.id,
                Metric.superseded_by.is_(None),
            )
        )
        prior_metrics = {m.metric_key: m for m in prior_result.scalars().all()}

    cells = []
    for metric_key in HEATMAP_METRIC_KEYS:
        latest_metric = latest_metrics.get(metric_key)
        prior_metric = prior_metrics.get(metric_key)
        has_open_alert = metric_key in open_alerts
        status_str = _compute_heatmap_status(latest_metric, prior_metric, has_open_alert)
        cells.append(
            HeatmapCell(
                company_id=company_id,
                display_name=company.display_name,
                metric_key=metric_key,
                value=float(latest_metric.value) if latest_metric else None,
                currency=company.base_currency,
                status=status_str,
                confidence=latest_metric.confidence if latest_metric else None,
                period_label=latest_period.calendar_period_label,
            )
        )

    return HeatmapResponse(
        period_label=latest_period.calendar_period_label,
        cells=cells,
        generated_at=datetime.now(timezone.utc),
    )
