---
type: DECISION
date: 2026-05-01
created_at: 2026-05-01T07:00:00Z
author: co-authored
session_id: current
session_turn: 1
project: yield-payment-infrastructure
topic: Capital sequencing — ILC charter, CUSO, and Sponsor Bank paths
phase: analyze
tags: [capital, ilc-charter, cuso, sponsor-bank, business-model, strategic]
---

## The Problem

FloatYield faces a cash flow timing collapse risk:

- **ILC charter** (strategic independence): 18-36 months, requires $4-8M total capital
- **Sponsor Bank partnership** (near-term revenue): 9-18 months post-Synapse
- **Year 1 operating runway**: ~12 months
- **Gap**: Revenue arrives after 9-18 months; ILC approval takes 18-36 months; capital depletes before either materializes

This is the **fintech death spiral**: partnerships needed for revenue → partnerships take 12-18 months → revenue delayed → capital depleted during delay → cannot sustain ILC application → ILC lapses → strategic independence lost.

---

## The Three Paths

### Path A: Sponsor Bank Partnership (Required to Exist)

- **Capital**: $50K-$200K/yr in bank fees; no upfront raise
- **Timeline**: 9-18 months (post-Synapse reality; was 3-6 months pre-Synapse)
- **Revenue**: Platform fees once live
- **Structural problem**: Bank owns FDIC exposure; FloatYield captures upside — conflict at scale ($500M+ deposits)
- **ILC relevance**: Must be running to generate fee revenue during ILC runway

### Path B: CUSO Partnership (Parallel Track)

- **Capital**: ~$500K legal and setup costs
- **Timeline**: 12-18 months (stated 6-12; realistic is longer per GAP-002)
- **Mechanism**: FloatYield partners with credit unions as deposit-taking counterparty; NCUA-insured
- **Economics**: Credit unions earn full interest spread; FloatYield earns bps platform fee on ADB
- **ILC relevance**: If successful, eliminates Sponsor Bank dependency. Must be running alongside ILC application.

### Path C: ILC Charter (Long-Term Strategic Goal)

- **Capital**: $2-5M application + 12-18 months operating runway = **$4-8M total**
- **Timeline**: 18-36 months to charter approval
- **Mechanism**: FloatYield obtains own depository institution charter (available in UT, SD, NV)
- **Denial risk**: 2024-2026 data — 3 of 7 denied, 2 withdrawn, 2 approved (~29% approval rate)
- **ILC relevance**: Eliminates Sponsor Bank dependency entirely; strategic independence

---

## The Fatal Flaw Chain

```
1. FloatYield needs ILC charter for strategic independence
2. ILC requires $4-8M capital (application + operating runway)
3. Capital is raised assuming CUSO partnership fee revenue arrives in 6-12 months
4. CUSO partnership actually takes 12-18 months (per GAP-002 post-Synapse reality)
5. Fee revenue delayed by 6-12 months beyond plan
6. Operating runway consumed faster than planned
7. FloatYield runs out of capital before ILC approval
8. ILC application lapses or is abandoned
9. No charter → no strategic independence → Sponsor Bank dependency permanent
```

**Source**: `04-validate/redesign-red-team.md` §7 — confirmed by red team.

---

## The Three Sequencing Options

### Option 1: Sponsor Bank First, ILC Later (Sequential)

1. Secure Sponsor Bank partnership (9-18 months, $50-200K/yr)
2. Generate fee revenue for 12-24 months
3. Raise $4-8M ILC capital once revenue trajectory is established
4. File ILC application

**Risk**: Revenue may not be sufficient to raise IC capital at step 3; ILC window closes.

### Option 2: Raise ILC Capital Upfront, Run Parallel Tracks

1. Raise $4-8M ILC capital first (dilutive)
2. File ILC application
3. Simultaneously pursue CUSO partnerships
4. Operate Sponsor Bank in parallel for fee revenue

**Risk**: ILC denial with no fallback use of capital; 29% denial rate means ~70% chance of capital wasted on failed application.

### Option 3: CUSO-First, ILC as Contingency

1. Pursue CUSO partnerships aggressively (12-18 months)
2. Use CUSO fee revenue to fund ILC application over time
3. File ILC when CUSO revenue proves the model

**Risk**: If CUSO appetite is lower than expected, ILC timeline slips indefinitely.

---

## ILC Capital Adequacy Question

Per `04-validate/redesign-red-team.md`:

> "The ILC charter is a strategic goal with a 50% probability of success within the 24-36 month window. The model does not have a contingency for denial."

**Key questions**:

1. Is the $4-8M capital raise contingent on ILC approval or unconditional?
2. What is the fallback use of capital if ILC is denied at month 18?
3. Can the ILC application be paused (not abandoned) if capital runs low, then resumed?

---

## Decision Made: Option 2 — Raise ILC Capital Upfront, Run Parallel Tracks

**Selected path:**

1. Raise $2M seed round (per pitch deck "The Ask") — covers ILC application + 12-month operating runway
2. File ILC application immediately — start the 18-36 month regulatory clock
3. Pursue Sponsor Bank partnership in parallel — generates fee revenue during ILC review
4. Pursue CUSO partnerships in parallel — reduces Sponsor Bank dependency at Year 2-3
5. ILC denial contingency: continue with Sponsor Bank + CUSO dual-track; CUSO fee revenue funds indefinite Sponsor Bank operation

**Why Option 2 over Option 1 (Sequential):**
Option 1's fatal flaw is the dependency chain: CUSO takes 12-18 months (realistic, post-Synapse), not 6-12. Revenue arrives after ILC capital is partially depleted. The ILC application lapses before approval — the "fintech death spiral" documented in §5.4 of the report.

**Why Option 2 over Option 3 (CUSO-first):**
Option 3 makes the ILC charter contingent on CUSO success — if CUSO appetite is lower than expected, the ILC timeline slips indefinitely. Option 2 runs both tracks simultaneously.

**ILC denial risk (29% approval rate, 2024-2026):**
With $2M seed covering 12 months operating runway post-IC application, denial at month 18 leaves FloatYield with Sponsor Bank partnership running + CUSO partnerships established. The business survives; ILC becomes a future filing with a larger capital base (CUSO revenue).

**Capital adequacy check:**

- ILC application cost: $500K-$1M (legal + filing fees)
- 12-month operating runway: $1M-$1.5M
- Total: $1.5M-$2.5M — within the $2M seed raise
- Buffer: $0-$500K contingency

---

## For Discussion

1. **If $4-8M in ILC capital were available today with no dilution**, would the sequential path (Sponsor Bank → CUSO → ILC filed at month 18) be the right sequence — or should ILC be filed immediately in parallel to start the regulatory clock?

2. **Counterfactual**: If the ILC application were denied at month 24 with $3M of the $4-8M already spent, would the remaining capital be sufficient to continue CUSO partnerships indefinitely, or would FloatYield face a second capital raise at a worse valuation?

3. **The 29% approval rate question**: Given that ILC denial is a ~70% probability event, should FloatYield design the capital structure assuming ILC approval as the base case (optimizing for the happy path) or assuming denial (conserving capital for a CUSO-only future)?
