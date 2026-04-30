# FloatYield Unit Economics & Yield Reconciliation Red Team

## Executive Summary

**Complexity Score: Complex** — The yield reconciliation problem is commercially dangerous, the unit economics are structurally thin, and the interest rate risk is existential rather than theoretical.

**Critical Finding**: The 2bp/day reconciliation divergence on a $1B book compounds into a $600K/month dispute that will consume legal and finance teams for years. At $100K–250K/month revenue on that same $1B book, FloatYield is earning a fee representing 0.01–0.025% of the assets it is reconciling — a ratio that does not survive a single contested dispute.

---

## 1. Yield Reconciliation: The Compounding Liability

### The Mathematics Are Damning

The stated 1–3bp daily divergence sounds manageable in isolation. It is not.

| Scenario | Book Size | Daily Divergence | 30-Day Cumulative | 90-Day Cumulative |
| -------- | --------- | ---------------- | ----------------- | ----------------- |
| Base     | $1B       | 1bp              | $300K             | $900K             |
| Mid      | $1B       | 2bp              | $600K             | $1.8M             |
| Stress   | $1B       | 3bp              | $900K             | $2.7M             |

**At 90 days, a $1B book has a $1.8M–2.7M unresolved discrepancy.** This is not a rounding error. This is a material liability that will require commercial negotiation, potentially legal escalation, and almost certainly will damage the sponsor bank relationship permanently.

### The Day-Count Convention Is Not a Technicality

FloatYield accrues: `principal × rate × (days/365)`
Treasuries accrue: `principal × rate × (actual days/actual days)`

This is not a rounding difference. This is a structurally different accrual method that will _always_ produce divergence when:

- Any month has >28 days (all of them)
- Any leap year (Feb 29 vs. Feb 28 creates a 1-day perpetual offset)

The 1–3bp daily range masks the fact that the divergence is **non-random** — it systematically over- or under-accrues depending on the rate environment and calendar. A $1B book at 4.5% Treasury with 30/360 vs actual/actual creates a 0.09% annual difference, not 1–3bp.

**Actual expected annual divergence**: ~$900K/year on $1B at 4.5% (0.09% of notional). This is not a 1–3bp daily problem. This is a $900K/year problem.

### The Tolerance Threshold Is a Ticking Clock

Contractually agreeing a tolerance threshold does not resolve the underlying economics — it defers the reckoning.

**Who absorbs the difference within tolerance?**

- If FloatYield absorbs it: At 2bp/day on $1B over 30 days = $600K absorbed by FloatYield. This wipes out 2–6 months of platform fee revenue.
- If the bank absorbs it: Banks will eventually notice and renegotiate the contract, or exit the relationship.
- If passed to end-users: Compliance risk. Regulators do not look kindly on fractional yield discrepancies being silently distributed.

**What happens when tolerance is breached?** The contract must define a resolution mechanism. If it defaults to litigation, both parties know the cost exceeds the dispute. The practical result: commercial negotiation under duress, with FloatYield having structural disadvantage (they need the bank relationship more than the bank needs FloatYield).

**RISK-001**: Daily reconciliation divergence compounds into material liability. At $1B book, 90-day cumulative divergence = $1.8–2.7M. Tolerance thresholds defer but do not resolve this liability.

---

## 2. Reconciliation Resolution: Commercial Veto Points

### The Contractual Solution Has Holes

The proposed resolution — agree a tolerance threshold in the contract — assumes:

1. The threshold is set correctly (requires predicting 3 years of rate environments)
2. Both parties accept the loss within tolerance (they won't quietly)
3. Breaches trigger clean resolution (they won't — they'll trigger renegotiation)

### What Happens When Tolerance Is Breached

| Trigger                         | Likely Outcome                    | FloatYield Impact                       |
| ------------------------------- | --------------------------------- | --------------------------------------- |
| 2bp/day for 45 days on $1B book | Bank demands retrocession         | $900K liability                         |
| Sustained 3bp divergence        | Contract renegotiation threat     | Either accept loss or lose the customer |
| Multiple banks simultaneously   | Systemic issue, class-action risk | Existential                             |

**The asymmetry is structural**: A sponsor bank has options (build internally, switch to competitor, renegotiate). FloatYield has one product, one market, and a cost structure built on the assumption of $0.10–0.25/account/month.

**GAP-001**: No defined resolution mechanism for when tolerance is breached. The contract draft must specify: who absorbs the variance, what triggers renegotiation, and what the exit terms are.

---

## 3. Unit Economics at Scale: Thin Margins, Large Fixed Costs

### Revenue Model

| Accounts  | Monthly Fee | Annual Revenue |
| --------- | ----------- | -------------- |
| 100,000   | $0.10       | $120K          |
| 100,000   | $0.25       | $300K          |
| 1,000,000 | $0.10       | $1.2M          |
| 1,000,000 | $0.25       | $3.0M          |

**Year 3 SOM**: 1M accounts × $0.10–0.25/month = **$1.2M–3.0M annual revenue**

### What Does It Cost to Run a Regulated Financial Infrastructure?

| Cost Category                                                 | Estimated Annual Cost | Notes                                   |
| ------------------------------------------------------------- | --------------------- | --------------------------------------- |
| Regulatory compliance (SOC 2, FFIEC, state money-transmitter) | $200K–500K            | Minimum for B2B fintech infrastructure  |
| Treasury reconciliation ops (manual daily)                    | $150K–300K            | 1–2 FTE + legal support                 |
| Sponsor bank relationships                                    | $100K–200K            | Legal, compliance, relationship mgmt    |
| Fraud/AML monitoring                                          | $100K–250K            | Required for regulated payment accounts |
| Technology infrastructure                                     | $100K–200K            | AWS, security, uptime                   |
| **Total minimum fixed cost**                                  | **$650K–1.45M**       | Before any customer acquisition         |

**At Year 3 SOM ($1.2–3.0M revenue), FloatYield has $550K–2.35M gross margin.** This must cover:

- Sales and business development (banks and fintechs have long sales cycles: 6–18 months)
- Product development (regulatory changes require ongoing development)
- Legal (defending the reconciliation disputes)
- Capital (regulatory capital requirements for money-transmitter license in some states)

**Net margin before growth investment**: Potentially negative or near-zero for years 1–3.

### The Unit Economics Do Not Scale Linearly

The $0.10–0.25/account/month fee is modeled as pure margin. It is not:

- Each new account requires onboarding, compliance screening, and ongoing monitoring
- Reconciliation cost is **per-book**, not per-account — the $1B book reconciliation costs the same whether it holds 10K or 100K accounts
- Regulatory capital requirements scale with deposit volume, not account count

**RISK-002**: Unit economics at $0.10–0.25/account/month do not support the fixed cost base of a regulated financial infrastructure company. Revenue scales with account count; costs scale with deposit book size and regulatory requirements.

---

## 4. Interest Rate Risk: The Breakeven Analysis

### Rate Sensitivity

| Treasury Yield | FloatYield Spread Assumption | Bank Incentive       | FloatYield Viable?            |
| -------------- | ---------------------------- | -------------------- | ----------------------------- |
| 5.5%           | 4.5% + 100bp = 5.5%          | None (parity)        | No spread                     |
| 4.5%           | 4.5% + 100bp = 5.5%          | 100bp above Treasury | Strong                        |
| 3.5%           | 4.5% + 100bp = 5.5%          | 200bp above Treasury | Strong but rates falling      |
| 2.5%           | 4.5% + 100bp = 5.5%          | 300bp above Treasury | Banks may not need FloatYield |
| 1.5%           | 4.5% + 100bp = 5.5%          | 400bp above Treasury | Value prop collapses          |

### The Breakeven Question

If Treasury yields drop to 2%:

- Banks can offer 3–4% on deposits and still have margin
- FloatYield's value proposition (enabling banks to offer competitive yield) diminishes
- Banks have less pressure to partner with FloatYield
- The platform fee ($0.10–0.25/account/month) becomes a larger portion of the bank's cost

**Breakeven rate for FloatYield's value proposition**: Approximately 3.5–4.0% Treasury. Below that, banks can build or buy alternatives more cheaply.

**RISK-003**: Interest rate environment is existential. At <3.5% Treasury, FloatYield's value proposition weakens materially. The current model assumes 4.5% Treasury — a 200bp drop to 2.5% Treasury fundamentally changes the commercial case.

---

## 5. Credit Risk: The Liability Cascade

### Who Bears Loss If Sponsor Bank Fails?

| Scenario                       | Who Loses                   | FloatYield Liable?                             |
| ------------------------------ | --------------------------- | ---------------------------------------------- |
| Sponsor Bank insolvency        | Depositors first, then FDIC | Potentially — depends on contract              |
| Treasury reserves lose value   | Depositors                  | Potentially — if FloatYield held reserves      |
| FloatYield operational failure | Banks' end-customers        | Yes — reputational and potentially contractual |

**The critical gap**: FloatYield is offering infrastructure that sits between the bank and the end-user. If the sponsor bank fails, FloatYield's bank/fintech partners will look to FloatYield for answers. The contracts likely do not specify this liability clearly (MVP focus = getting the product working, not liability allocation).

**GAP-002**: No defined credit risk waterfall in the architecture. Who absorbs loss if the sponsor bank fails? If FloatYield is holding any intermediate balances, they may be deemed to have custody liability.

### Treasury Reserve Risk

If FloatYield is in the flow of funds (even as a pass-through), there may be moments where FloatYield holds Treasury proceeds before distribution. In a stress scenario, these balances could be at risk.

**RISK-004**: FloatYield may have implicit custody liability that is not captured in the current architecture or contracts.

---

## 6. Competitive Moat: Why Doesn't JPMorgan Build This?

### The Replication Threat Is Real

If FloatYield proves that:

1. Banks will pay $0.10–0.25/account/month for yield infrastructure
2. The reconciliation problem is solvable with a tolerance threshold
3. End-users will accept interest-bearing payment accounts

Then the logical response from a JPMorgan, Bank of America, or Wells Fargo is: **"We'll build that internally."**

### What Stops a Large Bank From Replicating?

| Moat Factor                   | Assessment                                                       | Strength                                            |
| ----------------------------- | ---------------------------------------------------------------- | --------------------------------------------------- |
| Regulatory licensing          | FloatYield has money-transmitter licenses; bank has bank charter | Neutral — both have regulatory path                 |
| Treasury management expertise | Banks have this internally                                       | Weak — banks already know how to manage yield       |
| Reconciliation infrastructure | This is the "secret sauce"                                       | Weak — it's a tolerance threshold, not a patent     |
| Relationships with fintechs   | FloatYield's only real asset                                     | Moderate — but easily poached with better economics |
| Network effects               | More banks = more fintechs = more banks                          | None yet — pure B2B with no network effects         |

**The honest assessment**: FloatYield's moat is narrow and fragile. It is built on:

1. First-mover advantage in offering this as a B2B service (temporary)
2. Existing relationships (relationship-specific, not structural)
3. The reconciliation tolerance framework (contractual, not proprietary)

A large bank with 6 months of development and a small team could replicate the core functionality. The regulatory path takes longer (12–18 months), but a large bank can parallel-track that work.

**RISK-005**: No durable competitive moat. The primary moat (relationships) is the first thing a well-capitalized competitor can buy.

---

## 7. The Fatal Flaws

### Fatal Flaw #1: The Reconciliation Liability Exceeds the Revenue Opportunity

At $1B book, the annual reconciliation liability is ~$900K/year (0.09% of notional). The annual platform revenue at 1M accounts is $1.2–3.0M/year. If FloatYield absorbs even 30% of reconciliation losses, it costs $270K/year — 9–22% of gross revenue.

But the reconciliation loss is **not distributed evenly**. It hits all banks simultaneously in a rate environment shift. In a falling rate environment (the existential risk), banks are already under margin pressure and will scrutinize every discrepancy. The reconciliation disputes will be simultaneous, large, and politically toxic.

**This is not a manageable risk. This is an existential liability.**

### Fatal Flaw #2: Unit Economics Do Not Support Regulatory Infrastructure

$1.2–3.0M/year in revenue cannot sustain a regulated financial infrastructure company. Regulatory compliance alone costs $200K–500K/year. The reconciliation operations cost another $150K–300K/year. Technology infrastructure is $100K–200K/year.

**Total minimum cost: $650K–1.45M/year, leaving $550K–1.55M for everything else** (sales, product, legal disputes, capital reserves). This is not a venture-scale business at Year 3 SOM.

### Fatal Flaw #3: The Interest Rate Dependency Creates a One-Way Door

FloatYield's business is only viable in a specific interest rate environment (Treasury >3.5%). The moment rates fall below that, the business model weakens. But FloatYield is building infrastructure that requires years of investment and regulatory work. By the time the product is mature, the rate environment may have changed.

**This is a timing bet disguised as a infrastructure business.**

---

## Risk Register

| Risk ID  | Description                                                               | Likelihood | Impact       | Mitigation                                                                      |
| -------- | ------------------------------------------------------------------------- | ---------- | ------------ | ------------------------------------------------------------------------------- |
| RISK-001 | Reconciliation divergence creates material liability ($900K+/year on $1B) | High       | Critical     | Pre-fund reconciliation reserve; restructure fee to absorb variance             |
| RISK-002 | Unit economics cannot support regulated infrastructure fixed costs        | High       | Critical     | Shift to variable fee structure tied to deposit notional                        |
| RISK-003 | Interest rate decline (<3.5% Treasury) destroys value proposition         | Medium     | Critical     | Diversify into fee-based services; hedge rate exposure                          |
| RISK-004 | Credit risk liability if sponsor bank fails                               | Low-Medium | Catastrophic | Explicit liability limitation in all contracts; no intermediate balances        |
| RISK-005 | Large bank replicates internally                                          | Medium     | High         | Accelerate network effects; build switching costs; patent tolerance methodology |
| RISK-006 | Regulatory changes require re-architecture                                | Medium     | High         | Modular design; regulatory monitoring function                                  |

---

## Gap Register

| Gap ID  | Description                                                                         | Impact | Required Action                                                                                      |
| ------- | ----------------------------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------- |
| GAP-001 | No resolution mechanism defined for tolerance breach                                | High   | Add explicit contract language specifying: absorption terms, renegotiation triggers, exit provisions |
| GAP-002 | Credit risk waterfall not defined                                                   | High   | Legal review of liability exposure; add explicit liability limitation clause                         |
| GAP-003 | Fee structure not tied to notional — revenue is per-account, not per-dollar-managed | Medium | Consider hybrid model: base fee + basis-point share of deposits managed                              |
| GAP-004 | No stress testing of reconciliation model under rate shocks                         | Medium | Build stochastic reconciliation model; publish tolerance methodology                                 |

---

## Cross-Reference Audit

- **SPEC.md**: Unit economics section does not account for reconciliation operational costs or regulatory fixed costs. Revenue model is optimistic.
- **Reconciliation architecture**: The tolerance threshold is presented as a solution but is actually a liability deferral mechanism.
- **Sponsor Bank agreement (assumed)**: No liability waterfall defined; likely silent on credit risk allocation.

---

## Decision Points

1. **Can the reconciliation liability be restructured as a pass-through?** If FloatYield charges a bps fee on deposits rather than a per-account fee, the reconciliation liability can be economically neutral. Is this commercially viable?

2. **Is the regulatory cost estimate ($650K–1.45M/year) accurate?** This is the threshold question. If actual costs are higher, the business model does not work.

3. **What is the path to $10M ARR?** At $1.2–3.0M Year 3 revenue, FloatYield is not venture-scale. What is the growth model?

4. **Is the rate environment bet acceptable?** Building infrastructure for a 4.5% Treasury environment in 2026-2027 may mean the business is obsolete by the time it reaches scale if rates fall.

---

## Conclusion

FloatYield's fundamental problem is a **structural mismatch between revenue and liability**. The platform earns $0.10–0.25/account/month. The reconciliation liability is $900K/year on a $1B book — not per-account, per-book. At scale, this liability scales with deposits; revenue scales with accounts.

The business only works if:

1. The reconciliation tolerance is effectively zero (not realistic)
2. The fee structure is restructured to bps of deposits (not the current model)
3. The rate environment stays above 3.5% Treasury (not guaranteed)

**Recommendation**: Do not proceed without restructuring the fee model to align incentives. The current per-account model creates a structurally adverse risk profile where liability scales with success (more deposits = more liability) while revenue does not scale proportionally.
