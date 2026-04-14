"""
Daily Nifty 50 next-day direction prediction using the saved LSTM model.

Usage:
    python predict_nn.py                          # predict next trading day
    python predict_nn.py --model path/to/model.pt # use a specific checkpoint
    python predict_nn.py --days 5                 # show last 5 days + next prediction

Requires: yfinance, torch, pandas, numpy, scipy, PyEMD, scikit-learn
"""

import os
import sys
import ssl
import argparse
import warnings
from datetime import datetime, timedelta

ssl._create_default_https_context = ssl._create_unverified_context

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import yfinance as yf
from scipy.signal import hilbert
from PyEMD import EMD

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODEL = os.path.join(
    SCRIPT_DIR, "saved_models", "model_0p6467_20260402_151845.pt"
)

INSTRUMENTS = {
    "nifty50": "^NSEI",
    "sp500": "^GSPC",
    "gold": "GC=F",
    "silver": "SI=F",
    "crude": "CL=F",
    "usdinr": "INR=X",
}

# ---------------------------------------------------------------------------
# Model architecture — must match train.py exactly
# ---------------------------------------------------------------------------

class DirectionPredictor(nn.Module):
    def __init__(self, input_dim, hidden_dim=128, num_layers=2, dropout=0.3):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.head = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        _, (h_n, _) = self.lstm(x)
        return self.head(h_n[-1]).squeeze(-1)


# ---------------------------------------------------------------------------
# Feature engineering — copied from train.py to keep predict_nn.py standalone
# ---------------------------------------------------------------------------

def _hht_features(series, prefix, slope_window=5, n_imfs_max=6):
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

    analytic_signals, amplitudes, phases = [], [], []
    for i in range(n_imfs):
        analytic = hilbert(imfs[i])
        analytic_signals.append(analytic)
        amplitudes.append(np.abs(analytic))
        phases.append(np.unwrap(np.angle(analytic)))

    dominant_amp = amplitudes[0]
    dominant_phase = phases[0]

    total_amp = np.sum(amplitudes, axis=0)
    total_amp[total_amp == 0] = 1e-10
    result[f"{prefix}_hht_amp_div"] = pd.Series(dominant_amp / total_amp, index=idx)

    inst_freq = np.diff(dominant_phase) / (2.0 * np.pi)
    inst_freq = np.concatenate([[np.nan], inst_freq])
    result[f"{prefix}_hht_inst_freq"] = pd.Series(inst_freq, index=idx)

    low_freq_start = max(n_imfs // 2, 1)
    energy_per_imf = np.array([np.sum(imf ** 2) for imf in imfs])
    total_energy = energy_per_imf.sum()
    low_freq_ratio = energy_per_imf[low_freq_start:].sum() / total_energy if total_energy > 0 else 0.5
    result[f"{prefix}_hht_energy_ratio"] = pd.Series(low_freq_ratio, index=idx)

    result[f"{prefix}_hht_phase_pos"] = pd.Series(np.sin(dominant_phase), index=idx)

    for i in range(min(4, n_imfs)):
        phase_i = phases[i]
        amp_i = amplitudes[i]
        result[f"{prefix}_hht_imf{i}_sin"] = pd.Series(np.sin(phase_i), index=idx)
        result[f"{prefix}_hht_imf{i}_cos"] = pd.Series(np.cos(phase_i), index=idx)
        result[f"{prefix}_hht_imf{i}_amp"] = pd.Series(amp_i, index=idx)
        result[f"{prefix}_hht_imf{i}_amp_ma5"] = pd.Series(amp_i, index=idx).rolling(5).mean()
        if i > 0:
            phase_diff = phases[0] - phase_i
            result[f"{prefix}_hht_phase_diff_0_{i}"] = pd.Series(np.sin(phase_diff), index=idx)

    phase_vel = np.concatenate([[np.nan], np.diff(dominant_phase)])
    phase_accel = np.concatenate([[np.nan], np.diff(phase_vel)])
    result[f"{prefix}_hht_phase_vel"] = pd.Series(phase_vel, index=idx)
    result[f"{prefix}_hht_phase_accel"] = pd.Series(phase_accel, index=idx)

    trend_mean = np.mean(np.abs(trend_imf))
    if trend_mean > 0:
        result[f"{prefix}_hht_trend_norm"] = pd.Series(trend_imf / trend_mean, index=idx)

    return result


def build_features(df):
    """Exact replica of the feature pipeline from train.py."""
    feat = {}
    instruments = list(INSTRUMENTS.keys())

    for inst in instruments:
        close_col = f"{inst}_close"
        high_col = f"{inst}_high"
        low_col = f"{inst}_low"
        volume_col = f"{inst}_volume"

        if close_col not in df.columns:
            continue

        close = df[close_col]
        ret_1d = close.pct_change(1)

        feat[f"{inst}_ret_1d"] = ret_1d
        feat[f"{inst}_ret_2d"] = close.pct_change(2)
        feat[f"{inst}_ret_3d"] = close.pct_change(3)
        feat[f"{inst}_ret_5d"] = close.pct_change(5)
        feat[f"{inst}_ret_10d"] = close.pct_change(10)
        feat[f"{inst}_ret_20d"] = close.pct_change(20)

        feat[f"{inst}_vol_5d"] = ret_1d.rolling(5).std()
        feat[f"{inst}_vol_10d"] = ret_1d.rolling(10).std()
        feat[f"{inst}_vol_20d"] = ret_1d.rolling(20).std()

        vol_20d = ret_1d.rolling(20).std()
        vol_60d_med = vol_20d.rolling(60).median()
        feat[f"{inst}_high_vol"] = (vol_20d > vol_60d_med).astype(float)

        ma5 = close.rolling(5).mean()
        ma10 = close.rolling(10).mean()
        ma20 = close.rolling(20).mean()
        ma50 = close.rolling(50).mean()
        feat[f"{inst}_ma5_20"] = ma5 / ma20
        feat[f"{inst}_ma10_50"] = ma10 / ma50
        feat[f"{inst}_above_ma20"] = (close > ma20).astype(float)
        feat[f"{inst}_above_ma50"] = (close > ma50).astype(float)

        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss_s = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss_s.replace(0, 1e-10)
        rsi = 100 - (100 / (1 + rs))
        feat[f"{inst}_rsi_14"] = rsi
        feat[f"{inst}_rsi_ob"] = (rsi > 70).astype(float)
        feat[f"{inst}_rsi_os"] = (rsi < 30).astype(float)

        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        macd_signal = macd_line.ewm(span=9, adjust=False).mean()
        feat[f"{inst}_macd_hist"] = macd_line - macd_signal
        feat[f"{inst}_macd_above"] = (macd_line > macd_signal).astype(float)

        bb_std = close.rolling(20).std()
        bb_upper = ma20 + 2 * bb_std
        bb_lower = ma20 - 2 * bb_std
        bb_range = (bb_upper - bb_lower).replace(0, 1e-10)
        feat[f"{inst}_bb_pctb"] = (close - bb_lower) / bb_range
        feat[f"{inst}_bb_width"] = (bb_upper - bb_lower) / ma20
        feat[f"{inst}_bb_above"] = (close > bb_upper).astype(float)
        feat[f"{inst}_bb_below"] = (close < bb_lower).astype(float)

        if high_col in df.columns and low_col in df.columns:
            high, low = df[high_col], df[low_col]
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
            if up.iloc[i] == up.iloc[i - 1]:
                streak.iloc[i] = streak.iloc[i - 1] + 1
            else:
                streak.iloc[i] = 1
        feat["nifty50_streak"] = streak.shift(1)
        ret_mean = nifty_ret.rolling(20).mean()
        ret_std = nifty_ret.rolling(20).std().replace(0, 1e-10)
        feat["nifty50_ret_zscore"] = (nifty_ret - ret_mean) / ret_std

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

    feat["dow_mon"] = pd.Series((df.index.dayofweek == 0).astype(float), index=df.index)
    feat["dow_tue"] = pd.Series((df.index.dayofweek == 1).astype(float), index=df.index)
    feat["dow_wed"] = pd.Series((df.index.dayofweek == 2).astype(float), index=df.index)
    feat["dow_thu"] = pd.Series((df.index.dayofweek == 3).astype(float), index=df.index)
    feat["dow_fri"] = pd.Series((df.index.dayofweek == 4).astype(float), index=df.index)
    feat["month_sin"] = pd.Series(np.sin(2 * np.pi * df.index.month / 12), index=df.index)
    feat["month_cos"] = pd.Series(np.cos(2 * np.pi * df.index.month / 12), index=df.index)

    hht_all = {}
    for inst in instruments:
        close_col = f"{inst}_close"
        if close_col not in df.columns:
            continue
        hht = _hht_features(df[close_col], inst)
        hht_all[inst] = hht
        for fname, fseries in hht.items():
            feat[fname] = fseries.reindex(df.index)

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
# Data download
# ---------------------------------------------------------------------------

def _download_ticker(ticker, start_str, end_str, max_retries=3):
    """Download a single ticker with retry logic for transient yfinance failures."""
    import time as _time
    for attempt in range(1, max_retries + 1):
        try:
            df = yf.download(ticker, start=start_str, end=end_str,
                             progress=False, auto_adjust=True)
            if df is not None and not df.empty:
                return df
        except Exception:
            pass
        if attempt < max_retries:
            _time.sleep(2 * attempt)
    return None


def download_recent_data(lookback_calendar_days=400):
    """Download recent OHLCV for all instruments and merge into a single DataFrame."""
    end = datetime.now()
    start = end - timedelta(days=lookback_calendar_days)
    start_str, end_str = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    frames = {}
    for name, ticker in INSTRUMENTS.items():
        df = _download_ticker(ticker, start_str, end_str)
        if df is None or df.empty:
            print(f"  WARNING: No data for {name} ({ticker}) after retries")
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_localize(None) if df.index.tz else df.index
        df.index.name = "date"

        rename_map = {col: f"{name}_{col.lower().replace(' ', '_')}" for col in df.columns}
        df = df.rename(columns=rename_map)
        frames[name] = df

    if "nifty50" not in frames:
        print("ERROR: Nifty 50 data is required but could not be downloaded.")
        sys.exit(1)

    if not frames:
        print("ERROR: Could not download any data.")
        sys.exit(1)

    merged = pd.concat(frames.values(), axis=1, join="inner")
    merged = merged.sort_index().ffill().dropna()
    return merged


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------

def load_model(model_path):
    checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
    input_dim = checkpoint["input_dim"]
    hidden_dim = checkpoint.get("hidden_dim", 128)
    num_layers = checkpoint.get("num_layers", 2)
    dropout = checkpoint.get("dropout", 0.3)
    lookback = checkpoint.get("lookback", 20)

    model = DirectionPredictor(input_dim, hidden_dim, num_layers, dropout)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    return model, checkpoint


def predict_next_day(model, checkpoint, merged_df):
    """
    Build features from merged data, normalize with saved stats,
    take the last `lookback` rows as input sequence, and predict.
    """
    lookback = checkpoint.get("lookback", 20)
    feature_mean = checkpoint["feature_mean"]
    feature_std = checkpoint["feature_std"]

    features_df = build_features(merged_df)

    if len(features_df) < lookback:
        print(f"ERROR: Need at least {lookback} feature rows, got {len(features_df)}")
        sys.exit(1)

    feat_np = features_df.values
    expected_cols = len(feature_mean)
    if feat_np.shape[1] != expected_cols:
        print(f"WARNING: Feature count mismatch — got {feat_np.shape[1]}, "
              f"model expects {expected_cols}.")
        print("  The model was trained with a specific feature set. Results may be unreliable.")
        if feat_np.shape[1] > expected_cols:
            feat_np = feat_np[:, :expected_cols]
        else:
            pad = np.zeros((feat_np.shape[0], expected_cols - feat_np.shape[1]))
            feat_np = np.hstack([feat_np, pad])

    feat_std_safe = feature_std.copy()
    feat_std_safe[feat_std_safe == 0] = 1.0
    feat_norm = (feat_np - feature_mean) / feat_std_safe

    seq = feat_norm[-lookback:]
    seq_tensor = torch.tensor(seq, dtype=torch.float32).unsqueeze(0)

    with torch.no_grad():
        prob = model(seq_tensor).item()

    prediction = "UP" if prob >= 0.5 else "DOWN"
    confidence = prob if prob >= 0.5 else 1.0 - prob

    last_date = features_df.index[-1]

    return {
        "prediction_for": "Next trading day",
        "based_on_data_through": str(last_date.date()),
        "direction": prediction,
        "probability_up": round(prob, 4),
        "confidence": round(confidence, 4),
        "nifty50_last_close": round(merged_df["nifty50_close"].iloc[-1], 2),
        "features_used": feat_np.shape[1],
        "lookback_days": lookback,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Nifty 50 next-day direction prediction (LSTM/NN)")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help="Path to saved model .pt file")
    parser.add_argument("--days", type=int, default=0,
                        help="Show last N days of Nifty 50 prices alongside prediction")
    args = parser.parse_args()

    if not os.path.exists(args.model):
        print(f"ERROR: Model file not found: {args.model}")
        sys.exit(1)

    print("=" * 60)
    print("  Nifty 50 Next-Day Direction Predictor (LSTM)")
    print("=" * 60)
    print()

    print(f"Model: {os.path.basename(args.model)}")
    model, checkpoint = load_model(args.model)
    print(f"  Accuracy (walk-forward): {checkpoint.get('accuracy', 'N/A'):.4f}")
    print(f"  Trained: {checkpoint.get('timestamp', 'N/A')}")
    print(f"  Features: {checkpoint['input_dim']}, Lookback: {checkpoint.get('lookback', 20)}d")
    print()

    print("Downloading latest market data...")
    merged = download_recent_data()
    print(f"  Data: {len(merged)} trading days, through {merged.index[-1].date()}")
    print(f"  Nifty 50 last close: {merged['nifty50_close'].iloc[-1]:,.2f}")
    print()

    if args.days > 0:
        recent = merged[["nifty50_close"]].tail(args.days).copy()
        recent["change"] = recent["nifty50_close"].pct_change() * 100
        recent["direction"] = recent["change"].apply(
            lambda x: "UP" if x > 0 else ("DOWN" if x < 0 else "FLAT"))
        print(f"Last {args.days} trading days:")
        print("-" * 45)
        for date, row in recent.iterrows():
            chg = f"{row['change']:+.2f}%" if not pd.isna(row["change"]) else "    —"
            print(f"  {date.date()}  {row['nifty50_close']:>10,.2f}  {chg:>8}  {row['direction']}")
        print()

    print("Running prediction...")
    result = predict_next_day(model, checkpoint, merged)
    print()

    print("=" * 60)
    print("  PREDICTION")
    print("=" * 60)
    arrow = "▲" if result["direction"] == "UP" else "▼"
    print(f"  {result['prediction_for']}: {arrow} {result['direction']}")
    print(f"  P(up) = {result['probability_up']:.2%}")
    print(f"  Confidence: {result['confidence']:.2%}")
    print(f"  Based on data through: {result['based_on_data_through']}")
    print(f"  Nifty 50 last close: {result['nifty50_last_close']:,.2f}")
    print(f"  Lookback: {result['lookback_days']}d")
    print("=" * 60)
    print()
    print("Disclaimer: This is a statistical model prediction, not financial advice.")


if __name__ == "__main__":
    main()
