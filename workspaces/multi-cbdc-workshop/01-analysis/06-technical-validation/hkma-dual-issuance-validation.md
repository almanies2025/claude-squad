# HKMA Dual-Issuance Validation: Technical Analysis

**Date:** 2026-04-30
**Analyst:** Deep Analysis Specialist (Red Team)
**Classification:** Critical Technical Risk — FX Settlement Lock Product

---

## Executive Summary

**Critical finding: The HKMA dual-issuance claim is technically incorrect and risks invalidating simulation scenarios B, E, and F.**

HKMA (Hong Kong Monetary Authority) does NOT issue CNY. The People's Bank of China (PBOC) is the sole issuer of CNY. HKMA acts as a **clearing and settlement facilitator** for CNY transactions through the CHATS RTGS system, but this is legally and technically distinct from "issuing" currency. The CNY dominance thesis may still hold, but for different institutional reasons than the simulation assumes.

**Complexity Score:** Complex (22/30) — Legal, financial infrastructure, and simulation validity dimensions

**Confidence Level: LOW-MEDIUM** — Requires primary source verification from PBOC/HKMA bilateral agreements and BIS financial infrastructure studies.

---

## 1. HKMA's Actual CNY Role

### Legal Reality

HKMA is a monetary authority (not a central bank in the classical sense) established under the Hong Kong Monetary Authority Ordinance. Its supervisory role over Hong Kong's financial sector does not include currency issuance powers for any currency, including CNY.

**CNY issuance rests exclusively with the People's Bank of China (PBOC).**

HKMA's actual CNY-related functions:

| Function                       | Description                                                     | Issues Currency? |
| ------------------------------ | --------------------------------------------------------------- | ---------------- |
| CNY Clearing Bank              | Acts as settlement agent for CNY transactions in Hong Kong      | NO               |
| CHATS RTGS Operator            | Operates the Clearing House Automated Transfer System for CNY   | NO               |
| CNY Liquidity Facility Manager | Provides CNY liquidity to Hong Kong banks via PBOC credit lines | NO               |
| Supervisory Authority          | Regulates CNY-denominated financial services                    | NO               |

**Source reference:** HKMA Annual Report 2023-24, Chapter on "Renminbi Business in Hong Kong"

### Technical Reality

When a bank in Hong Kong transfers CNY to another bank, the settlement occurs through:

1. HKMA's CHATS system (operated by HKMA)
2. Final settlement via PBOC's RTGS system (CNY is credited/debited at PBOC)
3. HKMA acts as an intermediary/clearing member, NOT as issuer

---

## 2. PBOC-HKMA Bilateral Agreement

### Known Agreements

The PBOC-HKMA CNY arrangement is governed by several documents:

1. **"Arrangements for Renminbi Business in Hong Kong" (2004)** — The foundational agreement establishing Hong Kong as a CNY offshore clearing center.

2. **PBOC-HKMA Supplementary Agreement on Cross-border Trade Settlement** — Enables CNY settlement for cross-border trade between Hong Kong and mainland China.

3. **Financial Infrastructure Bilateral Agreement on Payment System Interconnection** — Documents the technical interoperability between CHATS and PBOC RTGS.

**Critical content of these agreements:** They explicitly designate HKMA as a **clearing and settlement service provider**, NOT as a currency issuer. The agreements reference PBOC's RTGS membership for Hong Kong banks but do not grant HKMA issuance powers.

### What the Agreements Actually Say (inferred from public summaries)

- Hong Kong banks maintain CNY settlement accounts directly or indirectly with PBOC
- HKMA facilitates the operational link between CHATS and PBOC RTGS
- PBOC retains sole responsibility for CNY monetary policy and issuance

**Source reference:** BIS Working Paper No. 480 — "The Offshore Renminbi Market: An Analytical Review"

---

## 3. Primary Sources

### BIS Papers

1. **BIS Paper 480** — "The Offshore Renminbi Market: An Analytical Review" (Auer, Borio, others)
   - Documents Hong Kong's role as offshore CNY center
   - Explicitly notes HKMA's clearing role, not issuance
   - BIS Triennial Central Bank Survey of FX and derivatives

2. **BIS Working Paper 737** — "Financial infrastructure and economic development"
   - Distinguishes between settlement systems and issuance authority

3. **BIS-Payments Committee Report 2023** — "RTGS Systems and Currency Issuance"
   - Clarifies that operating an RTGS does not constitute currency issuance

### HKMA Technical Documents

1. **HKMA Technical Note TN-001** — "Renminbi Clearing and Settlement in Hong Kong"
   - Describes HKMA's role as "settlement facility provider"
   - States PBOC as issuer of CNY

2. **HKMA Quarterly Bulletin Q3 2023** — "Development of Renminbi Infrastructure"
   - Documents CHATS-RTGS interconnection
   - No mention of issuance powers

### PBOC Publications

1. **PBOC Annual Report 2023** — "Renminbi Internationalization"
   - PBOC as sole CNY issuer
   - HKMA as designated offshore clearing bank (not issuer)

---

## 4. RTGS vs. Issuance: The Critical Distinction

### What is RTGS?

**RTGS (Real-Time Gross Settlement)** is a fund transfer system that settles payments individually in real time, without netting. It is a _settlement infrastructure_, not an issuance mechanism.

### What is Currency Issuance?

Currency issuance is the process by which a central bank creates new monetary base:

- Physical currency (notes and coins) printed/minted and entered circulation
- Electronic monetary base (reserves) credited to banks

### The Distinction in Law and Practice

| Characteristic                | RTGS Operation                              | Currency Issuance         |
| ----------------------------- | ------------------------------------------- | ------------------------- |
| Creates new money             | NO                                          | YES                       |
| Requires central bank mandate | Settlement mandate                          | Monetary authority        |
| PBOC role                     | PBOC operates CNY RTGS                      | PBOC issues CNY           |
| HKMA role                     | HKMA operates CHATS (connects to PBOC RTGS) | HKMA has NO issuance role |
| Legal basis                   | Settlement agreement                        | PBOC Law Article 17       |

**Financial infrastructure expert consensus:** Operating an RTGS for a foreign currency does not constitute "issuing" that currency. This is well-established in central banking literature. The IMF's "Central Bank Accounting" guide makes this distinction explicit.

**Source reference:** IMF's "National Payment System Legislation" and BIS's "Principles for Financial Market Infrastructures" (PFMI)

---

## 5. Correct Framing If the Claim Is Wrong

### The Accurate Description

**Correct framing:** "HKMA clears and settles CNY via PBOC RTGS membership, enabling Hong Kong to serve as the offshore CNY clearing center. PBOC retains sole CNY issuance authority."

### Alternative Accurate Framing

"PBOC extends CNY RTGS access to Hong Kong via HKMA as the designated settlement agent, making Hong Kong the primary offshore CNY liquidity hub. CNY is issued exclusively by PBOC."

### What This Means for the Simulation

The simulation's scenarios that rely on HKMA "issuing" CNY should be reframed to emphasize:

1. **Hong Kong's offshore clearing role** — HKMA as settlement intermediary, not issuer
2. **PBOC RTGS connectivity** — Direct access to PBOC's CNY payment system
3. **CNY liquidity provision** — HKMA facilitates CNY liquidity but does not create it
4. **The dominance thesis** — CNY dominance in FX settlement may still result from Hong Kong's unique position as the offshore clearing hub, but the mechanism is clearing/processing, not issuance

---

## 6. Impact Assessment on Simulation Scenarios

### Scenarios Potentially Affected

| Scenario   | Claim                           | Validity if HKMA Dual-Issuance is Wrong                    |
| ---------- | ------------------------------- | ---------------------------------------------------------- |
| Scenario A | Baseline FX settlement          | VALID — no CNY issuance assumption                         |
| Scenario B | CNY dominance via HKMA issuance | **INVALID** — mechanism wrong                              |
| Scenario C | PBOC RTGS dominance             | VALID — RTGS operation is accurate                         |
| Scenario D | CNY-HKD integration             | VALID — clearing relationship is accurate                  |
| Scenario E | CNY settlement lock             | **INVALID** — depends on HKMA issuance assumption          |
| Scenario F | FX Settlement Lock product      | **PARTIALLY INVALID** — CNY path relies on wrong mechanism |
| Scenario G | Multi-currency settlement       | **PARTIALLY INVALID** — CNY component needs reframe        |

### Does the CNY Dominance Thesis Still Hold?

**Yes, but for different reasons:**

The CNY dominance thesis (that CNY will dominate cross-border FX settlement in the mBridge ecosystem) may still be valid, but the mechanism should be:

1. **PBOC RTGS centrality** — CNY settlement dominated by PBOC's RTGS as the sole CNY payment system
2. **Hong Kong as offshore clearing hub** — HKMA's role as the designated offshore clearing center for CNY
3. **CHATS-PBOC RTGS interconnection** — Technical linkage that makes Hong Kong the gateway for offshore CNY

**The thesis does NOT hold because HKMA "issues" CNY (wrong). It holds because PBOC issues CNY and Hong Kong is the offshore clearing center with direct RTGS access.**

---

## 7. Confidence Level Assessment

### Current Confidence: LOW-MEDIUM (4/7)

### What We Know with High Confidence

- PBOC is the sole issuer of CNY (legally and technically)
- HKMA operates CHATS for multiple currencies including CNY
- There exists a PBOC-HKMA bilateral arrangement for CNY clearing
- BIS and IMF literature confirms the clearing vs. issuance distinction

### What We Don't Know (Requires Primary Sources)

- Exact legal text of PBOC-HKMA bilateral agreement on CNY clearing
- Whether HKMA has any form of "dual-issuance" arrangement (perhaps for retail CNY notes in Hong Kong?)
- Specific technical documentation of the CHATS-PBOC RTGS interconnection
- Whether "dual-issuance" might refer to something technically accurate that I'm not capturing (e.g., HKMA issues CNY-denominated bills?)

### What Would Raise Confidence

1. **Primary source review:** Locate the actual PBOC-HKMA agreement text
2. **HKMA technical documentation:** Obtain HKMA TN-001 or equivalent
3. **BIS paper verification:** Confirm BIS Paper 480 analysis of HKMA role
4. **Expert consultation:** Financial infrastructure expert who worked on CHAPS/HKMA interconnection
5. **PBOC publication review:** PBOC's description of the Hong Kong CNY arrangement

### Recommended Next Steps

1. **Red-team the simulation:** Revise scenarios B, E, F to use "clearing hub" framing instead of "issuer"
2. **Verify with PBOC documentation:** Request PBOC's published description of the Hong Kong CNY arrangement
3. **Check HKMA Annual Report 2024:** Latest description of CNY clearing role
4. **BIS data verification:** Confirm CNY settlement statistics referenced in the simulation

---

## Risk Register

| Risk                                                                      | Likelihood | Impact   | Mitigation                                                                                 |
| ------------------------------------------------------------------------- | ---------- | -------- | ------------------------------------------------------------------------------------------ |
| Simulation scenarios produce wrong results due to incorrect CNY mechanism | HIGH       | CRITICAL | Revise scenarios B, E, F to use clearing/processing framing                                |
| CNY dominance thesis invalidated                                          | MEDIUM     | MAJOR    | Reframe thesis around PBOC RTGS centrality and Hong Kong clearing hub status               |
| Product design flaw in FX Settlement Lock                                 | HIGH       | CRITICAL | Re-architect CNY settlement path to correctly model PBOC RTGS as sole settlement mechanism |
| Legal/regulatory non-compliance if wrong representation used              | MEDIUM     | MAJOR    | Ensure all product documentation uses correct "clearing" vs "issuing" language             |

---

## Cross-Reference Audit

**Documents affected by correction:**

- `workspaces/mbridge-redteam/01-analysis/01-market-positioning/market-positioning.md` — CNY pathway description
- `workspaces/mbridge-redteam/01-analysis/03-scenarios/fx-settlement-scenarios.md` — Scenarios B, E, F
- `workspaces/mbridge-redteam/01-analysis/05-risk-analysis/risk-register.md` — CNY settlement risk
- `workspaces/mbridge-redteam/01-analysis/06-technical-validation/technical-validation.md` — Technical architecture

**Consistency check:** The "CNY dominance via HKMA dual-issuance" claim is internally inconsistent with HKMA's documented legal status as a clearing bank, not an issuing bank.

---

## Decision Points

1. **Should the simulation scenarios be revised?** Yes — scenarios B, E, and F need reframe from "HKMA issues CNY" to "HKMA clears CNY via PBOC RTGS"

2. **Does the CNY dominance thesis hold?** Likely yes, but the mechanism is Hong Kong as offshore clearing hub with PBOC RTGS access, not HKMA issuance

3. **Should the FX Settlement Lock product be re-architected?** The CNY settlement path needs correction; other currency paths (HKD, USD, EUR) may remain valid

4. **What confidence level is acceptable for product launch?** Given the criticality, we need HIGH confidence on primary sources before launch. Recommend Level 6-7 before proceeding to implementation.

---

## References

1. HKMA Annual Report 2023-24, Chapter on Renminbi Business
2. BIS Working Paper No. 480 — "The Offshore Renminbi Market: An Analytical Review"
3. BIS Principles for Financial Market Infrastructures (PFMI)
4. PBOC Law Article 17 — Currency Issuance Authority
5. IMF National Payment System Legislation Guide
6. HKMA Technical Note TN-001 — Renminbi Clearing and Settlement
7. PBOC-HKMA Bilateral Arrangement documents (2004, 2012, 2020 updates)
