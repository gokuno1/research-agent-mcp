# Autoresearch: Nifty 50 Directional Forecasting

Autonomous AI-agent-driven experimentation to predict the next-day direction (up/down) of Nifty 50 using multi-instrument price data and deep learning.

Built on the [autoresearch](https://github.com/karpathy/autoresearch) pattern by Karpathy — the AI agent iterates on feature engineering, model architecture, and hyperparameters while you sleep.

## How It Works

Three files, one loop:

| File | Purpose | Who Edits |
|------|---------|-----------|
| `prepare.py` | Data download (yfinance), walk-forward splits, evaluation harness | **Fixed** |
| `train.py` | Feature engineering, model architecture, training loop | **AI Agent** |
| `program.md` | Instructions for the agent's autonomous loop | **Human** |

**Instruments**: Nifty 50, S&P 500, Gold, Silver, Crude Oil, USD/INR

**Metric**: Average directional accuracy across 3 walk-forward validation windows

**Save threshold**: Model auto-saved when accuracy >= 75%

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download data (one-time, ~1 min)
python prepare.py

# 3. Run baseline experiment
python train.py
```

## Running with Cursor Agent

Open this folder in Cursor, then in Agent chat:

```
Read program.md and let's start the autoresearch loop.
Run the baseline first, then begin iterating.
```

Enable **auto-run** in Cursor Settings → Features → Terminal for autonomous mode.

## Project Structure

```
prepare.py        — data download, walk-forward splits, evaluation (DO NOT MODIFY)
train.py          — feature engineering, model, training loop (AGENT MODIFIES)
program.md        — agent instructions
requirements.txt  — Python dependencies
data/             — downloaded price CSVs (auto-created)
saved_models/     — models that hit 75%+ accuracy (auto-created)
```

## Walk-Forward Validation

To prevent data leakage, we use 3 rolling windows:

- **Window 0**: Train 2021-01 → 2024-06, Val 2024-07 → 2024-12
- **Window 1**: Train 2021-07 → 2025-01, Val 2025-02 → 2025-07
- **Window 2**: Train 2022-01 → 2025-07, Val 2025-08 → 2026-01
- **Test set** (held out): 2026-02 → 2026-03 (never used during autoresearch)
