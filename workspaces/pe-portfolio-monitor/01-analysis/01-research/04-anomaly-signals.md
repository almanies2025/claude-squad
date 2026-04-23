# Anomaly Signals — PE Portfolio Monitoring

## Signal Ranking Framework

Each KPI rated 1–5 on three axes:

- **Predictive**: how strongly the signal forecasts distress
- **Earliness**: how early the signal appears before the distress event
- **Computability**: how easy to derive from accounting data

**Composite score** = (Predictive × 2) + Earliness + Computability (max 20; Predictive double-weighted)

## Tier 1 — Must-Have Signals (v1)

| #   | Signal                                      | Pred | Early | Compute | Score  | Notes                                                                                                                     |
| --- | ------------------------------------------- | ---- | ----- | ------- | ------ | ------------------------------------------------------------------------------------------------------------------------- |
| 1   | **DSO trend (Days Sales Outstanding)**      | 5    | 5     | 5       | **20** | Rising DSO = customers paying slower = distress 3–6 months out. Pure AR/revenue from GL. Gold-standard leading indicator. |
| 2   | **Gross margin compression (rolling 3-mo)** | 5    | 4     | 5       | **19** | COGS inflation, pricing erosion, mix shift. Directly visible in P&L. Deteriorates ahead of EBITDA.                        |
| 3   | **Cash runway**                             | 5    | 5     | 4       | **19** | Cash balance ÷ trailing-3-mo net burn. Covenant and solvency alarm.                                                       |
| 4   | **Working capital % of revenue**            | 5    | 4     | 4       | **18** | AR + inventory − AP. Creeping OWC = cash trapped. Strong PE-operator signal.                                              |
| 5   | **EBITDA margin trend (rolling 3-mo)**      | 5    | 3     | 5       | **18** | Lagging vs. gross margin but essential — it's the covenant metric.                                                        |
| 6   | **Headcount-to-revenue ratio drift**        | 4    | 5     | 4       | **17** | Revenue per FTE declining = overhiring or revenue stalling. Needs headcount data (Finch/HRIS or GL salary lines).         |

## Tier 2 — Secondary Signals (v1.5)

| #   | Signal                                        | Pred | Early | Compute | Score  | Notes                                                                              |
| --- | --------------------------------------------- | ---- | ----- | ------- | ------ | ---------------------------------------------------------------------------------- |
| 7   | **DPO (Days Payable Outstanding)**            | 4    | 4     | 5       | **17** | Stretching vendors is an early liquidity tell. Pair with DSO and cash-on-hand.     |
| 8   | **Inventory turns**                           | 4    | 4     | 4       | **16** | Slowing turns = demand weakness or overbuying. Only for ~30% of portfolios.        |
| 9   | **Customer concentration (top-10 revenue %)** | 4    | 5     | 3       | **16** | Needs subledger access, not just GL. Top-10 climbing = fragile.                    |
| 10  | **Churn / Net Revenue Retention (SaaS)**      | 5    | 4     | 2       | **16** | Gold metric for SaaS portcos. Requires subscription subledger (Stripe, ChargeBee). |

## Tier 3 — Context Signals (v2)

| #   | Signal                                          | Notes                                                                                                                |
| --- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| 11  | **Covenant headroom**                           | Requires debt schedule + covenant terms per portco. High-value but onboarding-heavy.                                 |
| 12  | **Accrual-to-cash EBITDA reconciliation delta** | If reported EBITDA diverges from cash EBITDA, earnings quality is degrading. PE-operator favorite. Hard to automate. |
| 13  | **CAC payback / CAC ratio (SaaS)**              | Needs S&M classification + new customer data.                                                                        |
| 14  | **Revenue growth trend (YoY and sequential)**   | Lagging; value is pairing with gross margin (growth-at-what-cost).                                                   |

## Signals to Skip Entirely

- Employee NPS / culture signals — not derivable from accounting data
- Net Promoter Score / customer sentiment — external data, separate integration
- Web traffic / digital engagement — not a distress signal
- Social media listening — too noisy

## The Multi-Signal Insight

Individual threshold alerts ("EBITDA dropped 10%") are table stakes every incumbent offers. The real differentiation is **co-occurring signals as a compound alert**:

> "PortCo X shows DSO up 12 days, gross margin down 150 bps, and headcount-to-revenue ratio worsening over 8 weeks. Historical pattern: this combination preceded a covenant breach in 60% of similar situations."

Single-signal alerts create noise; co-occurring signals create signal. This is the correct application of ML in v2 — **pattern classification across combined signals**, not forecasting any single metric.

## Recommended v1 Signal Set

Ship signals 1–6. They:

- Cover the core distress patterns PE operators actually care about
- Compute cleanly from GL + AR + AP subledgers (no exotic data required)
- Each has a clear one-sentence operating-partner narrative
- Work on day one with no historical training data
