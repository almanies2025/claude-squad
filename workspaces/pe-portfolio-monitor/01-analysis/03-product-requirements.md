# Product Requirements — PE Portfolio Monitoring Dashboard

## Guiding Principles

1. **The buyer is the PE deal partner, not the portfolio CFO.** Every design decision resolves in favor of what the PE partner sees.
2. **Time-to-first-signal is the product.** The value is "I knew about margin compression six weeks before the board pack." Everything else is secondary.
3. **Heterogeneity is permanent.** 15 portfolio companies on 6 different ERPs is steady state, not a migration problem.
4. **Wrong answers destroy the product.** A false "EBITDA down 40%" alert that escalates to a GP is worse than no product.

---

## Functional Area 1 — Data Ingestion Layer

**What it does**: Pulls GL, AR/AP, and operational data from portfolio company ERP/accounting systems on a daily cadence into a raw staging area, then normalizes into the canonical schema.

**Who uses it**: PE firm's internal ops/analytics team (configures connectors, monitors health). Portfolio company CFO/controller (grants OAuth consent at onboarding, then invisible).

**Data required**: Per company: ERP vendor, instance URL, OAuth tokens, entity IDs, chart of accounts, fiscal calendar. Per pull: trial balance, GL detail, AR aging, AP aging, revenue by customer (where available), headcount (where available).

**Output**: Raw JSON/Parquet in object storage partitioned by company/date/entity; ingestion status events; per-company ingestion health score.

**Supported ERPs for v1**: QuickBooks Online, NetSuite, Sage Intacct, CSV/XLSX upload fallback. Dynamics 365 BC and Xero in v1.5.

**Hard requirements**:

- Daily pulls, idempotent — same-day re-run produces the same canonical output
- Incremental extraction where supported; full refresh weekly as reconciliation
- Tenant isolation at storage layer — portco A's raw data never in the same prefix as portco B
- Unmappable GL accounts flagged `unmapped`, never silently zero

---

## Functional Area 2 — KPI Computation Engine

**What it does**: Transforms normalized GL/operational data into 18 standardized KPIs computed identically across every portco regardless of ERP or chart of accounts.

**Who uses it**: Consumed by dashboard, alerting, LP reporting. Configured by PE firm's ops team (which KPIs apply to which companies).

**Canonical v1 KPI set (18 metrics)**:

Financial (all companies): Revenue (net), Gross profit, Gross margin %, EBITDA (PE-adjusted with per-company addbacks), EBITDA margin %, Operating cash flow, Working capital, DSO, DPO, DIO (null for services), Cash balance, Net debt.

Growth: Revenue YoY %, Revenue MoM %.

SaaS-only: ARR, Net revenue retention, Logo churn %.

Headcount (where HRIS/payroll available): Total FTE.

**Hard requirements**:

- Every metric carries `computation_version` — formula changes trigger history recomputation; old values retained
- Every metric carries `confidence`: `high` / `medium` / `low` with human-readable reason
- Rolling 13-month window minimum; quarterly and TTM views derived from monthly
- EBITDA reconciles to within 1% of portco's own ledger — this is the product's credibility floor

---

## Functional Area 3 — Anomaly Detection

**What it does**: Detects KPI deviations that warrant human attention and converts them into alerts.

**Approach for v1**: Rule-based thresholds with per-company calibration. ML-based detection deferred to v2. See ADR-001.

**Rule categories (v1)**:

1. **Absolute threshold** — "Gross margin below 25% for any month"
2. **Relative threshold** — "EBITDA falls >15% vs trailing 3-month average"
3. **Directional sustained** — "DSO rises for 3 consecutive months"
4. **Ratio breach** — "Working capital / revenue > 1.5x historical median"
5. **Plan variance** — "Actual revenue < 90% of plan" (requires plan upload)

**Hard requirements**:

- Every alert explainable in one sentence — no black-box scores
- Deduplication: same breach fires once, stays open until resolved or recovers for 2 consecutive periods
- Alert lifecycle: `open` → `acknowledged` → `resolved` / `false_positive` / `suppressed`
- False-positive marking feeds threshold-tuning ops dashboard
- Suppression for known events (system migration, one-time restatement) is first-class

---

## Functional Area 4 — Alerting and Notification

**Channels (v1)**: Email (non-negotiable), Slack (DM for critical, channel for elevated), in-app. SMS/push explicitly out of v1.

**Delivery rules**:

- Critical: immediate email + Slack DM, no batching
- Elevated: once-daily digest at 7:30am local time
- Informational: in-app only

**Hard requirements**:

- No alert delivered more than once via the same channel for the same incident
- Delivery failures surface to firm admin within 1 hour
- One-click unsubscribe at per-metric-per-company granularity

---

## Functional Area 5 — Dashboard and Visualization

**5a — PE Partner view** (primary buyer surface):

- Portfolio heatmap: rows = companies, columns = KPIs, cell color encodes deviation from expectation
- Per-company page: 6 highest-priority KPIs as 13-month sparklines, open alerts, one-line "what changed this month"
- Not here: transaction-level detail, GL balances, reconciliation tools

**5b — Operating Partner view (v1)**:

- Uses PE Partner view + raw metric time series (exportable to CSV/Excel)
- Purpose-built Operating Partner deep-dive view is v2

**5c — Portfolio Company CFO view**:

- Own company only (strict tenant isolation)
- Same KPIs the PE firm sees for them + integration health + "request a correction" workflow
- Cannot see: any other portco, portfolio aggregates, other companies' alerts, PE firm internal data

**Hard requirements across views**:

- Every number traceable to source in one click: metric → contributing GL accounts → underlying transactions
- Currency and fiscal calendar honored per company
- Portfolio heatmap load time: <2s p95 on 25-company portfolio with 13 months of data

---

## Functional Area 6 — LP Reporting Automation

**v1 scope**:

1. Portfolio summary table — one row per company with revenue, EBITDA, growth %, PE firm commentary (free text)
2. Company one-pagers — auto-generated PDF per company with 13-month charts + PE-firm-authored commentary
3. XLSX export of full portfolio metrics set

**Explicitly out of v1**: ILPA template compliance, waterfall/carry calculations, custom report builder, LLM-generated commentary.

**Hard requirement**: No LLM-generated commentary in v1 — hallucinated fact in an LP report is a company-ending event. Humans write narrative; product generates data.

---

## Functional Area 7 — User Management and Permissions

**Role model**:

| Role            | Scope                                            |
| --------------- | ------------------------------------------------ |
| `pe_admin`      | Full firm access + user management               |
| `pe_partner`    | Assigned companies, configurable                 |
| `pe_operator`   | Same as partner, typically fewer companies       |
| `pe_ops`        | Full read + integration management               |
| `portco_admin`  | Own company only — integration + user management |
| `portco_viewer` | Own company only, read-only                      |

**Authentication**: Email + password + TOTP 2FA minimum. SSO (SAML/OIDC) for PE firm users — **must-have v1**. PE firms run Okta/Azure AD and will not accept password-only.

**Hard requirements**:

- Tenant isolation enforced at DB query layer (RLS), not application layer alone
- Every cross-tenant read and portco-side read logged in immutable audit log
- ERP OAuth tokens refreshed automatically; expiry surfaced 14 days before breaking ingestion

---

## Cross-Cutting Non-Functional Requirements

| Requirement                                  | Target                            |
| -------------------------------------------- | --------------------------------- |
| Portfolio heatmap load time                  | <2s p95 (25-company portfolio)    |
| Single-company dashboard load                | <1.5s p95                         |
| Ingestion cycle completion                   | <4 hours                          |
| Alert delivery (data arrival → notification) | <30 minutes p95                   |
| EBITDA accuracy vs source ledger             | Within 1%                         |
| Alert false-positive rate                    | <10% within 90 days of onboarding |
| Uptime (US business hours)                   | 99.5%                             |
| RTO / RPO                                    | 4h / 1h                           |

## Success Criteria (First 90 Days in Production)

- 3 paying PE firms with ≥10 portcos each live
- <1% of alerts reported as false-positive after 60 days of tuning per company
- Canonical EBITDA reconciles to within 1% of source on every company
- At least one documented instance per firm of an alert catching a real issue before the next board pack
- SSO live for all paying firms
- Zero cross-tenant data leakage incidents
