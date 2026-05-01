---
type: CONNECTION
date: 2026-05-01
created_at: 2026-05-01T08:00:00Z
author: agent
session_id: current
session_turn: 1
project: yield-payment-infrastructure
topic: Trust-plane reasoning patterns transferable to any B2B financial forecasting product
phase: codify
tags:
  [trust-plane, ci-intervals, reconciliation-gap, model-evaluation, patterns]
---

## What Transfers to the Next Domain

FloatYield produced five patterns worth carrying forward into any B2B financial forecasting product.

---

## Pattern 1: The Three-Question Trust-Plane Framework

**What it is**: Before deploying any model that affects financial distributions, answer three questions:

1. **Transparency** — what does it rely on most heavily; can ops explain a specific prediction?
2. **Robustness** — where does it fail worst; which conditions break it?
3. **Safety** — silent failure dollar damage; who gets hurt; is the error asymmetric?

**Why it transfers**: Every B2B financial product has the same trust problem — a model outputs a number that becomes a partner obligation. The three-question filter is domain-agnostic.

**The CI interval ratio test**: For any model claiming prediction intervals, verify span(h=60)/span(h=7) equals the expected mathematical function (√h for random-walk processes, constant for ARIMA, h² for no-damping trend). If the ratio is wrong, the interval formula is wrong. This test would have caught the Naive double-scaling bug in 30 seconds.

---

## Pattern 2: Reconciliation Gap as the Primary Metric

**What it is**: The product deliverable is not "yield forecast" — it is **reconciliation accuracy**. Partners care whether FloatYield's calculated yield matches what the sponsor bank reports. The metric is the gap between those two numbers, not the raw forecast error.

`measured_gap_bps = mean(actual_yield - calculated_yield) × 365 / balance × 10000`

**Why it transfers**: Any B2B payment infrastructure product has the same structure — FloatYield calculates, bank reports, partner reconciles. The gap is the product. Forecast accuracy is only valuable insofar as it reduces the gap.

**The description must be dynamic**: "Measured gap" when you have enough history; "System reference" when you don't. Never show a measured number that isn't measured — that is how demos lose credibility with sophisticated partners.

---

## Pattern 3: Synthetic Data Warning Signs

**What it is**: Three symptoms that signal models are running on non-informative synthetic data:

- Balance is constant across all rows
- Rate is constant across all rows
- Identical autocorrelation structure across accounts (same phi, same sigma2)

**The test**: Change one seed, rerun ETL. If model outputs change — the models are forecasting your noise generator, not real yield dynamics.

**Why it transfers**: Any ML project that starts with synthetic data to bootstrap development will eventually run into this. The warning signs are recognizable early. The cure is either real data or explicitly accepting that the model is structurally unvalidated.

---

## Pattern 4: Rate Environment Blindness

**What it is**: Models that ignore the macro rate environment (Fed Funds, Treasury yields, scenario rates) will systematically misforecast after Fed meetings. The `rate_scenario` parameter in FloatYield sets the `scenario_description` in the API response — but none of the three models actually incorporate scenario rates into predictions.

**The problem**: The product claims to support stress/upside scenarios but the models don't use them. A partner reading "Stress scenario" in the UI sees a description with no corresponding change in the yield projection.

**Why it transfers**: Any yield product needs rate sensitivity. If the model doesn't know about Fed moves, it will be wrong precisely when the stakes are highest — immediately after a Fed announcement.

---

## Pattern 5: Deployment Gate as the Safety Case

**What it is**: Monitoring gates convert a model from a demo feature into a production system:

1. Reconciliation gap drift (5 bps / 10 bps)
2. Holt initialization spike (trend direction flip or >2× average)
3. Model vs Naive divergence (>20% at 30d)
4. ETL pipeline lag (>2 business days)

**Why it transfers**: The dollar damage table is the engagement tool. "If this silently misforecasts for a week at Year 3 scale, here is what happens and who absorbs it" — that is what gets a B2B partner's attention and what justifies the monitoring budget.

---

## What Does NOT Transfer

- **ARIMA(1,1,1) as the right model**: phi=-0.385 was specific to the synthetic data. Real yield data will have different phi structure. The model class transfers; the specific architecture does not.
- **Holt trend initialization from two endpoints**: This is a known fragility. Any production system should use a rolling window for trend initialization, not two endpoints.
- **The 1.23 bps system reference**: This is a FloatYield-specific normalized gap. The concept transfers (a known system reference for when measurement isn't available); the value does not.

---

## Codified As

- `workspaces/yield-payment-infrastructure/.claude/agents/trust-plane-reasoner.md` — `trust-plane-reasoner` agent
