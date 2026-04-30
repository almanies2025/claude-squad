---
type: GAP
date: 2026-04-30
created_at: 2026-04-30T00:00:00Z
author: agent
session_id: sdk-redteam-session
session_turn: 3
project: multi-cbdc-workshop
topic: No discovery calls with commercial treasury directors conducted
phase: redteam
tags: [treasury-buyers, market-validation, discovery, bloomberg, fxall]
---

## Gap

The SDK commercial path assumes commercial bank treasury directors want CBDC settlement simulation embedded in their TMS. No discovery calls with actual treasury directors have been conducted to validate this assumption.

**Evidence**:

- Treasury directors use Bloomberg Terminal and FXall for FX analysis and execution
- TMS is a book-of-record system, not a predictive analytics platform
- CBDC is viewed as a regulatory/central bank issue, not a treasury operations issue
- No budget line exists for "CBDC corridor simulation modules"

**The TMS is miscast**: Asking a treasury director to pay for CBDC settlement simulation embedded in their TMS is like asking them to buy a weather prediction module for their accounting software.

**Required action**: Conduct 3-5 discovery calls with commercial bank treasury directors before any further investment in the vendor licensing path.

## For Discussion

1. **Evidence requirement**: What is the specific source for the claim that treasuries want this capability? Can we name 3 commercial banks whose treasury directors have expressed interest in CBDC settlement simulation?
2. **Counterfactual**: If discovery calls reveal treasuries do NOT want this in their TMS, what is the contingency? Do we pivot to Bloomberg/FXall integration, or abandon the path entirely?
3. **Validation design**: How would we conduct discovery calls without revealing proprietary methodology? Is there a standard CBDC vendor positioning that allows discovery without exposing the simulation's technical details?
