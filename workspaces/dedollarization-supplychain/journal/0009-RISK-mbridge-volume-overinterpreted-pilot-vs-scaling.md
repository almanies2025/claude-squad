---
type: RISK
date: 2026-04-22
created_at: 2026-04-22T12:04:00Z
author: agent
session_id: dedollarization-supplychain-2026-04-22
session_turn: 12
project: dedollarization-supplychain
topic: mBridge $55B cumulative volume overinterpreted — 0.2% of global trade is pilot scale, not early-stage adoption
phase: redteam
tags:
  [
    mbridge,
    volume-misinterpretation,
    pilot-vs-scaling,
    0.2percent,
    infrastructure-adoption,
  ]
---

## RISK: mBridge Volume Overinterpreted as Early-Stage Adoption When It Represents Pilot Scale

**What was found**: The analysis at 02-payment-infrastructure.md and 00-executive-summary.md uses mBridge's $55B cumulative transaction volume and 2,500x growth since 2022 as evidence of "early-stage adoption" suggesting an exponential adoption curve.

**The volume context**:

- $55B cumulative mBridge transactions since 2022
- Annual global trade: ~$32 trillion
- $55B / $32T = 0.17% of annual global trade
- Daily global FX settlement: ~$7.5 trillion (BIS data)
- mBridge cumulative = ~2 days of global FX settlement

**The framing error**: "2,500x growth since 2022" implies exponential adoption. But this growth is from a near-zero base — it could represent 10 pilot transactions in 2022 and 4,000 pilot transactions in 2026. Growth rate from near-zero is statistically meaningless.

**What we don't know**:

1. What is the actual transaction composition? (Real trade settlements vs. central bank pilot exercises?)
2. Are mBridge participants using it for primary settlement or just testing?
3. What is the repeat usage rate? (Are participants using it consistently or sampling once?)
4. What is the average transaction size? (4,000 transactions could be small-value tests)
5. Why has Russia (a major BRICS member and SWIFT-sanctioned country) NOT joined mBridge?

**The critical question the analysis avoids**: If mBridge is genuinely gaining adoption, why hasn't Russia joined? Russia was expelled from SWIFT and has the strongest motivation to use alternatives. Its absence from mBridge suggests the platform has limitations (political, technical, or participant acceptance) that the analysis ignores.

**What "early-stage adoption" would look like**:

- mBridge transaction volume growing 100%+ year-over-year for 3+ consecutive years
- Non-BIS-country participants joining (India, Indonesia absent)
- Russia participating or SPFS interoperability demonstrated
- Commercial banks (not just central banks) as primary users
- Transaction sizes increasing (not just transaction count)

## For Discussion

1. Should mBridge be treated as "early-stage adoption" or "successful pilot"? What is the operational distinction in practice?
2. Russia's absence from mBridge (despite being SWIFT-sanctioned and motivated) is the most important data point. What constraints prevent Russia from using mBridge?
3. If mBridge were truly on an exponential adoption curve, what observable indicators would appear in 2026-2027 data?
