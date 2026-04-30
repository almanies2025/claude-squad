---
type: RISK
date: 2026-04-30
created_at: 2026-04-30T00:00:00Z
author: agent
session_id: sdk-redteam-session
session_turn: 1
project: multi-cbdc-workshop
topic: TMS vendors reject Python modules — Java/.NET tech stack lock-in
phase: redteam
tags: [tms-vendors, python, integration, technical-debt, market-timing]
---

## Risk

TMS vendors (Finastra, FIS, Temenos) operate exclusively on Java/.NET tech stacks and do not accept Python modules without extraordinary justification. The FX Settlement Lock simulation, built as a Python library, cannot be embedded directly into any major TMS product.

**Severity**: Critical
**Likelihood**: 90%
**Impact**: Complete path failure if pursued

**Evidence**:

- Finastra FusionBanking: Java-only platform
- FIS: Java/.NET hybrid with strict architecture review
- Temenos: Java cloud-native; Python only for AI modules (exception-based)
- Vendor engineering bandwidth: zero for speculative 2026 CBDC features

**Timeline impact**: Even if a vendor accepted the module, integration would require 24-36 months (not 12-18). Python wrapper overhead introduces latency and support complexity.

## For Discussion

1. **Evidence check**: Can we confirm Temenos's Python tolerance for AI modules specifically? Is there a documented exception process that could be leveraged for a CBDC simulation module?
2. **Counterfactual**: If the simulation were rewritten in Java (8-12 months engineering), would vendor acceptance rates increase significantly? Is the reimplementation cost justified by the license revenue potential?
3. **Alternative**: Could a REST API wrapper (Python backend + Java binding) satisfy vendor integration requirements without full reimplementation?
