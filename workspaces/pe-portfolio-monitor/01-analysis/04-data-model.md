# Data Model — PE Portfolio Monitoring Dashboard

## Design Principle

Normalization across heterogeneous ERPs is solved by a **two-layer model**:

- **Raw layer**: preserves source-system shape exactly as received, never modified after ingestion
- **Canonical layer**: everything else reads from here

The bridge is a declarative, per-company **account mapping config** — version-controlled, human-reviewable, and the locus of all "this company maps revenue differently" complexity.

The KPI engine, alerting, dashboards, and LP reporting never touch raw ERP data.

---

## Entity 1 — Company

```
Company
  id: uuid
  firm_id: uuid                    # the PE firm tenant
  legal_name: string
  display_name: string
  classification: enum             # saas | services | manufacturing | distribution | healthcare | other
  base_currency: ISO-4217
  fiscal_year_end_month: int       # 1-12
  reporting_timezone: IANA tz
  erp_vendor: enum                 # quickbooks_online | netsuite | sage_intacct | dynamics_bc | csv_upload
  erp_instance_id: string
  onboarded_at: timestamp
  status: enum                     # onboarding | live | paused | offboarded
  deal_partners: [user_id]
  operating_partners: [user_id]
  addback_config_id: uuid          # EBITDA addback configuration
```

`classification` drives which KPIs apply. `base_currency` and `fiscal_year_end_month` are per-company because a US PE firm may own a Canadian company on a different fiscal year. `addback_config_id` is required — PE-adjusted EBITDA is the whole point.

---

## Entity 2 — Period

```
Period
  id: uuid
  company_id: uuid
  period_type: enum                # month | quarter | trailing_3m | trailing_12m | fiscal_year
  start_date: date
  end_date: date
  fiscal_period_label: string      # e.g. "FY2026-Q2" in the company's fiscal calendar
  calendar_period_label: string    # e.g. "2026-03" — always calendar-based
  status: enum                     # open | soft_closed | closed
```

Every company has a different fiscal calendar. Period is the join key that lets the UI show "March 2026" for everyone while the underlying metric is computed on the company's actual fiscal month. `status` matters: alerts on a `closed` period are facts; on `open` they may be timing issues.

---

## Entity 3 — CanonicalAccount + AccountMapping

```
CanonicalAccount
  key: string (PK)                 # e.g. 'revenue_gross', 'cogs_direct_labor', 'opex_sga_rent'
  category: enum                   # revenue | cogs | opex | other_income | other_expense | asset | liability | equity
  normal_balance: enum             # debit | credit
  description: string
```

```
AccountMapping
  id: uuid
  company_id: uuid
  source_account_id: string        # as it appears in the company's ERP
  source_account_name: string
  canonical_account_key: string    # FK to CanonicalAccount
  mapping_confidence: enum         # high | medium | low
  effective_from: date
  effective_to: date | null        # null = currently active
  mapped_by: user_id
  reviewed_by: user_id | null
  created_at: timestamp
```

Company A's `40000 - Product Revenue` and Company B's `4100 - Subscription Income` both map to canonical key `revenue_gross`. The effective date range handles COA re-charters without rewriting history. `mapping_confidence` feeds directly into the Metric `confidence` field.

---

## Entity 4 — Metric

```
Metric
  id: uuid
  company_id: uuid
  metric_key: string               # from canonical KPI list
  period_id: uuid
  value: decimal(20,4)
  currency: ISO-4217
  computation_version: string      # semver; bumped when formula changes
  confidence: enum                 # high | medium | low
  confidence_reason: string        # e.g. "OtherIncome unmapped, estimated from prior period share"
  source_lineage: jsonb            # pointers to CanonicalAccount rows + periods that fed this metric
  computed_at: timestamp
  superseded_by: uuid | null       # if recomputed, links forward; original retained
```

**Immutable with supersession**: when the EBITDA formula changes, old Metric rows are NOT deleted — they are marked `superseded_by` the new ones. Any LP report or email that referenced the old value still resolves correctly. `source_lineage` enables "click a number, see where it came from."

---

## Entity 5 — Alert + AlertRule

```
Alert
  id: uuid
  company_id: uuid
  metric_key: string
  period_id: uuid
  rule_id: uuid
  severity: enum                   # critical | elevated | informational
  triggered_at: timestamp
  metric_value: decimal
  threshold_value: decimal
  rule_snapshot: jsonb             # the rule as it existed when fired
  context: jsonb                   # prior period values, surrounding data
  explanation: string              # one-sentence human-readable reason
  status: enum                     # open | acknowledged | resolved | false_positive | suppressed
  status_changed_at: timestamp
  status_changed_by: user_id | null
  resolution_note: string | null
```

```
AlertRule
  id: uuid
  company_id: uuid | null          # null = firm default; non-null = company override
  metric_key: string
  rule_type: enum                  # absolute_threshold | relative_threshold | directional_sustained | ratio_breach | plan_variance
  parameters: jsonb                # { floor: 0.25 } or { window: 3, direction: 'up', min_delta: 0.02 }
  severity: enum
  active: boolean
  created_by: user_id
  created_at: timestamp
```

`rule_snapshot` on the alert is critical — rules change over time, and an alert that fired in March under an old rule must remain explainable after the rule is edited in May.

---

## Entity 6 — Supporting Entities

```
Firm         — id, name, timezone, slack_workspace_id, sso_config, subscription_status
User         — id, email, name, firm_id, portco_id (one null), role, totp_secret, sso_external_id
DealAssignment — user_id, company_id, role_in_deal, effective_from, effective_to
Subscription — user_id, metric_key|null, company_id|null, channel, severity_threshold, muted_until
NotificationDelivery — id, alert_id, user_id, channel, delivered_at, status, provider_message_id
AuditLog     — id, actor_user_id, action, resource_type, resource_id, firm_id, portco_id, timestamp, ip, metadata
```

---

## Normalization Worked Example

Three portcos reporting Q1 2026 revenue, landing in the same `Metric` table:

**CompanyA (QuickBooks, calendar year)**: GL has `40000 Product Revenue $3,200,000`, `40100 Service Revenue $450,000`, `40900 Revenue Adjustments -$120,000`. All map to `revenue_gross`. Metric `revenue_net` for period `2026-03` = $3,530,000 USD, confidence `high`.

**CompanyB (NetSuite, June fiscal year end)**: Calendar Q1 2026 = their Q3 FY2026. GL has `4000 Subscription Revenue €2,800,000`, `4050 Usage Revenue €310,000`, `4090 Refunds -€95,000`. FX rate from period-end snapshot applies. Metric = $3,280,000 USD equivalent, confidence `high`.

**CompanyC (CSV upload, manufacturing)**: Controller uploads spreadsheet. Parser extracts `Total Sales $5,100,000`, `Less: Returns -$340,000`. Maps to `revenue_gross`. Single-line revenue prevents product/service split → `revenue_mix` metric is null, `revenue_net` is confidence `medium`.

All three render side-by-side in the portfolio heatmap. No downstream code knows any of this heterogeneity existed.

---

## What Is Deliberately NOT in the Data Model

- **Transaction-level storage**: we store canonical mapped balances per period. Transactions fetched on-demand from ERP for drill-down. Rationale: 15 companies × GL transaction volume would create a massive storage and security blast radius for a feature used occasionally.
- **Customer-level detail**: stored only when the ERP exposes it cleanly in v1.
- **Budget/plan as a rich model**: v1 is a single number per metric per period, uploaded quarterly.
