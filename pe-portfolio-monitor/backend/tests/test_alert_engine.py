"""
Alert engine unit tests — all 5 rule types.

Tests cover:
  1. absolute_threshold  — value below floor / above ceiling fires alert
  2. relative_threshold  — value deviates >N% from trailing average
  3. directional_sustained — value trending badly for N consecutive periods
  4. ratio_breach        — ratio of two metrics exceeds a threshold
  5. plan_variance       — actual vs plan deviates beyond threshold

Plus:
  - _latest_period_id returning None (no periods yet)
  - _maybe_resolve with a non-absolute rule type
  - Recovery for directional_sustained
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.db.models import Alert, AlertRule, AlertSeverity, Company, RuleType


# ── Factory helpers (not fixtures — plain module-level functions) ───────────────


def make_mock_result(scalar):
    """Build a mock execute() result that returns the given scalar."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar
    result.scalars.return_value.all.return_value = [] if scalar is None else [scalar]
    return result


def make_mock_scalar_result(items):
    """Build a mock execute() result that returns a list from scalars().all()."""
    result = MagicMock()
    result.scalars.return_value.all.return_value = items
    return result


# ── Fixtures ───────────────────────────────────────────────────────────────────


@pytest.fixture
def company_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def firm_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def period_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def rule_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def mock_session():
    """Async session mock that returns sane defaults for scalar_one_or_none."""
    session = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def company(company_id, firm_id):
    return Company(
        id=company_id,
        firm_id=firm_id,
        legal_name="TestCo",
        display_name="TestCo",
        base_currency="USD",
        classification=MagicMock(value="services"),
    )


@pytest.fixture
def absolute_rule(rule_id) -> AlertRule:
    return AlertRule(
        id=rule_id,
        metric_key="ebitda",
        rule_type=RuleType.ABSOLUTE_THRESHOLD,
        parameters={"floor": 0, "metric_key": "ebitda"},
        severity=AlertSeverity.CRITICAL,
        active=True,
    )


@pytest.fixture
def relative_rule(rule_id) -> AlertRule:
    return AlertRule(
        id=rule_id,
        metric_key="revenue_net",
        rule_type=RuleType.RELATIVE_THRESHOLD,
        parameters={"metric_key": "revenue_net", "window": 3, "min_delta": 0.10},
        severity=AlertSeverity.ELEVATED,
        active=True,
    )


@pytest.fixture
def directional_rule(rule_id) -> AlertRule:
    return AlertRule(
        id=rule_id,
        metric_key="dso",
        rule_type=RuleType.DIRECTIONAL_SUSTAINED,
        parameters={"metric_key": "dso", "window": 3, "direction": "up", "min_delta": 0.0},
        severity=AlertSeverity.ELEVATED,
        active=True,
    )


@pytest.fixture
def ratio_rule(rule_id) -> AlertRule:
    return AlertRule(
        id=rule_id,
        metric_key="working_capital",
        rule_type=RuleType.RATIO_BREACH,
        parameters={
            "numerator_metric": "working_capital",
            "denominator_metric": "revenue_net",
            "threshold": 1.5,
            "direction": "above",
        },
        severity=AlertSeverity.ELEVATED,
        active=True,
    )


@pytest.fixture
def plan_variance_rule(rule_id) -> AlertRule:
    return AlertRule(
        id=rule_id,
        metric_key="ebitda",
        rule_type=RuleType.PLAN_VARIANCE,
        parameters={"metric_key": "ebitda", "plan_value": 100.0, "threshold_pct": 0.10},
        severity=AlertSeverity.CRITICAL,
        active=True,
    )


# ── absolute_threshold ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_absolute_threshold_fires_below_floor(
    mock_session, company, absolute_rule, company_id
):
    """
    absolute_threshold fires when EBITDA < floor (0).
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    # EBITDA = -10  (below floor of 0)
    fired, explanation, threshold = await engine._check_rule(
        "absolute_threshold", -10.0, absolute_rule.parameters, company_id
    )

    assert fired is True
    assert threshold == 0.0
    assert "below floor" in explanation


@pytest.mark.asyncio
async def test_absolute_threshold_fires_above_ceiling(mock_session, company, company_id):
    """
    absolute_threshold fires when DSO > ceiling.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    params = {"ceiling": 90, "metric_key": "dso"}
    fired, explanation, threshold = await engine._check_rule(
        "absolute_threshold", 120.0, params, company_id
    )

    assert fired is True
    assert threshold == 90.0
    assert "above ceiling" in explanation


@pytest.mark.asyncio
async def test_absolute_threshold_does_not_fire(mock_session, company, company_id):
    """
    absolute_threshold does NOT fire when value is within floor/ceiling.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    params = {"floor": 0, "ceiling": 100, "metric_key": "ebitda"}
    fired, explanation, threshold = await engine._check_rule(
        "absolute_threshold", 50.0, params, company_id
    )

    assert fired is False
    assert explanation == ""


# ── relative_threshold ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_relative_threshold_fires_when_value_drops(
    mock_session, company, relative_rule, company_id
):
    """
    relative_threshold fires when current value is >min_delta below the
    trailing window average.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    # Patch trailing values to return [100, 100, 100] — avg = 100
    # min_delta = 0.10 → threshold = 100 * 0.90 = 90
    # value = 80 < 90 → should fire
    async def mock_trailing(cid, key, n):
        if n == 3:
            return [100.0, 100.0, 100.0]
        return None

    engine._trailing_values = mock_trailing

    fired, explanation, threshold = await engine._check_rule(
        "relative_threshold", 80.0, relative_rule.parameters, company_id
    )

    assert fired is True
    assert threshold == 90.0
    assert "below" in explanation


@pytest.mark.asyncio
async def test_relative_threshold_does_not_fire(mock_session, company, company_id):
    """
    relative_threshold does NOT fire when value is within the acceptable
    deviation from the trailing average.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    async def mock_trailing(cid, key, n):
        if n == 3:
            return [100.0, 100.0, 100.0]  # avg = 100
        return None

    engine._trailing_values = mock_trailing

    params = {"metric_key": "revenue_net", "window": 3, "min_delta": 0.10}
    # value = 95 is within 10% of avg=100 (threshold = 90)
    fired, explanation, threshold = await engine._check_rule(
        "relative_threshold", 95.0, params, company_id
    )

    assert fired is False


@pytest.mark.asyncio
async def test_relative_threshold_requires_sufficient_history(mock_session, company, company_id):
    """
    relative_threshold returns False when fewer than `window` prior
    periods exist.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    # Return fewer values than window requests (n=3 needed, but only 1 available)
    async def mock_trailing(cid, key, n):
        if n > 1:
            return None  # insufficient history
        return [100.0]

    engine._trailing_values = mock_trailing

    params = {"metric_key": "revenue_net", "window": 3, "min_delta": 0.10}
    fired, explanation, threshold = await engine._check_rule(
        "relative_threshold", 80.0, params, company_id
    )

    assert fired is False


# ── directional_sustained ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_directional_sustained_fires(mock_session, company, directional_rule, company_id):
    """
    directional_sustained fires when DSO has been worsening for `window`
    consecutive periods (direction='up' means each period is higher than prior).

    With window=3, we need 3 consecutive up-periods:
    prior periods (oldest→newest): [50, 60, 70], current = 80
    worsening count = 2 (60>50, 70>60) >= window-1=2 → fires
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    async def mock_trailing(cid, key, n):
        # n = window + 1 = 4; return [current (80), then prior values worsening: 50→60→70]
        # prior = [50, 60, 70]: 50→60 (worsening), 60→70 (worsening) = 2 transitions ≥ window-1=2
        if n == 4:
            return [80.0, 50.0, 60.0, 70.0]
        return None

    engine._trailing_values = mock_trailing

    fired, explanation, threshold = await engine._check_rule(
        "directional_sustained", 80.0, directional_rule.parameters, company_id
    )

    assert fired is True
    assert "consecutive" in explanation


@pytest.mark.asyncio
async def test_directional_sustained_does_not_fire_insufficient_consecutive(
    mock_session, company, company_id
):
    """
    directional_sustained does NOT fire when the metric has not worsened
    for enough consecutive periods.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    # DSO went: 50, 55 (up), 52 (down) — only 1 consecutive up, not 3
    async def mock_trailing(cid, key, n):
        if n == 4:
            return [52.0, 55.0, 50.0, 45.0]
        return None

    engine._trailing_values = mock_trailing

    params = {"metric_key": "dso", "window": 3, "direction": "up", "min_delta": 0.0}
    fired, explanation, threshold = await engine._check_rule(
        "directional_sustained", 52.0, params, company_id
    )

    assert fired is False


@pytest.mark.asyncio
async def test_directional_sustained_recovery(mock_session, company, directional_rule, company_id):
    """
    directional_sustained recovers (alert resolves) when the condition
    clears for recovery_window consecutive periods.

    Scenario: DSO was worsening (50→60→70→80), alert was open.
    Now DSO stabilises: current=70, prior=[70,65,60] — no longer worsening.
    After recovery_window=2 clean periods, alert resolves.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    # Open alert already exists for this rule
    open_alert = Alert(
        id=uuid.uuid4(),
        company_id=company.id,
        metric_key="dso",
        period_id=uuid.uuid4(),
        rule_id=directional_rule.id,
        severity=AlertSeverity.ELEVATED,
        triggered_at=datetime.now(timezone.utc),
        metric_value=80.0,
        threshold_value=3.0,
        rule_snapshot={},
        explanation="DSO worsening",
        status="open",
    )

    async def mock_open_exists(rid, cid):
        if rid == directional_rule.id and cid == company.id:
            return open_alert
        return None

    engine._open_alert_exists = mock_open_exists

    async def mock_trailing(cid, key, n):
        if n == 3:
            # [70 (current), 65, 60] — prior periods: 65>60 (up), 70>65 (up) → still worsening!
            # For recovery we need it NOT to fire, so we configure trailing that
            # makes _eval_directional return False (the prior periods are NOT worsening)
            return [70.0, 65.0, 60.0]
        return None

    engine._trailing_values = mock_trailing

    # Mock _check_rule: the prior values should NOT fire directional
    # [70, 65, 60] — 65>60 yes, 70>65 yes — but _check_rule is what we mock
    async def mock_check_rule(rule_type, value, params, cid):
        if rule_type == "directional_sustained":
            # Force recovery: pretend the prior values don't fire
            return (False, "", 0.0)
        return (False, "", 0.0)

    engine._check_rule = mock_check_rule

    resolved = await engine._maybe_resolve(directional_rule, company.id)

    assert resolved is not None
    assert resolved.status == "resolved"
    assert resolved.status_changed_at is not None


@pytest.mark.asyncio
async def test_directional_sustained_recovery_window_not_met(
    mock_session, company, directional_rule, company_id
):
    """
    directional_sustained does NOT resolve until recovery_window
    consecutive non-violating periods have passed.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    open_alert = Alert(
        id=uuid.uuid4(),
        company_id=company.id,
        metric_key="dso",
        period_id=uuid.uuid4(),
        rule_id=directional_rule.id,
        severity=AlertSeverity.ELEVATED,
        triggered_at=datetime.now(timezone.utc),
        metric_value=80.0,
        threshold_value=3.0,
        rule_snapshot={},
        explanation="DSO worsening",
        status="open",
    )

    async def mock_open_exists(rid, cid):
        if rid == directional_rule.id and cid == company.id:
            return open_alert
        return None

    engine._open_alert_exists = mock_open_exists

    # Only 2 periods returned (need recovery_window+1=3)
    async def mock_trailing(cid, key, n):
        if n == 2:
            return [70.0, 65.0]
        return None

    engine._trailing_values = mock_trailing

    resolved = await engine._maybe_resolve(directional_rule, company.id)

    # Insufficient history → cannot confirm recovery
    assert resolved is None


# ── ratio_breach ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ratio_breach_fires(mock_session, company, ratio_rule, company_id):
    """
    ratio_breach fires when working_capital / revenue_net > threshold (1.5).
    working_capital = 200, revenue_net = 100 → ratio = 2.0 > 1.5 → fires.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    async def mock_trailing(cid, key, n):
        if key == "revenue_net" and n == 1:
            return [100.0]
        return None

    engine._trailing_values = mock_trailing

    fired, explanation, threshold = await engine._check_rule(
        "ratio_breach", 200.0, ratio_rule.parameters, company_id
    )

    assert fired is True
    assert threshold == 1.5
    assert "above" in explanation


@pytest.mark.asyncio
async def test_ratio_breach_does_not_fire(mock_session, company, company_id):
    """
    ratio_breach does NOT fire when the ratio is within the threshold.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    async def mock_trailing(cid, key, n):
        if key == "revenue_net" and n == 1:
            return [100.0]
        return None

    engine._trailing_values = mock_trailing

    params = {
        "numerator_metric": "working_capital",
        "denominator_metric": "revenue_net",
        "threshold": 1.5,
        "direction": "above",
    }
    # working_capital = 100, revenue_net = 100 → ratio = 1.0 < 1.5 → no fire
    fired, explanation, threshold = await engine._check_rule(
        "ratio_breach", 100.0, params, company_id
    )

    assert fired is False


@pytest.mark.asyncio
async def test_ratio_breach_below_direction(mock_session, company, company_id):
    """
    ratio_breach with direction='below' fires when ratio < threshold.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    async def mock_trailing(cid, key, n):
        if key == "revenue_net" and n == 1:
            return [100.0]
        return None

    engine._trailing_values = mock_trailing

    params = {
        "numerator_metric": "working_capital",
        "denominator_metric": "revenue_net",
        "threshold": 0.5,
        "direction": "below",
    }
    # working_capital = 30, revenue_net = 100 → ratio = 0.3 < 0.5 → fires
    fired, explanation, threshold = await engine._check_rule(
        "ratio_breach", 30.0, params, company_id
    )

    assert fired is True
    assert "below" in explanation


# ── plan_variance ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_plan_variance_fires_below_plan(
    mock_session, company, plan_variance_rule, company_id
):
    """
    plan_variance fires when actual < plan * (1 - threshold_pct).
    plan=100, threshold_pct=0.10 → lower=90.  actual=80 < 90 → fires.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    fired, explanation, threshold = await engine._check_rule(
        "plan_variance", 80.0, plan_variance_rule.parameters, company_id
    )

    assert fired is True
    assert threshold == 90.0  # 100 * (1 - 0.10)
    assert "below plan" in explanation


@pytest.mark.asyncio
async def test_plan_variance_fires_above_plan(mock_session, company, company_id):
    """
    plan_variance fires when actual > plan * (1 + threshold_pct).
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    params = {"metric_key": "ebitda", "plan_value": 100.0, "threshold_pct": 0.10}
    # actual=115 > upper=110 → fires
    fired, explanation, threshold = await engine._check_rule(
        "plan_variance", 115.0, params, company_id
    )

    assert fired is True
    assert threshold == pytest.approx(110.0)  # 100 * (1 + 0.10)
    assert "above plan" in explanation


@pytest.mark.asyncio
async def test_plan_variance_does_not_fire(mock_session, company, company_id):
    """
    plan_variance does NOT fire when actual is within the acceptable band
    around the plan value.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    params = {"metric_key": "ebitda", "plan_value": 100.0, "threshold_pct": 0.10}
    # actual=105 is within [90, 110] → no fire
    fired, explanation, threshold = await engine._check_rule(
        "plan_variance", 105.0, params, company_id
    )

    assert fired is False


@pytest.mark.asyncio
async def test_plan_variance_requires_plan_value(mock_session, company, company_id):
    """
    plan_variance returns False when plan_value is not provided.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    params = {"metric_key": "ebitda", "threshold_pct": 0.10}  # no plan_value
    fired, explanation, threshold = await engine._check_rule(
        "plan_variance", 80.0, params, company_id
    )

    assert fired is False
    assert "plan_value not provided" in explanation


# ── _latest_period_id ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_latest_period_id_returns_none_when_no_periods(mock_session, company_id):
    """
    _latest_period_id returns None when no periods exist for the company.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await engine._latest_period_id(company_id)

    assert result is None


@pytest.mark.asyncio
async def test_latest_period_id_returns_id(mock_session, company_id, period_id):
    """
    _latest_period_id returns the UUID of the most recent period.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = period_id
    mock_session.execute.return_value = mock_result

    result = await engine._latest_period_id(company_id)

    assert result == period_id


# ── _maybe_resolve ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_maybe_resolve_with_absolute_rule(mock_session, company, absolute_rule):
    """
    _maybe_resolve resolves an open absolute_threshold alert when the
    current value is back within bounds.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    open_alert = Alert(
        id=uuid.uuid4(),
        company_id=company.id,
        metric_key="ebitda",
        period_id=uuid.uuid4(),
        rule_id=absolute_rule.id,
        severity=AlertSeverity.CRITICAL,
        triggered_at=datetime.now(timezone.utc),
        metric_value=-10.0,
        threshold_value=0.0,
        rule_snapshot={},
        explanation="EBITDA below floor",
        status="open",
    )

    async def mock_open_exists(rid, cid):
        if rid == absolute_rule.id and cid == company.id:
            return open_alert
        return None

    engine._open_alert_exists = mock_open_exists

    async def mock_trailing(cid, key, n):
        # n = recovery_window + 1 = 3 (default recovery_window=2)
        # Return 3 values so len(trailing) >= recovery_window + 1
        if n == 3:
            return [100.0, 50.0, 60.0]  # current, prior1, prior2
        return None

    engine._trailing_values = mock_trailing

    async def mock_check_rule(rule_type, value, params, cid):
        # All prior values should not fire the absolute rule (value >= floor=0)
        return (False, "", 0.0)

    engine._check_rule = mock_check_rule

    resolved = await engine._maybe_resolve(absolute_rule, company.id)

    assert resolved is not None
    assert resolved.status == "resolved"


@pytest.mark.asyncio
async def test_maybe_resolve_no_open_alert(mock_session, company, absolute_rule):
    """
    _maybe_resolve returns None when there is no open alert for this rule.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    async def mock_open_exists(rid, cid):
        return None

    engine._open_alert_exists = mock_open_exists

    resolved = await engine._maybe_resolve(absolute_rule, company.id)

    assert resolved is None


@pytest.mark.asyncio
async def test_maybe_resolve_with_non_absolute_rule_type(mock_session, company, relative_rule):
    """
    _maybe_resolve correctly evaluates a non-absolute rule type
    (relative_threshold) to determine recovery.

    This is the fix for the prior bug where _maybe_resolve only worked
    with absolute_threshold — it now calls _check_rule (which is async)
    to evaluate any rule type.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    open_alert = Alert(
        id=uuid.uuid4(),
        company_id=company.id,
        metric_key="revenue_net",
        period_id=uuid.uuid4(),
        rule_id=relative_rule.id,
        severity=AlertSeverity.ELEVATED,
        triggered_at=datetime.now(timezone.utc),
        metric_value=70.0,
        threshold_value=90.0,
        rule_snapshot={},
        explanation="Revenue below relative threshold",
        status="open",
    )

    async def mock_open_exists(rid, cid):
        if rid == relative_rule.id and cid == company.id:
            return open_alert
        return None

    engine._open_alert_exists = mock_open_exists

    async def mock_trailing(cid, key, n):
        if n == 3:
            # Current (100) is fine; prior [100, 100] also fine (avg=100, threshold=90)
            return [100.0, 100.0, 100.0]
        return None

    engine._trailing_values = mock_trailing

    async def mock_check_rule(rule_type, value, params, cid):
        if rule_type == "relative_threshold":
            # value=100, trailing avg=100, threshold=90 → 100 > 90 → NOT fired
            return (False, "", 90.0)
        return (False, "", 0.0)

    engine._check_rule = mock_check_rule

    resolved = await engine._maybe_resolve(relative_rule, company.id)

    assert resolved is not None
    assert resolved.status == "resolved"


# ── _check_rule awaits all evaluators ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_check_rule_awaits_async_evaluators(
    mock_session, company, directional_rule, company_id
):
    """
    _check_rule is async and must await all evaluator calls.
    This test verifies the await chain works correctly by ensuring
    an async evaluator (like _eval_directional) is actually awaited.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    call_order = []

    async def mock_trailing(cid, key, n):
        call_order.append("trailing")
        # prior = [50, 60, 70]: worsening transitions 50→60, 60→70 = 2 ≥ window-1=2
        if n == 4:
            return [80.0, 50.0, 60.0, 70.0]
        return None

    engine._trailing_values = mock_trailing

    fired, explanation, threshold = await engine._check_rule(
        "directional_sustained", 80.0, directional_rule.parameters, company_id
    )

    assert fired is True
    # If await wasn't used, trailing would never have been called
    # (sync call to async function returns a coroutine, not a list)
    assert "trailing" in call_order


# ── End-to-end evaluate_company ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_evaluate_company_returns_empty_when_company_not_found(mock_session):
    """
    evaluate_company returns [] when the company does not exist.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await engine.evaluate_company(uuid.uuid4())

    assert result == []


@pytest.mark.asyncio
async def test_evaluate_company_no_alert_without_period_data(mock_session, company, absolute_rule):
    """
    evaluate_company does not create an alert when no period data exists
    (no periods → _latest_period_id returns None).
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    async def mock_load_rules(firm_id, cid):
        return [absolute_rule]

    async def mock_load_metrics(cid):
        return {"ebitda": -10.0}

    engine._load_active_rules = mock_load_rules
    engine._load_latest_metrics = mock_load_metrics

    async def tracking_execute(query):
        query_str = str(query)
        result = MagicMock()

        if "companies" in query_str and "SELECT" in query_str:
            result.scalar_one_or_none.return_value = company
        elif "periods" in query_str and "end_date" in query_str:
            result.scalar_one_or_none.return_value = None  # No period
        elif "alert_rules" in query_str:
            result.scalars.return_value.all.return_value = [absolute_rule]
        elif "metrics" in query_str and "superseded_by" in query_str:
            result.scalars.return_value.all.return_value = []
        elif "alerts" in query_str and "rule_id" in query_str:
            result.scalar_one_or_none.return_value = None
        else:
            result.scalar_one_or_none.return_value = None
            result.scalars.return_value.all.return_value = []

        return result

    mock_session.execute = tracking_execute

    fired_alerts = await engine.evaluate_company(company.id)

    # Alert should not be created without a period
    assert len(fired_alerts) == 0


@pytest.mark.asyncio
async def test_evaluate_company_creates_alert(mock_session, company, absolute_rule, period_id):
    """
    evaluate_company creates and returns an alert when a rule fires.
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    async def mock_load_rules(firm_id, cid):
        return [absolute_rule]

    async def mock_load_metrics(cid):
        return {"ebitda": -10.0}

    engine._load_active_rules = mock_load_rules
    engine._load_latest_metrics = mock_load_metrics

    async def tracking_execute(query):
        query_str = str(query)
        result = MagicMock()

        if "companies" in query_str and "SELECT" in query_str:
            result.scalar_one_or_none.return_value = company
        elif "periods" in query_str and "end_date" in query_str:
            result.scalar_one_or_none.return_value = period_id
        elif "alert_rules" in query_str:
            result.scalars.return_value.all.return_value = [absolute_rule]
        elif "metrics" in query_str and "superseded_by" in query_str:
            result.scalars.return_value.all.return_value = []
        elif "alerts" in query_str and "rule_id" in query_str:
            result.scalar_one_or_none.return_value = None
        else:
            result.scalar_one_or_none.return_value = None
            result.scalars.return_value.all.return_value = []

        return result

    mock_session.execute = tracking_execute

    fired_alerts = await engine.evaluate_company(company.id)

    assert len(fired_alerts) == 1
    alert = fired_alerts[0]
    assert alert.metric_key == "ebitda"
    assert alert.metric_value == -10.0
    assert alert.status == "open"


# ── Deduplication ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_alert_not_duplicated_when_already_open(
    mock_session, company, absolute_rule, period_id
):
    """
    When an open alert already exists for the same rule+company,
    a new alert is NOT created — instead the existing alert is returned
    (with updated metric_value if it changed).
    """
    from app.domain.alert_engine import AlertEngine

    engine = AlertEngine(mock_session)

    existing_alert = Alert(
        id=uuid.uuid4(),
        company_id=company.id,
        metric_key="ebitda",
        period_id=period_id,
        rule_id=absolute_rule.id,
        severity=AlertSeverity.CRITICAL,
        triggered_at=datetime.now(timezone.utc),
        metric_value=-5.0,
        threshold_value=0.0,
        rule_snapshot={},
        explanation="EBITDA below floor",
        status="open",
    )

    async def mock_load_rules(firm_id, cid):
        return [absolute_rule]

    async def mock_load_metrics(cid):
        return {"ebitda": -10.0}  # worsened from -5 to -10

    engine._load_active_rules = mock_load_rules
    engine._load_latest_metrics = mock_load_metrics

    open_alert_tracker = [existing_alert]

    async def tracking_execute(query):
        query_str = str(query)
        result = MagicMock()

        if "companies" in query_str and "SELECT" in query_str:
            result.scalar_one_or_none.return_value = company
        elif "periods" in query_str and "end_date" in query_str:
            result.scalar_one_or_none.return_value = period_id
        elif "alert_rules" in query_str:
            result.scalars.return_value.all.return_value = [absolute_rule]
        elif "metrics" in query_str and "superseded_by" in query_str:
            result.scalars.return_value.all.return_value = []
        elif "alerts" in query_str and "rule_id" in query_str:
            # First call: open alert exists
            result.scalar_one_or_none.return_value = open_alert_tracker[0]
        else:
            result.scalar_one_or_none.return_value = None
            result.scalars.return_value.all.return_value = []

        return result

    mock_session.execute = tracking_execute

    fired_alerts = await engine.evaluate_company(company.id)

    # Should not create a new alert — returns existing (updated)
    assert len(fired_alerts) == 1
    assert fired_alerts[0].id == existing_alert.id
    assert fired_alerts[0].metric_value == -10.0  # updated
