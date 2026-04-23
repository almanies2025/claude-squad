"""initial schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-04-20

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ── Enums ──────────────────────────────────────────────────────────────────

    op.execute("""
        CREATE TYPE erp_vendor AS ENUM (
            'quickbooks_online', 'netsuite', 'sage_intacct',
            'dynamics_bc', 'csv_upload'
        )
    """)
    op.execute("""
        CREATE TYPE company_status AS ENUM (
            'onboarding', 'live', 'paused', 'offboarded'
        )
    """)
    op.execute("""
        CREATE TYPE company_classification AS ENUM (
            'saas', 'services', 'manufacturing', 'distribution', 'healthcare', 'other'
        )
    """)
    op.execute("""
        CREATE TYPE period_type AS ENUM (
            'month', 'quarter', 'trailing_3m', 'trailing_12m', 'fiscal_year'
        )
    """)
    op.execute("""
        CREATE TYPE period_status AS ENUM ('open', 'soft_closed', 'closed')
    """)
    op.execute("""
        CREATE TYPE account_category AS ENUM (
            'revenue', 'cogs', 'opex', 'other_income',
            'other_expense', 'asset', 'liability', 'equity'
        )
    """)
    op.execute("""
        CREATE TYPE normal_balance AS ENUM ('debit', 'credit')
    """)
    op.execute("""
        CREATE TYPE mapping_confidence AS ENUM ('high', 'medium', 'low')
    """)
    op.execute("""
        CREATE TYPE alert_severity AS ENUM ('critical', 'elevated', 'informational')
    """)
    op.execute("""
        CREATE TYPE alert_status AS ENUM (
            'open', 'acknowledged', 'resolved', 'false_positive', 'suppressed'
        )
    """)
    op.execute("""
        CREATE TYPE rule_type AS ENUM (
            'absolute_threshold', 'relative_threshold',
            'directional_sustained', 'ratio_breach', 'plan_variance'
        )
    """)
    op.execute("""
        CREATE TYPE user_role AS ENUM (
            'pe_admin', 'pe_partner', 'pe_operator', 'pe_ops',
            'portco_admin', 'portco_viewer'
        )
    """)

    # ── Core Tables ────────────────────────────────────────────────────────────

    op.create_table(
        "firms",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="UTC"),
        sa.Column("slack_workspace_id", sa.String(64), nullable=True),
        sa.Column("sso_config", postgresql.JSONB, nullable=True),
        sa.Column("subscription_status", sa.String(32), nullable=False, server_default="trial"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "firm_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("firms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM(
                "pe_admin",
                "pe_partner",
                "pe_operator",
                "pe_ops",
                "portco_admin",
                "portco_viewer",
                name="user_role",
                create_type=False,
            ),
            nullable=False,
            server_default="pe_partner",
        ),
        sa.Column("totp_secret", sa.String(32), nullable=True),
        sa.Column("totp_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("sso_external_id", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_users_firm_id", "users", ["firm_id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "companies",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "firm_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("firms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("legal_name", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column(
            "classification",
            postgresql.ENUM(
                "saas",
                "services",
                "manufacturing",
                "distribution",
                "healthcare",
                "other",
                name="company_classification",
                create_type=False,
            ),
            nullable=False,
            server_default="services",
        ),
        sa.Column("base_currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("fiscal_year_end_month", sa.Integer(), nullable=False, server_default="12"),
        sa.Column("reporting_timezone", sa.String(64), nullable=False, server_default="UTC"),
        sa.Column(
            "erp_vendor",
            postgresql.ENUM(
                "quickbooks_online",
                "netsuite",
                "sage_intacct",
                "dynamics_bc",
                "csv_upload",
                name="erp_vendor",
                create_type=False,
            ),
            nullable=False,
            server_default="csv_upload",
        ),
        sa.Column("erp_instance_id", sa.String(255), nullable=True),
        sa.Column("erp_oauth_tokens", postgresql.JSONB, nullable=True),
        sa.Column("onboarded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "onboarding",
                "live",
                "paused",
                "offboarded",
                name="company_status",
                create_type=False,
            ),
            nullable=False,
            server_default="onboarding",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_companies_firm_id", "companies", ["firm_id"])

    op.create_table(
        "periods",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "period_type",
            postgresql.ENUM(
                "month",
                "quarter",
                "trailing_3m",
                "trailing_12m",
                "fiscal_year",
                name="period_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("fiscal_period_label", sa.String(32), nullable=False),
        sa.Column("calendar_period_label", sa.String(16), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "open", "soft_closed", "closed", name="period_status", create_type=False
            ),
            nullable=False,
            server_default="open",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_periods_company_id", "periods", ["company_id"])
    op.create_index("ix_periods_start_end", "periods", ["start_date", "end_date"])

    op.create_table(
        "canonical_accounts",
        sa.Column("key", sa.String(128), primary_key=True),
        sa.Column(
            "category",
            postgresql.ENUM(
                "revenue",
                "cogs",
                "opex",
                "other_income",
                "other_expense",
                "asset",
                "liability",
                "equity",
                name="account_category",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "normal_balance",
            postgresql.ENUM("debit", "credit", name="normal_balance", create_type=False),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
    )

    # Seed canonical account keys
    canonical_keys = [
        ("revenue_gross", "revenue", "credit"),
        ("revenue_returns", "revenue", "credit"),
        ("revenue_net", "revenue", "credit"),
        ("cogs_direct_labor", "cogs", "debit"),
        ("cogs_materials", "cogs", "debit"),
        ("cogs_overhead", "cogs", "debit"),
        ("gross_profit", "revenue", "credit"),
        ("opex_sga_rent", "opex", "debit"),
        ("opex_sga_salaries", "opex", "debit"),
        ("opex_sga_other", "opex", "debit"),
        ("ebitda", "revenue", "credit"),
        ("ebitda_margin_pct", "revenue", "credit"),
        ("dso", "asset", "debit"),
        ("dpo", "liability", "credit"),
        ("dio", "asset", "debit"),
        ("working_capital", "asset", "debit"),
        ("cash_balance", "asset", "debit"),
        ("net_debt", "liability", "credit"),
        ("revenue_yoy_pct", "revenue", "credit"),
        ("revenue_mom_pct", "revenue", "credit"),
        ("arr", "revenue", "credit"),
        ("net_revenue_retention_pct", "revenue", "credit"),
        ("logo_churn_pct", "revenue", "credit"),
        ("total_fte", "asset", "debit"),
        ("operating_cash_flow", "asset", "debit"),
    ]
    for key, cat, nb in canonical_keys:
        op.execute(
            f"INSERT INTO canonical_accounts (key, category, normal_balance) "
            f"VALUES ('{key}', '{cat}', '{nb}')"
        )

    op.create_table(
        "account_mappings",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_account_id", sa.String(255), nullable=False),
        sa.Column("source_account_name", sa.String(255), nullable=False),
        sa.Column(
            "canonical_account_key",
            sa.String(128),
            sa.ForeignKey("canonical_accounts.key"),
            nullable=False,
        ),
        sa.Column(
            "mapping_confidence",
            postgresql.ENUM("high", "medium", "low", name="mapping_confidence", create_type=False),
            nullable=False,
            server_default="medium",
        ),
        sa.Column(
            "effective_from", sa.Date(), nullable=False, server_default=sa.text("CURRENT_DATE")
        ),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column(
            "mapped_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True
        ),
        sa.Column(
            "reviewed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_account_mappings_company_id", "account_mappings", ["company_id"])
    op.create_index(
        "ix_account_mappings_company_source_effective",
        "account_mappings",
        ["company_id", "source_account_id", "effective_from"],
        unique=True,
    )

    # Raw staging table — preserves source ERP shape
    op.create_table(
        "raw_staging",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "period_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("periods.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_account_id", sa.String(255), nullable=False),
        sa.Column("source_account_name", sa.String(255), nullable=False),
        sa.Column("amount", sa.Numeric(20, 4), nullable=False),
        sa.Column("amount_currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("fx_rate", sa.Numeric(18, 8), nullable=True),
        sa.Column(
            "fetched_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("raw_payload", postgresql.JSONB, nullable=True),
    )
    op.create_index("ix_raw_staging_company_period", "raw_staging", ["company_id", "period_id"])

    op.create_table(
        "metrics",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("metric_key", sa.String(128), nullable=False),
        sa.Column(
            "period_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("periods.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("value", sa.Numeric(20, 4), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("computation_version", sa.String(32), nullable=False, server_default="1.0.0"),
        sa.Column(
            "confidence",
            postgresql.ENUM("high", "medium", "low", name="mapping_confidence", create_type=False),
            nullable=False,
            server_default="high",
        ),
        sa.Column("confidence_reason", sa.Text(), nullable=True),
        sa.Column("source_lineage", postgresql.JSONB, nullable=True),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("superseded_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_metrics_company_metric", "metrics", ["company_id", "metric_key"])
    op.create_index("ix_metrics_period_id", "metrics", ["period_id"])
    op.create_index("ix_metrics_metric_key", "metrics", ["metric_key"])

    op.create_table(
        "alert_rules",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=True,
        ),
        # null company_id = firm-wide default
        sa.Column(
            "firm_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("firms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("metric_key", sa.String(128), nullable=False),
        sa.Column(
            "rule_type",
            postgresql.ENUM(
                "absolute_threshold",
                "relative_threshold",
                "directional_sustained",
                "ratio_breach",
                "plan_variance",
                name="rule_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("parameters", postgresql.JSONB, nullable=False),
        sa.Column(
            "severity",
            postgresql.ENUM(
                "critical", "elevated", "informational", name="alert_severity", create_type=False
            ),
            nullable=False,
            server_default="elevated",
        ),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_alert_rules_firm_id", "alert_rules", ["firm_id"])
    op.create_index("ix_alert_rules_company_id", "alert_rules", ["company_id"])

    op.create_table(
        "alerts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("metric_key", sa.String(128), nullable=False),
        sa.Column(
            "period_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("periods.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "rule_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("alert_rules.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "severity",
            postgresql.ENUM(
                "critical", "elevated", "informational", name="alert_severity", create_type=False
            ),
            nullable=False,
        ),
        sa.Column(
            "triggered_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("metric_value", sa.Numeric(20, 4), nullable=False),
        sa.Column("threshold_value", sa.Numeric(20, 4), nullable=False),
        sa.Column("rule_snapshot", postgresql.JSONB, nullable=False),
        sa.Column("context", postgresql.JSONB, nullable=True),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "open",
                "acknowledged",
                "resolved",
                "false_positive",
                "suppressed",
                name="alert_status",
                create_type=False,
            ),
            nullable=False,
            server_default="open",
        ),
        sa.Column("status_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status_changed_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("resolution_note", sa.Text(), nullable=True),
    )
    op.create_index("ix_alerts_company_id", "alerts", ["company_id"])
    op.create_index("ix_alerts_status", "alerts", ["status"])
    op.create_index("ix_alerts_triggered_at", "alerts", ["triggered_at"])

    op.create_table(
        "subscriptions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("metric_key", sa.String(128), nullable=True),
        sa.Column("channel", sa.String(32), nullable=False, server_default="email"),
        sa.Column(
            "severity_threshold",
            postgresql.ENUM(
                "critical", "elevated", "informational", name="alert_severity", create_type=False
            ),
            nullable=False,
            server_default="elevated",
        ),
        sa.Column("muted_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])

    op.create_table(
        "notification_deliveries",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "alert_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("alerts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("channel", sa.String(32), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("provider_message_id", sa.String(255), nullable=True),
    )
    op.create_index("ix_notification_deliveries_alert_id", "notification_deliveries", ["alert_id"])

    op.create_table(
        "audit_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "actor_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("resource_type", sa.String(64), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "firm_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("firms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_audit_logs_firm_id", "audit_logs", ["firm_id"])
    op.create_index("ix_audit_logs_occurred_at", "audit_logs", ["occurred_at"])
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])

    # ── RLS Policy ─────────────────────────────────────────────────────────────
    # Tables with firm_id directly
    for table in ["users", "companies", "audit_logs"]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY tenant_isolation_{table} ON {table} "
            f"FOR ALL USING ("
            f"current_setting('app.current_firm_id', true) IS NOT NULL "
            f"AND current_setting('app.current_firm_id') <> '' "
            f"AND firm_id = current_setting('app.current_firm_id')::uuid)"
        )

    # Tables with company_id (scoped via company → firm)
    for table in [
        "periods",
        "account_mappings",
        "raw_staging",
        "metrics",
        "alert_rules",
        "alerts",
        "subscriptions",
    ]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY tenant_isolation_{table} ON {table} "
            f"FOR ALL USING ("
            f"current_setting('app.current_firm_id', true) IS NOT NULL "
            f"AND current_setting('app.current_firm_id') <> '' "
            f"AND company_id IN ("
            f"  SELECT id FROM companies "
            f"  WHERE firm_id = current_setting('app.current_firm_id')::uuid"
            f"))"
        )

    # notification_deliveries: scoped via alert_id → alerts → company → firm
    # Uses user_id as alternative join path via users → firm
    op.execute("ALTER TABLE notification_deliveries ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY tenant_isolation_notification_deliveries "
        "ON notification_deliveries FOR ALL USING ("
        "current_setting('app.current_firm_id', true) IS NOT NULL AND "
        "current_setting('app.current_firm_id') <> '' AND "
        "alert_id IN ("
        "  SELECT a.id FROM alerts a "
        "  JOIN companies c ON a.company_id = c.id "
        "  WHERE c.firm_id = current_setting('app.current_firm_id')::uuid)"
        ")"
    )

    # ── Updated_at trigger ─────────────────────────────────────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql'
    """)
    for table in ["firms", "users", "companies"]:
        op.execute(
            f"CREATE TRIGGER update_{table}_updated_at "
            f"BEFORE UPDATE ON {table} "
            f"FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()"
        )


def downgrade() -> None:
    for table in [
        "audit_logs",
        "notification_deliveries",
        "subscriptions",
        "alerts",
        "alert_rules",
        "metrics",
        "raw_staging",
        "account_mappings",
        "canonical_accounts",
        "periods",
        "companies",
        "users",
        "firms",
    ]:
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")

    for enum_name in [
        "erp_vendor",
        "company_status",
        "company_classification",
        "period_type",
        "period_status",
        "account_category",
        "normal_balance",
        "mapping_confidence",
        "alert_severity",
        "alert_status",
        "rule_type",
        "user_role",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")

    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
