import uuid
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── Enums ──────────────────────────────────────────────────────────────────────


class ErpVendor(str, Enum):
    QUICKBOOKS_ONLINE = "quickbooks_online"
    NETSUITE = "netsuite"
    SAGE_INTACCT = "sage_intacct"
    DYNAMICS_BC = "dynamics_bc"
    CSV_UPLOAD = "csv_upload"


class CompanyStatus(str, Enum):
    ONBOARDING = "onboarding"
    LIVE = "live"
    PAUSED = "paused"
    OFFBOARDED = "offboarded"


class CompanyClassification(str, Enum):
    SAAS = "saas"
    SERVICES = "services"
    MANUFACTURING = "manufacturing"
    DISTRIBUTION = "distribution"
    HEALTHCARE = "healthcare"
    OTHER = "other"


class PeriodType(str, Enum):
    MONTH = "month"
    QUARTER = "quarter"
    TRAILING_3M = "trailing_3m"
    TRAILING_12M = "trailing_12m"
    FISCAL_YEAR = "fiscal_year"


class PeriodStatus(str, Enum):
    OPEN = "open"
    SOFT_CLOSED = "soft_closed"
    CLOSED = "closed"


class AccountCategory(str, Enum):
    REVENUE = "revenue"
    COGS = "cogs"
    OPEX = "opex"
    OTHER_INCOME = "other_income"
    OTHER_EXPENSE = "other_expense"
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"


class NormalBalance(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class MappingConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    ELEVATED = "elevated"
    INFORMATIONAL = "informational"


class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    SUPPRESSED = "suppressed"


class RuleType(str, Enum):
    ABSOLUTE_THRESHOLD = "absolute_threshold"
    RELATIVE_THRESHOLD = "relative_threshold"
    DIRECTIONAL_SUSTAINED = "directional_sustained"
    RATIO_BREACH = "ratio_breach"
    PLAN_VARIANCE = "plan_variance"


class UserRole(str, Enum):
    PE_ADMIN = "pe_admin"
    PE_PARTNER = "pe_partner"
    PE_OPERATOR = "pe_operator"
    PE_OPS = "pe_ops"
    PORTCO_ADMIN = "portco_admin"
    PORTCO_VIEWER = "portco_viewer"


# ── Firm ────────────────────────────────────────────────────────────────────────


class FirmBase(BaseModel):
    name: str
    timezone: str = "UTC"


class FirmCreate(FirmBase):
    pass


class Firm(FirmBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subscription_status: str
    created_at: datetime
    updated_at: datetime


# ── User ──────────────────────────────────────────────────────────────────────


class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole = UserRole.PE_PARTNER


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    firm_id: uuid.UUID
    totp_enabled: bool
    is_active: bool
    sso_external_id: str | None
    created_at: datetime
    updated_at: datetime


# ── Company ────────────────────────────────────────────────────────────────────


class CompanyBase(BaseModel):
    legal_name: str
    display_name: str
    classification: CompanyClassification = CompanyClassification.SERVICES
    base_currency: str = "USD"
    fiscal_year_end_month: int = 12
    reporting_timezone: str = "UTC"
    erp_vendor: ErpVendor = ErpVendor.CSV_UPLOAD
    erp_instance_id: str | None = None


class CompanyCreate(CompanyBase):
    """firm_id is set server-side from the authenticated user's firm."""


class CompanyUpdate(BaseModel):
    legal_name: str | None = None
    display_name: str | None = None
    classification: CompanyClassification | None = None
    status: CompanyStatus | None = None


class Company(CompanyBase):
    model_config = ConfigDict(from_attributes=True, exclude=["erp_oauth_tokens"])

    id: uuid.UUID
    firm_id: uuid.UUID
    status: CompanyStatus
    onboarded_at: datetime | None
    created_at: datetime
    updated_at: datetime


# ── Period ─────────────────────────────────────────────────────────────────────


class PeriodBase(BaseModel):
    period_type: PeriodType
    start_date: date
    end_date: date
    fiscal_period_label: str
    calendar_period_label: str


class PeriodCreate(PeriodBase):
    company_id: uuid.UUID


class Period(PeriodBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    status: PeriodStatus
    created_at: datetime


# ── CanonicalAccount ───────────────────────────────────────────────────────────


class CanonicalAccount(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    category: AccountCategory
    normal_balance: NormalBalance
    description: str | None = None


# ── AccountMapping ─────────────────────────────────────────────────────────────


class AccountMappingBase(BaseModel):
    source_account_id: str
    source_account_name: str
    canonical_account_key: str
    mapping_confidence: MappingConfidence = MappingConfidence.MEDIUM
    effective_from: date


class AccountMappingCreate(AccountMappingBase):
    company_id: uuid.UUID


class AccountMapping(AccountMappingBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    effective_to: date | None
    mapped_by: uuid.UUID | None
    reviewed_by: uuid.UUID | None
    created_at: datetime


# ── Metric ─────────────────────────────────────────────────────────────────────


class Metric(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    metric_key: str
    period_id: uuid.UUID
    value: float
    currency: str
    computation_version: str
    confidence: MappingConfidence
    confidence_reason: str | None
    source_lineage: dict | None
    computed_at: datetime
    superseded_by: uuid.UUID | None


class MetricHistory(BaseModel):
    """Per-company metric time series for sparklines."""

    company_id: uuid.UUID
    display_name: str
    metric_key: str
    periods: list[dict]  # [{period_id, calendar_label, value, status}]


# ── Heatmap ────────────────────────────────────────────────────────────────────


class HeatmapCell(BaseModel):
    """One KPI cell in the portfolio heatmap."""

    company_id: uuid.UUID
    display_name: str
    metric_key: str
    value: float | None
    currency: str
    status: str | None  # green | amber | red | null
    confidence: MappingConfidence | None
    period_label: str


class HeatmapResponse(BaseModel):
    """Full portfolio heatmap."""

    period_label: str
    cells: list[HeatmapCell]
    generated_at: datetime


# ── AlertRule ──────────────────────────────────────────────────────────────────


class AlertRuleBase(BaseModel):
    metric_key: str
    rule_type: RuleType
    parameters: dict
    severity: AlertSeverity = AlertSeverity.ELEVATED
    active: bool = True


class AlertRuleCreate(AlertRuleBase):
    company_id: uuid.UUID | None = None  # null = firm-wide default


class AlertRule(AlertRuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    firm_id: uuid.UUID
    company_id: uuid.UUID | None
    created_by: uuid.UUID | None
    created_at: datetime


# ── Alert ──────────────────────────────────────────────────────────────────────


class Alert(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    metric_key: str
    period_id: uuid.UUID
    rule_id: uuid.UUID | None
    severity: AlertSeverity
    triggered_at: datetime
    metric_value: float
    threshold_value: float
    rule_snapshot: dict
    context: dict | None
    explanation: str
    status: AlertStatus
    status_changed_at: datetime | None
    status_changed_by: uuid.UUID | None
    resolution_note: str | None


class AlertUpdate(BaseModel):
    status: AlertStatus
    resolution_note: str | None = None


# ── Auth ──────────────────────────────────────────────────────────────────────


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # user_id as string
    exp: datetime | None = None


class TOTPVerify(BaseModel):
    code: str


# ── CSV Upload ─────────────────────────────────────────────────────────────────


class CSVUploadResponse(BaseModel):
    company_id: uuid.UUID
    rows_processed: int
    periods_created: int
    metrics_computed: int
    unmapped_accounts: list[str]


# ── Subscription ────────────────────────────────────────────────────────────────


class Subscription(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    company_id: uuid.UUID | None
    metric_key: str | None
    channel: str
    severity_threshold: AlertSeverity
    muted_until: datetime | None
    created_at: datetime


class NotificationDelivery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    alert_id: uuid.UUID
    user_id: uuid.UUID
    channel: str
    delivered_at: datetime | None
    status: str
    provider_message_id: str | None


# ── AuditLog ──────────────────────────────────────────────────────────────────


class AuditLog(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    firm_id: uuid.UUID
    actor_user_id: uuid.UUID | None
    action: str
    resource_type: str
    resource_id: uuid.UUID | None
    company_id: uuid.UUID | None
    ip_address: str | None
    extra: dict | None
    occurred_at: datetime
