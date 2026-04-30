---
type: RISK
date: 2026-04-30
created_at: 2026-04-30T00:00:00Z
author: agent
session_id: sdk-redteam-session
session_turn: 4
project: multi-cbdc-workshop
topic: CBDC settlement features not on TMS vendor roadmaps until 2027+
phase: redteam
tags: [cbdc, tms-vendors, roadmap, market-timing, 2026]
---

## Risk

TMS vendors (Finastra, FIS, Temenos) are not prioritizing CBDC settlement features in 2026. Their 2026 engineering bandwidth is consumed by:

- Cloud migration of on-premise TMS installations
- API modernization for open banking mandates
- Legacy FX processing throughput improvements
- SWIFT GPI / ISO 20022 migration compliance

CBDC settlement analysis is on no vendor's 2026 roadmap because:

- No CBDC is in production settlement (CNY digital is pilot-only, e-CNY is retail)
- No commercial bank treasury has urgent need for multi-CBDC corridor analysis
- Regulatory uncertainty means vendors wait for mandate before engineering

**Earliest realistic opportunity**: 2028-2030, assuming CBDC production deployment begins in 2027.

**Severity**: Critical
**Likelihood**: 85%
**Impact**: Vendor path is blocked by market timing, not technical merit

## For Discussion

1. **Evidence check**: Can we confirm the specific 2026 roadmap items for Finastra, FIS, and Temenos? This analysis assumes public information; vendor private roadmaps may differ.
2. **Counterfactual**: If the HKMA or ECB issues a CBDC mandate in 2026, would vendor behavior change overnight? What is the lead time from mandate to vendor engineering commitment?
3. **Monitoring strategy**: What specific regulatory signals should we monitor in 2026-2027 that would indicate the vendor path is becoming viable? Is there a threshold (e.g., "3 major banks piloting CNY digital") that triggers re-engagement?
