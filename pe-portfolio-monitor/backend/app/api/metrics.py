"""Metrics API: portfolio-wide heatmap endpoint."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Alert, Company, Metric, Period, User
from app.dependencies import get_current_user
from app.domain.entities import (
    HeatmapCell,
    HeatmapResponse,
    Metric as MetricSchema,
)

router = APIRouter()

# Metric keys included in the heatmap
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
    """
    Compute traffic-light status string.

    Returns None if insufficient data.
    Returns 'red' if there's an open alert for this metric.
    Otherwise computes % change vs prior period:
      green — within 5%
      amber — 5–15%
      red  — >15%
    """
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


# ── GET /heatmap ─────────────────────────────────────────────────────────────────


@router.get("/heatmap", response_model=HeatmapResponse)
async def get_heatmap(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Build the portfolio-wide KPI heatmap for the current user's firm.

    For each company, fetches the most recent period's metrics and assigns a
    traffic-light status:
      green  — value within 5% of the prior period
      amber  — value changed 5–15% vs prior period
      red    — value changed >15% vs prior period, OR an open alert exists

    Returns a flat list of HeatmapCell objects keyed by (company_id, metric_key).
    """
    companies_result = await session.execute(
        select(Company).where(
            Company.firm_id == user.firm_id,
            Company.status != "offboarded",
        )
    )
    companies = list(companies_result.scalars().all())

    if not companies:
        return HeatmapResponse(
            period_label="",
            cells=[],
            generated_at=datetime.now(timezone.utc),
        )

    open_alerts: dict[uuid.UUID, set[str]] = {}
    if companies:
        alerts_result = await session.execute(
            select(Alert).where(
                Alert.company_id.in_([c.id for c in companies]),
                Alert.status == "open",
            )
        )
        for alert in alerts_result.scalars().all():
            open_alerts.setdefault(alert.company_id, set()).add(alert.metric_key)

    cells: list[HeatmapCell] = []
    period_label = ""

    for company in companies:
        latest_period_result = await session.execute(
            select(Period)
            .where(Period.company_id == company.id)
            .order_by(Period.end_date.desc())
            .limit(1)
        )
        latest_period = latest_period_result.scalar_one_or_none()
        if latest_period is None:
            continue

        period_label = latest_period.calendar_period_label

        latest_metrics_result = await session.execute(
            select(Metric).where(
                Metric.company_id == company.id,
                Metric.period_id == latest_period.id,
                Metric.superseded_by.is_(None),
            )
        )
        latest_metrics: dict[str, Metric] = {
            m.metric_key: m for m in latest_metrics_result.scalars().all()
        }

        prior_period_result = await session.execute(
            select(Period)
            .where(
                Period.company_id == company.id,
                Period.end_date < latest_period.end_date,
            )
            .order_by(Period.end_date.desc())
            .limit(1)
        )
        prior_period = prior_period_result.scalar_one_or_none()
        prior_metrics: dict[str, Metric] = {}
        if prior_period:
            prior_result = await session.execute(
                select(Metric).where(
                    Metric.company_id == company.id,
                    Metric.period_id == prior_period.id,
                    Metric.superseded_by.is_(None),
                )
            )
            prior_metrics = {m.metric_key: m for m in prior_result.scalars().all()}

        company_open_keys = open_alerts.get(company.id, set())

        for metric_key in HEATMAP_METRIC_KEYS:
            latest_metric = latest_metrics.get(metric_key)
            prior_metric = prior_metrics.get(metric_key)
            has_open_alert = metric_key in company_open_keys
            status_str = _compute_heatmap_status(latest_metric, prior_metric, has_open_alert)

            cells.append(
                HeatmapCell(
                    company_id=company.id,
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
        period_label=period_label,
        cells=cells,
        generated_at=datetime.now(timezone.utc),
    )
