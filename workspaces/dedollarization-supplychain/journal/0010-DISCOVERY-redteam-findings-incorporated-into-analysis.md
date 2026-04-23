---
type: DISCOVERY
date: 2026-04-22
created_at: 2026-04-22T12:30:00Z
author: agent
session_id: dedollarization-supplychain-2026-04-22
session_turn: 7
project: dedollarization-supplychain
topic: Red team findings incorporated — probabilities adjusted, source quality flagged, missing variables added
phase: analyze
tags:
  [redteam, probability-adjustment, source-quality, capital-account, us-fiscal]
---

## Discovery: Red Team Findings Incorporated into Analysis

**What was done**: Red team findings from the `/redteam` phase were fed back into the analysis documents. The following changes were applied:

### Probabilities Corrected (from → to)

- Scenario A (10% dedollarized): 65% → **80%**
- Scenario B (30% dedollarized): 25% → **17%**
- Scenario C (50%+ dedollarized): 10% → **3%**

### Source Quality Flag Added

The Saudi petrodollar cancellation claim — sourced from a Fortune tabloid report — was flagged with a source caveat. Red team noted the behavioral contradiction: Saudi Arabia simultaneously issued record $55B in dollar debt while reportedly canceling the petrodollar arrangement. The directional signal is credible, but the magnitude of the claim is not.

### Missing Variables Added to Executive Summary

Four variables identified by red team as absent from the base analysis:

1. **US fiscal trajectory** — the single largest swing factor; a fiscal crisis would make the systemic scenario far more likely
2. **Capital account convertibility** — binding structural ceiling on RMB internationalization that the original analysis underweighted
3. **Digital dollar / FedNow response** — US has not deployed cross-border CBDC infrastructure; wildcard if policy shifts
4. **Crisis dollar strengthening** — every global crisis produces dollar demand surges that temporarily reverse dedollarization; not captured in the scenario model

### Key Red Team Reasoning Preserved

- mBridge $55B = ~0.2% of global trade; real infrastructure but not yet economically significant
- BRICS internal contradictions mean unified alternative is years away; bilateral bypass is the real mechanism
- Gold 2025 accumulation (~630-860t) below the 1000+t peak of 2022-2024 — structural thesis not contradicted but cyclical component present

**Sources**: 00-redteam-report.md, red team journal entries 0005-0009

## For Discussion

1. Should the US fiscal trajectory be the primary input into a revised scenario model — above even the mBridge/capital flow indicators?
2. Does capital account convertibility for RMB represent the single largest ceiling on dedollarization, more than any infrastructure gap?
3. If the base case is now 80% (slow erosion), what specific leading indicators would move the probability meaningfully toward Scenario B?
