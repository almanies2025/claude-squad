# MVP Scope — PE Portfolio Monitoring Dashboard

## The Test for "In v1"

A feature is in v1 only if its removal would cause a prospective buyer to say "then I'll keep using Excel." Everything else is v2.

## What a First Paying Customer Gets

A PE firm signs an annual contract. Within 30 days, they have:

1. **3 portfolio companies live** — connected to their ERP (QuickBooks, NetSuite, or Sage Intacct) or uploading monthly CSVs, with validated canonical mappings and a dashboard matching the portco's own ledger
2. **A portfolio heatmap** — 12 KPIs × 3 companies, refreshed daily, partners can see every portco's most recent month at a glance
3. **Rule-based alerts firing on real data** — seeded with sensible defaults at onboarding, tuned in the first 30 days
4. **Email and Slack notifications** — subscribed by metric, one-click unsubscribe
5. **Quarterly LP export** — Excel file covering portfolio's standardized KPIs, refreshed on demand, version-stamped
6. **SSO login** — Okta or Azure AD wired up on day one

That is the whole product.

---

## In v1 (Must-Have)

| Area                  | What's included                                                                                   |
| --------------------- | ------------------------------------------------------------------------------------------------- |
| **ERP connectors**    | QuickBooks Online, NetSuite, Sage Intacct, CSV upload                                             |
| **Data model**        | Canonical mapping config + confidence tracking + versioned computation                            |
| **KPI engine**        | 18 canonical metrics with EBITDA addback config                                                   |
| **Anomaly detection** | 5 rule types (absolute, relative, directional, ratio, plan variance) with per-company calibration |
| **Dashboard**         | Portfolio heatmap + per-company drill-in with 13-month sparklines                                 |
| **CFO view**          | Own-company-only dashboard, integration management, correction workflow                           |
| **Notifications**     | Email + Slack + in-app; daily digest for elevated alerts                                          |
| **Auth**              | Email + TOTP 2FA + SSO (SAML/OIDC) for PE firm users                                              |
| **Access control**    | RBAC with DB-layer row-level security                                                             |
| **LP reporting v1**   | Portfolio summary table, company one-pagers (PDF), XLSX export                                    |
| **Audit log**         | Immutable, queryable by firm admin                                                                |

---

## Explicitly Out of v1

| Feature                              | Reason                                                      |
| ------------------------------------ | ----------------------------------------------------------- |
| ML-based anomaly detection           | Data volume insufficient; explainability fails; see ADR-001 |
| Dynamics 365 BC connector            | Nice-to-have; not a dealbreaker at launch                   |
| SAP connector                        | Address via CSV upload                                      |
| Predictive forecasting               | Science project; v2                                         |
| Covenant tracking                    | Complex per-deal documentation; v2                          |
| Valuation / fair-value marks         | Fund admin territory, not this product                      |
| Carry and waterfall calculations     | Fund admin territory                                        |
| Fund-level reporting                 | Not this product                                            |
| Operating Partner purpose-built view | Uses Partner view + raw exports until v2                    |
| 13-week cash forecast                | v2                                                          |
| Deal sourcing / CRM                  | Not this product                                            |
| Natural-language query               | v2 at earliest                                              |
| Mobile app                           | Responsive web only                                         |
| ILPA template compliance             | Firm-specific; v2                                           |
| Custom report builder                | v2                                                          |
| LLM-generated commentary             | Hallucination risk in LP reports is unacceptable            |
| SMS / push notifications             | Partners don't want physical interruptions                  |
| Portfolio company SSO                | v1 portco users use password + 2FA                          |
| White-label / reseller               | Not a v1 business model                                     |
| Transaction-level storage            | Fetch on-demand from ERP for drill-down                     |

---

## The Dealbreaker List

Missing any of these kills the deal:

1. **QuickBooks, NetSuite, Sage Intacct connectors** — missing any one cuts addressable market by 15–40%
2. **EBITDA accuracy within 1% of portco's own ledger** — first board meeting catches a wrong number and the deal dies
3. **Per-company EBITDA addback configuration** — PE-adjusted EBITDA is the whole point; without addbacks the number is useless
4. **SSO for PE firm users** — PE firm IT will not accept password-only auth
5. **Tenant isolation** (cross-tenant leak = company-ending event)
6. **Alert false-positive control** — partners unsubscribe after 3 bad alerts; without per-company calibration the alerts become noise
7. **Portfolio heatmap loads in <2s** — partners open this between meetings; slow load = they stop opening it

---

## The "Science Project" Test

Each v1 feature must answer yes to all three:

1. Can we build it deterministically? (No "if the model works.")
2. Can the buyer evaluate it without a data science background?
3. Does it work correctly on day one for a company we just onboarded?

ML anomaly detection fails all three. Rule-based thresholds pass all three. That is why rules ship in v1.

---

## Pricing Anchor (for context)

- Target ACV: $75,000 per firm for up to 15 companies; $4,000 per additional company
- Comparable spend: a PE ops team member costs $180,000 all-in; this replaces ~40% of their time — paying $75K to free up 40% of one person is an easy board approval
- Annual contract, paid upfront; multi-year discount offered
