#!/usr/bin/env python3
"""
FloatYield — T+1 Batch ETL Simulator
=====================================
Simulates the daily yield events feed from a sponsor bank Treasury statement.

In production: this would be replaced by a real bank webhook or polling job.
For the course project: this generates yesterday's yield event for each account,
using the same synthetic noise model as the initial seed.

Usage:
    # Run today's T+1 batch (generate yesterday's events)
    python run_t1_batch.py

    # Run for a specific date
    python run_t1_batch.py --date 2026-05-01

    # Backfill N days
    python run_t1_batch.py --backfill 7

    # Run continuously (check every 60 seconds)
    python run_t1_batch.py --continuous

The script uses INSERT OR IGNORE so it's safe to re-run — already-loaded
dates are silently skipped.
"""

import argparse
import sqlite3
import sys
import time
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "backend" / "floatyield.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_accounts() -> list[sqlite3.Row]:
    with get_db() as db:
        return db.execute(
            "SELECT id, partner_name, balance, yield_rate FROM accounts"
        ).fetchall()


def generate_t1_event(
    account_id: int,
    event_date: date,
    balance: float,
    yield_rate: float,
) -> dict:
    """
    Generate a single T+1 yield event.

    Uses the same noise model as the initial seed (noise_std=0.02).
    Balance and rate are treated as fixed for this simulation —
    in production, these would come from the bank's actual settlement data.
    """
    import random

    # Deterministic seed from account_id + date so the same day
    # always produces the same yield (reproducible, no surprises on re-run)
    seed = account_id * 10000 + event_date.toordinal()
    rng = random.Random(seed)

    base_yield = balance * (yield_rate / 365)

    # 2% daily noise — realistic for settlement timing variance
    noise = rng.gauss(0, 0.02)
    daily_yield = base_yield * (1 + noise)
    daily_yield = max(base_yield * 0.5, min(base_yield * 1.5, daily_yield))

    return {
        "account_id": account_id,
        "event_date": event_date.isoformat(),
        "balance_snapshot": round(balance, 2),
        "rate_snapshot": yield_rate,
        "daily_yield": round(daily_yield, 2),
        "accrued_yield": 0.0,  # computed client-side; not needed for reconciliation
    }


def insert_event(event: dict) -> bool:
    """Insert one event. Returns True if inserted, False if deduplicated."""
    with get_db() as db:
        cursor = db.execute(
            """
            INSERT OR IGNORE INTO yield_events
                (account_id, event_date, balance_snapshot, rate_snapshot,
                 daily_yield, accrued_yield)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event["account_id"],
                event["event_date"],
                event["balance_snapshot"],
                event["rate_snapshot"],
                event["daily_yield"],
                event["accrued_yield"],
            ),
        )
        db.commit()
        return cursor.rowcount > 0


def run_batch(target_date: date) -> tuple[int, int]:
    """
    Run the T+1 batch for a single date.

    Returns (inserted, skipped) counts.
    """
    accounts = get_accounts()
    inserted = 0
    skipped = 0

    print(f"  T+1 batch for {target_date.isoformat()}:")

    for acct in accounts:
        event = generate_t1_event(
            account_id=acct["id"],
            event_date=target_date,
            balance=acct["balance"],
            yield_rate=acct["yield_rate"],
        )
        if insert_event(event):
            inserted += 1
            print(
                f"    [{acct['id']}] {acct['partner_name']}: "
                f"${event['daily_yield']:,.2f} (+{event['daily_yield'] - (acct['balance'] * acct['yield_rate'] / 365):+.2f} vs base)"
            )
        else:
            skipped += 1
            print(
                f"    [{acct['id']}] {acct['partner_name']}: already loaded (skipped)"
            )

    return inserted, skipped


def run_backfill(days: int) -> None:
    """Backfill the last N business days."""
    today = date.today()
    inserted_total = 0
    skipped_total = 0

    print(f"Backfill: last {days} business days\n")

    count = 0
    d = today - timedelta(days=1)
    while count < days:
        if d.weekday() < 5:  # skip weekends
            inserted, skipped = run_batch(d)
            inserted_total += inserted
            skipped_total += skipped
            print(f"    → inserted={inserted}, skipped={skipped}\n")
            count += 1
        d -= timedelta(days=1)

    print(
        f"Backfill complete: {inserted_total} new events, {skipped_total} deduplicated."
    )


def run_continuous(interval: int = 60) -> None:
    """Poll continuously, running the batch each time we cross midnight."""
    print(f"Continuous mode: checking every {interval}s. Press Ctrl+C to stop.\n")
    last_run_date = None

    while True:
        today = date.today()
        if today != last_run_date:
            inserted, skipped = run_batch(today - timedelta(days=1))
            print(f"[{today.isoformat()}] inserted={inserted}, skipped={skipped}\n")
            last_run_date = today
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="FloatYield T+1 Batch ETL Simulator")
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Target date (YYYY-MM-DD). Default: yesterday.",
    )
    parser.add_argument(
        "--backfill",
        type=int,
        default=0,
        help="Backfill N business days instead of running today.",
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run continuously, executing the batch each calendar day.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Seconds between checks in continuous mode (default: 60).",
    )

    args = parser.parse_args()

    if args.backfill > 0:
        run_backfill(args.backfill)
        return

    if args.continuous:
        run_continuous(args.interval)
        return

    target = (
        date.fromisoformat(args.date) if args.date else date.today() - timedelta(days=1)
    )

    print(f"FloatYield T+1 Batch ETL")
    print(f"{'=' * 40}")
    inserted, skipped = run_batch(target)
    print(f"\nDone: {inserted} inserted, {skipped} deduplicated.")


if __name__ == "__main__":
    main()
