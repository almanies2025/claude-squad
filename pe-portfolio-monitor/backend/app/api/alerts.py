"""Alerts API: list, get, update status, and trigger evaluation."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Alert, AlertRule, Company, User
from app.dependencies import get_current_user, require_role
from app.domain.alert_engine import AlertEngine
from app.domain.entities import (
    Alert as AlertSchema,
    AlertStatus,
    AlertUpdate,
)

router = APIRouter()


def _alert_to_schema(a: Alert) -> AlertSchema:
    """Convert ORM Alert to Pydantic schema."""
    return AlertSchema(
        id=a.id,
        company_id=a.company_id,
        metric_key=a.metric_key,
        period_id=a.period_id,
        rule_id=a.rule_id,
        severity=a.severity,
        triggered_at=a.triggered_at,
        metric_value=float(a.metric_value),
        threshold_value=float(a.threshold_value),
        rule_snapshot=a.rule_snapshot,
        context=a.context,
        explanation=a.explanation,
        status=a.status,
        status_changed_at=a.status_changed_at,
        status_changed_by=a.status_changed_by,
        resolution_note=a.resolution_note,
    )


# ── GET /alerts ─────────────────────────────────────────────────────────────────


@router.get("", response_model=list[AlertSchema])
async def list_alerts(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    company_id: uuid.UUID | None = Query(None, description="Filter by company"),
    alert_status: str | None = Query(
        None,
        description="Filter by status: open, acknowledged, resolved, false_positive, suppressed",
    ),
):
    """
    List alerts for the current firm, optionally filtered by company or status.

    Results are ordered by triggered_at descending (most recent first).
    """
    conditions = [Alert.company_id.in_(select(Company.id).where(Company.firm_id == user.firm_id))]

    if company_id is not None:
        # Validate company belongs to firm
        company_check = await session.execute(
            select(Company.id).where(
                Company.id == company_id,
                Company.firm_id == user.firm_id,
            )
        )
        if company_check.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        conditions.append(Alert.company_id == company_id)

    if alert_status is not None:
        try:
            _ = AlertStatus(alert_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {[s.value for s in AlertStatus]}",
            )
        conditions.append(Alert.status == alert_status)

    result = await session.execute(
        select(Alert).where(and_(*conditions)).order_by(Alert.triggered_at.desc())
    )
    alerts = result.scalars().all()
    return [_alert_to_schema(a) for a in alerts]


# ── GET /alerts/{id} ───────────────────────────────────────────────────────────


@router.get("/{alert_id}", response_model=AlertSchema)
async def get_alert(
    alert_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a single alert by ID, scoped to the current user's firm."""
    result = await session.execute(
        select(Alert)
        .join(Company, Alert.company_id == Company.id)
        .where(Alert.id == alert_id, Company.firm_id == user.firm_id)
    )
    alert: Alert | None = result.scalar_one_or_none()
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return _alert_to_schema(alert)


# ── PATCH /alerts/{id} ─────────────────────────────────────────────────────────


_VALID_TRANSITIONS: dict[AlertStatus, set[AlertStatus]] = {
    AlertStatus.OPEN: {AlertStatus.ACKNOWLEDGED},
    AlertStatus.ACKNOWLEDGED: {
        AlertStatus.RESOLVED,
        AlertStatus.FALSE_POSITIVE,
        AlertStatus.SUPPRESSED,
    },
    AlertStatus.RESOLVED: set(),
    AlertStatus.FALSE_POSITIVE: set(),
    AlertStatus.SUPPRESSED: set(),
}


@router.patch("/{alert_id}", response_model=AlertSchema)
async def update_alert(
    alert_id: uuid.UUID,
    data: AlertUpdate = Body(...),
    _: User = Depends(require_role(["pe_admin", "pe_ops", "pe_operator", "pe_partner"])),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Update an alert's status and optionally add a resolution note.

    Valid status transitions:
      open → acknowledged
      acknowledged → resolved / false_positive / suppressed
      resolved / false_positive / suppressed — terminal, no further transitions
    """
    result = await session.execute(
        select(Alert)
        .join(Company, Alert.company_id == Company.id)
        .where(Alert.id == alert_id, Company.firm_id == user.firm_id)
    )
    alert: Alert | None = result.scalar_one_or_none()
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    current_status = AlertStatus(alert.status)
    new_status = data.status

    if new_status not in _VALID_TRANSITIONS.get(current_status, set()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transition: {current_status.value} → {new_status.value}",
        )

    alert.status = new_status.value
    alert.status_changed_at = datetime.now(timezone.utc)
    alert.status_changed_by = user.id
    if data.resolution_note:
        alert.resolution_note = data.resolution_note

    await session.flush()
    await session.refresh(alert)
    return _alert_to_schema(alert)


# ── POST /alerts/evaluate ───────────────────────────────────────────────────────


class EvaluateRequest(BaseModel):
    """Body for POST /alerts/evaluate. company_id is optional."""

    company_id: uuid.UUID | None = None


@router.post("/evaluate", response_model=list[AlertSchema])
async def evaluate_alerts(
    _: User = Depends(require_role(["pe_admin", "pe_ops", "pe_operator", "pe_partner"])),
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    body: EvaluateRequest | None = None,
):
    """
    Trigger the alert engine for one company or the entire firm.

    If body.company_id is provided, evaluates that company only.
    If body is absent or company_id is null, evaluates all companies in the firm.

    Returns all alerts that fired (new or worsened) or were auto-resolved.
    """
    engine = AlertEngine(session)

    if body is not None and body.company_id is not None:
        # Validate company belongs to firm
        company_result = await session.execute(
            select(Company).where(
                Company.id == body.company_id,
                Company.firm_id == user.firm_id,
            )
        )
        if company_result.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        fired = await engine.evaluate_company(body.company_id)
    else:
        fired = await engine.evaluate_firm(user.firm_id)

    return [_alert_to_schema(a) for a in fired]
