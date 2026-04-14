# Nifty 50 Directional Forecast — Autoresearch Program

## Objective

Maximize **average directional accuracy** of next-day Nifty 50 movement prediction
across walk-forward validation windows. Target: **>= 75% accuracy** to trigger model save.

## Setup

1. **Ensure data exists**: Run `python prepare.py` once to download 5 years of price data from yfinance.
   If `data/merged.csv` already exists, this step is skipped automatically.
2. **Run baseline**: `python train.py` — establishes the starting accuracy.
3. **Begin iterating**: modify `train.py`, run, check results, keep or revert.

## How It Works

- `prepare.py` — **DO NOT MODIFY**. Downloads data, provides walk-forward splits, evaluation function.
- `train.py` — **THE FILE YOU MODIFY**. Feature engineering, model architecture, training loop.
- `program.md` — **This file**. Your instructions.

The script runs walk-forward validation across 3 time windows:
- Window 0: Train 2021-01 → 2024-06, Validate 2024-07 → 2024-12
- Window 1: Train 2021-07 → 2025-01, Validate 2025-02 → 2025-07
- Window 2: Train 2022-01 → 2025-07, Validate 2025-08 → 2026-01

Average directional accuracy across all windows is the metric. Higher is better.

## What You Can Modify

Only `train.py`. Everything in it is fair game:

### Feature Engineering (`build_features` function)
*** Derive binary features (wherever possible) from below given feature engineering topics ***
-	**Core technical indicators (continuous)**: RSI (e.g., 14-period), MACD (MACD line, signal line, histogram), Bollinger Bands (upper band, lower band, bandwidth, %B), ATR (e.g., 14-period), Stochastic Oscillator (%K, %D), OBV (On-Balance Volume),
-	**Lagged returns & momentum**: Simple log/percentage returns at horizons: 1d, 2d, 3d, 5d, 10d, 20d, 60d, Rate of Change (ROC) over selected windows (e.g., 5d, 10d, 20d), Windowed momentum: cumulative return over short/mid windows (e.g., 5d, 20d), optionally normalized
-	**Volatility & regime features**: Rolling volatility of returns (e.g., 5d, 10d, 20d), Vol-of-vol: rolling volatility of the rolling-vol series, Volatility regime flags: high-vol vs low-vol (e.g., rolling-vol above/below percentile thresholds)
-	**Mean reversion / distance-from-levels**: Moving averages: SMA and/or EMA over 5, 10, 20, 50 days, Distance from moving averages: Close − MA(5, 10, 20, 50), and/or Close / MA ratios, Price/return z-scores: standardized deviation from rolling mean over chosen windows, Mean-reversion strength flags: |z-score| above given thresholds
-	**Calendar / seasonality features**: Day-of-week (one-hot or integer), Month (one-hot or integer), Quarter (1–4), Expiry-week flag (binary; 1 if in derivatives expiry week, else 0),
-	**Volume-related features**: Volume z-score relative to rolling mean (volume spike indicator), Volume spike flag: 1 if volume z-score above threshold, Volume–price divergence indicators (e.g., price up with falling volume, price down with rising volume)
-	**Macro-Related features**: currency_stress_zscore, gold_crude_ratio, gold_silver_ratio, gold_nifty_beta, crude_nifty_beta, usdinr_nifty_beta, cointegration_pvalue (USD/INR, GOLD, SILVER, CRUDE OIL and NIFTY 50), correlation (between USD/INR, GOLD, SILVER, CRUDE OIL and NIFTY 50)
-   **Hilbert-Huang Transform**: Trend IMF slope, Instantaneous Amplitude Divergence, Instantaneous Frequency (IF) of Dominant IMF, Energy ratio (low-freq / total), Phase positioning

### Model Architecture (`DirectionPredictor` class)
- LSTM → GRU, Transformer encoder, 1D CNN, CNN+LSTM hybrid
- Attention mechanisms over the lookback window
- Stacked autoencoders
- Multi-head architecture: separate branches for different feature groups, merged
- Residual connections, layer normalization, batch normalization
- Ensemble stacking
- Wider/deeper networks, bottleneck layers

### Hyperparameters (all UPPER_CASE constants)
- `LOOKBACK`: sequence length (try 5, 10, 20, 40, 60)
- `HIDDEN_DIM`: model width (try 32, 64, 128, 256)
- `NUM_LAYERS`: depth (try 1, 2, 3, 4)
- `DROPOUT`: regularization (try 0.1, 0.2, 0.3, 0.5)
- `LEARNING_RATE`: optimizer step size (try 1e-2, 5e-3, 1e-3, 5e-4, 1e-4)
- `BATCH_SIZE`: mini-batch (try 16, 32, 64, 128)
- `MAX_EPOCHS`: training epochs (try 100, 200, 500)
- `PATIENCE`: early stopping (try 10, 20, 30, 50)
- `WEIGHT_DECAY`: L2 regularization (try 0, 1e-5, 1e-4, 1e-3)

### Training Loop
- Optimizer: Adam → AdamW, SGD+momentum, RAdam, Lookahead
- Learning rate schedules: cosine annealing, step decay, warmup+decay
- Loss function: BCE → focal loss, label smoothing, weighted BCE
- Data augmentation: noise injection, time warping, mixup
- Gradient clipping strategies
- Class weighting for imbalanced directions

## What You CANNOT Modify

- `prepare.py` — the evaluation harness is fixed
- The walk-forward windows — these are fixed for fair comparison
- The target column — always `nifty50_direction` (1=up, 0=down)

## Rules

1. **ONE change per experiment**. State your hypothesis before modifying code.
2. **Run `python train.py`** after each change. Redirect output: `python train.py > run.log 2>&1`
3. **Read the result**: `grep "avg_directional_accuracy:" run.log`
4. **If accuracy improved** → KEEP the change.
5. **If accuracy is equal or worse** → REVERT the change.
6. **Watch for trivial solutions**: if `up_prediction_pct` > 0.85, the model is just predicting "up" always. Fix this with class weighting, focal loss, or balanced sampling.
7. **Watch for overfitting**: if train accuracy >> val accuracy, add regularization.
8. **If model crashes**: fix trivial bugs and re-run. If fundamentally broken, revert and try something else.
9. **Log every experiment** in the Experiment Log table below.
10. **If accuracy >= 75%**: the model is automatically saved to `saved_models/`. Keep iterating to find even better.

## Output Format

The script prints:
```
avg_directional_accuracy: 0.XXXXXX
training_seconds:         XXX.X
num_params:               XXXX
lookback:                 XX
hidden_dim:               XXX
num_features:             XX
```

Extract the key metric: `grep "avg_directional_accuracy:" run.log`

If a model is saved, you'll also see:
```
MODEL_SAVED: saved_models/model_0pXXXX_YYYYMMDD_HHMMSS.pt
```

## NEVER STOP

Once the experiment loop has begun, do NOT pause to ask if you should continue.
Keep running experiments indefinitely until manually stopped.
If you run out of ideas, re-read this file, try combining previous near-misses,
try more radical changes, or revisit experiments that showed promise.

## Current Best

- Metric: 0.6609
- Configuration: GBT(350,depth=2,lr=0.02,subsample=0.8,min_leaf=10,max_feat=sqrt) + class_weight + NO normalization + 379 features (enhanced HHT: per-IMF sin/cos/amp, phase diffs, phase vel/accel, cross-instrument phase)
- Saved: saved_models/model_0p6609_20260408_113217/
- Per-window: W0=0.6016, W1=0.6667, W2=0.7143

## Experiment Log

| # | Hypothesis | Change | Accuracy | Keep? |
|---|-----------|--------|----------|-------|
| 0 | Baseline | Original train.py | 0.5541 | base |
| 1 | Add comprehensive binary/threshold features | Enhanced build_features (RSI/MACD/BB/Stoch/calendar/etc) | 0.5623 | YES |
| 2 | Class weighting eliminates balance penalty | Inverse-frequency sample_weight | 0.5960 | YES |
| 3 | GBT+HistGBT+RF ensemble improves | 3-model probability average | 0.5683 | NO |
| 4 | Deeper trees (depth=3) capture interactions | max_depth=3, n_estimators=500, lr=0.02 | 0.5629 | NO |
| 5 | HistGBT more robust to noise | Replace GBT with HistGBT | 0.5539 | NO |
| 6 | Feature importance selection removes noise | 2-stage: pre-fit GBT → top 80 features | 0.5655 | NO |
| 7 | Lookback returns add temporal context | Flattened 5-day lagged returns per instrument | 0.5652 | NO |
| 8 | More trees + lower LR | n_estimators=600, lr=0.015 | 0.5902 | NO (close) |
| 9 | GBT+ExtraTrees ensemble | 60/40 weighted probability average | 0.5738 | NO |
| 10 | HHT features add noise | Remove HHT features | 0.5766 | NO |
| 11 | Threshold optimization on cal set | Optimized prob threshold per window | 0.5830 | NO |
| 12 | Seed ensemble reduces variance | Average 5 seeds | 0.5626 | NO |
| 13 | Stronger regularization | subsample=0.6, min_samples_leaf=20 | 0.5712 | NO |
| 14 | LSTM captures sequential patterns | GBT+LSTM hybrid (70/30) | 0.5763 | NO |
| 16 | XGBoost/LightGBM better impl | Install xgboost/lightgbm | CRASH | NO |
| 17 | Regime-specific models | Separate high/low vol GBTs | 0.5710 | NO |
| 18 | Stronger down-class weight | 1.3× extra on down class | 0.5713 | NO |
| 19 | Lagged cross-instrument features | SP500/gold/crude lag1-2 returns | 0.5486 | NO |
| 20 | More features per split | max_features=0.3 | 0.5544 | NO |
| 21 | Skip normalization for trees | Remove z-score normalization | 0.5932 | NO |
| 22 | GBT+LogReg ensemble | 70/30 weighted probability | 0.5880 | NO |
| 23 | Expiry-week calendar feature | Indian derivatives expiry flag | 0.5628 | NO |
| 24 | Recent training data only | Use last 70% of training data | 0.5628 | NO |
| 25 | Extreme feature subsampling | max_features='log2' | 0.5597 | NO |
| 26 | Binary features only | Select only 0/1 features | 0.4988 | NO |
| 27 | Decision stumps + many trees | max_depth=1, n_estimators=1000, lr=0.01 | 0.5740 | NO |
| 28 | Curated 20-feature set | Hand-picked domain features | 0.5572 | NO |
| 29 | Time-series stacking | GBT+GBT_reg+LogReg → meta-GBT | 0.5766 | NO |
| 30 | Gap/intraday features | Open-close, high-low features | 0.5316 | NO |
| 31 | GBT early stopping | n_iter_no_change=20, val_frac=0.15 | 0.5374 | NO |
| 32 | Regression on returns | GBT regressor → threshold at 0 | 0.5630 | NO |
| 33 | Noise augmentation | 3 models on noisy copies, averaged | 0.5657 | NO |
| 34 | Rolling percentile rank | 60d percentile rank transform | 0.5738 | NO |
| 35 | Time-decayed sample weights | Exponential decay (half-life=250d) | 0.5630 | NO |
| 36 | Two-config GBT average | 50/50 blend of 350/0.025 + 600/0.015 | 0.5902 | NO |
| 37 | Exponential loss | loss='exponential' (AdaBoost-style) | 0.5765 | NO |
| 38 | OBV features | On-Balance Volume + divergence | 0.5598 | NO |
| 39 | Adaptive seed selection | Best seed per window from cal set | 0.5651 | NO |
| 40 | PCA augmented features | Original + 20 PCA components | 0.5575 | NO |
| 41 | CatBoost replaces GBT | CatBoost(500,depth=4,lr=0.03,balanced) | 0.6213 | NO |
| 42 | CatBoost shallow+regularized | CatBoost(700,depth=3,lr=0.02,rsm=0.7) | 0.6271 | NO |
| 43 | CatBoost depth=2 | CatBoost(500,depth=2,lr=0.025) | 0.6240 | NO |
| 44 | Rolling beta features | GBT + rolling betas + currency stress (401 feat) | 0.6465 | NO |
| 45 | Vol-of-vol + ROC features | Added vol-of-vol + ROC + n_est=400 (425 feat) | 0.6326 | NO |
| 46 | Rank normalization | Percentile-rank instead of z-score | 0.6411 | NO |
| 47 | 3-seed prob averaging | Average proba from seeds 42,123,456 | 0.6358 | NO |
| 48 | Subsample tuning | subsample=0.85 / 0.75 | 0.6412 | NO |
| 49 | min_samples_leaf=10 | Increase leaf reg 8→10 | 0.6552 | YES |
| 50 | min_samples_leaf=12 | Too much regularization | 0.6357 | NO |
| 51 | n_estimators=400 + leaf=10 | More trees with new leaf | 0.6524 | NO |
| 52 | lr=0.02 + leaf=10 | Slower learning rate | 0.6582 | YES |
| 53 | lr=0.015 | Even slower learning | 0.6440 | NO |
| 54 | n_est=450 + lr=0.02 | More iterations | 0.6468 | NO |
| 55 | Rolling betas + lr=0.02 | Feature additions with new config | 0.6410 | NO |
| 56 | max_features=None | All features per split | 0.6128 | NO |
| 57 | Calibrated threshold | predict_proba + cal set threshold | 0.6155 | NO |
| 58 | No normalization | Skip z-score normalization | 0.6609 | YES |
| 59 | Softer class weighting | sqrt inverse frequency | 0.6471 | NO |
| 60-81 | Various tuning | Seeds, thresholds, ensembles, features | ≤0.6548 | NO |
| 82 | 60d returns | Added 60d pct_change per instrument | 0.6240 | NO |
| 83 | Vol-price divergence | Binary bullish/bearish vol-price signals | 0.6298 | NO |
| 84 | Stochastic %D + K/D cross | Added smoothed stochastic + crossover | 0.6438 | NO |
| 85 | HHT Nifty-only | Remove HHT for non-Nifty instruments (238 feat) | 0.6350 | NO |
| 86 | HHT Nifty+SP500 | HHT for equity indices only (268 feat) | 0.6577 | NO |
| 87 | HHT Nifty+SP500+Gold | HHT for 3 key instruments (296 feat) | 0.6523 | NO |
| 88 | min_impurity_decrease | min_impurity_decrease=0.001 | 0.6609 | NO (same) |
| 89 | max_features=0.5 | 50% features per split | 0.6155 | NO |
| 90 | n_est=250, lr=0.025 | Fewer trees, faster learning | 0.6442 | NO |
| 91 | n_est=300 | Slightly fewer trees | 0.6469 | NO |
| 92 | subsample=0.75 | More aggressive subsampling | 0.6414 | NO |
| 93 | subsample=0.85 | Less aggressive subsampling | 0.6524 | NO |
| 94 | Time-decayed class weight | Exp decay (half-life=500d) + class weight | 0.6242 | NO |
| 95 | Seed=7 | Different random initialization | 0.6384 | NO |
| 96 | Seed=0 | Different random initialization (W0=0.6341!) | 0.6519 | NO |
| 97 | 2-seed prob avg (42,0) | Average probabilities from 2 seeds | 0.6552 | NO |
| 98 | Top-100 feature selection | GBT importance → top 100 → retrain | 0.6298 | NO |
| 99 | leaf=8 + lr=0.02 + no norm | Old leaf with new config | 0.6439 | NO |
| 100 | n_est=375 | Fine-grained between 350 and 400 | 0.6495 | NO |
| 101 | Outlier clipping ±3σ | Clip features to ±3 std | 0.6525 | NO |
| 102 | Outlier clipping ±5σ | Gentler clipping | 0.6580 | NO |
| 103 | Outlier clipping ±4σ | Between 3σ and 5σ | 0.6580 | NO |
| 104 | loss=exponential | AdaBoost-style loss | 0.6468 | NO |
| 105 | Remove calendar features | No DOW/month features (372 feat) | 0.6437 | NO |
| 106 | Remove Nifty lag features | No dir_lag/streak/zscore (373 feat) | 0.6330 | NO |
| 107 | Two-stage GBT | Nifty-only GBT → full GBT w/ stage1 proba | 0.6131 | NO |
| 108 | RandomForest | RF(500,depth=5) — W2=0.7395 best ever! | 0.6326 | NO |
| 109 | 70/30 GBT+RF blend | Probability average GBT+RF | 0.6580 | NO |
| 110 | 80/20 GBT+RF blend | Less RF influence | 0.6580 | NO |
| 111 | CatBoost depth=2 lr=0.02 | CatBoost matching GBT params | 0.6102 | NO |
| 112 | Nifty RSI(5)+RSI(21) | Multi-period RSI | 0.6520 | NO |
| 113 | Last 500 train days | Trim old training data | 0.6297 | NO |
| 114 | ccp_alpha=0.001 | Cost-complexity pruning | 0.6582 | NO |
| 115 | ccp_alpha=0.0001 | Gentler pruning | 0.6609 | NO (same) |
| 116 | ccp_alpha=0.0005 | Between 0.001 and 0.0001 | 0.6552 | NO |
| 117 | EMA ratios | Replace SMA with EMA for MA features | 0.6464 | NO |
| 118 | dist_high/low_20d | Nifty distance from 20d high/low | 0.6604 | NO (close!) |
| 119 | dist_high/low_10d | 10d variant | 0.6521 | NO |
| 120 | dist_high_20d only | Only high distance (low redundant) | 0.6415 | NO |
| 121 | dist_20d + n_est=375 | More trees for extra features | 0.6492 | NO |
| 122 | dist_20d + lr=0.025 | Original LR with dist features | 0.6438 | NO |
| 123 | dist_20d + leaf=12 | More regularization with dist features | 0.6518 | NO |
| 124 | Quarter features | Quarter sin/cos seasonality | 0.6354 | NO |
| 125 | GBT early stopping | n_iter_no_change=30, val_frac=0.1 | 0.6243 | NO |
| 126 | ExtraTrees | ExtraTrees(500,depth=5) | 0.6022 | NO |
| 127 | Cross-instrument signals | SP500 lead/strong lag features | 0.6464 | NO |
| 128 | leaf=11 | Micro-tuning leaf | 0.6497 | NO |
| 129 | leaf=9 | Between 8 and 10 | 0.6496 | NO |
| 130 | Noise injection 1% | Gaussian noise on training features | 0.6471 | NO |
| 131 | 80/20 depth2+depth3 blend | Two-depth GBT probability blend | 0.6607 | NO (close!) |
| 132 | 90/10 depth2+depth3 blend | Less depth3 influence | 0.6580 | NO |
| 133 | 80/20 depth2+depth3(leaf=20) | More regularized depth3 | 0.6607 | NO (close!) |
| 134 | Blend + threshold=0.49 | Probability shift favoring up | 0.6470 | NO |
| 135 | Blend + threshold=0.51 | Probability shift favoring down | 0.6522 | NO |
| 136 | Decision stumps depth=1 | max_depth=1, n_est=700, lr=0.01 | 0.6215 | NO |
| 137 | Rolling Sharpe ratio | Nifty50 20d rolling Sharpe feature | 0.6358 | NO |
| 138 | dist_20d + depth blend | Combining two near-misses | 0.6547 | NO |
| 139 | HistGBT | HistGradientBoostingClassifier | 0.6269 | NO |
| 140 | max_features=25 | Slightly more than sqrt | 0.6437 | NO |
| 141 | max_features=15 | Less than sqrt | 0.6354 | NO |
| 142 | lr=0.018 | Between 0.015 and 0.02 | 0.6442 | NO |
| 143 | lr=0.022 | Between 0.02 and 0.025 | 0.6523 | NO |
| 144 | 3-seed hard vote | Majority vote seeds 42,0,7 | 0.6493 | NO |
| 145 | Half-strength class weight | Softer class weighting | 0.6471 | NO |
| 146 | min_samples_split=20 | Constrain splits | 0.6609 | NO (same) |
| 147 | min_samples_split=30 | More restrictive splits | 0.6441 | NO |
| 148 | Yeo-Johnson transform | Power transform on features | 0.6582 | NO |
| 149 | Quantile transform | Uniform quantile mapping | 0.6553 | NO |
| 150 | 85/15 depth blend | Fine-tuned blend weight | 0.6580 | NO |

