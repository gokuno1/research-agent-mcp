"""
Nifty 50 next-day directional forecasting — autoresearch target file.
THIS IS THE FILE THE AGENT MODIFIES.

Usage: python train.py

The agent iterates on:
  - Feature engineering (build_features)
  - Model architecture (DirectionPredictor)
  - Hyperparameters (all UPPER_CASE constants)
  - Training loop details

The fixed evaluation harness is in prepare.py (do not modify).
"""

import os
import time
import math
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from datetime import datetime
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, HistGradientBoostingClassifier, ExtraTreesClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from catboost import CatBoostClassifier

from scipy.signal import hilbert
from PyEMD import EMD

from prepare import (
    load_data, evaluate_walk_forward, evaluate, should_save_model,
    get_save_path, get_instrument_names, TARGET_COL, TIME_BUDGET,
    SAVE_THRESHOLD, get_walk_forward_splits, SAVED_MODELS_DIR,
)

# ---------------------------------------------------------------------------
# Hyperparameters (AGENT: tune these)
# ---------------------------------------------------------------------------

LOOKBACK = 20           # number of past trading days as input sequence
HIDDEN_DIM = 128        # LSTM hidden dimension
NUM_LAYERS = 2          # number of LSTM layers
DROPOUT = 0.3           # dropout rate
LEARNING_RATE = 1e-3    # initial learning rate
BATCH_SIZE = 64         # training batch size
MAX_EPOCHS = 200        # max training epochs (early stopping may cut short)
PATIENCE = 20           # early stopping patience (epochs without improvement)
WEIGHT_DECAY = 1e-4     # L2 regularization

SEED = 42
CURRENT_BEST = 0.6609

# ---------------------------------------------------------------------------
# Feature engineering (AGENT: experiment here)
# ---------------------------------------------------------------------------

def _hht_features(series, prefix, slope_window=5, n_imfs_max=6):
    """
    Compute Hilbert-Huang Transform indicators from a price series.
    """
    result = {}
    values = series.dropna().values.astype(np.float64)

    if len(values) < 50:
        return result

    emd = EMD()
    emd.MAX_ITERATION = 100
    try:
        imfs = emd.emd(values, max_imf=n_imfs_max)
    except Exception:
        return result

    if imfs is None or len(imfs) == 0:
        return result

    n_imfs = imfs.shape[0]
    idx = series.dropna().index

    dominant_imf = imfs[0]
    trend_imf = imfs[-1]

    trend_s = pd.Series(trend_imf, index=idx)
    x_vals = np.arange(slope_window, dtype=np.float64)
    x_mean = x_vals.mean()
    x_var = ((x_vals - x_mean) ** 2).sum()
    trend_slope = trend_s.rolling(slope_window).apply(
        lambda w: np.sum((x_vals - x_mean) * (w.values - w.values.mean())) / x_var
        if x_var > 0 else 0.0,
        raw=False,
    )
    result[f"{prefix}_hht_trend_slope"] = trend_slope

    analytic_signals = []
    amplitudes = []
    phases = []
    for i in range(n_imfs):
        analytic = hilbert(imfs[i])
        analytic_signals.append(analytic)
        amplitudes.append(np.abs(analytic))
        phases.append(np.unwrap(np.angle(analytic)))

    dominant_amp = amplitudes[0]
    dominant_phase = phases[0]

    total_amp = np.sum(amplitudes, axis=0)
    total_amp[total_amp == 0] = 1e-10
    amp_divergence = dominant_amp / total_amp
    result[f"{prefix}_hht_amp_div"] = pd.Series(amp_divergence, index=idx)

    inst_freq = np.diff(dominant_phase) / (2.0 * np.pi)
    inst_freq = np.concatenate([[np.nan], inst_freq])
    result[f"{prefix}_hht_inst_freq"] = pd.Series(inst_freq, index=idx)

    low_freq_start = max(n_imfs // 2, 1)
    energy_per_imf = np.array([np.sum(imf ** 2) for imf in imfs])
    total_energy = energy_per_imf.sum()
    if total_energy > 0:
        low_freq_ratio = energy_per_imf[low_freq_start:].sum() / total_energy
    else:
        low_freq_ratio = 0.5
    result[f"{prefix}_hht_energy_ratio"] = pd.Series(low_freq_ratio, index=idx)

    phase_pos = np.sin(dominant_phase)
    result[f"{prefix}_hht_phase_pos"] = pd.Series(phase_pos, index=idx)

    # Enhanced: per-IMF features for first 4 IMFs
    for i in range(min(4, n_imfs)):
        amp_i = amplitudes[i]
        phase_i = phases[i]
        result[f"{prefix}_hht_imf{i}_sin"] = pd.Series(np.sin(phase_i), index=idx)
        result[f"{prefix}_hht_imf{i}_cos"] = pd.Series(np.cos(phase_i), index=idx)
        result[f"{prefix}_hht_imf{i}_amp"] = pd.Series(amp_i, index=idx)
        amp_s = pd.Series(amp_i, index=idx)
        result[f"{prefix}_hht_imf{i}_amp_ma5"] = amp_s.rolling(5).mean()
        if i > 0:
            phase_diff = phases[0] - phase_i
            result[f"{prefix}_hht_phase_diff_0_{i}"] = pd.Series(np.sin(phase_diff), index=idx)

    # Phase velocity (rate of change of dominant phase)
    phase_vel = np.diff(dominant_phase)
    phase_vel = np.concatenate([[np.nan], phase_vel])
    phase_accel = np.diff(phase_vel)
    phase_accel = np.concatenate([[np.nan], phase_accel])
    result[f"{prefix}_hht_phase_vel"] = pd.Series(phase_vel, index=idx)
    result[f"{prefix}_hht_phase_accel"] = pd.Series(phase_accel, index=idx)

    # Trend IMF normalized value
    trend_mean = np.mean(np.abs(trend_imf))
    if trend_mean > 0:
        result[f"{prefix}_hht_trend_norm"] = pd.Series(trend_imf / trend_mean, index=idx)

    return result


def build_features(df):
    """Transform raw OHLCV data into model features (continuous + binary)."""
    feat = {}
    instruments = get_instrument_names()

    for inst in instruments:
        close_col = f"{inst}_close"
        high_col = f"{inst}_high"
        low_col = f"{inst}_low"
        volume_col = f"{inst}_volume"

        if close_col not in df.columns:
            continue

        close = df[close_col]
        ret_1d = close.pct_change(1)

        # Returns at various horizons
        feat[f"{inst}_ret_1d"] = ret_1d
        feat[f"{inst}_ret_2d"] = close.pct_change(2)
        feat[f"{inst}_ret_3d"] = close.pct_change(3)
        feat[f"{inst}_ret_5d"] = close.pct_change(5)
        feat[f"{inst}_ret_10d"] = close.pct_change(10)
        feat[f"{inst}_ret_20d"] = close.pct_change(20)

        # Volatility
        feat[f"{inst}_vol_5d"] = ret_1d.rolling(5).std()
        feat[f"{inst}_vol_10d"] = ret_1d.rolling(10).std()
        feat[f"{inst}_vol_20d"] = ret_1d.rolling(20).std()

        # Volatility regime (binary)
        vol_20d = ret_1d.rolling(20).std()
        vol_60d_med = vol_20d.rolling(60).median()
        feat[f"{inst}_high_vol"] = (vol_20d > vol_60d_med).astype(float)

        # Moving averages and ratios
        ma5 = close.rolling(5).mean()
        ma10 = close.rolling(10).mean()
        ma20 = close.rolling(20).mean()
        ma50 = close.rolling(50).mean()
        feat[f"{inst}_ma5_20"] = ma5 / ma20
        feat[f"{inst}_ma10_50"] = ma10 / ma50
        feat[f"{inst}_above_ma20"] = (close > ma20).astype(float)
        feat[f"{inst}_above_ma50"] = (close > ma50).astype(float)

        # RSI 14
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss_s = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss_s.replace(0, 1e-10)
        rsi = 100 - (100 / (1 + rs))
        feat[f"{inst}_rsi_14"] = rsi
        feat[f"{inst}_rsi_ob"] = (rsi > 70).astype(float)
        feat[f"{inst}_rsi_os"] = (rsi < 30).astype(float)

        # MACD
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        macd_signal = macd_line.ewm(span=9, adjust=False).mean()
        feat[f"{inst}_macd_hist"] = macd_line - macd_signal
        feat[f"{inst}_macd_above"] = (macd_line > macd_signal).astype(float)

        # Bollinger Bands
        bb_std = close.rolling(20).std()
        bb_upper = ma20 + 2 * bb_std
        bb_lower = ma20 - 2 * bb_std
        bb_range = (bb_upper - bb_lower).replace(0, 1e-10)
        feat[f"{inst}_bb_pctb"] = (close - bb_lower) / bb_range
        feat[f"{inst}_bb_width"] = (bb_upper - bb_lower) / ma20
        feat[f"{inst}_bb_above"] = (close > bb_upper).astype(float)
        feat[f"{inst}_bb_below"] = (close < bb_lower).astype(float)

        # Stochastic Oscillator & ATR (need High/Low)
        if high_col in df.columns and low_col in df.columns:
            high = df[high_col]
            low = df[low_col]
            feat[f"{inst}_hl_range"] = (high - low) / close

            low14 = low.rolling(14).min()
            high14 = high.rolling(14).max()
            denom = (high14 - low14).replace(0, 1e-10)
            stoch_k = 100 * (close - low14) / denom
            feat[f"{inst}_stoch_k"] = stoch_k
            feat[f"{inst}_stoch_os"] = (stoch_k < 20).astype(float)
            feat[f"{inst}_stoch_ob"] = (stoch_k > 80).astype(float)

            tr = pd.concat([high - low, (high - close.shift(1)).abs(),
                            (low - close.shift(1)).abs()], axis=1).max(axis=1)
            feat[f"{inst}_atr_14"] = tr.rolling(14).mean() / close

        # Volume features
        if volume_col in df.columns:
            vol = df[volume_col]
            if vol.sum() > 0:
                feat[f"{inst}_vol_chg"] = vol.pct_change(1)
                feat[f"{inst}_vol_ma5_ratio"] = vol.rolling(5).mean() / vol.rolling(20).mean().replace(0, 1e-10)
                vol_mean = vol.rolling(20).mean()
                vol_std_s = vol.rolling(20).std().replace(0, 1e-10)
                vol_z = (vol - vol_mean) / vol_std_s
                feat[f"{inst}_vol_z"] = vol_z
                feat[f"{inst}_vol_spike"] = (vol_z > 2.0).astype(float)

    # Nifty-specific lagged direction features
    if "nifty50_close" in df.columns:
        nclose = df["nifty50_close"]
        nifty_ret = nclose.pct_change()
        feat["nifty50_dir_lag1"] = (nifty_ret.shift(1) > 0).astype(float)
        feat["nifty50_dir_lag2"] = (nifty_ret.shift(2) > 0).astype(float)
        feat["nifty50_dir_lag3"] = (nifty_ret.shift(3) > 0).astype(float)
        feat["nifty50_dir_lag5"] = (nifty_ret.shift(5) > 0).astype(float)
        up = (nifty_ret > 0).astype(int)
        streak = up.copy().astype(float)
        for i in range(1, len(streak)):
            if up.iloc[i] == up.iloc[i-1]:
                streak.iloc[i] = streak.iloc[i-1] + 1
            else:
                streak.iloc[i] = 1
        feat["nifty50_streak"] = streak.shift(1)
        ret_mean = nifty_ret.rolling(20).mean()
        ret_std = nifty_ret.rolling(20).std().replace(0, 1e-10)
        feat["nifty50_ret_zscore"] = (nifty_ret - ret_mean) / ret_std

    # Cross-instrument features
    if "nifty50_close" in df.columns and "sp500_close" in df.columns:
        nifty_ret = df["nifty50_close"].pct_change()
        sp500_ret = df["sp500_close"].pct_change()
        feat["nifty_sp500_ret_diff"] = nifty_ret - sp500_ret
        feat["sp500_ret_lag1"] = sp500_ret.shift(1)
        feat["nifty_sp500_corr_20d"] = nifty_ret.rolling(20).corr(sp500_ret)

    if "gold_close" in df.columns and "usdinr_close" in df.columns:
        feat["gold_usdinr_corr_20d"] = df["gold_close"].pct_change().rolling(20).corr(
            df["usdinr_close"].pct_change())

    if "gold_close" in df.columns and "crude_close" in df.columns:
        feat["gold_crude_ratio"] = df["gold_close"] / df["crude_close"]

    if "gold_close" in df.columns and "silver_close" in df.columns:
        feat["gold_silver_ratio"] = df["gold_close"] / df["silver_close"]

    if "nifty50_close" in df.columns:
        nifty_ret = df["nifty50_close"].pct_change()
        for other in ["crude", "gold", "usdinr", "silver"]:
            if f"{other}_close" in df.columns:
                feat[f"nifty_{other}_corr_20d"] = nifty_ret.rolling(20).corr(
                    df[f"{other}_close"].pct_change())

    # Calendar / seasonality
    feat["dow_mon"] = pd.Series((df.index.dayofweek == 0).astype(float), index=df.index)
    feat["dow_tue"] = pd.Series((df.index.dayofweek == 1).astype(float), index=df.index)
    feat["dow_wed"] = pd.Series((df.index.dayofweek == 2).astype(float), index=df.index)
    feat["dow_thu"] = pd.Series((df.index.dayofweek == 3).astype(float), index=df.index)
    feat["dow_fri"] = pd.Series((df.index.dayofweek == 4).astype(float), index=df.index)
    feat["month_sin"] = pd.Series(np.sin(2 * np.pi * df.index.month / 12), index=df.index)
    feat["month_cos"] = pd.Series(np.cos(2 * np.pi * df.index.month / 12), index=df.index)


    # Hilbert-Huang Transform features
    hht_all = {}
    for inst in instruments:
        close_col = f"{inst}_close"
        if close_col not in df.columns:
            continue
        hht = _hht_features(df[close_col], inst)
        hht_all[inst] = hht
        for fname, fseries in hht.items():
            feat[fname] = fseries.reindex(df.index)

    # Cross-instrument HHT phase differences
    if "nifty50" in hht_all and "sp500" in hht_all:
        for imf_i in range(3):
            nk = f"nifty50_hht_imf{imf_i}_sin"
            sk = f"sp500_hht_imf{imf_i}_sin"
            nck = f"nifty50_hht_imf{imf_i}_cos"
            sck = f"sp500_hht_imf{imf_i}_cos"
            if nk in feat and sk in feat:
                feat[f"nifty_sp500_phase_diff_imf{imf_i}"] = feat[nk] * feat[sck] - feat[nck] * feat[sk]

    for other in ["gold", "crude", "usdinr"]:
        if "nifty50" in hht_all and other in hht_all:
            nk = "nifty50_hht_phase_pos"
            ok = f"{other}_hht_phase_pos"
            if nk in feat and ok in feat:
                feat[f"nifty_{other}_phase_diff"] = feat[nk] - feat[ok]

    features = pd.DataFrame(feat, index=df.index)
    features = features.replace([np.inf, -np.inf], np.nan)
    features = features.dropna()

    return features


# ---------------------------------------------------------------------------
# Model (AGENT: experiment with architecture)
# ---------------------------------------------------------------------------

class DirectionPredictor(nn.Module):
    """LSTM-based directional predictor. Agent can replace with GRU, Transformer, CNN, etc."""

    def __init__(self, input_dim):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=HIDDEN_DIM,
            num_layers=NUM_LAYERS,
            batch_first=True,
            dropout=DROPOUT if NUM_LAYERS > 1 else 0.0,
        )
        self.head = nn.Sequential(
            nn.Linear(HIDDEN_DIM, 64),
            nn.ReLU(),
            nn.Dropout(DROPOUT),
            nn.Linear(64, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        # x shape: (batch, lookback, features)
        lstm_out, (h_n, _) = self.lstm(x)
        last_hidden = h_n[-1]  # (batch, hidden_dim)
        return self.head(last_hidden).squeeze(-1)


# ---------------------------------------------------------------------------
# Data preparation utilities
# ---------------------------------------------------------------------------

def make_sequences(features_np, targets_np, lookback):
    """Create overlapping sequences from feature matrix and target vector."""
    X, y = [], []
    for i in range(lookback, len(features_np)):
        X.append(features_np[i - lookback:i])
        y.append(targets_np[i])
    return np.array(X), np.array(y)


def normalize_features(train_feat, val_feat):
    """Normalize using ONLY training set statistics (prevents data leakage)."""
    mean = train_feat.mean(axis=0)
    std = train_feat.std(axis=0)
    std[std == 0] = 1.0

    train_norm = (train_feat - mean) / std
    val_norm = (val_feat - mean) / std

    return train_norm, val_norm, mean, std


# ---------------------------------------------------------------------------
# Training function for one walk-forward window
# ---------------------------------------------------------------------------

def train_single_window(train_df, val_df, time_limit=None):
    """
    Train GBT model on train_df, predict on val_df.
    """
    all_data = pd.concat([train_df, val_df])
    all_features = build_features(all_data)

    common_train_idx = train_df.index.intersection(all_features.index)
    common_val_idx = val_df.index.intersection(all_features.index)

    if len(common_train_idx) < LOOKBACK + 10 or len(common_val_idx) < 1:
        print("  WARNING: Insufficient data after feature engineering")
        return np.zeros(len(val_df))

    train_feat = all_features.loc[common_train_idx].values
    val_feat = all_features.loc[common_val_idx].values

    train_targets = train_df.loc[common_train_idx, TARGET_COL].values
    val_targets = val_df.loc[common_val_idx, TARGET_COL].values

    train_feat = np.nan_to_num(train_feat.copy(), nan=0.0, posinf=0.0, neginf=0.0)
    val_feat = np.nan_to_num(val_feat.copy(), nan=0.0, posinf=0.0, neginf=0.0)

    # Class weighting: extra weight on down class for balanced predictions
    sample_weights = np.ones(len(train_targets))
    up_frac = train_targets.mean()
    down_frac = 1.0 - up_frac
    sample_weights[train_targets == 1] = 0.5 / max(up_frac, 1e-10)
    sample_weights[train_targets == 0] = 0.5 / max(down_frac, 1e-10)

    clf = GradientBoostingClassifier(
        n_estimators=350, max_depth=2, learning_rate=0.02,
        subsample=0.8, min_samples_leaf=10, max_features='sqrt',
        random_state=SEED,
    )
    clf.fit(train_feat, train_targets, sample_weight=sample_weights)
    final_predictions = clf.predict(val_feat)

    full_predictions = np.zeros(len(val_df), dtype=int)
    aligned_start = len(val_df) - len(final_predictions)
    if aligned_start >= 0:
        full_predictions[aligned_start:] = final_predictions
    else:
        full_predictions = final_predictions[-len(val_df):]

    return full_predictions


# ---------------------------------------------------------------------------
# Main: autoresearch entry point
# ---------------------------------------------------------------------------

def main():
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(SEED)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name()}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f} GB")
    print()

    print("Loading data...")
    df = load_data()
    print(f"Data: {len(df)} rows, {len(df.columns)} columns")
    print(f"Date range: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"Target distribution: up={df[TARGET_COL].sum()}, "
          f"down={len(df) - df[TARGET_COL].sum()}, "
          f"up%={df[TARGET_COL].mean():.2%}")
    print()

    # Feature info
    sample_features = build_features(df)
    print(f"Features: {sample_features.shape[1]} columns after engineering")
    print(f"Feature names: {list(sample_features.columns)}")
    print()

    # Model info
    input_dim = sample_features.shape[1]
    model = DirectionPredictor(input_dim)
    num_params = sum(p.numel() for p in model.parameters())
    print(f"Model: {model.__class__.__name__}")
    print(f"Parameters: {num_params:,}")
    print(f"Lookback: {LOOKBACK} days")
    print(f"Hidden dim: {HIDDEN_DIM}, Layers: {NUM_LAYERS}, Dropout: {DROPOUT}")
    print(f"LR: {LEARNING_RATE}, Batch: {BATCH_SIZE}, Max epochs: {MAX_EPOCHS}")
    print()

    print("=" * 60)
    print("Walk-Forward Evaluation")
    print("=" * 60)

    t_start = time.time()

    # Time allocation: split budget across walk-forward windows
    splits = get_walk_forward_splits(df)
    num_windows = len(splits)
    time_per_window = (TIME_BUDGET * 0.9) / num_windows  # 90% for training, 10% buffer

    def model_fn(train_df, val_df):
        return train_single_window(train_df, val_df, time_limit=time_per_window)

    results = evaluate_walk_forward(model_fn, df)

    t_elapsed = time.time() - t_start

    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    avg_acc = results["avg_directional_accuracy"]
    print(f"avg_directional_accuracy: {avg_acc:.6f}")
    print(f"avg_raw_accuracy:         {results['avg_raw_accuracy']:.6f}")
    print(f"total_correct:            {results['total_correct']}")
    print(f"total_samples:            {results['total_samples']}")
    print(f"num_windows:              {results['num_windows']}")
    print(f"training_seconds:         {t_elapsed:.1f}")
    print(f"time_budget:              {TIME_BUDGET}")
    print()

    # Save model if threshold met
    if should_save_model(avg_acc):
        save_path = get_save_path(avg_acc)
        # Retrain on latest window to save a usable model
        last_train, last_val = splits[-1]
        all_data = pd.concat([last_train, last_val])
        all_features = build_features(all_data)
        common_idx = all_data.index.intersection(all_features.index)
        feat = all_features.loc[common_idx].values
        targets = all_data.loc[common_idx, TARGET_COL].values
        mean = feat.mean(axis=0)
        std = feat.std(axis=0)
        std[std == 0] = 1.0
        feat_norm = (feat - mean) / std
        X, y = make_sequences(feat_norm, targets, LOOKBACK)
        X_t = torch.tensor(X, dtype=torch.float32).to(device)
        y_t = torch.tensor(y, dtype=torch.float32).to(device)
        final_model = DirectionPredictor(X.shape[2]).to(device)
        opt = torch.optim.Adam(final_model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
        crit = nn.BCELoss()
        final_model.train()
        for epoch in range(min(MAX_EPOCHS, 100)):
            idx = torch.randperm(len(X_t), device=device)
            for start in range(0, len(X_t), BATCH_SIZE):
                batch_idx = idx[start:start + BATCH_SIZE]
                pred = final_model(X_t[batch_idx])
                loss = crit(pred, y_t[batch_idx])
                opt.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(final_model.parameters(), max_norm=1.0)
                opt.step()

        torch.save({
            "model_state_dict": final_model.state_dict(),
            "accuracy": avg_acc,
            "input_dim": X.shape[2],
            "lookback": LOOKBACK,
            "hidden_dim": HIDDEN_DIM,
            "num_layers": NUM_LAYERS,
            "dropout": DROPOUT,
            "feature_mean": mean,
            "feature_std": std,
            "timestamp": datetime.now().isoformat(),
        }, save_path)

        print(f"MODEL_SAVED: {save_path}")
        print(f"  accuracy: {avg_acc:.4f} (threshold: {SAVE_THRESHOLD})")
    else:
        print(f"Model NOT saved (accuracy {avg_acc:.4f} < threshold {SAVE_THRESHOLD})")

    if avg_acc > CURRENT_BEST:
        acc_tag = f"{avg_acc:.4f}".replace(".", "p")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_dir = os.path.join(SAVED_MODELS_DIR, f"model_{acc_tag}_{ts}")
        os.makedirs(new_dir, exist_ok=True)

        last_train, last_val = splits[-1]
        all_data = pd.concat([last_train, last_val])
        all_features = build_features(all_data)
        common_idx = all_data.index.intersection(all_features.index)
        feat = all_features.loc[common_idx].values
        targets = all_data.loc[common_idx, TARGET_COL].values
        feat_clean = np.nan_to_num(feat.copy(), nan=0.0, posinf=0.0, neginf=0.0)
        mean = feat.mean(axis=0)
        std = feat.std(axis=0)
        std[std == 0] = 1.0

        sample_w = np.ones(len(targets))
        up_f = targets.mean()
        down_f = 1.0 - up_f
        sample_w[targets == 1] = 0.5 / max(up_f, 1e-10)
        sample_w[targets == 0] = 0.5 / max(down_f, 1e-10)

        save_clf = GradientBoostingClassifier(
            n_estimators=350, max_depth=2, learning_rate=0.02,
            subsample=0.8, min_samples_leaf=10, max_features='sqrt',
            random_state=SEED,
        )
        save_clf.fit(feat_clean, targets, sample_weight=sample_w)

        import pickle
        with open(os.path.join(new_dir, "gbt_model.pkl"), "wb") as f:
            pickle.dump(save_clf, f)

        torch.save({
            "accuracy": avg_acc,
            "input_dim": feat.shape[1],
            "lookback": LOOKBACK,
            "hidden_dim": HIDDEN_DIM,
            "num_layers": NUM_LAYERS,
            "dropout": DROPOUT,
            "feature_mean": mean,
            "feature_std": std,
            "timestamp": datetime.now().isoformat(),
            "model_type": "gbt",
        }, os.path.join(new_dir, "checkpoint.pt"))

        print(f"BETTER_MODEL_SAVED: {new_dir}")
        print(f"  accuracy: {avg_acc:.4f} > current_best: {CURRENT_BEST:.4f}")

    print()
    print("---")
    print(f"avg_directional_accuracy: {avg_acc:.6f}")
    print(f"training_seconds:         {t_elapsed:.1f}")
    print(f"num_params:               {num_params}")
    print(f"lookback:                 {LOOKBACK}")
    print(f"hidden_dim:               {HIDDEN_DIM}")
    print(f"num_features:             {sample_features.shape[1]}")


if __name__ == "__main__":
    main()
