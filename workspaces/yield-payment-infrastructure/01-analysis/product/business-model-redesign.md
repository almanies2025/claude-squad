# FloatYield Business Model Redesign

## Executive Summary

| Flaw                             | Problem                                                      | Fix                                                            |
| -------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------- |
| Reconciliation Fee Misalignment  | Revenue scales with accounts; liability scales with deposits | Switch to basis points (bps) on Average Daily Balance (ADB)    |
| Sponsor Bank Structural Conflict | Bank bears FDIC risk; FloatYield captures upside             | Restructure bank economics via ILC charter or CUSO partnership |

---

## Flaw 1: Reconciliation Fee Misalignment

### Current State

- **Pricing**: $0.10–$0.25/account/month
- **Year 3 scale**: 1M accounts, $1B deposits
- **Revenue at Year 3**: $1.2M–$3.0M/year
- **Reconciliation liability**: ~$900K/year per $1B book (day-count mismatch)
- **Problem**: Revenue scales with _accounts_; liability scales with _deposits_. At Year 3, 30–75% of revenue is eaten by reconciliation losses.

### Day-Count Mismatch Explained

FloatYield credits accountholders daily using T-1 balances but collects actual/365 interest from the bank. The mismatch between "credited days" and "interest days" creates systematic leakage:

- FloatYield owes accountholders: (364/365) × nominal annual interest
- FloatYield receives from bank: (365/365) × nominal annual interest
- **Leakage**: ~0.27% of annual interest per $1B book = ~$900K/year

This liability _scales with float_, not accounts. The per-account fee model creates a structural misalignment.

### Proposed Fix: Basis Points on Average Daily Balance (ADB)

**The math at Year 3 scale:**

| Variable                  | Value                            |
| ------------------------- | -------------------------------- |
| Deposits (ADB)            | $1.0B–$2.0B (use $1.5B midpoint) |
| Treasury yield            | 4.5%                             |
| Annual interest generated | $45M–$90M                        |
| FloatYield target revenue | $4M–$10M/year                    |
| Reconcilation liability   | ~$900K/year per $1B book         |

**Solving for required bps:**

```
Required bps = Target Revenue / ADB

At $4M target:  $4M / $1,500M = 0.00267 = 2.67 bps
At $10M target: $10M / $1,500M = 0.00667 = 6.67 bps
```

**Recommended fee: 50 bps on ADB per year**

| Metric                               | Calculation     | Value             |
| ------------------------------------ | --------------- | ----------------- |
| Revenue at 50 bps × $1.5B ADB        | 0.005 × $1.5B   | **$7.5M/year**    |
| Reconciliation liability             | ~$900K × 1.5    | $1.35M/year       |
| **Net revenue after reconciliation** | $7.5M – $1.35M  | **$6.15M/year**   |
| Margin on liability                  | $6.15M / $1.35M | **4.6× coverage** |

### Does This Align Revenue with Liability?

**YES.** Both revenue and reconciliation liability now scale with float:

- Revenue: 50 bps × ADB
- Liability: ~60 bps × $1B book (900K/1B = 0.0009 = 90 bps... wait)

Let me recalculate. The reconciliation liability is $900K per $1B per year:

```
Liability rate = $900K / $1B = 0.0009 = 90 bps per $1B book
```

At $1.5B: liability = 90 bps × 1.5 = $1.35M

With 50 bps revenue on $1.5B = $7.5M

**Coverage ratio: $7.5M / $1.35M = 5.6×**

The revenue-to-liability ratio is constant regardless of scale. This is the key alignment property.

### Proposed Fee Schedule

| Tier   | ADB Threshold | Fee (bps/year) | Rationale                        |
| ------ | ------------- | -------------- | -------------------------------- |
| Pilot  | <$50M         | 75 bps         | Cover setup costs; low scale     |
| Growth | $50M–$500M    | 60 bps         | Scaling efficiency               |
| Scale  | >$500M        | 50 bps         | Volume discount; lower unit risk |

### Flaw 1 Conclusion

Switching from per-account pricing to bps on ADB:

1. Aligns revenue with liability (both scale with float)
2. Generates $7.5M/year at Year 3 scale vs. $1.2–3M under current model
3. Provides 5.6× coverage of reconciliation liability
4. Scales gracefully: more deposits = more revenue, more liability, constant margin

---

## Flaw 2: Sponsor Bank Structural Conflict

### Current State

- Sponsor bank bears: FDIC exposure, compliance burden, regulatory risk
- FloatYield captures: Platform fees, most economic upside
- At scale ($20–50M/year platform value), bank has strong incentive to renegotiate or terminate
- Termination = existential threat to FloatYield

### Evaluation Framework

For each option, assess:

- **Cost**: Capital, fees, ongoing expenses
- **Timeline**: How fast can it be implemented?
- **Regulatory feasibility**: Can this actually be done?
- **Termination risk**: Does this actually solve the renegotiation/termination problem?

---

### Option A: Equity Stake Model

**Mechanism**: Bank takes 5–10% equity in FloatYield in exchange for favorable Program Manager Agreement terms.

| Dimension                  | Assessment                                                                                                                                                                                           |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Cost**                   | Dilution of 5–10%; opportunity cost of equity                                                                                                                                                        |
| **Timeline**               | 3–6 months for term sheet and closing                                                                                                                                                                |
| **Regulatory feasibility** | Straightforward; no regulatory approval needed for equity deal                                                                                                                                       |
| **Termination risk**       | **Partially mitigated.** Bank now shares upside, but can still terminate. Termination destroys equity value, but bank may calculate that renegotiation captures more value than equity appreciation. |

**Verdict**: Does not fully solve termination risk. Bank can still force renegotiation; equity stake adds cost but not structural protection.

---

### Option B: CUSO Structure (Credit Union Service Organization)

**Mechanism**: FloatYield partners with credit unions (not banks) as the deposit-taking counterparty. Credit unions are:

- NCUA-insured (not FDIC)
- Already have compliance infrastructure
- Not subject to the same safety-and-soundness incentives as banks

| Dimension                  | Assessment                                                                                                                                               |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Cost**                   | Partnership structure; potentially lower than ILC charter                                                                                                |
| **Timeline**               | 6–12 months to establish CUSO partnership network                                                                                                        |
| **Regulatory feasibility** | High. CUSOs are well-established regulatory framework.                                                                                                   |
| **Termination risk**       | **Low.** Credit unions have different incentive structure — they benefit from loanable deposits and don't face the same "too-big-to-terminate" pressure. |

**Economic viability**: Credit union deposit base is ~$1.3T nationally. A CUSO partnership capturing 1% = $13B potential deposits. At 50 bps, this = $65M potential annual revenue.

**Verdict**: Strong option. CUSO structure removes bank dependency entirely, leverages existing regulatory framework, and aligns with credit union business model.

---

### Option C: Industrial Loan Company (ILC) Charter

**Mechanism**: FloatYield obtains its own depository institution charter (available in UT, SD, NV). No Sponsor Bank needed.

| Dimension                  | Assessment                                                                       |
| -------------------------- | -------------------------------------------------------------------------------- |
| **Cost**                   | $10M+ minimum capital; FDIC insurance; compliance infrastructure                 |
| **Timeline**               | 18–36 months for charter approval                                                |
| **Regulatory feasibility** | Moderate. ILC charters are scrutinized; Fed and FDIC both have input.            |
| **Termination risk**       | **Eliminated.** FloatYield holds its own charter; no external bank relationship. |

**Requirements**:

- Minimum capital: $10M–$50M depending on state and anticipated scale
- FDIC insurance application
- Regulatory examination capability
- Board composition requirements

**Verdict**: Most durable solution, but highest cost and longest timeline. Best for long-term strategic independence.

---

### Option D: Contractual Revenue Share

**Mechanism**: Replace fixed Program Manager fees with 20–30% share of platform gross margin.

| Dimension                  | Assessment                                                                                                                                                                 |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Cost**                   | FloatYield keeps 70–80% of margin vs. 100% currently                                                                                                                       |
| **Timeline**               | 1–3 months for contract renegotiation                                                                                                                                      |
| **Regulatory feasibility** | Straightforward if both parties agree                                                                                                                                      |
| **Termination risk**       | **Partially mitigated.** Bank now benefits from FloatYield's success, but renegotiation leverage remains. If FloatYield becomes very valuable, bank can still demand more. |

**Unit economics check**:

- At Year 3: $7.5M gross margin (from Flaw 1 fix)
- FloatYield share (70%): $5.25M
- Bank share (30%): $2.25M

This gives bank $2.25M/year at Year 3 — meaningful but not transformative. May not be enough to prevent renegotiation pressure at higher scales.

**Verdict**: Quick fix, but doesn't structurally solve the incentive problem long-term.

---

### Option Comparison Matrix

| Option           | Cost                | Timeline     | Regulatory Feasibility | Termination Risk Solved? |
| ---------------- | ------------------- | ------------ | ---------------------- | ------------------------ |
| A: Equity Stake  | Dilution 5–10%      | 3–6 months   | High                   | Partially                |
| B: CUSO          | Partnership model   | 6–12 months  | High                   | Mostly                   |
| C: ILC Charter   | $10M+ capital       | 18–36 months | Moderate               | Yes                      |
| D: Revenue Share | 20–30% margin share | 1–3 months   | High                   | Partially                |

---

## Recommendations

### Fee Model Fix (Flaw 1)

**Use: 50 bps on ADB per year, tiered by scale**

**Why**:

- Aligns revenue with liability (both scale with float)
- Generates $7.5M/year at Year 3 scale (vs. $1.2–3M currently)
- Provides 5.6× coverage of reconciliation liability
- Tiered pricing protects early-stage economics while rewarding scale

### Bank Conflict Fix (Flaw 2)

**Use: CUSO Structure (Option B) as primary, ILC Charter (Option C) as long-term goal**

**Why**:

- CUSO removes bank dependency within 6–12 months
- Existing regulatory framework (NCUA)
- Credit unions have complementary business model (need loanable deposits)
- No capital raise required (partnership vs. charter)
- ILC charter as 24–36 month strategic objective for full independence

**Immediate action**: Begin credit union partnership discussions while current sponsor bank agreement is in place. The goal is to migrate to CUSO structure before Year 3 scale triggers renegotiation pressure.

---

## Revised Unit Economics (with fixes applied)

### Year 1–5 Projections

| Year | Accounts | ADB   | Fee (bps) | Revenue | Reconciliation Liability | Net Revenue |
| ---- | -------- | ----- | --------- | ------- | ------------------------ | ----------- |
| 1    | 50K      | $100M | 75        | $750K   | $90K                     | $660K       |
| 2    | 200K     | $400M | 65        | $2.6M   | $360K                    | $2.24M      |
| 3    | 1M       | $1.5B | 50        | $7.5M   | $1.35M                   | $6.15M      |
| 4    | 2M       | $2.5B | 50        | $12.5M  | $2.25M                   | $10.25M     |
| 5    | 3M       | $4B   | 50        | $20M    | $3.6M                    | $16.4M      |

### Bank Economics Under CUSO Model

| Metric                                                      | Year 3                     | Year 5 |
| ----------------------------------------------------------- | -------------------------- | ------ |
| FloatYield net revenue                                      | $6.15M                     | $16.4M |
| CUSO partnership cost (10% of revenue)                      | $750K                      | $2M    |
| FloatYield net after partnership                            | $5.4M                      | $14.4M |
| Credit union benefit (spread on $1.5B/$4B deposits at 4.5%) | $67.5M/$180M interest pool | —      |

**Key insight**: Credit union earns the full interest spread ($45–90M/year at Year 3) on deposits it originates. FloatYield earns platform fees. Aligned incentives — credit union wants more deposits; FloatYield wants more accounts.

### Break-Even Analysis

| Scenario         | Investment                  | Year 3 Net Revenue             | Payback  |
| ---------------- | --------------------------- | ------------------------------ | -------- |
| CUSO Partnership | ~$500K (legal + setup)      | $5.4M                          | < 1 year |
| ILC Charter      | $10M (capital + regulatory) | $5.4M (but no partnership cut) | ~2 years |

---

## Risk Factors

1. **CUSO adoption speed**: If credit union partnerships take >18 months, sponsor bank renegotiation pressure may hit first
2. **Regulatory change**: ILC charter availability has varied by administration; monitor regulatory environment
3. **Yield environment**: At lower interest rates, reconciliation liability stays constant while revenue opportunity shrinks
4. **Scale concentration**: If 80% of deposits come from one credit union partner, termination risk shifts to that relationship

---

## Next Steps

1. **Immediate (0–3 months)**: Model CUSO economics with 2–3 credit union prospects; get LOIs
2. **Short-term (3–6 months)**: Negotiate CUSO framework agreement; begin ILC charter feasibility analysis
3. **Medium-term (6–12 months)**: Execute CUSO partnerships; file ILC application if board approves
4. **Long-term (18–36 months)**: ILC charter approval (if pursued); full migration from sponsor bank model
