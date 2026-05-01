#!/usr/bin/env python3
"""
FloatYield — Yield Events ETL Loader

Loads daily yield data from sponsor bank Treasury statements into the
yield_events table. Designed for T+1 batch operation.

Usage:
    # Load from a CSV export (sponsor bank format)
    python load_yield_events.py --source /path/to/treasury_export.csv

    # Generate synthetic history for demo purposes (90 days)
    python load_yield_events.py --source synthetic --account-id 1

    # Load all accounts with synthetic data
    python load_yield_events.py --source synthetic --all-accounts

Expected CSV format (sponsor bank Treasury statement):
    account_id,event_date,balance_snapshot,rate_snapshot,daily_yield,accrued_yield
    1,2026-01-15,50000000.00,0.0450,6171.23,185135.50
    ...

The loader deduplicates on (account_id, event_date) — already-loaded
records are silently skipped. No partial loads; either a record inserts
fully or it is logged and discarded.
"""

import argparse
import csv
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import TextIO

# ─── DB path (relative to backend/) ────────────────────────────────────────────

# scripts/etl/load_yield_events.py → scripts/etl/ → scripts/ → workspace root
DB_PATH = Path(__file__).resolve().parent.parent.parent / "backend" / "floatyield.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ─── Synthetic data generator ──────────────────────────────────────────────────


def generate_synthetic_history(
    account_id: int,
    start_date: date,
    end_date: date,
    balance: float,
    yield_rate: float,
    noise_std: float = 0.02,
) -> list[dict]:
    """
    Generate realistic synthetic yield history for an account.

    Uses a random-walk model with small daily noise to produce differentiated
    model outputs — unlike the flat in-memory history in the production API.

    noise_std=0.02 means daily yield varies by ~2% (realistic for settlement
    timing and balance fluctuations around month-end).
    """
    import math
    import random

    rows = []
    import random as _r

    _r.seed(42)  # reproducible for demo
    current_date = start_date
    days = 0
    accrued = 0.0

    # Slight downward drift to make ARIMA find something interesting
    drift = -0.00002  # ~-7bps per year

    while current_date <= end_date:
        # Skip weekends for sponsor bank settlement
        if current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue

        daily_yield = balance * (yield_rate / 365)
        # Add small random noise
        noise_multiplier = 1.0 + _r.gauss(0, noise_std)
        daily_yield *= max(0.5, min(1.5, noise_multiplier))

        # Slight drift over time
        daily_yield *= max(0.8, min(1.2, 1.0 + drift * days))

        accrued += daily_yield
        rows.append(
            {
                "account_id": account_id,
                "event_date": current_date.isoformat(),
                "balance_snapshot": round(balance, 2),
                "rate_snapshot": yield_rate,
                "daily_yield": round(daily_yield, 2),
                "accrued_yield": round(accrued, 2),
            }
        )
        current_date += timedelta(days=1)
        days += 1

    return rows


# ─── CSV parser ───────────────────────────────────────────────────────────────


def parse_treasury_csv(f: TextIO) -> list[dict]:
    """
    Parse sponsor bank Treasury statement CSV.

    Expected columns (header required):
        account_id, event_date, balance_snapshot,
        rate_snapshot, daily_yield, accrued_yield
    """
    reader = csv.DictReader(f)
    rows = []
    for lineno, raw in enumerate(reader, start=2):
        try:
            rows.append(
                {
                    "account_id": int(raw["account_id"].strip()),
                    "event_date": raw["event_date"].strip(),
                    "balance_snapshot": float(raw["balance_snapshot"]),
                    "rate_snapshot": float(raw["rate_snapshot"]),
                    "daily_yield": float(raw["daily_yield"]),
                    "accrued_yield": float(raw["accrued_yield"]),
                }
            )
        except (KeyError, ValueError) as e:
            print(f"  [WARN] Line {lineno}: skipped — {e} ({raw})", file=sys.stderr)
    return rows


# ─── DB loader ─────────────────────────────────────────────────────────────────


def load_records(records: list[dict]) -> tuple[int, int]:
    """
    Insert yield event records into yield_events.

    Deduplicates on (account_id, event_date). Already-loaded records
    are silently skipped. Returns (inserted, skipped) counts.
    """
    if not records:
        return 0, 0

    inserted = 0
    skipped = 0

    with get_db() as db:
        for rec in records:
            cursor = db.execute(
                """
                INSERT OR IGNORE INTO yield_events
                    (account_id, event_date, balance_snapshot, rate_snapshot,
                     daily_yield, accrued_yield)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    rec["account_id"],
                    rec["event_date"],
                    rec["balance_snapshot"],
                    rec["rate_snapshot"],
                    rec["daily_yield"],
                    rec["accrued_yield"],
                ),
            )
            if cursor.rowcount == 0:
                skipped += 1
            else:
                inserted += 1

        db.commit()

    return inserted, skipped


# ─── CLI ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Load yield events into FloatYield database."
    )
    parser.add_argument(
        "--source",
        required=True,
        help=(
            "Path to CSV file (sponsor bank Treasury export), "
            "or 'synthetic' to generate demo history."
        ),
    )
    parser.add_argument(
        "--account-id",
        type=int,
        default=None,
        help="Account ID for synthetic generation (required unless --all-accounts).",
    )
    parser.add_argument(
        "--all-accounts",
        action="store_true",
        help="Generate synthetic history for all seeded accounts.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Number of days of synthetic history to generate (default: 90).",
    )
    args = parser.parse_args()

    # ── Synthetic path ────────────────────────────────────────────────────────
    if args.source == "synthetic":
        if not args.all_accounts and args.account_id is None:
            parser.error(
                "--all-accounts or --account-id required with synthetic source"
            )

        end_date = date.today()
        start_date = end_date - timedelta(days=args.days)

        print(f"Generating synthetic yield history: {start_date} → {end_date}")

        with get_db() as db:
            if args.all_accounts:
                accounts = db.execute(
                    "SELECT id, balance, yield_rate FROM accounts"
                ).fetchall()
            else:
                accounts = db.execute(
                    "SELECT id, balance, yield_rate FROM accounts WHERE id = ?",
                    (args.account_id,),
                ).fetchall()

        all_records = []
        for acct in accounts:
            rows = generate_synthetic_history(
                account_id=acct["id"],
                start_date=start_date,
                end_date=end_date,
                balance=acct["balance"],
                yield_rate=acct["yield_rate"],
            )
            all_records.extend(rows)
            print(
                f"  [{acct['id']}] {acct['id']} — {len(rows)} day(s) generated "
                f"(balance=${acct['balance']:,.0f}, rate={acct['yield_rate']:.4f})"
            )

        inserted, skipped = load_records(all_records)
        print(f"ETL complete: {inserted} inserted, {skipped} deduplicated")
        return

    # ── CSV path — validate containment ─────────────────────────────────────
    source_path = Path(args.source).resolve()
    # Anchor to workspace data directory — reject paths that escape upward
    allowed_dir = Path(__file__).resolve().parent.parent.parent / "data"
    try:
        source_path.relative_to(allowed_dir)
    except ValueError:
        print(
            f"[ERROR] Source path must be within {allowed_dir}: {source_path}",
            file=sys.stderr,
        )
        sys.exit(1)
    if not source_path.exists():
        print(f"[ERROR] File not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading Treasury CSV: {source_path}")
    with open(source_path, newline="") as f:
        records = parse_treasury_csv(f)

    if not records:
        print("[WARN] No valid records found in CSV.")
        return

    # Group by account for progress output
    from collections import Counter

    by_account = Counter(r["account_id"] for r in records)
    for acct_id, count in sorted(by_account.items()):
        print(f"  [{acct_id}] {count} row(s) to load")

    inserted, skipped = load_records(records)
    print(f"ETL complete: {inserted} inserted, {skipped} deduplicated")


if __name__ == "__main__":
    main()
