# FloatYield — Yield-Bearing Payment Infrastructure

**FloatYield** is a B2B infrastructure platform that enables banks and fintechs to offer interest-bearing payment accounts to their customers.

---

## What It Does

FloatYield provides the yield calculation engine, reconciliation logic, and partner economics engine that banks and fintechs need to offer competitive yield on transaction balances — without building the capability in-house.

---

## Architecture

```
Customer deposits → Sponsor Bank (holds at Fed) → Bank invests in Treasuries
Yield accrues → FloatYield calculates daily yield → Bank distributes to customer
FloatYield takes platform fee → monthly
```

**Critical rule:** FloatYield never holds customer funds directly. All funds flow through the Sponsor Bank's balance sheet.

---

## Quick Start

### Prerequisites

- Python 3.8+ (stdlib only — no external dependencies)

### Yield Engine

```bash
cd 05-materials

# Run a scenario
python3 yield_engine.py --scenario --deposit 1000000 --rate 0.045 --days 30

# Run partner economics
python3 yield_engine.py --partner --accounts 100000 --avg-balance 2000
```

### Interactive CLI

```bash
python3 yield_cli.py

# Then type commands:
(FloatYield) scenario 1000000 0.045 30
(FloatYield) partner 100000 2000
(FloatYield) compare 1000000 30
(FloatYield) help reconciliation
(FloatYield) quit
```

---

## Project Structure

```
05-materials/
├── yield_engine.py    # Core yield calculation engine
├── yield_cli.py       # Interactive CLI interface
├── pitch_deck.html    # Investor pitch deck (open in browser)
├── FloatYield_Report.md  # Comprehensive written report
├── README.md          # This file
└── demo_test_run.txt  # Verified test output
```

---

## Core Engine API

```python
from yield_engine import (
    calculate_daily_yield,
    calculate_yield_series,
    calculate_reconciliation_divergence,
    calculate_partner_fee,
    run_scenario,
)

# Basic daily yield
daily = calculate_daily_yield(1_000_000, 0.045, 1)
# Returns: 123.28767123287673 (daily yield on $1M at 4.5%)

# Reconciliation divergence (FloatYield linear vs Treasury actual/actual)
result = calculate_reconciliation_divergence(1_000_000_000, 0.045, 365)
# Returns ReconciliationResult with gap in bps

# Partner fee (tiered bps on ADB)
fee = calculate_partner_fee(100_000, 2000, "year1")
# Returns: {'accounts': 100000, 'adb': 200000000, 'annual_fee': 1500000, ...}

# Full scenario
scenario = run_scenario(1_000_000, 0.045, 30)
```

---

## Key Concepts

### Reconciliation Divergence

FloatYield uses simple interest (`balance × rate × 1/365`). Treasuries accrue using actual/actual day-count. For a $1B deposit book at 4.5%, this divergence is ~1.23 bps annually — approximately **$900K/year**.

This is not a bug. It is a structural feature that requires a contractual tolerance threshold.

### Tiered Fee Model

| Tier   | Scale         | Rate   | Notes                     |
| ------ | ------------- | ------ | ------------------------- |
| Year 1 | <$200M ADB    | 75 bps | Launch phase, setup costs |
| Year 2 | $200M–$1B ADB | 65 bps | Scaling efficiency        |
| Year 3 | >$1B ADB      | 50 bps | Volume discount           |

---

## Regulatory Path

**Sponsor Bank model** (US): Partner with a community/regional bank. Bank holds deposits, extends FDIC insurance. FloatYield operates as technology/service provider.

- Timeline: 3–6 months to MVP
- Cost: $50K–$200K/year
- Banks: Pathward, Celtic Bank, Blue Ridge Bank, Coastal Community Bank

**EMI partnership** (EU): Partner with an existing e-money institution.

- Timeline: 3–6 months to MVP
- Cost: €100K–200K
- One license covers all 27 EU member states

---

## Market Opportunity

| Metric                | Value                |
| --------------------- | -------------------- |
| TAM (US float income) | $50–80B/year         |
| SAM (B2B platform)    | $500M–2B/year        |
| SOM (Year 3)          | $4–10M/year          |
| Direct competitor     | None (pure-play B2B) |

---

## Competitive Position

| Feature                       | FloatYield | Neobanks (Dave, Chime) | Stablecoins (USDC) |
| ----------------------------- | ---------- | ---------------------- | ------------------ |
| Yield on checking             | Yes        | No                     | N/A                |
| FDIC insurance                | Yes        | No                     | No                 |
| B2B infrastructure model      | Yes        | No                     | No                 |
| No customer KYC by FloatYield | Yes        | Yes                    | Self-custody       |

---

## Running Tests

```bash
# All tests (engine + CLI)
python3 yield_engine.py --scenario --deposit 1000000 --rate 0.045 --days 30
python3 yield_engine.py --partner --accounts 100000 --avg-balance 2000
```

See `demo_test_run.txt` for the full verified test output.

---

## Files

| File                   | Description                          |
| ---------------------- | ------------------------------------ |
| `yield_engine.py`      | Python stdlib yield engine           |
| `yield_cli.py`         | Interactive CLI (cmd module, stdlib) |
| `pitch_deck.html`      | 12-slide HTML pitch deck             |
| `FloatYield_Report.md` | 25-page written report               |
| `README.md`            | This file                            |
| `demo_test_run.txt`    | Verified test output                 |

---

_FloatYield — B2B yield infrastructure for banks and fintechs._
