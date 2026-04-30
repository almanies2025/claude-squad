---
name: RISK-002 Bank Economic Incentive Misalignment at Scale
description: At small scale economics work; at scale ($500M+ deposits), the bank realizes they bear all risk but capture a fraction of the value — leading to termination or renegotiation
type: risk
---

## Risk: Bank Will Capture Economic Diseconomies at Scale, Driving Termination

**Severity:** CRITICAL
**Category:** Strategic/Economic
**Root Cause:** Misaligned economic incentives between FloatYield (captures platform fees, takes rate, customer relationships) and Sponsor Bank (bears FDIC exposure, compliance burden, regulatory risk)

### Risk Description

At small deposit volumes ($10-50M), the Sponsor Bank's economics work. Program fees ($50-200K/year) plus deposit spread ($200-500K/year) cover compliance costs and provide modest profit. At scale ($500M+ in deposits), three things happen:

1. The bank captures ~$10-15M in net interest income from the deposit spread, but FloatYield is earning platform fees, takes rates, and customer relationships worth potentially $20-50M/year. The bank bears the regulatory and FDIC risk for a fraction of the economic value.

2. The bank's regulators (FDIC, OCC) begin treating the BaaS program as a material risk to the Deposit Insurance Fund. Examinations intensify. The bank's own risk committee questions whether the economics justify the risk.

3. The bank decides to build a competing product or acquire a BaaS competitor. They give FloatYield 12 months notice and launch their own version.

### Evidence

This is the standard lifecycle of BaaS partnerships observed across the industry:

- GreenSky ( Goldman Sachs built competing product, ended partnership)
- Various BaaS fintechs experienced termination when bank partners decided to vertically integrate
- Column Bank (a BaaS-native bank) explicitly builds and powers competing fintechs — partners know they may be acquired
- The "build vs partner" calculus always favors "build" at scale when the economics become attractive

### Why This Is Critical

Unlike a typical vendor relationship where termination means switching costs, Sponsor Bank termination means FloatYield loses its regulatory foundation. The core product (FDIC-insured interest-bearing accounts) becomes unavailable. Revenue drops to zero. Recovery requires 18+ months on a new bank charter.

### Mitigation

1. **Economics rebalancing:** Negotiate revenue sharing that gives the bank a larger share of platform economics at scale — aligning incentives
2. **Exclusivity provisions:** 3-5 year exclusivity with automatic renewal unless bank exercises opt-out with extended notice
3. **Most-favored-partner clauses:** Bank cannot offer better terms to a competing platform
4. **Strategic stake:** Consider giving the Sponsor Bank a minority equity stake in FloatYield — makes termination economically painful for both parties
5. **Vertical integration defense:** Document and demonstrate FloatYield's unique technology differentiation that the bank cannot easily replicate

### Status

OPEN — No evidence of economic alignment mechanisms in Program Manager Agreement framework

### Cross-References

- RISK-001 — Without a partner, this risk is moot but moot in the worst way (no business)
- RISK-003 — Termination cascade
- GAP-001 — Contract terms insufficient to protect against this scenario
