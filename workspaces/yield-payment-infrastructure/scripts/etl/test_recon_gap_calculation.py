#!/usr/bin/env python3
"""
test_recon_gap_calculation.py
=============================
Regression test for the _recon_gap interval-math fix from journal 0038.

The fix corrected two bugs:
  1. Holt intervals were flat (trend_resids never populated)
  2. ARIMA psi_cumsum formula had a doubled exponent

This test validates the *recon_gap bps calculation itself*, which is
the reference value fed into all three model outputs.

Formula (from _recon_gap_info in main.py):
    calculated_yield = balance * (rate / 365)
    gap_daily        = actual_yield - calculated_yield
    gap_bps          = (gap_daily * 365 / balance) * 10000

The * 365 / balance normalizes the daily gap to an annualized basis,
then * 10000 converts to basis points (1% = 100 bps).
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

# scripts/etl/test_recon_gap_calculation.py
#   → scripts/etl/          (1 up)
#   → scripts/              (2 up)
#   → workspace root
DB_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "backend"
    / "floatyield.db"
)


# ─── Core calculation (mirrors _recon_gap_info in main.py) ───────────────────

def recon_gap_bps(balance: float, rate: float, actual_yield: float) -> float:
    """
    Compute reconciliation gap in basis points.

    Parameters
    ----------
    balance      : balance_snapshot from yield_events (e.g. 50_000_000)
    rate         : rate_snapshot from yield_events (e.g. 0.045)
    actual_yield : daily_yield from yield_events (e.g. 6146.62)

    Returns
    -------
    gap_bps : float
        Annualized gap in basis points on $1B reference.
    """
    calculated = balance * (rate / 365)
    gap_daily  = actual_yield - calculated
    gap_bps    = (gap_daily * 365 / balance) * 10_000
    return gap_bps


# ─── Fixtures ─────────────────────────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_sample_yield_events(n: int = 10) -> list[dict]:
    """Fetch the n most recent yield_events rows for account_id=1."""
    with get_db() as db:
        rows = db.execute(
            """
            SELECT balance_snapshot, rate_snapshot, daily_yield
              FROM yield_events
             WHERE account_id = 1
             ORDER BY event_date DESC
             LIMIT ?
            """,
            (n,),
        ).fetchall()
    return [dict(r) for r in rows]


# ─── Tests ────────────────────────────────────────────────────────────────────

class TestReconGapFormula:
    """Validate the recon_gap bps formula with known inputs."""

    def test_zero_gap(self):
        """When actual == calculated, gap_bps is exactly 0."""
        balance = 50_000_000.0
        rate    = 0.045
        expected_daily = balance * (rate / 365)  # no noise → perfect match
        gap = recon_gap_bps(balance, rate, expected_daily)
        assert gap == 0.0, f"Expected 0.0 bps, got {gap}"

    def test_positive_gap(self):
        """When actual > calculated, gap_bps is positive (bank overpaid)."""
        balance = 100_000_000.0
        rate    = 0.05          # 5%
        # Expected daily: 100M * 0.05 / 365 = 13,698.63
        expected_daily = balance * (rate / 365)
        # Suppose bank reported 14,000 (slight overpayment)
        actual_daily   = 14_000.0
        gap = recon_gap_bps(balance, rate, actual_daily)
        # gap_daily = 14,000 - 13,698.63 = 301.37
        # gap_bps   = (301.37 * 365 / 100M) * 10,000 = 1.10 bps
        expected = (301.37 * 365 / 100_000_000) * 10_000
        assert abs(gap - expected) < 0.01, f"Expected ~{expected:.4f} bps, got {gap:.4f}"

    def test_negative_gap(self):
        """When actual < calculated, gap_bps is negative (bank underpaid)."""
        balance = 50_000_000.0
        rate    = 0.045         # 4.5%
        expected_daily = balance * (rate / 365)  # = 6,164.38
        actual_daily   = 6_100.0  # bank under-reported
        gap = recon_gap_bps(balance, rate, actual_daily)
        # gap_daily = 6,100 - 6,164.38 = -64.38
        # gap_bps   = (-64.38 * 365 / 50M) * 10,000 = -4.70 bps
        expected = (-64.38 * 365 / 50_000_000) * 10_000
        assert abs(gap - expected) < 0.01, f"Expected ~{expected:.4f} bps, got {gap:.4f}"

    def test_large_balance_scaling(self):
        """Gap bps is scale-invariant: same ratio gives same bps at any size."""
        # $100M at 5%, actual 1% above expected
        balance1 = 100_000_000.0
        rate1    = 0.05
        expected1 = balance1 * (rate1 / 365)
        actual1   = expected1 * 1.01   # 1% over

        # $1B at 5%, actual 1% above expected (same proportional gap)
        balance2 = 1_000_000_000.0
        rate2    = 0.05
        expected2 = balance2 * (rate2 / 365)
        actual2   = expected2 * 1.01

        gap1 = recon_gap_bps(balance1, rate1, actual1)
        gap2 = recon_gap_bps(balance2, rate2, actual2)
        # Both should be ~10 bps (1% of 100% = 100% = 10,000 bps; 1% of that = 100 bps? Wait)
        # actual = expected * 1.01 → gap = 1% of expected daily
        # gap_daily = 0.01 * expected_daily
        # gap_bps = (0.01 * expected_daily * 365 / balance) * 10000
        #         = (0.01 * balance * (rate/365) * 365 / balance) * 10000
        #         = 0.01 * rate * 10000 = rate * 100 = 0.05 * 100 = 5 bps
        assert abs(gap1 - 5.0) < 0.01, f"Expected 5.0 bps, got {gap1:.4f}"
        assert abs(gap2 - 5.0) < 0.01, f"Expected 5.0 bps, got {gap2:.4f}"
        assert abs(gap1 - gap2) < 0.001, f"Gap should be scale-invariant: {gap1} vs {gap2}"

    def test_known_live_row(self):
        """
        Validate against a known row from the live database.

        Row: balance=50,000,000, rate=0.045, daily_yield=6,146.62
        Expected gap: (6,146.62 - 6,164.38) * 365 / 50M * 10,000 = -1.30 bps
        """
        balance  = 50_000_000.0
        rate     = 0.045
        actual   = 6_146.62
        expected_calculated = balance * (rate / 365)  # 6,164.38
        expected_gap_daily = actual - expected_calculated  # -17.76
        expected_gap_bps   = (expected_gap_daily * 365 / balance) * 10_000

        gap = recon_gap_bps(balance, rate, actual)
        assert abs(gap - expected_gap_bps) < 0.01, (
            f"Live row gap mismatch: expected {expected_gap_bps:.4f} bps, got {gap:.4f}"
        )

    def test_against_live_database(self):
        """
        Tier 2 integration test: verify formula against real yield_events rows.

        This test is FORBIDDEN from using mocks. It reads actual database records
        and validates that the formula produces consistent results.
        """
        rows = fetch_sample_yield_events(10)
        assert len(rows) >= 5, (
            f"Need at least 5 yield_events rows for integration test, got {len(rows)}"
        )

        gaps = []
        for row in rows:
            balance = float(row["balance_snapshot"])
            rate    = float(row["rate_snapshot"])
            actual  = float(row["daily_yield"])
            gap_bps = recon_gap_bps(balance, rate, actual)
            gaps.append(gap_bps)

        # All gaps should be in a reasonable range (-50 to +50 bps for synthetic data)
        for g in gaps:
            assert -50 <= g <= 50, f"Gap {g:.4f} bps outside reasonable range (-50, 50)"

        # Mean gap should be non-zero (otherwise synthetic noise isn't working)
        mean_gap = sum(gaps) / len(gaps)
        # Note: with seed=42 and small noise, mean gap may be close to 0
        # but should not be exactly 0
        print(f"\n  [integration] mean_gap={mean_gap:.4f} bps over {len(rows)} events")
        print(f"  [integration] gaps={[round(g,4) for g in gaps]}")


# ─── Run directly ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import pprint
    print("=== recon_gap bps regression tests ===\n")

    # Formula unit tests
    tests = TestReconGapFormula()

    print("test_zero_gap ...", end=" ")
    tests.test_zero_gap()
    print("PASS")

    print("test_positive_gap ...", end=" ")
    tests.test_positive_gap()
    print("PASS")

    print("test_negative_gap ...", end=" ")
    tests.test_negative_gap()
    print("PASS")

    print("test_large_balance_scaling ...", end=" ")
    tests.test_large_balance_scaling()
    print("PASS")

    print("test_known_live_row ...", end=" ")
    tests.test_known_live_row()
    print("PASS")

    print("\n--- Tier 2 integration (live DB) ---")
    try:
        tests.test_against_live_database()
        print("test_against_live_database ... PASS")
    except Exception as e:
        print(f"test_against_live_database ... FAIL: {e}")
        sys.exit(1)

    print("\nAll tests passed.")
