# RISK/GAP Journal — Treasury Path Red Team

**Date:** 2026-04-30
**Entry:** 0013
**Author:** Red Team Specialist
**Path Reviewed:** Path 1 — Commercial Bank Treasury Capital Efficiency Tool

---

## Risk Findings

### RISK-001: Fictional Buyer Persona

**Severity:** Critical
**Category:** Go-to-Market / ICP
**Finding:** The "FX Treasury Product Manager with sub-$250K approval authority and no IT procurement" does not exist at major commercial banks. All major banks (HSBC, Citi, JPMorgan, Deutsche, Standard Chartered) require procurement and risk review for external vendors touching treasury operations regardless of spend amount.
**Mitigation:** Redesign ICP. Actual buyer is likely Treasury Operations Director + IT Procurement + Risk. Requires committee sell, not single champion.
**Status:** Open

### RISK-002: CBDC Volume Timing Mismatch

**Severity:** High
**Category:** Product-Market Timing
**Finding:** Commercial bank CBDC rail volume in 2026 is negligible. mBridge is pilot stage. e-CNY is retail-focused. Project AGW and Project Cedar are wholesale探索, not operational. The "deadlock" problem does not yet exist at material scale.
**Mitigation:** Reposition as 2028-2030 scenario planning tool. Pitch: "build your model before volume arrives."
**Status:** Open

### RISK-003: CNY Path Error — HKMA Clearing vs. Issuing

**Severity:** High
**Category:** Analytical Credibility
**Finding:** The simulation incorrectly models HKMA as issuing CNY. HKMA clears CNY offshore transactions; PBoC issues CNY. This is a foundational error that destroys credibility with any CNY-focused treasury buyer (HSBC, Citi both have major CNY operations).
**Mitigation:** Correct CNY path logic before any commercial engagement involving CNY corridors. Requires external CNY market validation.
**Status:** Open

### RISK-004: Bloomberg Competitive Gap Unvalidated

**Severity:** High
**Category:** Competitive Positioning
**Finding:** The pitch assumes Bloomberg TXN does not cover CBDC-specific corridor analysis. This is unconfirmed. Bloomberg has extensive treasury analytics; the specific gap claim requires validation against Bloomberg TXN product documentation or demo.
**Mitigation:** Obtain Bloomberg TXN demonstration or product documentation for CBDC settlement analytics. Only claim gap if confirmed.
**Status:** Open

### RISK-005: Cold Outreach to Treasury = Zero Response

**Severity:** High
**Category:** Go-to-Market
**Finding:** Major bank treasury departments do not take cold calls or respond to cold emails from unknown vendors. All viable paths to treasury buyers involve warm introductions, industry events, or inbound thought leadership.
**Mitigation:** Establish warm introduction path before serious commercial pursuit. Alternative: publish CBDC analysis as thought leadership to generate inbound.
**Status:** Open

### RISK-006: Internal Build Refutes Differentiation Claim

**Severity:** Medium
**Category:** Value Proposition
**Finding:** If internal treasury quant team can build this in 2-3 weeks, the "unique methodology" claim is hollow. The 2-3 week estimate directly contradicts the "they won't build it" rationale.
**Mitigation:** Reframe value: "we have 6 months of multi-bank corridor comparative data you don't have." Not "you can't build it."
**Status:** Open

### RISK-007: Compound Failure Mode

**Severity:** Critical
**Category:** Strategic
**Finding:** The seven issues above are not independent — each compounds the others. Fictional buyer + no CBDC volume + cold outreach + unvalidated gap + CNY error = near-zero probability of first engagement success. This is not a "find right buyer" problem; it is a structural approach problem.
**Mitigation:** Fundamental reconception required before further pursuit.
**Status:** Open

---

## Gap Findings

### GAP-001: No Warm Introduction Path

**Category:** Go-to-Market
**Finding:** No identified pathway to reach treasury buyers at target banks. Industry associations (AFP, BAFT), conference speaking, or referral through existing bank relationships are required paths. None currently exist in the strategy.
**Action:** Identify specific conference, association, or network connection before proceeding.

### GAP-002: CNY Market Expertise

**Category:** Product
**Finding:** The simulation was built without CNY market specialist validation. The HKMA error is evidence of this gap. Any commercial CNY corridor analysis requires validation by an external CNY market expert.
**Action:** Engage CNY market specialist for audit of CNY path logic before commercial use.

### GAP-003: Bloomberg Gap Analysis

**Category:** Competitive
**Finding:** The competitive differentiation claim ("what Bloomberg doesn't have") is unvalidated. Requires side-by-side comparison of simulation capabilities vs. Bloomberg TXN CBDC coverage.
**Action:** Obtain Bloomberg TXN demo, document specific gaps, or remove Bloomberg comparison from pitch.

### GAP-004: Buyer Committee Mapping

**Category:** Sales
**Finding:** Single-champion sales model is invalid for major bank treasury tooling. Actual sale requires: Treasury Product Owner + IT Procurement + Risk/Compliance + potentially Finance Controls.
**Action:** Map full buying committee for each target bank. Design engagement strategy for each role.

---

## Recommendation Summary

**Kill Path 1 or fundamentally reconceive it.**

Path 1 as currently structured has:

- 7 open risks (2 Critical, 4 High, 1 Medium)
- 4 open gaps
- 0 confirmed mitigations in place
- 0 warm introduction paths identified
- 1 unfixable-in-2026 timing problem (CBDC volume)

The CBDC simulation is a legitimate technical artifact. The treasury commercial path is not viable in 2026 without structural reconception.

**If pursuing anyway:** Pivot to central bank/economic authority buyers who DO have CBDC urgency and authority, or to TMS vendors (Kyriba, Finastra) as distribution partners who already have the bank relationships.

---

**Next Entry:** 0014 — TBD
