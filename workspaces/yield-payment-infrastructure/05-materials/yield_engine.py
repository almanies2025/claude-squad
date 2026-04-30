#!/usr/bin/env python3
"""
FloatYield Yield Calculation Engine
Computes daily yield accrual, reconciliation divergence, and partner economics.
"""

from dataclasses import dataclass
from typing import List
from datetime import date, timedelta
import json


@dataclass
class YieldResult:
    total_yield: float
    daily_accruals: List[float]
    avg_daily_balance: float
    effective_rate: float


@dataclass
class ReconciliationResult:
    floatyield_accrual: float
    treasury_accrual: float
    daily_gaps: List[float]
    total_gap: float
    gap_bps: float


def calculate_daily_yield(balance: float, annual_rate: float, days: int = 1) -> float:
    return balance * (annual_rate / 365) * days


def calculate_yield_series(
    balance: float, annual_rate: float, days: int
) -> YieldResult:
    daily = [calculate_daily_yield(balance, annual_rate) for _ in range(days)]
    return YieldResult(
        total_yield=sum(daily),
        daily_accruals=daily,
        avg_daily_balance=balance,
        effective_rate=annual_rate,
    )


def _is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def simulate_treasury_accrual(balance: float, annual_rate: float, days: int) -> float:
    start = date(2024, 1, 1)
    total = 0.0
    for d in range(days):
        current = start + timedelta(days=d)
        year_days = 366 if _is_leap_year(current.year) else 365
        daily_rate = annual_rate / year_days
        total += balance * daily_rate
    return total


def calculate_reconciliation_divergence(
    balance: float, annual_rate: float, days: int
) -> ReconciliationResult:
    fy = calculate_yield_series(balance, annual_rate, days).total_yield
    treasury = simulate_treasury_accrual(balance, annual_rate, days)
    start = date(2024, 1, 1)
    daily_gaps = []
    for d in range(days):
        current = start + timedelta(days=d)
        year_days = 366 if _is_leap_year(current.year) else 365
        fy_daily = balance * (annual_rate / 365)
        t_daily = balance * (annual_rate / year_days)
        daily_gaps.append(round((fy_daily - t_daily) * 10000, 4))
    total_gap = fy - treasury
    gap_bps = (total_gap / balance) * 10000 * 365 / days
    return ReconciliationResult(
        floatyield_accrual=round(fy, 2),
        treasury_accrual=round(treasury, 2),
        daily_gaps=[round(g, 4) for g in daily_gaps],
        total_gap=round(total_gap, 2),
        gap_bps=round(gap_bps, 2),
    )


def calculate_partner_fee(
    accounts: int, avg_balance: float, tier: str = "year1"
) -> dict:
    rates = {"year1": 0.0075, "year2": 0.0065, "year3": 0.0050}
    adb = accounts * avg_balance
    fee = adb * rates.get(tier, 0.0050)
    return {
        "accounts": accounts,
        "avg_balance": avg_balance,
        "adb": round(adb, 2),
        "tier": tier,
        "rate_bps": int(rates.get(tier, 0.0050) * 10000),
        "annual_fee": round(fee, 2),
        "monthly_fee": round(fee / 12, 2),
    }


def run_scenario(deposit: float, rate: float, days: int) -> dict:
    yr = calculate_yield_series(deposit, rate, days)
    rr = calculate_reconciliation_divergence(deposit, rate, days)
    return {
        "deposit": deposit,
        "rate": rate,
        "days": days,
        "yield_earned": round(yr.total_yield, 2),
        "floatyield_accrual": rr.floatyield_accrual,
        "treasury_accrual": rr.treasury_accrual,
        "reconciliation_gap": rr.total_gap,
        "gap_bps_annualized": rr.gap_bps,
        "net_yield_to_customer": round(yr.total_yield - rr.total_gap, 2),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="FloatYield Yield Calculation Engine")
    parser.add_argument("--scenario", action="store_true", help="Run default scenario")
    parser.add_argument("--deposit", type=float, default=1_000_000)
    parser.add_argument("--rate", type=float, default=0.045)
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--partner", action="store_true", help="Show partner economics")
    parser.add_argument("--accounts", type=int, default=100_000)
    parser.add_argument("--avg-balance", type=float, default=2000)
    args = parser.parse_args()
    if args.partner:
        print("\n=== FloatYield Partner Economics ===")
        for tier in ["year1", "year2", "year3"]:
            r = calculate_partner_fee(args.accounts, args.avg_balance, tier)
            print(f"\n  Tier: {tier}")
            print(f"  Accounts: {r['accounts']:,}")
            print(f"  Avg Balance: ${r['avg_balance']:,.0f}")
            print(f"  ADB: ${r['adb']:,.0f}")
            print(f"  Rate: {r['rate_bps']} bps")
            print(f"  Annual Fee: ${r['annual_fee']:,.0f}")
            print(f"  Monthly Fee: ${r['monthly_fee']:,.0f}")
    else:
        result = run_scenario(args.deposit, args.rate, args.days)
        print(f"\n=== FloatYield Scenario ===")
        print(f"  Deposit: ${result['deposit']:,.0f}")
        print(f"  Rate: {result['rate'] * 100:.2f}%")
        print(f"  Days: {result['days']}")
        print(f"\n  FloatYield Accrual: ${result['floatyield_accrual']:,.2f}")
        print(f"  Treasury Accrual: ${result['treasury_accrual']:,.2f}")
        print(f"  Reconciliation Gap: ${result['reconciliation_gap']:,.2f}")
        print(f"  Gap (annualized): {result['gap_bps_annualized']:.2f} bps")
        print(f"  Net Yield: ${result['net_yield_to_customer']:,.2f}")
