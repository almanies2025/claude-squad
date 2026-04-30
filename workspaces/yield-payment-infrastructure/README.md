# FloatYield — Course Materials

**Yield-Bearing Payment Infrastructure** — A B2B platform enabling banks and fintechs to offer interest on payment accounts.

---

## Deliverables

### `yield_engine.py`
Python stdlib-only yield calculation engine with:
- `calculate_daily_yield(balance, rate, days)` — single day accrual
- `calculate_yield_series(balance, rate, days)` — series with total and daily breakdowns
- `simulate_treasury_accrual(balance, rate, days)` — actual/actual day-count for comparison
- `calculate_reconciliation_divergence(balance, rate, days)` — the core gap calculation
- `calculate_partner_fee(accounts, avg_balance, tier)` — tiered bps economics
- `run_scenario(deposit, rate, days)` — full scenario output

### `yield_cli.py`
Interactive cmd-based CLI with:
- `scenario [deposit [rate [days]]]` — yield + reconciliation analysis
- `partner [accounts [avg_balance]]` — tiered partner economics
- `compare [deposit [days]]` — Sponsor Bank vs CUSO vs FloatYield side-by-side
- `help [topic]` — explain yield accrual, reconciliation divergence, tiers, CUSO
- `quit` — exit

### `pitch_deck.html`
12-slide HTML presentation (keyboard navigation: arrow keys):
1. Title: FloatYield — Yield-Bearing Payment Infrastructure
2. The Problem: Banks earn 2-3% on your checking balance. You earn 0%.
3. The Solution: B2B infrastructure for interest-bearing accounts
4. How It Works: Customer → Bank → Treasury → Yield distribution
5. The Market: $50-80B float income; stablecoins proof of concept
6. Regulatory Path: Sponsor Bank (US) + EMI Partnership (EU)
7. The Structural Flaws: Reconciliation misalignment + Sponsor Bank conflict
8. The Fixes: Tiered bps pricing + CUSO structure
9. Unit Economics: Year 1-5 projections with tiered fees
10. Competitive Landscape: vs Stablecoins, vs Marcus, vs Unit/Column
11. Go-to-Market: First partner profile, pricing, timeline
12. Conclusion / Discussion

### `FloatYield_Report.md`
Comprehensive written report covering:
- Executive Summary
- Problem & Market (float income, TAM/SAM/SOM, competitive landscape)
- Product & Architecture (Sponsor Bank model, yield engine, reconciliation)
- Regulatory Framework (US Sponsor Bank, EU MiCA/EMI)
- Business Model Redesign (tiered bps, Year 1-5 projections)
- Red Team Analysis (flaws, fixes, remaining risks, capital sequencing)
- Go-to-Market
- Risk Register
- Conclusion

### `demo_test_run.txt`
Test output from running `yield_engine.py` with:
- Scenario: $1M deposit, 4.5%, 30 days → $10.11 reconciliation gap (1.23 bps annualized)
- Partner: 100K accounts, $2K avg balance → $1M-1.5M annual fee depending on tier

---

## How to Run the Demo

```bash
cd workspaces/yield-payment-infrastructure/05-materials

# Run scenario directly
python3 yield_engine.py --scenario --deposit 1000000 --rate 0.045 --days 30

# Run partner economics
python3 yield_engine.py --partner --accounts 100000 --avg-balance 2000

# Run interactive CLI
python3 yield_cli.py
# Then type: scenario 500000 0.05 60
# Or: compare 1000000 30
# Or: help reconciliation

# Open pitch deck in browser
open pitch_deck.html
# Navigate with arrow keys (← →) or spacebar
```

---

## Key Findings Summary

### The Core Problem
Banks earn $50-80B/year in float income on US checking deposits. Customers earn 0%. Stablecoins ($150B+ AUM) prove customers will shift for yield.

### The Structural Flaw
Original fee model: $0.10-0.25/account/month. Problem: **Revenue scales with accounts; liability scales with deposits**. At Year 3 with 1M accounts and $1B deposits, 30-75% of revenue is eaten by reconciliation losses.

### The Fix: Tiered bps on ADB

| Tier | ADB | Fee |
|------|-----|-----|
| Pilot | <$50M | 75 bps |
| Growth | $50-500M | 65 bps |
| Scale | >$500M | 50 bps |

At Year 3 ($1.5B ADB at 50 bps): **$7.5M revenue, $1.35M reconciliation liability, $6.15M net (5.6× coverage)**

### Reconciliation Gap Mechanics
- FloatYield calculates: `balance × rate × days/365`
- Treasury accrues: `balance × rate × actual/actual`
- On $1B at 4.5%: **~$900K/year gap** (not 1-3 bps — that's the daily; annual is ~90 bps)

### Regulatory Path
- **US:** Sponsor Bank model — $50-200K/year, 3-6 months to launch. Bank holds deposits, extends FDIC insurance. FloatYield is technology provider.
- **EU:** EMI Partnership — €100-200K, 3-6 months. MiCA fully in effect. EMD2 permits yield on e-money. One license covers all 27 EU states.

### Sponsor Bank Conflict (Red Team Finding)
At scale, bank bears FDIC risk but FloatYield captures most upside. Bank has structural incentive to build competing product or terminate. **CUSO structure (credit union partnership) removes this dependency.**

---

## ML Course Context: Analytical/Quantitative Concepts Demonstrated

| Concept | Application in FloatYield |
|---------|--------------------------|
| **Time-value of money** | Daily yield accrual using simple interest (balance × rate × 1/365) |
| **Day-count conventions** | 365-day year (FloatYield) vs actual/actual (Treasury) creates systematic divergence |
| **Basis points (bps)** | Pricing in bps on ADB rather than per-account aligns revenue with liability |
| **Average Daily Balance (ADB)** | Fee basis; ADB = accounts × avg_balance; used for revenue forecasting |
| **Reconciliation accounting** | Tracking divergence between two accrual methods; tolerance thresholds |
| **Yield curve sensitivity** | Break-even analysis at different Treasury rates (3.5-4.0% floor for viability) |
| **Risk-adjusted pricing** | 5.6× reconciliation coverage ratio as risk buffer |
| **Unit economics scaling** | Fixed costs (compliance, reconciliation ops) vs variable revenue (per-account) |
| ** TAM/SAM/SOM analysis** | Market sizing: $220-280B TAM → $500M-2B SAM → $100-300M SOM (Year 3) |
| **Monte Carlo intuition** | Red team model: what if CUSO partnership takes 18 months instead of 6-12? Capital runway collapse |

---

## Files in This Directory

```
05-materials/
├── yield_engine.py       # Python stdlib yield calculation engine
├── yield_cli.py          # Interactive cmd-based CLI
├── pitch_deck.html        # 12-slide HTML presentation
├── FloatYield_Report.md   # Comprehensive written report
├── demo_test_run.txt      # Test output from yield_engine.py
└── README.md              # This file
```