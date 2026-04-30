---
type: RISK
date: 2026-04-30
created_at: 2026-04-30T00:00:00Z
author: agent
session_id: deep-analysis-session
session_turn: 5
project: mbridge-redteam
topic: Buyer incentive mismatch — disadvantaged parties won't pay to quantify their disadvantage
phase: redteam
tags:
  [
    product-market-fit,
    buyer-incentive,
    cny-dominance,
    commercial-model,
    fatal-flaw,
  ]
---

## Risk

The product's most compelling narrative (CNY structural dominance) is actively harmful to three of the four parties in the simulation. The parties who most need this tool (CBUAE, BOT — structurally disadvantaged by CNY dominance) are the parties least likely to pay for it.

**The incentive inversion**:

| Party               | CNY Position     | Would They Buy This? | Why                                                                             |
| ------------------- | ---------------- | -------------------- | ------------------------------------------------------------------------------- |
| PBOC                | Dominant         | No                   | Already knows, no problem to solve                                              |
| HKMA                | Bridge, benefits | No                   | Tool confirms CNY dominance, not HKMA-specific advantage                        |
| CBUAE               | Disadvantaged    | Unlikely             | Tool quantifies their currency's weakness — embarrassing, not useful            |
| BOT                 | Disadvantaged    | Unlikely             | Same as CBUAE — structural disadvantage is a policy problem, not a tool problem |
| Correspondent Banks | Variable         | Maybe                | Would pay for optimization, but only if they have mBridge access and volume     |

**The core problem**: CBUAE and BOT using this tool to analyze AED/THB settlement paths is essentially paying a third party to confirm their currencies are structurally unusable on mBridge. This is not a pain point — it is a political liability. No treasury director presents this analysis to their board.

**The survivor bias in buyers**: The only buyer without a structural conflict is PBOC/HKMA. But PBOC/HKMA have the internal capability to build this themselves and no external motivation to buy.

## For Discussion

- Is there a reframing that makes CBUAE or BOT buyers rather than subjects of the analysis? (e.g., "here is how you can increase your mBridge settlement success rate" — but this requires real data they won't share)
- Could the product be positioned for non-mBridge use cases (e.g., general multi-CBDC corridor analysis) where CNY dominance is not the central narrative?
- Is there a third-party beneficiary who would pay without the incentive problem? (e.g., BIS paying for a network-wide diagnostic tool)
- What if the product were free and the monetization was in publishing the aggregate findings? Who would pay for that?
