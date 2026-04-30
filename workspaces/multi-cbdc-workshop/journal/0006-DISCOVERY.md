---
name: HKMA Dual-Issuance Claim is Technically Incorrect
description: HKMA does not issue CNY; it clears/processes CNY via PBOC RTGS membership. PBOC is sole CNY issuer.
type: DISCOVERY
date: 2026-04-30
---

## DISCOVERY: HKMA Dual-Issuance Claim is Technically Incorrect

**Scope:** FX Settlement Lock simulation — CNY settlement pathway

### What I Found

The simulation claims "HKMA dual-issues CNY via PBOC RTGS membership" as the linchpin of the CNY dominance thesis. This is **technically incorrect**.

**HKMA does NOT issue CNY.** PBOC is the sole issuer of CNY under PBOC Law Article 17. HKMA's role is:

- Clearing and settlement facilitator for CNY transactions
- Operator of CHATS RTGS (connects to PBOC RTGS)
- Designated offshore clearing center (not issuer)

**The distinction matters:**

- "Issuing" CNY = creating new monetary base (only PBOC does this)
- "Clearing" CNY = settling transactions through PBOC RTGS (HKMA does this)

### Why This Matters

Scenarios B, E, and F of the simulation rely on the incorrect framing. If HKMA only clears (not issues) CNY:

- The CNY dominance thesis may still hold, but for different reasons
- The mechanism is Hong Kong as offshore clearing hub with PBOC RTGS access
- The FX Settlement Lock product needs re-architecting for the CNY path

### Primary Sources Cited

1. BIS Working Paper 480 — "Offshore Renminbi Market"
2. HKMA Annual Report 2023-24 — Renminbi Business chapter
3. IMF National Payment System Legislation Guide — settlement vs issuance distinction
4. BIS PFMI — Principles for Financial Market Infrastructures

### Confidence: LOW-MEDIUM

Need primary source verification of PBOC-HKMA bilateral agreement text to raise confidence.

**Next:** Task #3 complete — marking done and reporting to team-lead
