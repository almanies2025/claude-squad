#!/usr/bin/env python3
"""
FloatYield Interactive CLI
Provides scenario analysis, partner economics, competitive comparison, and reconciliation analysis.
"""

import cmd
import sys
from datetime import date, timedelta
from yield_engine import (
    calculate_yield_series,
    calculate_reconciliation_divergence,
    calculate_partner_fee,
    run_scenario,
    _is_leap_year,
)

SPONSOR_BANK_RATE = 0.045
CUSO_RATE = 0.043
FLOATYIELD_RATE = 0.042


class FloatYieldCLI(cmd.Cmd):
    intro = """
============================================
  FloatYield Interactive CLI
  Yield-Bearing Payment Infrastructure
============================================

Type 'help' for available commands.
"""
    prompt = "(FloatYield) "

    def do_scenario(self, arg):
        """Calculate yield and reconciliation for a deposit scenario.
        Usage: scenario [deposit [rate [days]]]
        Examples:
          scenario           # $1M deposit, 4.5%, 30 days
          scenario 500000   # $500K deposit
          scenario 1000000 0.05 60  # $1M, 5%, 60 days
        """
        parts = arg.strip().split()
        deposit = float(parts[0]) if len(parts) >= 1 else 1_000_000
        rate = float(parts[1]) if len(parts) >= 2 else 0.045
        days = int(parts[2]) if len(parts) >= 3 else 30

        result = run_scenario(deposit, rate, days)
        print(f"""
----------------------------------------
  SCENARIO ANALYSIS
----------------------------------------
  Deposit:     ${result["deposit"]:>15,.2f}
  Annual Rate:  {result["rate"] * 100:>15.2f}%
  Days:         {result["days"]:>15}
----------------------------------------
  FloatYield Accrual: ${result["floatyield_accrual"]:>12,.2f}
  Treasury Accrual:    ${result["treasury_accrual"]:>12,.2f}
  Reconciliation Gap: ${result["reconciliation_gap"]:>12,.2f}
  Gap (annualized):   {result["gap_bps_annualized"]:>12.2f} bps
  Net Yield to Customer: ${result["net_yield_to_customer"]:>10,.2f}
----------------------------------------
""")

    def do_partner(self, arg):
        """Calculate tiered partner economics.
        Usage: partner [accounts [avg_balance]]
        Examples:
          partner              # 100K accounts, $2K avg balance
          partner 50000 1500  # 50K accounts, $1.5K avg balance
        """
        parts = arg.strip().split()
        accounts = int(parts[0]) if len(parts) >= 1 else 100_000
        avg_balance = float(parts[1]) if len(parts) >= 2 else 2000

        print(f"""
============================================
  PARTNER ECONOMICS
  {accounts:,} accounts | ${avg_balance:,.0f} avg balance
============================================
""")
        for tier in ["year1", "year2", "year3"]:
            r = calculate_partner_fee(accounts, avg_balance, tier)
            print(f"  Tier {tier}:")
            print(f"    ADB:           ${r['adb']:>15,.2f}")
            print(f"    Rate:          {r['rate_bps']:>15} bps")
            print(f"    Annual Fee:    ${r['annual_fee']:>15,.2f}")
            print(f"    Monthly Fee:   ${r['monthly_fee']:>15,.2f}")
            print()
        print("  Note: Year 1 = 75 bps | Year 2 = 65 bps | Year 3 = 50 bps")
        print("-" * 45)

    def do_reconcile(self, arg):
        """Show daily reconciliation divergence table across a time period.
        Usage: reconcile [deposit [rate [days]]]
        Examples:
          reconcile              # $1M, 4.5%, 30 days
          reconcile 500000 0.05 60  # $500K, 5%, 60 days
        """
        parts = arg.strip().split()
        deposit = float(parts[0]) if len(parts) >= 1 else 1_000_000
        rate = float(parts[1]) if len(parts) >= 2 else 0.045
        days = int(parts[2]) if len(parts) >= 3 else 30

        rr = calculate_reconciliation_divergence(deposit, rate, days)
        start = date(2024, 1, 1)

        print(f"""
=================================================================
  RECONCILIATION ANALYSIS
  ${deposit:,.0f} at {rate * 100:.2f}% | {days} days
=================================================================
""")
        print(
            f"{'Day':>4} {'Date':>12} {'FloatYield':>14} {'Treasury':>14} {'Gap (bps)':>10}"
        )
        print("-" * 60)
        for i, (d, g) in enumerate(zip(range(days), rr.daily_gaps)):
            current = start + timedelta(days=d)
            year_days = 366 if _is_leap_year(current.year) else 365
            fy_daily = deposit * (rate / 365)
            t_daily = deposit * (rate / year_days)
            print(
                f"{d + 1:>4} {current.strftime('%Y-%m-%d'):>12} "
                f"${fy_daily:>12,.4f} ${t_daily:>12,.4f} {g:>10.4f}"
            )

        print("-" * 60)
        print(
            f"{'TOTAL':>4} {'':<12} ${rr.floatyield_accrual:>12,.2f} ${rr.treasury_accrual:>12,.2f} "
            f"{sum(rr.daily_gaps):>10.4f}"
        )
        print(f"""
-----------------------------------------------------------------
  SUMMARY
  FloatYield Accrual:     ${rr.floatyield_accrual:>12,.2f}
  Treasury Accrual:      ${rr.treasury_accrual:>12,.2f}
  Total Gap:              ${rr.total_gap:>12,.2f}
  Gap (annualized):       {rr.gap_bps:>12.2f} bps
-----------------------------------------------------------------
  NOTE: Gap is due to day-count convention difference.
  FloatYield uses 365-day year; Treasuries use actual/actual.
  On $1B at 4.5%, annual gap is ~$900K (not a rounding error).
-----------------------------------------------------------------
""")

    def do_compare(self, arg):
        """Compare Sponsor Bank vs CUSO vs FloatYield economics side by side.
        Usage: compare [deposit [days]]
        """
        parts = arg.strip().split()
        deposit = float(parts[0]) if len(parts) >= 1 else 1_000_000
        days = int(parts[1]) if len(parts) >= 2 else 30

        scenarios = [
            ("Sponsor Bank", deposit, SPONSOR_BANK_RATE, days),
            ("CUSO", deposit, CUSO_RATE, days),
            ("FloatYield", deposit, FLOATYIELD_RATE, days),
        ]

        print(f"""
=================================================================
  COMPETITIVE ECONOMICS COMPARISON
  ${deposit:,.0f} deposit | {days} days | 4.5% reference rate
=================================================================
{"Model":<15} {"Rate":<10} {"Accrual":<15} {"Gap":<15} {"Net Yield":<15}
-----------------------------------------------------------------
""")
        for name, dep, rate, d in scenarios:
            r = run_scenario(dep, rate, d)
            print(
                f"{name:<15} {rate * 100:>7.2f}% ${r['floatyield_accrual']:>12,.2f} "
                f"${r['reconciliation_gap']:>12,.2f} ${r['net_yield_to_customer']:>12,.2f}"
            )

        print("""
-----------------------------------------------------------------
  INTERPRETATION:
  - Sponsor Bank model: Full FDIC coverage, bank bears compliance burden
  - CUSO model: Credit union holds deposits, aligned incentives
  - FloatYield model: B2B infrastructure platform, tiered fees
-----------------------------------------------------------------
""")

    def do_help(self, arg):
        """Explain key FloatYield concepts."""
        topics = {
            "yield": """
----------------------------------------
  YIELD ACCRUAL
----------------------------------------
  FloatYield calculates daily yield using:

    daily_yield = balance × (annual_rate / 365)

  This simple interest method is applied each
  business day. Monthly distribution to customers.

  Example: $1M at 4.5% for 30 days
    = $1,000,000 × 0.045 × 30/365
    = $37,397.26 in yield
""",
            "reconciliation": """
----------------------------------------
  RECONCILIATION DIVERGENCE
----------------------------------------
  FloatYield uses 365-day year (simple interest).
  Treasuries use actual/actual day count.
  This creates a systematic gap:

    FloatYield: balance × rate × days/365
    Treasury:   balance × rate × actual/actual

  On a $1B book at 4.5%:
    - Annual gap: ~$900K (0.09% of notional)
    - Daily gap: ~1-3 bps

  This gap is REAL, not a rounding error.
  Contractual tolerance thresholds manage it.
""",
            "tiers": """
----------------------------------------
  TIERED BPS PRICING
----------------------------------------
  FloatYield's redesigned fee model:

  | Tier   | ADB Range    | Fee (bps) |
  |--------|--------------|-----------|
  | Pilot  | <$50M        | 75 bps    |
  | Growth | $50M-$500M   | 65 bps    |
  | Scale  | >$500M       | 50 bps    |

  This aligns revenue (bps × ADB) with
  liability (also scales with deposits).

  Year 3 example ($1.5B ADB at 50 bps):
    - Revenue: $7.5M
    - Reconciliation liability: $1.35M
    - Net: $6.15M (5.6× coverage)
""",
            "cuso": """
----------------------------------------
  CUSO STRUCTURE
----------------------------------------
  Credit Union Service Organization:

  Problem: Sponsor banks bear FDIC risk but
  FloatYield captures most upside at scale.

  Solution: Partner with credit unions instead.

  Credit unions:
  - Are NCUA-insured (not FDIC)
  - Have different incentive structure
  - Need loanable deposits
  - Already have compliance infrastructure

  This removes bank dependency and aligns
  incentives: credit union wants deposits;
  FloatYield wants accounts.
""",
        }

        if arg.strip().lower() in topics:
            print(topics[arg.strip().lower()])
        else:
            print("""
----------------------------------------
  AVAILABLE HELP TOPICS
----------------------------------------
  help yield          - Yield accrual mechanics
  help reconciliation - Reconciliation divergence
  help tiers          - Tiered bps pricing model
  help cuso           - CUSO structure explained
  help reconcile      - Daily divergence table
----------------------------------------
""")

    def do_quit(self, arg):
        """Exit the FloatYield CLI."""
        print("\n  Thanks for using FloatYield CLI. Goodbye!\n")
        sys.exit(0)


if __name__ == "__main__":
    FloatYieldCLI().cmdloop()
