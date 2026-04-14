"""
Fixed infrastructure for Nifty 50 directional forecasting.
Downloads data from yfinance (once), provides walk-forward splits,
evaluation, and utilities.

DO NOT MODIFY — this file is the fixed evaluation harness.
The agent only modifies train.py.

Usage:
    python prepare.py                # download data (one-time)
    python prepare.py --force        # re-download even if data exists
"""

import os
import sys
import argparse
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# Constants (fixed, do not modify)
# ---------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SAVED_MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_models")

DATA_START = "2021-01-01"
DATA_END = "2026-03-30"

FORECAST_HORIZON = 1  # 1 = next trading day

TIME_BUDGET = 600  # 10 minutes per experiment

SAVE_THRESHOLD = 0.75  # save model if directional accuracy >= 75%

INSTRUMENTS = {
    "nifty50":  "^NSEI",
    "sp500":    "^GSPC",
    "gold":     "GC=F",
    "silver":   "SI=F",
    "crude":    "CL=F",
    "usdinr":   "INR=X",
}

# Walk-forward validation windows
# Each tuple: (train_start, train_end, val_start, val_end)
WALK_FORWARD_WINDOWS = [
    ("2021-01-01", "2024-06-30", "2024-07-01", "2024-12-31"),
    ("2021-07-01", "2025-01-31", "2025-02-01", "2025-07-31"),
    ("2022-01-01", "2025-07-31", "2025-08-01", "2026-01-31"),
]

# Held-out test set — NEVER used during autoresearch
TEST_START = "2026-02-01"
TEST_END = "2026-03-30"

TARGET_COL = "nifty50_direction"

# ---------------------------------------------------------------------------
# Data download
# ---------------------------------------------------------------------------

def download_data(force=False):
    """Download OHLCV data for all instruments from yfinance. Skips if data exists."""
    os.makedirs(DATA_DIR, exist_ok=True)

    merged_path = os.path.join(DATA_DIR, "merged.csv")
    if os.path.exists(merged_path) and not force:
        print(f"Data already exists at {merged_path}. Use --force to re-download.")
        return pd.read_csv(merged_path, parse_dates=["date"], index_col="date")

    try:
        import yfinance as yf
    except ImportError:
        print("yfinance not installed. Run: pip install yfinance")
        sys.exit(1)

    frames = {}
    for name, ticker in INSTRUMENTS.items():
        print(f"Downloading {name} ({ticker})...")
        try:
            df = yf.download(ticker, start=DATA_START, end=DATA_END,
                             progress=False, auto_adjust=True)
            if df.empty:
                print(f"  WARNING: No data returned for {name} ({ticker})")
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df.index = pd.to_datetime(df.index)
            df.index = df.index.tz_localize(None) if df.index.tz else df.index
            df.index.name = "date"

            rename_map = {}
            for col in df.columns:
                col_lower = col.lower().replace(" ", "_")
                rename_map[col] = f"{name}_{col_lower}"
            df = df.rename(columns=rename_map)

            csv_path = os.path.join(DATA_DIR, f"{name}.csv")
            df.to_csv(csv_path)
            print(f"  Saved {name}: {len(df)} rows to {csv_path}")
            frames[name] = df

        except Exception as e:
            print(f"  ERROR downloading {name}: {e}")
            continue

    if not frames:
        print("ERROR: No data downloaded. Check your internet connection.")
        sys.exit(1)

    print(f"\nMerging {len(frames)} instruments...")
    merged = pd.concat(frames.values(), axis=1, join="inner")
    merged = merged.sort_index()
    merged = merged.ffill().dropna()

    nifty_close = merged["nifty50_close"]
    future_close = nifty_close.shift(-FORECAST_HORIZON)
    merged[TARGET_COL] = (future_close > nifty_close).astype(int)
    merged = merged.iloc[:-FORECAST_HORIZON]

    merged.index.name = "date"
    merged.to_csv(merged_path)
    print(f"Merged data: {len(merged)} rows, {len(merged.columns)} columns")
    print(f"Saved to {merged_path}")
    print(f"Date range: {merged.index[0].date()} to {merged.index[-1].date()}")
    print(f"Target distribution: {merged[TARGET_COL].value_counts().to_dict()}")

    return merged


def load_data():
    """Load the merged dataset. Downloads if not present."""
    merged_path = os.path.join(DATA_DIR, "merged.csv")
    if not os.path.exists(merged_path):
        return download_data()
    return pd.read_csv(merged_path, parse_dates=["date"], index_col="date")


# ---------------------------------------------------------------------------
# Walk-forward splits
# ---------------------------------------------------------------------------

def get_walk_forward_splits(df):
    """
    Returns a list of (train_df, val_df) tuples for walk-forward validation.
    Ensures strict temporal ordering — no future data leaks into training.
    """
    splits = []
    for train_start, train_end, val_start, val_end in WALK_FORWARD_WINDOWS:
        train = df[train_start:train_end].copy()
        val = df[val_start:val_end].copy()

        if len(train) == 0 or len(val) == 0:
            print(f"  WARNING: Empty split for window {train_start}-{train_end} / {val_start}-{val_end}")
            continue

        splits.append((train, val))

    return splits


def get_test_set(df):
    """Returns the held-out test set. Only use for final evaluation, never during autoresearch."""
    return df[TEST_START:TEST_END].copy()


# ---------------------------------------------------------------------------
# Evaluation (DO NOT CHANGE — this is the fixed metric)
# ---------------------------------------------------------------------------

def evaluate(predictions, actuals):
    """
    Compute directional accuracy and supporting metrics.

    Args:
        predictions: numpy array or pandas Series of 0/1 predictions
        actuals: numpy array or pandas Series of 0/1 actual directions

    Returns:
        dict with metrics. PRIMARY metric: directional_accuracy
    """
    predictions = np.asarray(predictions).astype(int)
    actuals = np.asarray(actuals).astype(int)

    assert len(predictions) == len(actuals), \
        f"Length mismatch: predictions={len(predictions)}, actuals={len(actuals)}"

    correct = (predictions == actuals).sum()
    total = len(actuals)
    accuracy = correct / total if total > 0 else 0.0

    up_pred_pct = predictions.mean() if total > 0 else 0.0
    up_actual_pct = actuals.mean() if total > 0 else 0.0

    # Penalize trivial strategies (always predict same direction)
    balance_penalty = 0.0
    if up_pred_pct > 0.90 or up_pred_pct < 0.10:
        balance_penalty = 0.10
    elif up_pred_pct > 0.80 or up_pred_pct < 0.20:
        balance_penalty = 0.05

    return {
        "directional_accuracy": round(accuracy - balance_penalty, 6),
        "raw_accuracy": round(accuracy, 6),
        "balance_penalty": round(balance_penalty, 6),
        "up_prediction_pct": round(up_pred_pct, 4),
        "up_actual_pct": round(up_actual_pct, 4),
        "correct": int(correct),
        "total": int(total),
    }


def evaluate_walk_forward(model_fn, df):
    """
    Run walk-forward evaluation. The PRIMARY metric for autoresearch.

    Args:
        model_fn: callable(train_df, val_df) -> numpy array of 0/1 predictions
                  for val_df rows. Must only use train_df for fitting.
        df: full merged dataframe

    Returns:
        dict with average metrics across all walk-forward windows
    """
    splits = get_walk_forward_splits(df)
    all_metrics = []

    for i, (train_df, val_df) in enumerate(splits):
        predictions = model_fn(train_df, val_df)
        actuals = val_df[TARGET_COL].values
        metrics = evaluate(predictions, actuals)
        metrics["window"] = i
        all_metrics.append(metrics)
        print(f"  Window {i}: acc={metrics['directional_accuracy']:.4f} "
              f"(raw={metrics['raw_accuracy']:.4f}, "
              f"up%={metrics['up_prediction_pct']:.2f}, "
              f"n={metrics['total']})")

    avg_acc = np.mean([m["directional_accuracy"] for m in all_metrics])
    avg_raw = np.mean([m["raw_accuracy"] for m in all_metrics])
    total_correct = sum(m["correct"] for m in all_metrics)
    total_samples = sum(m["total"] for m in all_metrics)

    summary = {
        "avg_directional_accuracy": round(avg_acc, 6),
        "avg_raw_accuracy": round(avg_raw, 6),
        "total_correct": total_correct,
        "total_samples": total_samples,
        "num_windows": len(all_metrics),
        "per_window": all_metrics,
    }

    return summary


def should_save_model(avg_directional_accuracy):
    """Returns True if the model meets the save threshold."""
    return avg_directional_accuracy >= SAVE_THRESHOLD


def get_save_path(accuracy, tag=""):
    """Generate a path for saving a model checkpoint."""
    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    acc_str = f"{accuracy:.4f}".replace(".", "p")
    suffix = f"_{tag}" if tag else ""
    filename = f"model_{acc_str}_{timestamp}{suffix}.pt"
    return os.path.join(SAVED_MODELS_DIR, filename)


# ---------------------------------------------------------------------------
# Utilities for train.py
# ---------------------------------------------------------------------------

def get_instrument_names():
    """Returns list of instrument name prefixes."""
    return list(INSTRUMENTS.keys())


def get_feature_columns(df):
    """Returns columns that are NOT the target."""
    return [c for c in df.columns if c != TARGET_COL]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare data for Nifty 50 forecasting")
    parser.add_argument("--force", action="store_true", help="Re-download data even if it exists")
    args = parser.parse_args()

    print("=" * 60)
    print("Nifty 50 Directional Forecasting — Data Preparation")
    print("=" * 60)
    print()

    df = download_data(force=args.force)
    print()

    print("Walk-forward validation windows:")
    splits = get_walk_forward_splits(df)
    for i, (train_df, val_df) in enumerate(splits):
        print(f"  Window {i}: train={len(train_df)} rows "
              f"({train_df.index[0].date()} to {train_df.index[-1].date()}), "
              f"val={len(val_df)} rows "
              f"({val_df.index[0].date()} to {val_df.index[-1].date()})")
    print()

    test_df = get_test_set(df)
    if len(test_df) > 0:
        print(f"Held-out test set: {len(test_df)} rows "
              f"({test_df.index[0].date()} to {test_df.index[-1].date()})")
    else:
        print("Held-out test set: not yet available (future dates)")

    print()
    print("Done! Ready to train. Run: python train.py")
