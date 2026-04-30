---
type: GAP
date: 2026-04-30
created_at: 2026-04-30T00:00:00Z
author: agent
session_id: deep-analysis-session
session_turn: 3
project: mbridge-redteam
topic: HKMA dual-issuance CNY claim is central but unsourced — collapse risk if wrong
phase: redteam
tags:
  [
    hkma,
    cny-dual-issuance,
    architectural-assumption,
    source-gap,
    settlement-model,
  ]
---

## Gap

The simulation's entire CNY dominance thesis rests on one architectural claim: "HKMA dual-issues CNY via PBOC RTGS membership" (line 106 of fx_settlement_lock.py). This claim is the linchpin of scenarios B, E, and F. It is presented as a comment, not a cited fact.

**The distinction that matters**:

- **HKMA as CNY clearer**: HKMA operates the RMB RTGS system and clears CNY payments through PBOC's infrastructure. This is documented and uncontroversial.
- **HKMA as CNY issuer**: The simulation treats HKMA as a CNY issuer equivalent to PBOC — meaning HKMA can "create" CNY the same way PBOC does. This is a legally and technically distinct claim.

**Why this gap matters**:

If HKMA only clears CNY (not issues it), then HKMA cannot send CNY without a pre-funded Nostro account — just like any other non-issuer. This would block:

- Scenario B (CNY bridge via HKMA) — HKMA would need CNY Nostro to send CNY to CBUAE
- Scenario E (three-hop with AED return) — the CNY bridge legs would fail
- The entire CNY dominance argument — CNY's structural advantage depends on HKMA bridging

**The source problem**: The simulation summary references BIS papers (Project Agora, Project Mandola, Oxford/SMU 2023) but the HKMA dual-issuance claim does not appear in any of those sources. The Oxford/SMU trilemma paper discusses HKMA's role but does not characterize HKMA as a CNY issuer.

## For Discussion

- What is the precise legal and technical status of HKMA's CNY capability? Is there a definitive public source?
- If HKMA only clears CNY (does not issue it), how does the CNY bridge actually work in the real mBridge system? Is there an alternative explanation for CNY's dominance that doesn't require HKMA dual-issuance?
- Should the simulation add an uncertainty mode where HKMA's CNY capability is parameterized (issues vs. clears only)?
- What happens to the product's value proposition if the HKMA dual-issuance claim is corrected or removed?
