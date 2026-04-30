# FloatYield — Analysis Executive Summary

**Date:** April 30, 2026
**Phase:** 01 — Analysis
**Verdict:** PROCEED — Genuine market gap, clear regulatory path, hard but solvable technical problem

---

## What We Found

FloatYield is a B2B infrastructure platform that enables banks and fintechs to offer interest-bearing payment accounts. The platform manages Treasury reserve assets, calculates and distributes yield, and handles regulatory reporting. The Sponsor Bank model is the regulatory pathway.

---

## The Opportunity

US banks earn **$50–80B annually** in float income on transaction balances. Customers receive 0%. Stablecoins (USDC, USDT, $150B+ combined AUM) prove customers will shift behavior for yield — and earn their issuers ~$6–7B/year in seigniorage. Yet no B2B infrastructure platform exists to let banks and fintechs offer competitive yield on payment accounts at scale.

| Metric                        | Value                                              |
| ----------------------------- | -------------------------------------------------- |
| TAM (total US float income)   | $50–80B/year                                       |
| SAM (B2B platform accessible) | $500M–2B/year                                      |
| SOM (Year 3, base case)       | $4–10M/year                                        |
| Direct competitor             | Stablecoins ($150B AUM)                            |
| B2B infrastructure competitor | None (Unit/Column partial)                         |
| Market timing                 | Optimal — 4.5% Treasury yield makes economics work |

---

## The Regulatory Path

### United States: Sponsor Bank Model

**Recommendation: Sponsor Bank partnership, not direct licensing.**

- Direct state-by-state MTL licensing: $500K–$2M+, 18–36 months for full US coverage — not viable for launch
- Sponsor Bank model: Partner with a community/regional bank (Pathward, Celtic Bank, Blue Ridge Bank, Coastal Community Bank)
- Bank holds deposits, extends FDIC insurance, handles Reg E/CFPB compliance
- FloatYield operates as technology/service provider under a Program Manager Agreement
- Cost: $50K–$200K/year. Timeline: **3–6 months to launch**
- **Critical architectural rule:** FloatYield must NEVER hold customer funds directly. Funds flow through the Sponsor Bank's balance sheet at all times.

### European Union: EMI Partnership (MVP) / Direct EMI License (Long-term)

**MVP path:** Partner with an existing EMI (Electronic Money Institution)

- Timeline: **3–6 months to market**
- Cost: €100K–200K
- Covers all 27 EU member states via passporting immediately

**Long-term path:** Direct EMI license

- Timeline: 12–24 months, €600K–1.2M total, €350K minimum capital
- Covers all EU via passporting once licensed

**Key advantage over US:** One EU license covers all 27 states. US requires 50 separate state licenses for true national coverage.

**Yield legality:** PSD2/EMD2 do NOT prohibit paying interest on e-money accounts. Yield is legally permissible.

---

## The Technical Problem

### The Hardest Problem: Yield Ledger Reconciliation

**The issue:** FloatYield calculates yield as `balance × rate × 1/365` (simple interest). The bank earns actual Treasury yield on a different schedule (actual/actual day-count, market price adjustments). These numbers will never match exactly.

**For a $1B deposit book:** 1bp divergence = $100,000/day — meaningful enough to require resolution.

**Why it's hard:**

1. Requires a reconciliation process that both parties trust
2. Tolerance threshold must be agreed upon commercially
3. Resolution mechanism (who absorbs the difference) is a negotiation
4. Bank's legacy systems may not provide the data FloatYield needs
5. Automation at scale makes it harder, not easier

**MVP solution:** Manual daily reconciliation with tolerance threshold agreed in contract. Automation in Phase 2.

---

## Product Architecture

### Sponsor Bank Money Flow

```
Customer deposits → Sponsor Bank (holds at Fed) → Bank invests in Treasuries
Yield accrues → FloatYield calculates daily yield → Bank distributes to customer
FloatYield takes platform fee → monthly
```

### MVP Features (8–10)

1. Program Manager Agreement with Sponsor Bank
2. API: account creation, balance inquiry, yield balance, transaction history
3. Yield calculation engine (daily accrual, simple interest /365)
4. Yield distribution scheduling (monthly)
5. KYC ownership: bank owns KYC, FloatYield receives attested data
6. Regulatory reporting: IRS 1099-INT, state unclaimed property
7. Reserve reconciliation (manual, daily)
8. Partner dashboard: yield rates, account metrics, fee reporting

### 5 ADRs

1. **Sponsor Bank model** — all customer funds flow through bank balance sheet; FloatYield never holds funds
2. **Treasury custody** — bank holds reserves at Fed; FloatYield receives daily yield statements for reconciliation
3. **Daily yield accrual** — simple interest /365, monthly distribution to customers
4. **KYC ownership** — bank owns KYC; FloatYield receives attested compliance data
5. **REST API** — synchronous for account operations; events for yield calculations

---

## Go-to-Market

### First Partner Profile

- 50K–500K account holders
- Active transaction volume ($500M+/year in payments)
- Existing treasury function that can approve a new yield product
- No existing yield-on-checking capability

**Target:** Mid-tier neobanks, regional commercial banks, payment processors with consumer-facing apps

### Pricing to Partners

- Platform fee: $0.10–$0.25/account/month
- At 100K accounts: $10K–$25K/month ($120K–$300K/year)
- At 1M accounts: $100K–$250K/month ($1.2M–$3M/year)

---

## Key Risks

| Risk                                         | Likelihood | Impact   | Mitigation                                                     |
| -------------------------------------------- | ---------- | -------- | -------------------------------------------------------------- |
| Sponsor Bank terminates partnership          | Medium     | High     | Contractual minimum term; backup bank relationships            |
| Yield reconciliation disputes                | High       | Medium   | Tolerance threshold in contract; manual reconciliation for MVP |
| Interest rate decline                        | High       | Medium   | Diversify to fee-based services                                |
| Stablecoin competition                       | High       | Medium   | FDIC insurance advantage over stablecoins                      |
| MTL classification if funds touch FloatYield | Low        | Critical | Architecture review; no trust accounts                         |

---

## Verdict

**PROCEED.** The market gap is real, the regulatory path is clear (Sponsor Bank model, 3–6 months to MVP), the technical problem is hard but solvable (yield reconciliation requires contract-level tolerance thresholds and manual MVP reconciliation), and the competitive landscape has no pure-play B2B infrastructure winner.

The single most important action before building: **secure the Sponsor Bank partnership.** Everything else depends on it.

---

## Key Files Produced

| File                                                | Author                | Key Contribution                                    |
| --------------------------------------------------- | --------------------- | --------------------------------------------------- |
| `01-analysis/market/market-analysis.md`             | market-analyst        | TAM/SAM/SOM, competitive landscape, go-to-market    |
| `01-analysis/regulatory/us-regulatory-framework.md` | us-regulatory-analyst | Sponsor Bank model, MTL vs. bank charter            |
| `01-analysis/regulatory/eu-regulatory-framework.md` | eu-regulatory-analyst | EMI partnership, MiCA classification, EU vs US      |
| `01-analysis/product/product-requirements.md`       | product-analyst       | Architecture, yield reconciliation, MVP scope, ADRs |

---

_Analysis completed by: us-regulatory-analyst, eu-regulatory-analyst, market-analyst, product-analyst (parallel agents)_
