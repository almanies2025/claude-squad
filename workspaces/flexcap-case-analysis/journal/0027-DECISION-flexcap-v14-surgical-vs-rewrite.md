---
name: flexcap-v14-surgical-edit
description: FlexCap compliance gap fix — surgical edit of v11 preferred over rewrite; v14 produced
type: decision
---

## Decision: Surgical Edit of v11 Is Optimal — No Rewrite Needed

### Context

OPIM626 FlexCap case analysis. v11 rated by expert audit: Structural 8.5/10, Investment Thesis 6/10, Compliance 5/10 → estimated ~8/10 overall. Professor rubric requires: (1) all major root causes with course concepts, (2) all solutions with course concepts and mechanism explanation, (3) systematic presentation.

### The Three Compliance Gaps Identified

**Gap 1 — Section 2.5 root cause lacks explicit course concept:**
Heading: "SinoLife Strategic Distortion — Strategic vs. Financial Investor Risk." No session number or framework name cited. Other sections explicitly cite sessions (e.g., "LTV/CAC Framework (Session 1)", "Ethical AI Decision-Making Framework (Session 6)"). The report listed "VC/PE Governance Principles" in the Framework Applied line but never cited it as the analytical lens for 2.5.

**Gap 2 — Section 3.5 solution lacks course concept mechanism:**
Solutions 3.1–3.4 each have a "Why This Addresses Root Cause" paragraph that explicitly names the governing principle. Solution 3.5 says "structural problem that earn-outs cannot fix" but does not name the VC/PE Governance principle behind each recommended instrument (information rights cap, lock-up, ROFR).

**Gap 3 — Section 3.5 duplicate ROFR paragraph:**
The ROFR bullet was internally duplicated — two identical sentences concatenated.

### Options Evaluated

**Option A — Full rewrite (v12):** Discard v11 and rewrite from scratch.
Rejected. The mathematical derivation (2.7x > 2.5x target proof), Capital IQ data (Holmusk, 5 Health, M&A comparables), and gate-tiering are all correct and well-sourced. Rewriting risks introducing new errors and discards analytical work that meets rubric standards.

**Option B — Surgical targeted edit (v14):** Only the 6 paragraphs with compliance gaps are modified. All other content — including tables, valuation bridge, Capital IQ data, gate structure — preserved exactly.
Chosen.

### Changes Made in v14

| Para  | Change                                                                                                                                                                                         |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [48]  | 2.5 heading: "Strategic vs. Financial Investor Risk" → "VC/PE Governance Principles Failure"                                                                                                   |
| [49]  | 2.5 Root Cause body: rewritten to explicitly cite VC/PE Governance Principles (Session 6) and apply them analytically — agency risk theory, information asymmetry, holding period misalignment |
| [50]  | Duplicate sentence cleared (was orphaned from v11 text split)                                                                                                                                  |
| [66]  | 3.1 "Why This Addresses Root Cause" body preserved (was accidentally replaced in v12, restored)                                                                                                |
| [100] | 3.5 "Why This Addresses Root Cause" body: rewritten to name specific VC/PE Governance principles behind each mechanism (info rights separation, 24-month lock-up, ROFR obligation)             |

### Why This Addresses the Compliance Score

**Compliance criterion: "Used relevant course concepts to address the root causes identified."**

- v11: 2.5 cited "Strategic vs. Financial Investor Risk" as a description, not a course concept
- v14: 2.5 explicitly applies "VC/PE Governance Principles (Session 6)" as the analytical lens, showing HOW the concept diagnoses the SinoLife conflict

**Compliance criterion: "Solutions systematically solve the problems identified."**

- v11: 3.5 named the fixes but not the governing principle behind each
- v14: 3.5 "Why This Addresses" explicitly states "VC/PE Governance Principles identify three distinct agency risks... each requiring a specific governance instrument" — directly answering the rubric's requirement for course concept application, not just fix description

### Scripts Used

- `fix_v11.py` — initial surgical changes (v11 → v12)
- `fix_v12.py` — attempted Fix 2 (2.5 root cause reframe) + Fix 3 (3.5 mechanism reframe) + Fix 5 (bold label consistency — was over-aggressive, caused regressions)
- `fix_v13.py` — targeted fixes 1-3 only (from v12 base); Fix 1 (space restoration) failed to match pattern
- `fix_v14.py` — space restoration for "Why This Addresses Root Cause:" labels (5 paragraphs fixed)
- Inline Python one-liners for para [66] body restore and para [50] orphan cleanup

### Deliverable

`/mnt/c/Users/User/Desktop/FlexCap_Case_Analysis_v14.docx` — surgical edit result
`/mnt/c/Users/User/Desktop/FlexCap_Case_Analysis_v11.docx` — original (preserved)

### Verified

- All 5 course concepts present: LTV/CAC ✓, CIRCLE ✓, Ethical AI ✓, Porter's ✓, VC/PE Governance ✓
- 9 tables preserved unchanged
- 6 paragraphs changed, all intentional
- No new analysis, no new data, no new structure — framing fix only
