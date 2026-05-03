#!/usr/bin/env python3
"""
FloatYield — Walk-Forward Validation on Live DB History
=======================================================
Runs the same walk-forward validation as validate.py, but against
the actual yield_events in the database rather than synthetic data.

This is the real validation — it confirms which model actually earns
its forecast rights on the live history.

Usage:
    python validate_db.py
    python validate_db.py --account-id 1
    python validate_db.py --output scripts/backend/model_comparison.json
"""

import argparse
import json
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent.parent / "backend" / "floatyield.db"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from models import YieldModel, NaiveYield, HoltYield, ARIMAYield


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_account_history(
    account_id: int, limit: int = 120
) -> tuple[list[str], list[float]]:
    """
    Fetch yield history for an account from yield_events.
    Returns (dates, daily_yields) sorted ascending.
    """
    with get_db() as db:
        rows = db.execute(
            """
            SELECT event_date, daily_yield
              FROM yield_events
             WHERE account_id = ?
             ORDER BY event_date ASC
             LIMIT ?
            """,
            (account_id, limit),
        ).fetchall()
    dates = [r["event_date"] for r in rows]
    yields = [float(r["daily_yield"]) for r in rows]
    return dates, yields


def walk_forward_validate(
    series: np.ndarray,
    model_class: type[YieldModel],
    n_windows: int = 5,
    test_days: int = 30,
    train_min: int = 60,
) -> dict:
    """
    Walk forward: train on [0:t], predict [t:t+test_days], roll forward.
    Returns a flat dict with all validation metrics.
    """
    model_name = model_class().name
    total_len = len(series)

    mae_errors = []
    mape_errors = []
    dir_correct = 0
    total_dir = 0
    naive_loss_count = 0

    step = max(1, (total_len - train_min - test_days) // n_windows)
    windows = []
    for w in range(n_windows):
        train_end = train_min + w * step
        if train_end + test_days > total_len:
            break
        windows.append((train_end, train_end + test_days))

    for train_end, test_end in windows:
        train_series = series[:train_end]
        test_series = series[train_end:test_end]

        model = model_class()
        model.fit(pd.Series(train_series))
        preds = model.predict(test_days)

        naive_preds = np.full(test_days, train_series[-1])
        actuals = test_series

        mae_errors.extend(np.abs(preds - actuals))
        mape_errors.extend(np.abs((preds - actuals) / (actuals + 1e-9)) * 100)

        for i in range(1, min(len(preds), len(actuals) - 1)):
            if actuals[i] != actuals[i - 1]:
                total_dir += 1
                if (preds[i] - preds[i - 1] > 0) == (actuals[i] - actuals[i - 1] > 0):
                    dir_correct += 1

        naive_loss_count += np.sum(
            np.abs(preds - actuals) > np.abs(naive_preds - actuals)
        )

    # Final window forecast
    model = model_class()
    model.fit(pd.Series(series[:train_min]))
    final_preds = model.predict(30)
    naive_final = np.full(30, series[-1])

    return {
        "model_name": model_name,
        "mae": float(np.mean(mae_errors)) if mae_errors else 0.0,
        "mape": float(np.mean(mape_errors)) if mape_errors else 0.0,
        "dir_acc": float(dir_correct / total_dir) if total_dir > 0 else 0.0,
        "naive_loss_rate": float(naive_loss_count / max(len(mae_errors), 1)),
        "avg_forecast": float(np.mean(final_preds)),
        "final_30d_total": float(np.sum(final_preds)),
        "final_30d_naive": float(np.sum(naive_final)),
        "improvement_over_naive": float(np.sum(naive_final) - np.sum(final_preds)),
    }


def run_validation(account_id: int, history_days: int = 120) -> dict:
    dates, yields = get_account_history(account_id, limit=history_days)

    if len(yields) < 60:
        return {
            "error": f"Insufficient history: {len(yields)} days (need 60+)",
            "account_id": account_id,
        }

    series = np.array(yields)

    with get_db() as db:
        acct = db.execute(
            "SELECT id, partner_name, balance, yield_rate FROM accounts WHERE id = ?",
            (account_id,),
        ).fetchone()

    balance = float(acct["balance"])
    rate = float(acct["yield_rate"])
    name = acct["partner_name"]

    base_daily = balance * (rate / 365)
    stats = {
        "base_daily_yield": round(base_daily, 2),
        "mean_daily_yield": round(float(np.mean(series)), 2),
        "std_daily_yield": round(float(np.std(series)), 2),
        "signal_to_noise": round(float(np.mean(series) / (np.std(series) + 1e-9)), 3),
        "history_days": len(series),
    }

    results = [
        walk_forward_validate(series, NaiveYield),
        walk_forward_validate(series, HoltYield),
        walk_forward_validate(series, ARIMAYield),
    ]

    # Sort by MAE (ascending = best)
    results_sorted = sorted(results, key=lambda r: r["mae"])
    for i, r in enumerate(results_sorted):
        r["rank"] = i + 1

    winner = results_sorted[0]["model_name"]

    return {
        "account_id": account_id,
        "account_name": name,
        "balance": balance,
        "rate": rate,
        "series_stats": stats,
        "results": results_sorted,
        "winner": winner,
    }


def print_report(data: dict) -> None:
    if "error" in data:
        print(f"  [{data['account_id']}] ERROR: {data['error']}")
        return

    stats = data["series_stats"]
    print(
        f"\n  {data['account_name']} (${data['balance'] / 1e6:.0f}M @ {data['rate'] * 100:.2f}%)"
    )
    print(
        f"    History: {stats['history_days']} days | base=${stats['base_daily_yield']:,.0f}/day | σ=${stats['std_daily_yield']:,.0f}/day"
    )
    print(f"    Winner: {data['winner']}")
    print(
        f"  {'Model':<26} {'MAE ($/day)':<14} {'MAPE %':<10} {'Dir Acc':<10} {'vs Naive':<10} {'Rank'}"
    )
    print("  " + "-" * 80)
    for r in data["results"]:
        vs = (
            f"+${-r['improvement_over_naive']:,.0f}"
            if r["improvement_over_naive"] < 0
            else f"-${r['improvement_over_naive']:,.0f}"
        )
        winner_tag = "  ★" if r["rank"] == 1 else ""
        print(
            f"  {r['model_name']:<26} "
            f"${r['mae']:<13,.0f} "
            f"{r['mape']:<10.1f} "
            f"{r['dir_acc'] * 100:.0f}%{' ' * 6} "
            f"{vs:<10} "
            f"#{r['rank']}{winner_tag}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Walk-forward validation on live yield_events history."
    )
    parser.add_argument(
        "--account-id",
        type=int,
        default=None,
        help="Validate specific account. Default: all accounts.",
    )
    parser.add_argument(
        "--history-days",
        type=int,
        default=120,
        help="Days of history to fetch (default: 120).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Write results to JSON file (e.g., scripts/backend/model_comparison.json).",
    )
    args = parser.parse_args()

    print("FloatYield — Walk-Forward Validation on Live History")
    print("=" * 55)

    with get_db() as db:
        if args.account_id:
            accounts = [
                db.execute(
                    "SELECT id FROM accounts WHERE id = ?", (args.account_id,)
                ).fetchone()
            ]
        else:
            accounts = db.execute("SELECT id FROM accounts").fetchall()

    all_results = {}
    for acct_row in accounts:
        account_id = acct_row["id"]
        data = run_validation(account_id, args.history_days)
        print_report(data)
        if "error" not in data:
            all_results[data["account_name"]] = data

    print("\n" + "=" * 55)

    if all_results:
        winners = {
            v: k
            for k, v in {
                d["account_name"]: d["winner"] for d in all_results.values()
            }.items()
        }
        print("\nSummary:")
        for acct_name, result in all_results.items():
            print(
                f"  {acct_name}: winner = {result['winner']} (MAE ${result['results'][0]['mae']:,.0f}/day)"
            )

    if args.output and all_results:
        output_path = Path(args.output).resolve()
        allowed_dir = Path(__file__).resolve().parent.parent.parent / "scripts"
        try:
            output_path.relative_to(allowed_dir)
        except ValueError:
            print(
                f"[ERROR] Output path must be within {allowed_dir}: {output_path}",
                file=sys.stderr,
            )
            sys.exit(1)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"\nResults written to: {output_path}")


if __name__ == "__main__":
    main()
