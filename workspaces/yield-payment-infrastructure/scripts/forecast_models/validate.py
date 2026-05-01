"""
Walk-Forward Time-Series Validation
==================================
Proper validation: rolling window, always train on past → predict future.
Never leak future into training. 5 windows × 30-day test each.

Models compared:
1. Naive (Persistence)   — "tomorrow = today" baseline
2. Holt (Dbl Exp Smoothing) — level + trend
3. ARIMA(1,1,1)        — AR momentum + differencing + MA shock

Metrics:
- MAE  (mean absolute error) — how far off in dollars
- MAPE (mean absolute pct error) — relative accuracy
- Dir  (directional accuracy) — did we get the direction right?
- Loss (pct of forecasts that lost money vs naive)
"""
import sys
import json
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from data_generator import generate_yield_series
from models import YieldModel, NaiveYield, HoltYield, ARIMAYield


@dataclass
class ValidationResult:
    model_name: str
    mae: float          # mean absolute error in $
    mape: float         # MAPE in %
    dir_acc: float      # directional accuracy 0–1
    naive_loss_rate: float  # how often this model was worse than naive
    avg_forecast: float
    final_30d_total: float
    final_30d_naive: float
    improvement_over_naive: float  # $ improvement vs naive over 30d


def walk_forward_validate(
    series: pd.Series,
    model_class: type[YieldModel],
    n_windows: int = 5,
    test_days: int = 30,
    train_min: int = 120,
) -> ValidationResult:
    """
    Walk forward: train on [0:t], predict [t:t+test_days], roll forward.
    """
    model_name = model_class().name
    total_len = len(series)

    mae_errors = []
    mape_errors = []
    dir_correct = 0
    total_dir = 0
    naive_loss_count = 0

    # Rolling windows
    windows = []
    step = (total_len - train_min - test_days) // n_windows
    for w in range(n_windows):
        train_end = train_min + w * step
        if train_end + test_days > total_len:
            break
        windows.append((train_end, train_end + test_days))

    for train_end, test_end in windows:
        train_series = series.iloc[:train_end]
        test_series = series.iloc[train_end:test_end]

        # Fit
        model = model_class()
        model.fit(train_series)

        # Predict
        preds = model.predict(test_days)

        # Naive baseline
        naive_preds = np.full(test_days, train_series.iloc[-1])

        # Errors
        actuals = test_series.values
        mae_errors.extend(np.abs(preds - actuals))
        mape_errors.extend(np.abs((preds - actuals) / (actuals + 1e-9)) * 100)

        # Directional accuracy
        for i in range(1, min(len(preds), len(actuals) - 1)):
            if actuals[i] != actuals[i - 1]:
                total_dir += 1
                pred_dir = preds[i] - preds[i - 1]
                actual_dir = actuals[i] - actuals[i - 1]
                if (pred_dir > 0) == (actual_dir > 0):
                    dir_correct += 1

        # How often does this model lose vs naive?
        naive_loss_count += np.sum(np.abs(preds - actuals) > np.abs(naive_preds - actuals))

    model = model_class()
    model.fit(series.iloc[:train_min])
    final_preds = model.predict(30)
    naive_final = np.full(30, series.iloc[-1])

    return ValidationResult(
        model_name=model_name,
        mae=float(np.mean(mae_errors)),
        mape=float(np.mean(mape_errors)),
        dir_acc=float(dir_correct / total_dir) if total_dir > 0 else 0.0,
        naive_loss_rate=float(naive_loss_count / max(len(mae_errors), 1)),
        avg_forecast=float(np.mean(final_preds)),
        final_30d_total=float(np.sum(final_preds)),
        final_30d_naive=float(np.sum(naive_final)),
        improvement_over_naive=float(np.sum(naive_final) - np.sum(final_preds)),
    )


def run_validation(balance: float, rate: float, seed: int = 42) -> dict:
    df = generate_yield_series(
        balance=balance,
        nominal_rate=rate,
        start_date=pd.Timestamp("2024-01-01"),
        days=730,
        seed=seed,
    )
    series = df["daily_yield"]

    results = [
        walk_forward_validate(series, NaiveYield),
        walk_forward_validate(series, HoltYield),
        walk_forward_validate(series, ARIMAYield),
    ]

    # Rank
    by_mae = sorted(results, key=lambda r: r.mae)
    best_mae = by_mae[0]
    worst_mae = by_mae[-1]

    return {
        "balance": balance,
        "rate": rate,
        "account": f"${balance/1e6:.0f}M @ {rate*100:.2f}%",
        "results": [
            {
                **vars(r),
                "rank": list(sorted(results, key=lambda x: x.mae)).index(r) + 1,
                "mae_pct_worse_vs_best": round((r.mae - best_mae.mae) / best_mae.mae * 100, 1) if best_mae.mae > 0 else 0,
            }
            for r in sorted(results, key=lambda x: x.mae)
        ],
        "winner": best_mae.model_name,
    }


if __name__ == "__main__":
    accounts = [
        {"name": "Celtic Bank",           "balance": 50_000_000, "rate": 0.045, "seed": 10},
        {"name": "BlueRidge Credit Union", "balance": 120_000_000, "rate": 0.0475, "seed": 20},
        {"name": "Coastal Community Bank", "balance": 78_000_000,  "rate": 0.044,  "seed": 30},
    ]

    print(f"{'Model':<28} {'MAE ($/day)':<14} {'MAPE %':<10} {'Dir Acc':<10} {'vs Naive':<10} {'Rank'}")
    print("-" * 80)

    for acct in accounts:
        result = run_validation(acct["balance"], acct["rate"], acct["seed"])
        print(f"\n  {result['account']} — Winner: {result['winner']}")
        for r in result["results"]:
            print(
                f"  {r['model_name']:<26} "
                f"${r['mae']:<13.2f} "
                f"{r['mape']:<10.2f} "
                f"{r['dir_acc']*100:.0f}%{' '*6} "
                f"{'—':<10} "
                f"#{r['rank']}"
            )
