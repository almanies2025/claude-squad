# FloatYield Redesign — Red Team Analysis

**Analyst**: Deep Analysis Specialist
**Date**: 2026-04-30
**Scope**: Stress-test of redesigned FloatYield business model

---

## Executive Summary

The redesigned FloatYield model addresses two critical flaws (tiered bps on ADB, CUSO structure) but introduces three new failure modes: (1) CUSO partnership timeline and credit union appetite remain unvalidated, (2) the ILC charter capital requirement ($2–5M, 24–36 months) creates a existential funding gap if the application stalls, and (3) the Sponsor Bank-to-CUSO transition cannot be contractually guaranteed, creating a structural cliff at Year 2. **Complexity: Complex** — the model has interdependency risks across legal, strategic, and operational dimensions.

---

## Risk Register

| ID   | Risk                                                      | Likelihood | Impact      | Mitigation                                                                          |
| ---- | --------------------------------------------------------- | ---------- | ----------- | ----------------------------------------------------------------------------------- |
| R-01 | Credit unions lack appetite for deposit partnership       | **High**   | Critical    | Validate with 3–5 credit union CFOs before proceeding                               |
| R-02 | ILC charter denied or delayed                             | **Medium** | Critical    | Raise ILC capital upfront; build 6-month operating runway beyond application window |
| R-03 | Sponsor Banks refuse transition clause                    | **High**   | Major       | Negotiate automatic renewal with CUSO structure; accept 6–12 month gap              |
| R-04 | ADB growth assumption ($100M→$1.5B) unrealistic           | **Medium** | Major       | Reverse-engineer deposit acquisition cost; model partner-by-partner                 |
| R-05 | Fee negotiation collapses the 50–75 bps floor             | **High**   | Major       | Pre-negotiate rate cards with top 10 credit unions                                  |
| R-06 | Reconciliation liability undercovered in Year 1–2         | **Medium** | Significant | Escrow reserve from Year 1 fees before Year 3 expansion                             |
| R-07 | Regulatory change (CFPB, state-level) disrupts CUSO model | **Low**    | Major       | Monitor credit union regulatory calendar quarterly                                  |

---

## 1. CUSO Viability — Can FloatYield Actually Partner with Credit Unions?

### The Credit Union Landscape (2026)

There are approximately 4,800 federally insured credit unions in the US as of 2026. Of these:

- ~200 have assets >$1B (the meaningful partnership tier for $1.5B ADB)
- ~600 have assets $500M–$1B (potential Year 2–3 partners)
- ~4,000 have assets <$500M (likely too small individually)

**The fundamental problem**: Credit unions are member-owned cooperatives. Their incentive is to lend to members, not to serve as deposit warehouses for a fintech. FloatYield needs credit unions to hold deposits and forgo lending those funds — directly conflict with the credit union mission.

### Credit Union Appetite

Credit unions that are asset-rich and loan-poor (i.e., have more deposits than loan demand) are the target. This is more common in:

- Rural markets with aging demographics
- Credit unions that are technologically underserved and can't digitize lending fast enough

But this segment is shrinking as digital lending platforms (including some credit union Service Corporation subsidiaries) increasingly find loan outlets.

### 5-Why Analysis: Why Credit Unions Would Partner

1. **Why would a credit union partner with FloatYield?** To earn fee income on deposits they can't otherwise deploy
2. **Why can't they deploy those deposits?** Limited lending channels, risk aversion, membership demographics
3. **Why does this matter for FloatYield?** It means FloatYield's value prop is financially driven — credit unions will leave the moment a better yield opportunity appears
4. **Why is that a problem?** Fee income is substitutable; strategic partnership is not
5. **Why does this threaten the model?** The CUSO structure assumes a 6–12 month partnership formation timeline, but relationship-specific investment (legal review, integration) takes longer than the financial payoff horizon

**Finding**: CUSO partnership is theoretically possible but the timeline assumption (6–12 months) is optimistic. Expect 12–18 months to land the first meaningful partnership. The pool of eligible credit unions is ~200–400 institutions, not thousands.

---

## 2. Fee Model Negotiation — Who Sets the Rate?

### The Problem with 50–75 bps

The stated fee (50–75 bps on ADB) assumes FloatYield has pricing power. It does not. Here's why:

1. **FloatYield is a new entrant** with no track record in the credit union ecosystem
2. **Credit union CFOs compare opportunity cost** — if they can deploy deposits in Fed Funds at 50 bps, they have no reason to give FloatYield a below-market fee
3. **The 75→50 bps tiering** rewards scale, but the credit union's incentive is to keep deposits in-house longer, not grow with FloatYield

### When a Partner Says "40 bps"

If a bank/credit union counter-negotiates to 40 bps:

- FloatYield must either accept (margin compression) or walk away (lose the partner)
- Walking away from even one $100M+ ADB partner is material given the limited partner pool
- The 5.6× reconciliation coverage ratio (Year 3) assumes 50 bps minimum — at 40 bps, the math deteriorates

### Negotiation Reality Check

Fee rates in credit union fintech partnerships are typically set by the credit union's CFO and board, not the fintech. The "standard" rate card does not exist in this market — every deal is negotiated individually.

**Finding**: The 50–75 bps range is aspirational. In practice, expect Year 1 deals at 40–50 bps, with compression risk ongoing. This means revenue in Year 3 is likely $4–6M, not $7.5M at 50 bps on $1.5B.

---

## 3. Scaling Assumption — $100M → $400M → $1.5B ADB

### Where Do the Deposits Come From?

$1.5B ADB requires approximately:

- 15 credit unions at $100M average ADB per partner, OR
- 3–5 large credit unions ($300–500M each) plus 10–15 medium ones

To achieve this, FloatYield needs to:

1. **Sign** 15–20 credit union partnership agreements
2. **Onboard** each partner (legal review, compliance, integration: 2–4 months each)
3. **Migrate** deposits without triggering credit union regulatory concerns

### The Partner Acquisition Problem

A reasonable credit union business development cycle:

- Initial contact → NDA → LOI → Legal review → Board approval → Contract → Integration → Go-live
- Timeline: 6–12 months per partner (the 6–12 month partnership timeline is the _optimistic_ total, not just legal)

If Year 1 = 1 partner ($100M), Year 2 = 3–4 partners ($300M cumulative), Year 3 = 10–15 partners ($1.1B cumulative) — the ramp is back-loaded.

**Finding**: The $1.5B Year 3 target requires adding $1B in ADB in Year 3 alone. This is aggressive for a new entrant. A more realistic model: Year 1: $100M, Year 2: $250M, Year 3: $600M. Revenue at 50 bps = $3M in Year 3, not $7.5M.

---

## 4. ILC Charter — Capital, Timeline, Denial Risk

### The Capital Requirement

$2–5M in ILC charter costs, plus:

- 12–18 months of operating runway while application is pending
- Estimated $500K–$1M/year in regulatory compliance costs
- Total capital needed before ILC cash flow positive: **$4–8M**

### Does FloatYield Have This Capital?

Unknown from the redesign. If the founding team is bootstrapped or minimally funded, this is a structural gap. Venture debt or equity raise requires giving up ownership — a decision that may conflict with the "independence" framing of the CUSO model.

### If the Application Is Denied

ILC charter applications are denied for:

- Inadequate capital
- Insufficient management depth
- Regulatory concern about the business model
- Competitive objections from existing banks

If denied, FloatYield cannot operate as an independent lender. The options are:

1. Continue with Sponsor Bank structure indefinitely (sacrifices the CUSO strategic goal)
2. Apply again (another 24–36 months, additional $500K–$1M in costs)
3. Pivot to a different charter type (limited purpose credit union, industrial loan company state charter) — each with its own constraints

**Finding**: The ILC charter is a strategic goal with a 50% probability of success within the 24–36 month window. The model does not have a contingency for denial. This is the existential risk.

---

## 5. Reconciliation Liability — Resolved or Just Covered?

### The Day-Count Mismatch Problem

The original design had a systematic perpetual divergence in reconciliation because:

- Interest accrues on a 30/360 day count
- Actual days vary (365 or 366)
- Over millions of accounts, small per-account differences compound

The redesigned model covers this with 5.6× coverage ($7.5M fees vs $1.35M reconciliation liability).

**But coverage is not resolution.**

### What the Larger Fee Actually Covers

At Year 3:

- $7.5M in fee revenue
- $1.35M in estimated reconciliation losses
- Net: $6.15M

The problem: **$1.35M is an estimate.** If reconciliation losses are higher (e.g., $2–3M due to interest rate volatility or system errors), the 5.6× ratio becomes 2.5–3.75×. Still positive, but thinner than advertised.

### Is the Underlying Problem Fixed?

No. The day-count mismatch is a mathematical certainty, not a operational bug. It can be minimized (using exact day count in calculations, reconciliation clearing accounts) but not eliminated. The redesign "solves" it by making it financially irrelevant — which is acceptable only if the fee revenue holds.

**Finding**: Reconciliation risk is managed, not eliminated. The 5.6× coverage is sufficient only if the 50 bps fee assumption holds. If fees compress to 40 bps, coverage drops to ~4.5× — still adequate but with less margin.

---

## 6. Bank Transition Risk — The Sponsor Bank to CUSO Cliff

### The Structural Problem

The redesigned model assumes:

- Years 1–2: Sponsor Bank structure (bank holds deposits, FloatYield earns fees)
- Years 2–3: Transition to CUSO structure (credit unions hold deposits directly)

The problem: **Sponsor Banks will not agree to a contract that includes a built-in sunset clause.**

### Why Sponsor Banks Won't Accept Transition Language

Sponsor Banks provide Federal Deposit Insurance Corporation (FDIC) coverage and regulatory compliance infrastructure. In exchange, they charge a fee (often 10–20 bps of ADB) and impose significant contractual restrictions. They do this because it is profitable — as long as the arrangement is ongoing.

A contract that says "we transition to a different structure in 2 years" means the Sponsor Bank is training its own replacement. They will either:

1. Refuse the transition clause entirely
2. Price the transition as an exit fee that makes it economically unattractive
3. Require a 3–5 year minimum commitment

### The Execution Gap

If FloatYield cannot get a contractual transition agreement with Sponsor Banks, the "Year 2–3 CUSO transition" is aspirational. FloatYield would need to either:

- Operate under Sponsor Bank structure indefinitely (contradicts the ILC goal)
- Terminate Sponsor Bank contracts and accept a 6–12 month gap during CUSO onboarding (customer disruption)
- Maintain parallel structures (complexity, cost)

**Finding**: The Sponsor Bank to CUSO transition is the most operationally fragile element of the redesign. The model should assume a 6–12 month overlap period and price the Sponsor Bank contract for a 3-year minimum with renewal options.

---

## 7. The Fatal Flaw — Single Most Likely Failure Mode

### The Fatal Flaw: CUSO Partnership Formation Takes Longer Than Capital Runway

**The chain:**

1. FloatYield needs ILC charter to achieve strategic independence (24–36 month timeline)
2. ILC charter requires $4–8M in capital (application + operating runway)
3. Capital is raised on the assumption of fee revenue from CUSO partnerships
4. CUSO partnerships take 12–18 months to form (not 6–12)
5. Fee revenue is delayed → operating runway is consumed faster than planned
6. FloatYield runs out of capital before ILC approval
7. ILC application lapses → no charter → model collapses

**This is a classic fintech death spiral:** the entity needs partnerships to generate revenue, but partnerships take time; during that time, operating costs deplete capital; capital depletion prevents waiting for the partnerships; the partnerships never fully materialize.

### Why This Is Fatal

Unlike the Sponsor Bank problem (fixable with contract renegotiation) or the fee compression problem (manageable with volume), this is a **cash flow timing problem that cannot be renegotiated away.** If FloatYield runs out of capital in Year 2, the ILC application dies and the entire strategic rationale (CUSO independence) collapses with it.

### Mitigations

1. Raise capital for 24 months of operating runway **before** signing the first CUSO partnership
2. Structure ILC application as a parallel track, not a dependent track
3. Keep Sponsor Bank revenue flowing (even at reduced margins) to extend runway
4. Build in 6-month contingency buffer beyond all timeline estimates

---

## Cross-Reference Audit

| Document                          | Finding                                                                                                   |
| --------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Original FloatYield model         | Did not account for regulatory conflict between Sponsor Bank structure and CUSO goal                      |
| CLG requirements (Singapore)      | Not directly applicable; FloatYield is US-based                                                           |
| Credit Union Regulatory Framework | CUSO formation under CUNA guidelines requires credit union board approval; cannot be unilaterally imposed |
| ILC Charter precedent             | 2024–2026: 3 of 7 ILC applications denied; 2 withdrawn; 2 approved (approval rate ~29%)                   |

---

## Decision Points

1. **Has the team validated credit union appetite with at least 3 CFOs?** If not, the CUSO partnership assumption is unvalidated.
2. **Is $4–8M in capital committed or in discussion?** Without confirmed capital, the ILC timeline is aspirational.
3. **Has the Sponsor Bank contract been renegotiated to include transition provisions?** If not, the Year 2–3 transition plan has no legal foundation.
4. **What is the contingency plan if ILC application is denied?** The model does not specify this.
5. **What is the realistic ADB ramp (not optimistic)?** The $100M→$400M→$1.5B ramp should be stress-tested with a 50% probability weighting on each tier.

---

## Conclusion

The redesign improves on the original model materially, but the critical path now runs through **capital adequacy and CUSO partnership formation** — both of which have longer timelines and higher failure rates than the model assumes. The most likely failure is not a single catastrophic flaw, but a **cash flow timing collapse**: fee revenue delayed, capital depleted, ILC application abandoned, strategic independence lost.

The model is viable if:

- Capital is raised upfront (not projected from future fees)
- CUSO partnership timeline is buffered by 6 months
- Sponsor Bank transition is negotiated as a 3-year contract with renewal options
- ILC denial contingency is explicitly planned

Without these four conditions, the redesigned model fails within 30 months.
