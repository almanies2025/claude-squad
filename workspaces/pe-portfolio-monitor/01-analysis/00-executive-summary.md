# Executive Summary — PE Portfolio Monitoring Dashboard

**Date**: 2026-04-20
**Verdict**: PROCEED — real gap, defensible wedge, manageable risks, bounded TAM

---

## Bottom Line

US mid-market PE firms ($500M–$5B AUM) owning 10–20 portfolio companies have no good solution for monitoring operational health between quarterly board meetings. The market has incumbents at the top (iLEVEL, Allvue — expensive, templated, finance-team tools) and lightweight survey tools at the bottom (Visible.vc — VC-native, request-based). The gap is a **live-ERP-connected, anomaly-detecting, operating-partner-first product at a mid-market price point**. That gap is real and currently unserved.

The risks are also real: portco-CFO onboarding friction can kill deployments, incumbent AI feature additions can erode the wedge within 12–18 months, and the addressable market is bounded (~150–250 serviceable firms in the ICP window). None of these are fatal if addressed proactively.

---

## The Gap and Why It Exists

| Layer                 | Current Solutions        | What They Miss                                                               |
| --------------------- | ------------------------ | ---------------------------------------------------------------------------- |
| Large-cap PE          | iLEVEL ($100K–$500K ACV) | Request-based, not live ERP; months to implement; finance team only          |
| Upper mid-market      | Allvue, Dynamo           | Templated data collection, threshold-only anomalies, no operating-partner UX |
| Lower mid-market / VC | Visible.vc, Carta        | Survey/request-based, VC KPI taxonomy, no EBITDA/covenant focus              |
| DIY                   | Power BI + Excel         | Works until it doesn't; one technical OP departure kills it                  |

The gap is not "no one has thought of this." It's "the existing products were built for fund accountants and LP reporting, not for operating partners trying to catch problems early."

---

## Product in One Sentence

Connect to every portfolio company's ERP, normalize KPIs across the entire portfolio, and alert the operating partner when a company's margin, DSO, or working capital is trending wrong — weeks before the board pack.

---

## Revenue Model

**Target ACV: $75K–$120K per PE firm**

Structure: $30K platform base + $3K–$5K per portco connector + $2K per additional user seat.

- **Gross margin**: 70–80% (ERP maintenance overhead is real)
- **Net revenue retention target**: 110%+ (portfolio growth drives connector expansion)
- **Sales cycle**: 4–7 months; paid pilots ($15K–$25K) are standard

---

## Competitive Position

| Dimension              | Proposed Product        | Nearest Competitor                          |
| ---------------------- | ----------------------- | ------------------------------------------- |
| ERP connectivity       | Live daily pull         | Request-based / Excel template              |
| Anomaly detection      | Multi-signal compound   | Single-metric threshold                     |
| Operating partner UX   | Primary user            | Afterthought                                |
| Mid-market price point | $75K–$120K ACV          | $100K–$500K (iLEVEL) or $10K–$50K (Visible) |
| Time to first signal   | Same week as onboarding | Quarterly                                   |

**Most dangerous competitor**: 73 Strings (AI-driven, well-funded — **verify 2026 product scope**). **True competition**: the firm's internal Power BI build and Excel + email status quo.

---

## Top 3 Failure Risks

1. **Portco-CFO veto** (50–65% likelihood): CFOs who don't work for the PE firm can slow-walk ERP access for months. Mitigation: portco-facing value prop + pre-negotiated data-use agreement + 45-day onboarding guarantee.

2. **Incumbent AI catch-up** (40–55%): Allvue/iLEVEL shipping ML anomaly detection in 2026–2027 reduces the wedge. Mitigation: ship fast (6-month window), integrate _with_ fund accounting incumbents rather than competing on LP reporting.

3. **TAM smaller than modeled** (40–50%): Serviceable ICP is ~150–250 firms, not 500+. Mitigation: validate with data-driven firm count before scaling hiring; build for 125%+ NRR; plan adjacent-segment expansion.

---

## Key Product Decisions

| Decision                | Choice                                            | Rationale                                                                                                                            |
| ----------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Anomaly detection v1    | Rule-based thresholds                             | Data volume (13–36 obs/metric/company) too small for stable ML; explainability required; zero-data onboarding required. See ADR-001. |
| ERP v1 scope            | QuickBooks Online + NetSuite + Sage Intacct + CSV | Covers ~65–70% of mid-market portcos                                                                                                 |
| LP reporting commentary | Human-authored only                               | LLM hallucination in an LP report is company-ending                                                                                  |
| Operating partner view  | Uses PE Partner view + raw export in v1           | Purpose-built OP view is v2                                                                                                          |
| Tenant isolation        | DB-layer RLS + per-tenant CMK encryption          | App-layer-only isolation is insufficient given data sensitivity                                                                      |

---

## MVP Scope

First paying customer gets within 30 days:

- 3 portcos connected (ERP or CSV)
- Portfolio heatmap with 12 KPIs, refreshed daily
- Rule-based alerts via email + Slack
- Quarterly LP export (Excel + per-company PDF)
- SSO for PE firm users

Everything else is v2. Full scope in `05-mvp-scope.md`.

---

## Key Metrics at a Glance

| Metric                          | Value                                          |
| ------------------------------- | ---------------------------------------------- |
| Target ICP                      | US mid-market PE, $500M–$5B AUM, 10–20 portcos |
| Serviceable ICP (active window) | ~150–250 firms                                 |
| Target ACV                      | $75K–$120K                                     |
| Sales cycle                     | 4–7 months                                     |
| Gross margin                    | 70–80%                                         |
| CAC                             | $40K–$60K per customer                         |
| Y1 ARR target                   | $500K–$700K (8–12 customers)                   |
| Y3 ARR target                   | $8M–$12M (80–120 customers)                    |
| ERP v1 coverage                 | ~65–70% of mid-market portcos                  |
| EBITDA accuracy requirement     | Within 1% of source ledger                     |
| Alert false-positive target     | <10% within 90 days of onboarding              |
