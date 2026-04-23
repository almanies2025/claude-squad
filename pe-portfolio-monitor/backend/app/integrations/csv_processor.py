"""
CSV processor — normalizes a portfolio company's chart-of-accounts export
into the raw staging table and applies canonical account mappings.

Accepts CSV with columns: account_id, account_name, amount, [currency]
Produces: RawStaging rows, Period, and computed Metric rows.
"""

from __future__ import annotations

import csv
import io
import uuid
from datetime import date
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.db.models import (
    AccountMapping,
    Company,
    Metric,
    Period,
    RawStaging,
)
from app.domain.entities import CSVUploadResponse


COGS_KEYS = {"cogs_direct_labor", "cogs_materials", "cogs_overhead"}
OPEX_KEYS = {"opex_sga_rent", "opex_sga_salaries", "opex_sga_other"}
CASH_KEYS = {"cash_balance"}

AR_BY_CLASS: dict[str, set[str]] = {
    "saas": set(),
    "services": set(),
    "manufacturing": {"ar_trade", "inventory_receivable"},
    "distribution": {"ar_trade", "ar_other"},
    "healthcare": {"ar_healthcare", "ar_trade"},
    "other": {"ar_trade"},
}
AP_BY_CLASS: dict[str, set[str]] = {
    "saas": set(),
    "services": set(),
    "manufacturing": {"ap_trade", "ap_other"},
    "distribution": {"ap_trade"},
    "healthcare": {"ap_trade"},
    "other": {"ap_trade"},
}
INVENTORY_BY_CLASS: dict[str, set[str]] = {
    "saas": set(),
    "services": set(),
    "manufacturing": {"inventory_fg", "inventory_wip", "inventory_raw"},
    "distribution": {"inventory_fg"},
    "healthcare": set(),
    "other": set(),
}

# Operating cash flow accounts (simplified — from indirect method)
OCF_BY_CLASS: dict[str, set[str]] = {
    "saas": {"net_income", "depreciation", "amortization", "stock_compensation"},
    "services": {"net_income", "depreciation", "amortization"},
    "manufacturing": {"net_income", "depreciation", "amortization", "inventory_change"},
    "distribution": {"net_income", "depreciation", "amortization", "inventory_change"},
    "healthcare": {"net_income", "depreciation", "amortization"},
    "other": {"net_income", "depreciation", "amortization"},
}

# KPI keys computed by this module
KPI_KEYS = {
    "revenue_net",
    "gross_profit",
    "gross_margin_pct",
    "cogs_total",
    "opex_total",
    "ebitda",
    "ebitda_margin_pct",
    "dso",
    "dpo",
    "dio",
    "working_capital",
    "cash_balance",
    "net_debt",
    "operating_cash_flow",
}


async def process_csv(
    session: AsyncSession,
    company_id: uuid.UUID,
    csv_content: str,
    period_label: str,
    start_date: date,
    end_date: date,
) -> CSVUploadResponse:
    """
    Parse CSV → upsert raw staging → upsert period → compute canonical KPIs.

    CSV format:
        account_id, account_name, amount, [currency]

    Commits atomically only after all work succeeds.
    """
    # 1. Parse CSV
    reader = csv.DictReader(io.StringIO(csv_content))
    rows: list[dict[str, Any]] = list(reader)

    # 2. Load company for classification + currency
    company_result = await session.execute(select(Company).where(Company.id == company_id))
    company: Company = company_result.scalar_one()
    classification = company.classification.value
    currency = company.base_currency

    # 3. Upsert Period (update dates if already exists)
    period = await _upsert_period(session, company_id, period_label, start_date, end_date)

    # 4. Build raw staging rows
    raw_staging_rows: list[dict[str, Any]] = []
    all_source_ids: list[str] = []
    for row in rows:
        account_id = row.get("account_id", "").strip()
        account_name = row.get("account_name", "").strip()
        amount_str = row.get("amount", "0").strip().replace(",", "")
        row_currency = row.get("currency", "USD").strip()
        try:
            amount = float(amount_str)
        except ValueError:
            amount = 0.0
        if not account_id:
            continue
        raw_staging_rows.append(
            {
                "company_id": company_id,
                "period_id": period.id,
                "source_account_id": account_id,
                "source_account_name": account_name,
                "amount": amount,
                "amount_currency": row_currency or "USD",
            }
        )
        all_source_ids.append(account_id)

    # 5. Upsert raw staging (on conflict: update amount + name)
    if raw_staging_rows:
        stmt = insert(RawStaging).values(raw_staging_rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["company_id", "period_id", "source_account_id"],
            set_={
                "amount": stmt.excluded.amount,
                "source_account_name": stmt.excluded.source_account_name,
            },
        )
        await session.execute(stmt)

    # 6. Reload canonical mappings (after potential new mappings from this CSV)
    canonical_map = await _load_canonical_map(session, company_id)
    reverse_map: dict[str, tuple[str, str]] = {
        m.source_account_id: (m.canonical_account_key, m.mapping_confidence.value)
        for m in canonical_map
    }

    # 7. Reload raw staging from DB to get canonical totals
    staging_result = await session.execute(
        select(RawStaging).where(
            RawStaging.company_id == company_id,
            RawStaging.period_id == period.id,
        )
    )
    staging_rows = list(staging_result.scalars().all())

    # 8. Aggregate by canonical key
    # Fallback: if no explicit mapping, try name-based matching
    CANONICAL_NAME_PATTERNS = {
        "revenue_net": ["revenue net", "net revenue", "total revenue", "sales"],
        "cogs_direct_labor": ["direct labor", "labor cost"],
        "cogs_materials": ["materials", "cogs materials", "cost of materials"],
        "cogs_overhead": ["manufacturing overhead", "overhead"],
        "opex_sga_rent": ["rent", "facility"],
        "opex_sga_salaries": ["salaries", "wages", "compensation", "salaries & wages", "payroll"],
        "opex_sga_other": [
            "office",
            "admin",
            "general & admin",
            "g&a",
            "operating expenses",
            "other opex",
        ],
        "depreciation": ["depreciation", "depr"],
        "amortization": ["amortization", "amort"],
        "da_other": ["amortization", "da other"],
        "cash_balance": ["cash", "cash and equivalents", "cash equivalents"],
        "accounts_receivable": [
            "accounts receivable",
            "ar trade",
            "trade receivables",
            "receivables",
        ],
        "inventory": ["inventory", "inventory fg", "raw materials", "work in progress"],
        "accounts_payable": ["accounts payable", "ap trade", "trade payables", "payables"],
        "accrued_expenses": ["accrued", "accrued expenses", "accrued liabilities"],
        "long_term_debt": ["long-term debt", "long term debt", "lt debt", "debt"],
    }

    def _name_to_key(name: str) -> str | None:
        name_lower = name.lower()
        for key, patterns in CANONICAL_NAME_PATTERNS.items():
            if any(p in name_lower for p in patterns):
                return key
        return None

    canonical_totals: dict[str, float] = {}
    matched_ids: set[str] = set()
    for row in staging_rows:
        # Try explicit mapping first
        key = reverse_map.get(row.source_account_id, (None, None))[0]
        # Fallback: name-based matching
        if not key:
            key = _name_to_key(row.source_account_name)
        if key and not key.startswith("__"):
            canonical_totals[key] = canonical_totals.get(key, 0.0) + float(row.amount)
            matched_ids.add(row.source_account_id)

    # Truly unmapped: account IDs with no explicit mapping AND name didn't match
    unmapped = [aid for aid in all_source_ids if aid not in matched_ids]

    # 9. Compute KPIs
    metrics_computed = await _upsert_metrics(
        session,
        company_id,
        period.id,
        classification,
        currency,
        canonical_totals,
        len(staging_rows),
    )

    # 10. Commit only after all work succeeds
    await session.commit()

    return CSVUploadResponse(
        company_id=company_id,
        rows_processed=len(rows),
        periods_created=1,
        metrics_computed=metrics_computed,
        unmapped_accounts=unmapped,
    )


async def _upsert_period(
    session: AsyncSession,
    company_id: uuid.UUID,
    period_label: str,
    start_date: date,
    end_date: date,
) -> Period:
    """Insert period if not exists; update dates if it does."""
    stmt = select(Period).where(
        Period.company_id == company_id,
        Period.calendar_period_label == period_label,
    )
    result = await session.execute(stmt)
    period = result.scalar_one_or_none()

    if period is None:
        period = Period(
            id=uuid.uuid4(),
            company_id=company_id,
            period_type="month",
            start_date=start_date,
            end_date=end_date,
            fiscal_period_label=period_label,
            calendar_period_label=period_label,
            status="open",
        )
        session.add(period)
    else:
        # Update dates if the period already existed
        period.start_date = start_date
        period.end_date = end_date

    await session.flush()
    return period


async def _load_canonical_map(
    session: AsyncSession,
    company_id: uuid.UUID,
) -> list[AccountMapping]:
    stmt = select(AccountMapping).where(
        AccountMapping.company_id == company_id,
        AccountMapping.effective_to.is_(None),
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def _upsert_metrics(
    session: AsyncSession,
    company_id: uuid.UUID,
    period_id: uuid.UUID,
    classification: str,
    currency: str,
    totals: dict[str, float],
    raw_row_count: int,
) -> int:
    """
    Compute KPIs from canonical totals and upsert into Metric table.

    Uses ON CONFLICT DO UPDATE to keep Metric rows immutable-with-supersession:
    - Existing metric's superseded_by is set to the new ID
    - New metric is inserted with the new computed value
    """
    # Derived KPIs
    revenue_net = totals.get("revenue_net", 0.0)
    cogs = sum(totals.get(k, 0.0) for k in COGS_KEYS)
    gross_profit = revenue_net - cogs
    gross_margin_pct = (gross_profit / revenue_net * 100) if revenue_net else 0.0
    opex = sum(totals.get(k, 0.0) for k in OPEX_KEYS)
    # D&A add-back: EBITDA = Gross Profit - OpEx + Depreciation + Amortization
    da = (
        totals.get("depreciation", 0.0)
        + totals.get("amortization", 0.0)
        + totals.get("da_other", 0.0)
    )
    ebitda = gross_profit - opex + da
    ebitda_margin_pct = (ebitda / revenue_net * 100) if revenue_net else 0.0

    ar_keys = AR_BY_CLASS.get(classification, set())
    ap_keys = AP_BY_CLASS.get(classification, set())
    inventory_keys = INVENTORY_BY_CLASS.get(classification, set())
    ocf_keys = OCF_BY_CLASS.get(classification, set())

    ar = sum(totals.get(k, 0.0) for k in ar_keys)
    ap = sum(totals.get(k, 0.0) for k in ap_keys)
    inventory = sum(totals.get(k, 0.0) for k in inventory_keys)
    cash = totals.get("cash_balance", 0.0)
    ocf = sum(totals.get(k, 0.0) for k in ocf_keys)

    # DSO/DPO/DIO: use period days (passed via caller or use 30 as fallback)
    days = 30.0
    # Note: period days should be passed in; default to 30 for csv-only path
    if revenue_net > 0:
        dso = ar / revenue_net * days
    else:
        dso = 0.0
    if cogs > 0:
        dpo = ap / cogs * days
        dio = inventory / cogs * days
    else:
        dpo = 0.0
        dio = 0.0

    working_capital = ar + inventory - ap
    # Net debt = total debt (long-term + short-term) - cash
    total_debt = totals.get("long_term_debt", 0.0) + totals.get("short_term_debt", 0.0)
    net_debt = total_debt - cash

    metrics_raw = [
        ("revenue_net", revenue_net),
        ("gross_profit", gross_profit),
        ("gross_margin_pct", gross_margin_pct),
        ("cogs_total", cogs),
        ("opex_total", opex),
        ("ebitda", ebitda),
        ("ebitda_margin_pct", ebitda_margin_pct),
        ("dso", dso),
        ("dpo", dpo),
        ("dio", dio),
        ("working_capital", working_capital),
        ("cash_balance", cash),
        ("net_debt", net_debt),
        ("operating_cash_flow", ocf),
    ]

    lineage = {"raw_row_count": raw_row_count}
    version = "1.0.0"
    computed = 0

    for metric_key, value in metrics_raw:
        new_id = uuid.uuid4()

        # Try to find existing metric for this company+period+key
        existing_stmt = select(Metric).where(
            Metric.company_id == company_id,
            Metric.period_id == period_id,
            Metric.metric_key == metric_key,
        )
        existing_result = await session.execute(existing_stmt)
        existing: Metric | None = existing_result.scalar_one_or_none()

        if existing:
            # Mark old as superseded
            await session.execute(
                update(Metric).where(Metric.id == existing.id).values(superseded_by=new_id)
            )

        # Insert new metric
        session.add(
            Metric(
                id=new_id,
                company_id=company_id,
                metric_key=metric_key,
                period_id=period_id,
                value=value,
                currency=currency,
                computation_version=version,
                confidence="high",
                confidence_reason=None,
                source_lineage=lineage,
            )
        )
        computed += 1

    return computed
