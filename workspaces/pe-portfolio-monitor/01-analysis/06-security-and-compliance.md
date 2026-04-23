# Security and Compliance — PE Portfolio Monitoring Dashboard

## Framing

This product aggregates the non-public financial operating data of 10-20 private companies per PE firm customer, with real-time ERP pipes into each company's books. A single compromised tenant yields a portfolio-wide M&A intelligence windfall: forward revenue curves, customer concentration, churn cohorts, headcount trajectories, cash runway, and covenant headroom for every company in that firm's fund. Unlike a generic SaaS breach, the exfiltrated data here is directly tradeable — short positions, activist targeting, competitor recruiting, covenant-negotiation leverage. The asymmetry between breach cost and attacker payoff is extreme. Security architecture must reflect that asymmetry, not the norms of a generic B2B SaaS.

---

## 1. Data Sensitivity Classification

| Tier                         | Category                                                                                                          | Examples                                         | Sensitivity                                         |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | --------------------------------------------------- |
| **T0 — Material Non-Public** | GL-level financials, revenue by customer, margin by SKU, headcount costs, cash position, AR aging, covenant calcs | NetSuite GL, QuickBooks P&L, Stripe MRR detail   | MNPI for any portco with public debt or planned IPO |
| **T1 — Sensitive Business**  | Normalized KPIs, anomaly scores, peer benchmarks, operating-partner commentary                                    | Dashboards, alerts, LP report drafts             | Portfolio-level competitive intelligence            |
| **T2 — Credentials**         | OAuth refresh/access tokens, API keys, webhook secrets                                                            | NetSuite TBA, QuickBooks OAuth2, Sage basic-auth | Credential compromise = T0 pipeline                 |
| **T3 — Identity/Authz**      | PE partner accounts, CFO accounts, MFA seeds, sessions, audit logs                                                | SSO, IdP metadata, WebAuthn keys                 | Account takeover = lateral T0 access                |
| **T4 — PII (secondary)**     | Employee names in headcount reports, customer names in revenue concentration                                      | GL memo lines, payroll summaries                 | Triggers GDPR / state privacy obligations           |

**Blast radius**: A single tenant compromise exposes the full portfolio snapshot of 10-20 private companies, cross-time history enabling trend analysis, live tokens continuing to pull fresh ERP data, and LP-facing materials. A platform-level compromise exposes all of these across every PE firm customer.

---

## 2. Access Control Architecture

### Principals and Scope

| Principal             | Scope                                             | Notes            |
| --------------------- | ------------------------------------------------- | ---------------- |
| PE Partner (GP)       | All portcos in the firm                           | 5-20 per firm    |
| Operating Partner     | Assigned portcos only                             | 2-5 portcos each |
| Portfolio Company CFO | Own company only                                  | One per portco   |
| Portco Analyst        | Own company, possibly KPI-restricted              | Variable         |
| LP (read-only)        | Firm-level aggregates only; no company drill-down | 20-200           |
| Platform Operator     | None in normal operation                          | Break-glass only |

### Three-Layer Enforcement (Fail-Closed)

1. **Database layer** — PostgreSQL RLS with `FORCE ROW LEVEL SECURITY` on every tenant-scoped table. Application connects as non-superuser with `BYPASSRLS=false`. Every transaction sets `app.current_tenant`, `app.current_principal`, `app.portco_scope` via `SET LOCAL`. Middleware refuses queries if these aren't set.

2. **Application layer** — Centralized OPA/Cedar policy engine answering `can(principal, action, resource)`. Every decision logged. No handler-level `if user.role ==` logic.

3. **API gateway / edge** — Coarse tenant-membership filtering and per-principal rate-limits. Cannot grant what lower layers deny.

### Portfolio Company CFO Isolation

JWT carries `tenant_id = <pe_firm>`, `portco_scope = [<own_portco_id>]`. Portco-scoped RLS: `portco_id = ANY(current_setting('app.portco_scope')::uuid[])`. PE-firm-scoped tables (benchmarks, GP commentary, anomaly scores) require role in `(gp_partner, op_partner, platform_admin)` — CFO structurally barred.

Benchmark subtlety: CFO's data is used as input to peer benchmarks, but CFO cannot see the aggregate. Materialized views that the CFO role has no grant on; GP-facing benchmark API enforces k-anonymity floor (n>=5).

### Operating Partner Assignment

`principal_portco_access(principal_id, portco_id, granted_at, granted_by, expires_at)` — default 12-month expiry, de-assignment is a hard delete plus session invalidation.

---

## 3. ERP Credential Handling

### Storage

- Never in the application database. Dedicated secrets store (AWS Secrets Manager / HashiCorp Vault) keyed by `(tenant_id, portco_id, integration_type)`.
- Envelope encryption with per-tenant Customer Master Keys (CMKs) in KMS. CMK deletion on offboarding = cryptoshred.
- No long-lived access tokens in memory. Ingestion worker fetches refresh token, exchanges, uses immediately, discards. Access tokens never persisted.
- No credentials in logs, stack traces, or error payloads.

### Rotation

- OAuth refresh tokens: per-provider cadence (QuickBooks rotates on every refresh; NetSuite TBA on 90-day schedule with 30-day overlap).
- Our own service secrets: 90-day automated rotation.
- On suspected compromise: one-click "revoke all credentials for tenant X" flow.

### Off-Boarding a Portfolio Company (Sale/Exit)

1. Revoke OAuth grants on the provider side.
2. Cryptoshred stored credential — delete from secrets store, rotate tenant CMK if portco was last version holder.
3. Archive portco historical data to write-only cold store encrypted under a separate key held only by the GP.
4. Disable portco-scoped principals (CFO, analysts). Sessions invalidated. Accounts archived, not deleted, for audit.
5. Record off-boarding event with timestamp, initiator, hash of archived snapshot.

**Full-tenant off-boarding**: CMK deletion cryptoshreds all tenant data across primary, replicas, and backups.

---

## 4. Compliance Requirements

### SOC 2 Type II — Table Stakes

PE firms will not sign without this. Plan Type I at month 6-9 of operation, Type II covering months 7-12. Controls to bake in day 1: change management, quarterly access reviews, vendor management, incident response SLAs, encryption in transit/at rest, logging/monitoring with retention.

### SEC / FINRA — Registered Investment Advisers

Most target customers are registered under the Investment Advisers Act of 1940:

- **Rule 206(4)-7**: GP must maintain vendor-oversight policies. Provide evidence of MNPI handling.
- **Marketing Rule 206(4)-1**: Do not compute our own IRR/MOIC/performance figures. Display normalized data; let the GP calculate performance.
- **Books and Records Rule 204-2**: 5-year retention.
- **SEC 2023 adviser cybersecurity rule**: 12-hour breach notification SLA to the GP.
- **MNPI on public securities**: portcos with public debt or pending IPOs. Staff walled off from trading those securities; personal trading policy attested quarterly.

### GDPR / UK GDPR

Triggered by any EU-operating portco:

- Legal basis: legitimate interest (portfolio monitoring). Joint-controller agreements with portcos required.
- DPAs with each portco, SCCs for US-to-EU transfers.
- DPIA required (Article 35 — scale/sensitivity).
- Article 17 erasure: off-boarding must support erasure of EU data subjects' PII in GL lines.
- Article 33: 72-hour authority notification on breach.

### US State Privacy Laws

- CCPA/CPRA: portcos with California employees surface CA-resident PII in GL lines. Contractual service-provider language required.
- Map state breach-notification timelines (NY SHIELD, CO, VA, etc.) into the incident runbook.

---

## 5. Tenant Isolation

### Model: Shared DB with Cryptographic Backstop

**Layer 1 — Schema**: Every row carries `tenant_id` and `portco_id`, NOT NULL, FK-constrained. Composite PKs include `tenant_id`.

**Layer 2 — RLS**: `FORCE ROW LEVEL SECURITY` on every tenant-scoped table. Application role is non-superuser, `BYPASSRLS=false`. Middleware refuses queries without tenant context set.

**Layer 3 — Per-Tenant Encryption Keys**: Each tenant has its own CMK in KMS. A storage-layer cross-tenant leak yields ciphertext the wrong CMK cannot decrypt.

**Layer 4 — Compute Isolation**: Risky workloads (PDF parsing, Excel ingestion, LLM narrative, memo extraction) run in per-tenant ephemeral sandboxes (gVisor/Firecracker) with no durable storage and narrow egress allow-list.

**Layer 5 — Caches and Derived Data**:

- Redis keys prefixed with `tenant_id`; clients reject reads where prefix doesn't match.
- Per-tenant search indices (NOT shared index with filter).
- Materialized views and analytics marts inherit and enforce `tenant_id`.
- No T0/T1 data behind a CDN. Short-lived signed URLs for downloadable reports.

### Tenant Isolation Testing

- Fuzz test (nightly + every PR): pick random tenant pairs, attempt every endpoint with A's creds against B's resource IDs. Any 2xx = test failure.
- Chaos test: periodically inject wrong `tenant_id` mid-request and assert failure.

---

## 6. Top 3 Security Risks

### Risk 1: Stolen ERP Credentials Used Directly Against Provider

**Likelihood: 4/5 | Impact: 5/5**

OAuth refresh tokens are bearer credentials — one exfiltrated token = unlimited direct ERP access bypassing our audit logs.

Mitigations: Provider-side IP allow-lists; mutual TLS on outbound; short TTLs and aggressive rotation; ingestion workers in dedicated VPCs with allow-listed egress only.

### Risk 2: Cross-Tenant Data Leak via Authorization Bug

**Likelihood: 3/5 | Impact: 5/5**

OWASP BOLA/IDOR — #1 SaaS vulnerability class. Five principal types, portco-scoped visibility, op-partner assignments — every new endpoint is a chance for a missing `WHERE tenant_id = ?`.

Mitigations: RLS with `FORCE` as enforcement floor; centralized policy engine; automated cross-tenant probe tests in CI; external pen test every 6 months; bug bounty scoped to authorization bypass.

### Risk 3: Insider Threat / Compromised Platform Operator

**Likelihood: 3/5 | Impact: 5/5**

Standing production access = T0 pivot across all tenants. A platform-operator compromise is a platform-level breach.

Mitigations: Zero standing access; JIT break-glass with two-person approval (60 min, every query logged, tenant-visible); no production data export to staging; separation of duties; personal trading policy; managed endpoints with EDR.

---

## Architectural Non-Negotiables (for /todos)

1. PostgreSQL RLS with `FORCE` on every tenant-scoped table + CI cross-tenant fuzz test.
2. Centralized policy engine (OPA or Cedar). No handler-level auth logic.
3. Per-tenant CMKs in KMS; envelope encryption for T0; CMK deletion as cryptoshred mechanism.
4. Dedicated secrets store for ERP credentials, never in app DB; provider-side IP allow-listing on every integration that supports it.
5. Zero standing operator access; JIT break-glass with two-person approval and tenant-visible audit.
6. SOC 2 Type II readiness from day 1; Type I at month 6-9.
7. Per-tenant search indices; tenant-prefixed cache keys.
8. Sandboxed parsing workers (gVisor/Firecracker) for untrusted-input paths.
9. Off-boarding runbook with cryptoshred guarantee for portco sale and tenant exit.
10. Advisers Act posture day 1: MNPI handling, personal trading policy, 12-hour breach-notification SLA.

## Open Questions

- On-prem / private-cloud deployment for $5B+ AUM firms? Changes architecture significantly.
- LPs as direct users, or GP-curated reports only? LP-as-user expands principal model and attack surface.
- Portcos that refuse API integration and send Excel? Untrusted-file ingestion is a distinct risk surface.
- Retention policy after portco sale? PE firm has audit/LP interests; new owner may demand deletion.
