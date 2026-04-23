import uuid
from datetime import date, datetime
from enum import Enum as PyEnum
from typing import NewType

import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

UUIDPk = NewType("UUIDPk", uuid.UUID)


# ── Enums ──────────────────────────────────────────────────────────────────────


class ErpVendor(PyEnum):
    QUICKBOOKS_ONLINE = "quickbooks_online"
    NETSUITE = "netsuite"
    SAGE_INTACCT = "sage_intacct"
    DYNAMICS_BC = "dynamics_bc"
    CSV_UPLOAD = "csv_upload"


class CompanyStatus(PyEnum):
    ONBOARDING = "onboarding"
    LIVE = "live"
    PAUSED = "paused"
    OFFBOARDED = "offboarded"


class CompanyClassification(PyEnum):
    SAAS = "saas"
    SERVICES = "services"
    MANUFACTURING = "manufacturing"
    DISTRIBUTION = "distribution"
    HEALTHCARE = "healthcare"
    OTHER = "other"


class PeriodType(PyEnum):
    MONTH = "month"
    QUARTER = "quarter"
    TRAILING_3M = "trailing_3m"
    TRAILING_12M = "trailing_12m"
    FISCAL_YEAR = "fiscal_year"


class PeriodStatus(PyEnum):
    OPEN = "open"
    SOFT_CLOSED = "soft_closed"
    CLOSED = "closed"


class AccountCategory(PyEnum):
    REVENUE = "revenue"
    COGS = "cogs"
    OPEX = "opex"
    OTHER_INCOME = "other_income"
    OTHER_EXPENSE = "other_expense"
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"


class NormalBalance(PyEnum):
    DEBIT = "debit"
    CREDIT = "credit"


class MappingConfidence(PyEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertSeverity(PyEnum):
    CRITICAL = "critical"
    ELEVATED = "elevated"
    INFORMATIONAL = "informational"


class AlertStatus(PyEnum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    SUPPRESSED = "suppressed"


class RuleType(PyEnum):
    ABSOLUTE_THRESHOLD = "absolute_threshold"
    RELATIVE_THRESHOLD = "relative_threshold"
    DIRECTIONAL_SUSTAINED = "directional_sustained"
    RATIO_BREACH = "ratio_breach"
    PLAN_VARIANCE = "plan_variance"


class UserRole(PyEnum):
    PE_ADMIN = "pe_admin"
    PE_PARTNER = "pe_partner"
    PE_OPERATOR = "pe_operator"
    PE_OPS = "pe_ops"
    PORTCO_ADMIN = "portco_admin"
    PORTCO_VIEWER = "portco_viewer"


# ── Mixin ──────────────────────────────────────────────────────────────────────


class TenantMixin:
    """Adds firm_id to any model that is tenant-scoped."""

    firm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("firms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )


# ── Firm ───────────────────────────────────────────────────────────────────────


class Firm(Base):
    __tablename__ = "firms"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, server_default="UTC")
    slack_workspace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sso_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    subscription_status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="trial"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    users: Mapped[list["User"]] = relationship(back_populates="firm", lazy="noload")
    companies: Mapped[list["Company"]] = relationship(back_populates="firm", lazy="noload")


# ── User ──────────────────────────────────────────────────────────────────────


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    firm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("firms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default="pe_partner",
    )
    totp_secret: Mapped[str | None] = mapped_column(String(32), nullable=True)
    totp_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    sso_external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    firm: Mapped["Firm"] = relationship(back_populates="users")


# ── Company ────────────────────────────────────────────────────────────────────


class Company(TenantMixin, Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    classification: Mapped[CompanyClassification] = mapped_column(
        Enum(
            CompanyClassification,
            name="company_classification",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default="services",
    )
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="USD")
    fiscal_year_end_month: Mapped[int] = mapped_column(Integer, nullable=False, server_default="12")
    reporting_timezone: Mapped[str] = mapped_column(
        String(64), nullable=False, server_default="UTC"
    )
    erp_vendor: Mapped[ErpVendor] = mapped_column(
        Enum(
            ErpVendor,
            name="erp_vendor",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default="csv_upload",
    )
    erp_instance_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    erp_oauth_tokens: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    onboarded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[CompanyStatus] = mapped_column(
        Enum(
            CompanyStatus,
            name="company_status",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default="onboarding",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    firm: Mapped["Firm"] = relationship(back_populates="companies")
    periods: Mapped[list["Period"]] = relationship(back_populates="company", lazy="noload")
    account_mappings: Mapped[list["AccountMapping"]] = relationship(
        back_populates="company", lazy="noload"
    )
    metrics: Mapped[list["Metric"]] = relationship(back_populates="company", lazy="noload")


# ── Period ──────────────────────────────────────────────────────────────────────


class Period(Base):
    __tablename__ = "periods"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period_type: Mapped[PeriodType] = mapped_column(
        Enum(
            PeriodType,
            name="period_type",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    fiscal_period_label: Mapped[str] = mapped_column(String(32), nullable=False)
    calendar_period_label: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[PeriodStatus] = mapped_column(
        Enum(
            PeriodStatus,
            name="period_status",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default="open",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    company: Mapped["Company"] = relationship(back_populates="periods")

    __table_args__ = (Index("ix_periods_start_end", "start_date", "end_date"),)


# ── CanonicalAccount ──────────────────────────────────────────────────────────


class CanonicalAccount(Base):
    __tablename__ = "canonical_accounts"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    category: Mapped[AccountCategory] = mapped_column(
        Enum(
            AccountCategory,
            name="account_category",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    normal_balance: Mapped[NormalBalance] = mapped_column(
        Enum(
            NormalBalance,
            name="normal_balance",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


# ── AccountMapping ─────────────────────────────────────────────────────────────


class AccountMapping(Base):
    __tablename__ = "account_mappings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_account_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source_account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_account_key: Mapped[str] = mapped_column(
        String(128), ForeignKey("canonical_accounts.key"), nullable=False
    )
    mapping_confidence: Mapped[MappingConfidence] = mapped_column(
        Enum(
            MappingConfidence,
            name="mapping_confidence",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default="medium",
    )
    effective_from: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=func.current_date()
    )
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    mapped_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    company: Mapped["Company"] = relationship(back_populates="account_mappings")

    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "source_account_id",
            "effective_from",
            name="uq_account_mappings_company_source_effective",
        ),
        Index(
            "ix_account_mappings_company_source_effective",
            "company_id",
            "source_account_id",
            "effective_from",
            unique=True,
        ),
    )


# ── RawStaging ─────────────────────────────────────────────────────────────────


class RawStaging(Base):
    __tablename__ = "raw_staging"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("periods.id", ondelete="CASCADE"), nullable=False
    )
    source_account_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source_account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(20, 4), nullable=False)
    amount_currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="USD")
    fx_rate: Mapped[float | None] = mapped_column(Numeric(18, 8), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    raw_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (Index("ix_raw_staging_company_period", "company_id", "period_id"),)


# ── Metric ─────────────────────────────────────────────────────────────────────


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    metric_key: Mapped[str] = mapped_column(String(128), nullable=False)
    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("periods.id", ondelete="CASCADE"), nullable=False
    )
    value: Mapped[float] = mapped_column(Numeric(20, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="USD")
    computation_version: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="1.0.0"
    )
    confidence: Mapped[MappingConfidence] = mapped_column(
        Enum(
            MappingConfidence,
            name="mapping_confidence",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default="high",
    )
    confidence_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_lineage: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    superseded_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    company: Mapped["Company"] = relationship(back_populates="metrics")

    __table_args__ = (
        Index("ix_metrics_company_metric", "company_id", "metric_key"),
        Index("ix_metrics_period_id", "period_id"),
        Index("ix_metrics_metric_key", "metric_key"),
    )


# ── AlertRule ──────────────────────────────────────────────────────────────────


class AlertRule(TenantMixin, Base):
    __tablename__ = "alert_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    metric_key: Mapped[str] = mapped_column(String(128), nullable=False)
    rule_type: Mapped[RuleType] = mapped_column(
        Enum(
            RuleType,
            name="rule_type",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(
            AlertSeverity,
            name="alert_severity",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default="elevated",
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


# ── Alert ──────────────────────────────────────────────────────────────────────


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    metric_key: Mapped[str] = mapped_column(String(128), nullable=False)
    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("periods.id", ondelete="CASCADE"), nullable=False
    )
    rule_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("alert_rules.id", ondelete="SET NULL"), nullable=True
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(
            AlertSeverity,
            name="alert_severity",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    metric_value: Mapped[float] = mapped_column(Numeric(20, 4), nullable=False)
    threshold_value: Mapped[float] = mapped_column(Numeric(20, 4), nullable=False)
    rule_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    context: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[AlertStatus] = mapped_column(
        Enum(
            AlertStatus,
            name="alert_status",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default="open",
    )
    status_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status_changed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_alerts_company_id", "company_id"),
        Index("ix_alerts_status", "status"),
        Index("ix_alerts_triggered_at", "triggered_at"),
    )


# ── Subscription ───────────────────────────────────────────────────────────────


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True
    )
    metric_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    channel: Mapped[str] = mapped_column(String(32), nullable=False, server_default="email")
    severity_threshold: Mapped[AlertSeverity] = mapped_column(
        Enum(
            AlertSeverity,
            name="alert_severity",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        server_default="elevated",
    )
    muted_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


# ── NotificationDelivery ────────────────────────────────────────────────────────


class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (Index("ix_notification_deliveries_alert_id", "alert_id"),)


# ── AuditLog ──────────────────────────────────────────────────────────────────


class AuditLog(TenantMixin, Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    extra: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("ix_audit_logs_firm_id", "firm_id"),
        Index("ix_audit_logs_occurred_at", "occurred_at"),
        Index("ix_audit_logs_actor_user_id", "actor_user_id"),
    )
