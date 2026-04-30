---
name: RISK-003 Sponsor Bank Termination Catastrophe
description: Sponsor Bank termination leaves FloatYield with no regulatory path, zero revenue, and no recoverable customer base — the business effectively dies
type: risk
---

## Risk: Sponsor Bank Termination Is a Business-Killing Event

**Severity:** CRITICAL
**Category:** Strategic/Existential
**Root Cause:** FloatYield's architecture delegates the most critical regulatory asset (the bank charter) to a third party whose interests diverge at scale and who faces regulatory pressure that can force immediate termination

### Risk Description

Sponsor Bank termination is not a "switch vendors" problem. It is an existential event because:

**1. The regulatory foundation disappears immediately.**
Without a Sponsor Bank, FloatYield cannot legally offer FDIC-insured accounts. The core product becomes unavailable overnight. Regulatory requirements do not allow a transition period.

**2. Revenue terminates within the notice period.**
A 90-180 day termination notice period sounds reasonable, but during that period:

- FloatYield cannot sign new customers (product is "sunset")
- Existing customers begin migrating to alternatives
- Revenue declines precipitously before the termination date

**3. Recovery timeline is 18-36 months.**
Finding a new Sponsor Bank requires:

- Initial outreach and relationship building: 3-6 months
- Due diligence and application: 3-6 months
- Contract negotiation: 3-6 months
- Regulatory approval: 3-6 months
- Technical integration and testing: 3-6 months

Total: 18-36 months of operating without the core product.

**4. Customers do not wait.**
Customers who chose FloatYield for FDIC-insured interest-bearing accounts will migrate to alternatives (Marcus, Ally, local credit unions) during the transition. FloatYield's customer base is not "parked" — it evaporates.

**5. Investor confidence collapses.**
A 12-18 month period with zero revenue from the core product is not a "pivot" — it is a death spiral. Investors in a growth-stage fintech do not wait 18 months for a regulatory fix.

### Termination Trigger Scenarios

| Trigger                                       | Likelihood  | Speed                   |
| --------------------------------------------- | ----------- | ----------------------- |
| Bank builds competing product                 | Medium-High | 12-18 month wind-down   |
| Regulatory action forces immediate exit       | Medium      | Immediate (no notice)   |
| Economic conditions make program unprofitable | Medium      | 6-12 months             |
| Compliance failure at FloatYield              | Medium-High | Immediate (with cause)  |
| Bank acquisition                              | Medium      | 6-12 months             |
| Synapse-style industry contagion              | Low-Medium  | Immediate (market-wide) |

### Mitigation

1. **Multi-bank architecture:** Design the product to operate on multiple bank charters simultaneously — if one terminates, others continue
2. **Parallel bank relationships:** Maintain active relationships with 2+ candidate banks at all times
3. **Alternative regulatory path in development:** Credit union charter exploration as a parallel path that does not depend on a single bank
4. **Customer portability:** Build the customer relationship (branding, UX, service) in a way that survives bank migration — even if the underlying charter changes, the customer experience does not
5. **Cash runway:** Maintain 24+ months of runway specifically to survive a Sponsor Bank transition

### Status

OPEN — No termination contingency plan documented in available materials

### Cross-References

- RISK-001 — Termination requires a bank partner to terminate; but having a partner creates the risk
- RISK-002 — Economic misalignment at scale is the primary termination trigger
- GAP-002 — Post-Synapse timeline means a replacement bank takes longer to find
