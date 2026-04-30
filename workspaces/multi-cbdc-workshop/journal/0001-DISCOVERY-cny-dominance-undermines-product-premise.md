---
type: DISCOVERY
date: 2026-04-30
created_at: 2026-04-30T00:00:00Z
author: agent
session_id: deep-analysis-session
session_turn: 1
project: mbridge-redteam
topic: CNY dominance claim is self-undermining — 95%+ volume makes the problem theoretical
phase: redteam
tags:
  [fx-settlement-lock, cny-dominance, product-premise, internal-inconsistency]
---

## Finding

The FX Settlement Lock simulation claims "e-CNY accounts for 95%+ of settlement volume by value" on mBridge (2024–2026). This figure is presented as supporting evidence for the CNY dominance thesis. However, it is internally self-undermining.

**If CNY dominates 95%+ of mBridge volume**, then the multi-currency settlement problem the product highlights is largely theoretical — there are very few non-CNY settlements to optimize. The product's core value proposition ("multi-CBDC settlement analysis tool") addresses a problem that barely exists in practice.

**The contradiction**:

- The simulation argues there is a significant multi-currency settlement architecture problem (CNY bias creates structural disadvantages for AED, THB)
- But 95%+ CNY dominance means non-CNY settlements are statistically negligible
- Either the problem is real but rare, or the dominance figure is inflated and the problem is larger

## Evidence

From fx_settlement_lock.py Scenario F and summary section:

- Scenario F: "e-CNY Dominance: Pairwise Settlement Matrix" shows CNY as dominant
- Summary: "e-CNY accounts for 95%+ of settlement volume by value"
- The simulation's purpose is to help parties navigate multi-currency settlement

**The issue**: A tool for optimizing multi-currency settlement is unnecessary if 95% of settlements are single-currency CNY.

## Why This Matters

The product brief (and the simulation) cannot simultaneously claim:

1. CNY dominates 95%+ of volume (monocurrence)
2. Multi-currency settlement optimization is a significant problem worth solving

If the product is repositioned as "understand why CNY dominates and what happens in the 5% edge cases," the addressable market shrinks proportionally.

## For Discussion

- If CNY truly dominates 95%+ of volume, what specific non-CNY settlement scenarios would a buyer pay to analyze? Can we name 2-3 concrete examples?
- Is the 95%+ figure sourced from verifiable mBridge data, or is it an estimate from the simulation authors? If unverified, should it be removed from the product narrative?
- Could the 5% non-CNY volume represent the highest-value, most complex settlements (e.g., large AED-THB trades) where the analysis is most valuable — and therefore the product is actually targeting the most valuable edge cases?
