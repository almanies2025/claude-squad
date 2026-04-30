---
type: RISK
date: 2026-04-30
created_at: 2026-04-30T00:00:00Z
author: agent
session_id: sdk-redteam-session
session_turn: 2
project: multi-cbdc-workshop
topic: "No new procurement" claim underestimates vendor integration burden by 10x
phase: redteam
tags: [procurement, timeline, tms-vendors, false-assumption]
---

## Risk

The claim that TMS vendor licensing bypasses procurement is false and dangerously misleading. Adding a new module to a TMS product requires:

1. **Pre-contract** (3-6 months): Legal review, security questionnaire, PoC evaluation
2. **Contract negotiation** (2-4 months): Liability, support SLA, IP assignment
3. **Architecture review** (6-12 months): Vendor platform team integration design
4. **Security/Compliance review** (6-9 months): Penetration testing, regulatory review
5. **Beta customer acquisition** (3-6 months): Finding willing treasury to pilot
6. **Production release** (3-6 months): Staged rollout

**Total: 24-36 months minimum**

The claim conflates "no central bank procurement" with "no procurement at all." Commercial bank treasury buyers and TMS vendors both require approval processes.

**Severity**: Critical
**Likelihood**: 80% (if pursued, will cause project failure)
**Impact**: 3-year engagement instead of 3-month sale; investor/management expectations completely misaligned

## For Discussion

1. **Source challenge**: Where did the "3-month sale" claim originate? Was this validated against actual TMS vendor procurement history, or assumed?
2. **Counterfactual**: If the team had correctly estimated 24-36 months, would the SDK licensing path still have been prioritized? If not, why are we still analyzing it?
3. **Recovery**: What is the minimum viable timeline reduction? Can vendor relationships compress the architecture review phase from 6-12 months to 2-3 months?
