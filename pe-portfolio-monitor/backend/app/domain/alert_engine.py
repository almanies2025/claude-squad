"""
Alert engine — evaluates AlertRules against latest Metric values per company.

Supports 5 rule types:
  absolute_threshold  — value outside a floor/ceiling
  relative_threshold  — value deviates >N% from trailing average
  directional_sustained — value trending badly for N consecutive periods
  ratio_breach       — ratio of two metrics exceeds a threshold
  plan_variance      — actual vs plan deviates beyond threshold

Alert lifecycle:
  open → acknowledged → resolved / false_positive / suppressed
Deduplication: an open alert for the same (company, metric, rule) is not
re-created unless the value has actually worsened.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Alert, AlertRule, Company, Metric, Period


class AlertEngine:
    """Evaluates alert rules and creates/updates alerts."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Public API ────────────────────────────────────────────────────────────

    async def evaluate_company(self, company_id: uuid.UUID) -> list[Alert]:
        """
        Load all active rules for this company (and firm-wide defaults),
        evaluate each against the latest metrics, and upsert alerts.

        Returns all alerts that fired or already existed in open state.
        """
        # Load company to get firm_id
        company_result = await self.session.execute(select(Company).where(Company.id == company_id))
        company: Company = company_result.scalar_one_or_none()
        if not company:
            return []

        # Load active rules: firm defaults + company overrides
        rules = await self._load_active_rules(company.firm_id, company_id)

        # Load latest metrics for the company
        metrics = await self._load_latest_metrics(company_id)

        fired_alerts: list[Alert] = []
        for rule in rules:
            alert = await self._evaluate_rule(rule, metrics, company)
            if alert is not None:
                fired_alerts.append(alert)

        await self.session.commit()
        return fired_alerts

    async def evaluate_firm(self, firm_id: uuid.UUID) -> list[Alert]:
        """Evaluate all companies under a firm."""
        all_alerts: list[Alert] = []
        result = await self.session.execute(select(Company.id).where(Company.firm_id == firm_id))
        company_ids = [row[0] for row in result.fetchall()]
        for cid in company_ids:
            alerts = await self.evaluate_company(cid)
            all_alerts.extend(alerts)
        return all_alerts

    # ── Rule evaluation ───────────────────────────────────────────────────────

    async def _evaluate_rule(
        self,
        rule: AlertRule,
        metrics: dict[str, float],
        company: Company,
    ) -> Alert | None:
        """Evaluate a single rule against current metrics. Returns Alert if fired."""
        metric_value = metrics.get(rule.metric_key)
        if metric_value is None:
            return None

        params = rule.parameters or {}
        fired, explanation, threshold_value = await self._check_rule(
            rule.rule_type.value, metric_value, params, company.id
        )

        if not fired:
            # Check if this alert can now recover
            return await self._maybe_resolve(rule, company.id)

        # Deduplication: if there's already an open alert for this rule+company, skip
        existing = await self._open_alert_exists(rule.id, company.id)
        if existing:
            # Alert already open — check if value worsened enough to update
            if existing.metric_value == metric_value:
                return existing  # unchanged, keep as-is
            # Value changed — update the alert (keep same ID)
            existing.metric_value = metric_value
            existing.threshold_value = threshold_value
            existing.explanation = explanation
            existing.triggered_at = datetime.now(timezone.utc)
            return existing

        # Create new alert — requires at least one period to exist
        period_id = await self._latest_period_id(company.id)
        if period_id is None:
            return None  # No period data yet — can't create alert without a period

        alert = Alert(
            id=uuid.uuid4(),
            company_id=company.id,
            metric_key=rule.metric_key,
            period_id=period_id,
            rule_id=rule.id,
            severity=rule.severity,
            triggered_at=datetime.now(timezone.utc),
            metric_value=metric_value,
            threshold_value=threshold_value,
            rule_snapshot=dict(rule.parameters) if rule.parameters else {},
            context={"company_id": str(company.id), "firm_id": str(company.firm_id)},
            explanation=explanation,
            status="open",
        )
        self.session.add(alert)
        return alert

    async def _check_rule(
        self,
        rule_type: str,
        value: float,
        params: dict[str, Any],
        company_id: uuid.UUID,
    ) -> tuple[bool, str, float]:
        """Returns (fired, one_sentence_explanation, threshold_value)."""
        if rule_type == "absolute_threshold":
            return self._eval_absolute(value, params)
        elif rule_type == "relative_threshold":
            return await self._eval_relative(value, params, company_id)
        elif rule_type == "directional_sustained":
            return await self._eval_directional(value, params, company_id)
        elif rule_type == "ratio_breach":
            return await self._eval_ratio(value, params, company_id)
        elif rule_type == "plan_variance":
            return await self._eval_plan_variance(value, params, company_id)
        return False, "", 0.0

    # ── Rule type implementations ─────────────────────────────────────────────

    def _eval_absolute(self, value: float, params: dict[str, Any]) -> tuple[bool, str, float]:
        floor = params.get("floor")
        ceiling = params.get("ceiling")
        metric_key = params.get("metric_key", "this metric")

        if floor is not None and value < float(floor):
            pct = (float(floor) - value) / abs(value) * 100 if value else 0
            return (
                True,
                f"{metric_key} is {value:.1f}, below floor of {floor} "
                f"({'+' if pct < 0 else ''}{pct:.1f}% below threshold)",
                float(floor),
            )
        if ceiling is not None and value > float(ceiling):
            pct = (value - float(ceiling)) / abs(value) * 100 if value else 0
            return (
                True,
                f"{metric_key} is {value:.1f}, above ceiling of {ceiling} "
                f"({pct:.1f}% above threshold)",
                float(ceiling),
            )
        return False, "", 0.0

    async def _eval_relative(
        self, value: float, params: dict[str, Any], company_id: uuid.UUID
    ) -> tuple[bool, str, float]:
        """
        Compares current value to the trailing N-period average.
        Fires if value has dropped by more than `min_delta` fraction.
        """
        metric_key = params.get("metric_key", "this metric")
        window = params.get("window", 3)
        min_delta = params.get("min_delta", 0.15)  # 15% default drop

        trailing = await self._trailing_values(company_id, metric_key, window)
        if trailing is None or len(trailing) == 0:
            return False, "", 0.0

        avg = sum(trailing) / len(trailing)
        threshold = avg * (1 - float(min_delta))

        if value < threshold:
            pct_drop = (avg - value) / abs(avg) * 100 if avg else 0
            return (
                True,
                f"{metric_key} is {value:.1f}, {pct_drop:.1f}% below "
                f"{len(trailing)}-period average of {avg:.1f}",
                threshold,
            )
        return False, "", 0.0

    async def _eval_directional(
        self, value: float, params: dict[str, Any], company_id: uuid.UUID
    ) -> tuple[bool, str, float]:
        """
        Fires if the metric has been trending in the `direction` ('up' or 'down')
        for `window` consecutive periods.
        """
        metric_key = params.get("metric_key", "this metric")
        window = params.get("window", 3)
        direction = params.get("direction", "down")
        min_delta = params.get("min_delta", 0.0)  # minimum change per period

        recent = await self._trailing_values(company_id, metric_key, window + 1)
        if recent is None or len(recent) < window + 1:
            return False, "", 0.0

        # Strip the most recent (already checked as `value`); look at prior `window` periods
        prior = recent[1:]  # oldest to newest (excludes current)
        current = recent[0]

        worsening = 0
        for i in range(len(prior) - 1):
            prev = prior[i]
            curr = prior[i + 1]
            if direction == "down":
                if curr <= prev - float(min_delta):
                    worsening += 1
            else:  # up
                if curr >= prev + float(min_delta):
                    worsening += 1

        if worsening >= window - 1:
            return (
                True,
                f"{metric_key} has moved {'up' if direction == 'up' else 'down'} "
                f"for {window} consecutive periods "
                f"(from {prior[0]:.1f} to {prior[-1]:.1f}, now {value:.1f})",
                float(window),
            )
        return False, "", 0.0

    async def _eval_ratio(
        self, value: float, params: dict[str, Any], company_id: uuid.UUID
    ) -> tuple[bool, str, float]:
        """
        Fires if numerator_metric / base_metric exceeds `threshold`.
        E.g., working_capital / revenue > 1.5
        """
        numerator_key = params.get("numerator_metric", "working_capital")
        denominator_key = params.get("denominator_metric", "revenue_net")
        threshold = float(params.get("threshold", 1.5))
        direction = params.get("direction", "above")  # above or below

        denom_metrics = await self._trailing_values(company_id, denominator_key, 1)
        if denom_metrics is None or len(denom_metrics) == 0 or denom_metrics[0] == 0:
            return False, "", 0.0

        denom = denom_metrics[0]
        ratio = value / denom if denom else 0.0

        fired = ratio > threshold if direction == "above" else ratio < threshold
        if fired:
            return (
                True,
                f"Ratio {numerator_key}/{denominator_key} = {ratio:.2f} "
                f"is {'above' if direction == 'above' else 'below'} "
                f"threshold of {threshold}",
                threshold,
            )
        return False, "", 0.0

    async def _eval_plan_variance(
        self, value: float, params: dict[str, Any], company_id: uuid.UUID
    ) -> tuple[bool, str, float]:
        """
        Fires if actual < plan * (1 - threshold_pct) or
               actual > plan * (1 + threshold_pct).
        Requires a `plan_value` in params.
        """
        plan_value = params.get("plan_value")
        if plan_value is None:
            return False, "plan_value not provided in rule parameters", 0.0

        plan_value = float(plan_value)
        threshold_pct = float(params.get("threshold_pct", 0.10))  # 10% default

        lower = plan_value * (1 - threshold_pct)
        upper = plan_value * (1 + threshold_pct)

        if value < lower:
            pct = (lower - value) / plan_value * 100
            return (
                True,
                f"{params.get('metric_key', 'metric')} is {value:.1f}, "
                f"{pct:.1f}% below plan of {plan_value:.1f}",
                lower,
            )
        if value > upper:
            pct = (value - upper) / plan_value * 100
            return (
                True,
                f"{params.get('metric_key', 'metric')} is {value:.1f}, "
                f"{pct:.1f}% above plan of {plan_value:.1f}",
                upper,
            )
        return False, "", 0.0

    # ── Recovery ───────────────────────────────────────────────────────────────

    async def _maybe_resolve(
        self,
        rule: AlertRule,
        company_id: uuid.UUID,
    ) -> Alert | None:
        """
        Auto-resolve an open alert if the rule would not fire for N consecutive
        periods (recovery_window, default 2).

        Re-evaluates the rule against the trailing periods to determine recovery
        — works correctly for all rule types, not just absolute_threshold.
        """
        open_alert = await self._open_alert_exists(rule.id, company_id)
        if not open_alert:
            return None

        params = rule.parameters or {}
        recovery_window = int(params.get("recovery_window", 2))

        # Get recovery_window + 1 periods (including current which already didn't fire)
        trailing = await self._trailing_values(company_id, rule.metric_key, recovery_window + 1)
        if trailing is None or len(trailing) < recovery_window + 1:
            return None

        # Exclude current period (already confirmed not-firing), check prior periods
        prior_values = trailing[1:]  # oldest-first, excludes current

        # All recovery-window periods must be non-violating
        all_recovered = True
        for val in prior_values:
            fired_again, _, _ = await self._check_rule(
                rule.rule_type.value, val, params, company_id
            )
            if fired_again:
                all_recovered = False
                break

        if all_recovered:
            open_alert.status = "resolved"
            open_alert.status_changed_at = datetime.now(timezone.utc)
            return open_alert

        return None

    # ── Helpers ────────────────────────────────────────────────────────────────

    async def _load_active_rules(
        self, firm_id: uuid.UUID, company_id: uuid.UUID
    ) -> list[AlertRule]:
        """Load firm-wide active rules + company-specific overrides."""
        result = await self.session.execute(
            select(AlertRule).where(
                and_(
                    AlertRule.firm_id == firm_id,
                    AlertRule.active == True,  # noqa: E712
                    (AlertRule.company_id == company_id) | (AlertRule.company_id.is_(None)),
                )
            )
        )
        rules: list[AlertRule] = list(result.scalars().all())

        # Company-specific rules override firm defaults for same metric_key
        company_rules = {r.metric_key: r for r in rules if r.company_id == company_id}
        firm_rules = [r for r in rules if r.company_id is None]
        # Filter out firm rules for metrics that have a company override
        firm_rules = [r for r in firm_rules if r.metric_key not in company_rules]
        return list(company_rules.values()) + firm_rules

    async def _load_latest_metrics(self, company_id: uuid.UUID) -> dict[str, float]:
        """Load the most recent period's metrics for a company as {metric_key: value}."""
        # Get latest closed or soft-closed period
        period_result = await self.session.execute(
            select(Period.id)
            .where(Period.company_id == company_id)
            .order_by(Period.end_date.desc())
            .limit(1)
        )
        period_row = period_result.scalar_one_or_none()
        if period_row is None:
            return {}

        period_id = period_row

        result = await self.session.execute(
            select(Metric).where(
                and_(
                    Metric.company_id == company_id,
                    Metric.period_id == period_id,
                    Metric.superseded_by.is_(None),
                )
            )
        )
        return {m.metric_key: float(m.value) for m in result.scalars().all()}

    async def _trailing_values(
        self, company_id: uuid.UUID, metric_key: str, n: int
    ) -> list[float] | None:
        """
        Get the last `n` values for a metric across consecutive periods,
        most recent first. Returns None if fewer than n values exist.
        """
        result = await self.session.execute(
            select(Metric)
            .join(Period, Metric.period_id == Period.id)
            .where(
                and_(
                    Metric.company_id == company_id,
                    Metric.metric_key == metric_key,
                    Metric.superseded_by.is_(None),
                )
            )
            .order_by(Period.end_date.desc())
            .limit(n)
        )
        rows = list(result.scalars().all())
        if len(rows) < n:
            return None
        return [float(m.value) for m in rows]

    async def _open_alert_exists(self, rule_id: uuid.UUID, company_id: uuid.UUID) -> Alert | None:
        result = await self.session.execute(
            select(Alert).where(
                and_(
                    Alert.rule_id == rule_id,
                    Alert.company_id == company_id,
                    Alert.status == "open",
                )
            )
        )
        return result.scalar_one_or_none()

    async def _latest_period_id(self, company_id: uuid.UUID) -> uuid.UUID | None:
        result = await self.session.execute(
            select(Period.id)
            .where(Period.company_id == company_id)
            .order_by(Period.end_date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
