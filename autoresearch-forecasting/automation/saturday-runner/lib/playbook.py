"""The 8 steps of the weekly playbook.

Each function maps explicitly to a section of:
    docs/research-runs/2026-05-02-systematic-swing-trading-evidence-based-playbook.md

Claim IDs (C1..C9) and Hypothesis IDs (H1..H5) are referenced inline.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd

from .data import Stock


# ============================================================
# Data structures
# ============================================================


@dataclass
class StockMetrics:
    symbol: str
    sector: str
    yf_ticker: str
    isin: str
    last_close: float
    momentum_12_1: float
    realised_vol_4w_annual: float
    atr_pct_14d: float
    quality_score: int
    quality_breakdown: dict
    pead_bonus: int
    pead_note: str
    earnings_within_3d: bool
    composite_rank: float = 0.0  # lower = better
    notes: list[str] = field(default_factory=list)


@dataclass
class Position:
    symbol: str
    sector: str
    isin: str
    last_close: float
    raw_weight_pct: float
    capped_weight_pct: float
    shares: int
    notional_inr: float
    realised_weight_pct: float
    weight_drift_pct: float
    hard_stop_price: float
    vol_stop_price: float
    final_stop_price: float
    risk_inr: float
    risk_pct_capital: float
    target_exit_date: str
    pead_overlay: bool
    earnings_blackout: bool
    notes: list[str] = field(default_factory=list)


@dataclass
class MarketState:
    nifty_close: float
    nifty_40w_sma: float
    trend_on: bool
    india_vix: float
    vol_scaling_factor: float
    target_portfolio_vol_pct: float
    notes: list[str] = field(default_factory=list)


# ============================================================
# Step 1 — Market state filter (claim C2 + C9)
# ============================================================


def assess_market_state(
    nifty_daily: pd.DataFrame, vix_daily: pd.DataFrame, cfg: dict
) -> MarketState:
    """Cooper-Gutierrez-Hameed (2004): momentum returns are conditional
    on prior market state. Faber & Richardson (2017): trend filter using
    the long-horizon SMA materially reduces drawdowns.
    """
    weeks_sma = int(cfg["market_filter"]["weeks_sma"])
    trading_days_in_window = weeks_sma * 5

    if len(nifty_daily) < trading_days_in_window + 5:
        raise RuntimeError(
            f"Need ≥{trading_days_in_window + 5} days of NIFTY history; got {len(nifty_daily)}"
        )

    closes = nifty_daily["Close"]
    sma = closes.rolling(window=trading_days_in_window).mean().iloc[-1]
    last_close = closes.iloc[-1]
    trend_on = last_close > sma

    last_vix = float(vix_daily["Close"].dropna().iloc[-1])
    base_target = float(cfg["portfolio"]["target_portfolio_vol_pct"])
    extreme = float(cfg["market_filter"]["vix_extreme_threshold"])
    high = float(cfg["market_filter"]["vix_high_threshold"])

    if last_vix > extreme:
        scaling = 0.25
    elif last_vix > high:
        scaling = 0.5
    else:
        scaling = 1.0

    notes = []
    if not trend_on:
        notes.append(
            "TREND-OFF: NIFTY < 40-WMA. Per playbook §8.3 Step 1, hold cash + "
            "quality-only single-leg portfolio (top 3 by quality, 5% each, no "
            "momentum overlay). Do NOT go to zero, do NOT be at full risk."
        )
    if last_vix > high:
        notes.append(
            f"India VIX {last_vix:.1f} > {high:.0f} → portfolio target vol scaled by {scaling}× "
            f"({base_target * scaling:.1f}% effective)."
        )

    return MarketState(
        nifty_close=float(last_close),
        nifty_40w_sma=float(sma),
        trend_on=bool(trend_on),
        india_vix=last_vix,
        vol_scaling_factor=scaling,
        target_portfolio_vol_pct=base_target * scaling,
        notes=notes,
    )


# ============================================================
# Step 2 — Quality screen (claim C4)
# ============================================================


def quality_score_for(
    symbol: str, fundamentals: dict, eps_cv_median: float | None, cfg: dict
) -> tuple[int, dict]:
    """Asness-Frazzini-Pedersen (2018) "Quality Minus Junk":
    high profitability + low leverage + stable earnings → durable premium.
    Score: 0–3. Pass = score >= cfg.quality.required_score (default 2).
    Banks/NBFCs/Insurance use Tier-1 capital instead of NetDebt/EBITDA.
    """
    f = fundamentals.get(symbol, {})
    breakdown = {}

    roe = f.get("roe_ttm_pct")
    breakdown["roe_pct"] = roe
    breakdown["roe_pass"] = roe is not None and roe >= cfg["quality"]["min_roe_pct"]

    nde = f.get("net_debt_ebitda")
    tier1 = f.get("tier1_capital_pct")
    if nde is not None:
        breakdown["leverage_metric"] = f"NetDebt/EBITDA={nde:.2f}"
        breakdown["leverage_pass"] = nde <= cfg["quality"]["max_net_debt_to_ebitda"]
    elif tier1 is not None:
        breakdown["leverage_metric"] = f"Tier1={tier1:.1f}%"
        breakdown["leverage_pass"] = tier1 >= 12.0
    else:
        breakdown["leverage_metric"] = "missing"
        breakdown["leverage_pass"] = False

    eps_cv = f.get("eps_cv_5y")
    if eps_cv is not None and eps_cv_median is not None:
        breakdown["eps_cv"] = eps_cv
        breakdown["eps_cv_median"] = eps_cv_median
        breakdown["eps_cv_pass"] = eps_cv < eps_cv_median
    else:
        breakdown["eps_cv"] = eps_cv
        breakdown["eps_cv_pass"] = False

    score = (
        int(bool(breakdown["roe_pass"]))
        + int(bool(breakdown["leverage_pass"]))
        + int(bool(breakdown["eps_cv_pass"]))
    )
    return score, breakdown


def apply_quality_screen(
    symbols: list[str], fundamentals: dict, cfg: dict
) -> tuple[list[str], dict[str, tuple[int, dict]]]:
    """Returns (passing_symbols, full_score_dict)."""
    eps_cvs = [
        fundamentals.get(s, {}).get("eps_cv_5y")
        for s in symbols
        if fundamentals.get(s, {}).get("eps_cv_5y") is not None
    ]
    eps_cv_median = float(np.median(eps_cvs)) if eps_cvs else None

    scores: dict[str, tuple[int, dict]] = {}
    passing: list[str] = []
    threshold = int(cfg["quality"]["required_score"])
    for s in symbols:
        score, breakdown = quality_score_for(s, fundamentals, eps_cv_median, cfg)
        scores[s] = (score, breakdown)
        if score >= threshold:
            passing.append(s)
    return passing, scores


# ============================================================
# Step 3 — Momentum (claim C1)
# ============================================================


def compute_momentum_12_1(daily_close: pd.Series, cfg: dict) -> float | None:
    """12-1 momentum: total return from t−12m to t−1m.
    Skip the most recent month because of well-documented short-term reversal.
    Returns None if insufficient data.
    """
    lookback = int(cfg["momentum"]["lookback_months"])
    skip = int(cfg["momentum"]["skip_months"])

    days_lookback = lookback * 21
    days_skip = skip * 21

    if len(daily_close) < days_lookback + 5:
        return None

    end_idx = len(daily_close) - days_skip
    start_idx = end_idx - (lookback - skip) * 21
    if start_idx < 0:
        return None

    p_start = float(daily_close.iloc[start_idx])
    p_end = float(daily_close.iloc[end_idx - 1])
    if p_start <= 0:
        return None
    return (p_end / p_start) - 1.0


def compute_realised_vol_annual(daily_close: pd.Series, weeks: int) -> float | None:
    """Annualised realised volatility from weekly returns."""
    if len(daily_close) < weeks * 5 + 5:
        return None
    weekly = daily_close.resample("W-FRI").last().tail(weeks + 1)
    if len(weekly) < weeks + 1:
        return None
    weekly_returns = weekly.pct_change().dropna()
    if len(weekly_returns) < weeks:
        return None
    return float(weekly_returns.std() * math.sqrt(52))


def compute_atr_pct(daily: pd.DataFrame, window: int) -> float | None:
    """Average True Range as a % of last close."""
    if len(daily) < window + 1:
        return None
    high = daily["High"]
    low = daily["Low"]
    close = daily["Close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [(high - low).abs(), (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    atr = tr.rolling(window=window).mean().iloc[-1]
    last_close = float(close.iloc[-1])
    if last_close <= 0 or pd.isna(atr):
        return None
    return float(atr) / last_close * 100.0


# ============================================================
# Step 4 — PEAD overlay (claim C3)
# ============================================================


def pead_bonus_for(symbol: str, earnings_data: dict, cfg: dict) -> tuple[int, str]:
    """Bernard-Thomas (1989); DellaVigna-Pollet (2009) Friday effect;
    Hirshleifer-Lim-Teoh (2009) distraction effect.
    Returns (priority bonus, human-readable note).
    """
    threshold = float(cfg["pead"]["surprise_threshold_sigma"])
    fri_bonus = int(cfg["pead"]["friday_bonus"])
    dist_bonus = int(cfg["pead"]["high_distraction_bonus"])

    for ann in earnings_data.get("announcements", []):
        if ann["symbol"] == symbol:
            sigma = float(ann.get("surprise_sigma", 0.0))
            if sigma > threshold:
                bonus = 1
                notes = [f"PEAD +1σ surprise (σ={sigma:+.1f})"]
                if ann.get("day_of_week", "").lower() == "friday":
                    bonus += fri_bonus
                    notes.append(f"Friday +{fri_bonus} (DellaVigna-Pollet)")
                if int(ann.get("same_day_count", 0)) > 10:
                    bonus += dist_bonus
                    notes.append(f"distraction-day +{dist_bonus} (Hirshleifer-Lim-Teoh)")
                return bonus, "; ".join(notes)
            elif sigma < -threshold:
                return -1, f"PEAD -1σ negative surprise (σ={sigma:+.1f}); avoid"
    return 0, ""


def is_earnings_within_3d(symbol: str, earnings_data: dict) -> bool:
    """Earnings-event rule (§8.3 step 7): if a held name has earnings in
    the next 3 trading days, halve or exit. Prevents entry in the first place.
    """
    for nxt in earnings_data.get("next_earnings_within_3d", []):
        if nxt["symbol"] == symbol:
            return True
    return False


# ============================================================
# Steps 5+6 — Sector cap + vol-targeted sizing (claim C5)
# ============================================================


def select_with_sector_cap(
    ranked_metrics: list[StockMetrics], cfg: dict
) -> list[StockMetrics]:
    """Walk down the ranked list, include only if sector hasn't hit cap."""
    target_n = int(cfg["portfolio"]["target_positions"])
    max_n = int(cfg["portfolio"]["max_positions"])
    max_per_sector = int(cfg["portfolio"]["max_per_sector"])

    sector_count: dict[str, int] = {}
    selected: list[StockMetrics] = []
    for m in ranked_metrics:
        if len(selected) >= max_n:
            break
        if m.earnings_within_3d:
            m.notes.append("Skipped (earnings within 3 trading days)")
            continue
        if sector_count.get(m.sector, 0) >= max_per_sector:
            m.notes.append(f"Skipped (sector cap reached: {m.sector})")
            continue
        selected.append(m)
        sector_count[m.sector] = sector_count.get(m.sector, 0) + 1
        if len(selected) >= target_n and len(selected) >= 5:
            # Allow up to max_n, but bias toward target_n
            pass
    return selected[:max_n]


def size_position(
    metric: StockMetrics, n_positions: int, target_portfolio_vol_pct: float, cfg: dict
) -> tuple[float, float]:
    """Moreira-Muir (2017) volatility targeting:
        w_i = (target_portfolio_vol / σ_i) × (1 / N)
    Return (raw_weight_pct, capped_weight_pct).
    """
    sigma_i_pct = metric.realised_vol_4w_annual * 100.0
    if sigma_i_pct <= 0:
        sigma_i_pct = 25.0  # fallback for missing data
    raw = (target_portfolio_vol_pct / sigma_i_pct) * (1.0 / n_positions) * 100.0
    capped = max(
        cfg["portfolio"]["min_position_pct"],
        min(raw, cfg["portfolio"]["max_position_pct"]),
    )
    return raw, capped


def build_positions(
    selected: list[StockMetrics],
    market: MarketState,
    pead_overlays: dict[str, str],
    earnings_data: dict,
    capital_inr: float,
    cfg: dict,
) -> tuple[list[Position], float]:
    """Build the final position list with shares, stops, weights, etc.
    Returns (positions, deployed_inr).
    """
    if not selected:
        return [], 0.0

    n = len(selected)
    target_vol = market.target_portfolio_vol_pct

    deployed = 0.0
    positions: list[Position] = []

    cash_floor = float(cfg["portfolio"]["cash_buffer_pct_floor"]) / 100.0 * capital_inr
    deployable_cap = capital_inr - cash_floor

    raw_weights = []
    capped_weights = []
    for m in selected:
        raw, capped = size_position(m, n, target_vol, cfg)
        raw_weights.append(raw)
        capped_weights.append(capped)

    total_capped = sum(capped_weights)
    max_total_pct = (deployable_cap / capital_inr) * 100.0
    if total_capped > max_total_pct:
        scale = max_total_pct / total_capped
        capped_weights = [w * scale for w in capped_weights]

    for m, raw_w, w in zip(selected, raw_weights, capped_weights):
        target_notional = capital_inr * (w / 100.0)
        shares = int(target_notional // m.last_close)
        if shares < 1:
            m.notes.append(
                f"Cannot afford 1 share at ₹{m.last_close:,.0f} within {w:.1f}% cap; skipped."
            )
            continue
        notional = shares * m.last_close
        realised_w = notional / capital_inr * 100.0
        drift = realised_w - w

        hard_stop_pct = float(cfg["risk"]["hard_stop_pct"])
        atr_mul = float(cfg["risk"]["atr_stop_multiplier"])
        hard_stop_distance_pct = hard_stop_pct
        atr_pct = m.atr_pct_14d if m.atr_pct_14d else hard_stop_pct
        vol_stop_distance_pct = min(hard_stop_pct, atr_mul * atr_pct)

        hard_stop_price = m.last_close * (1.0 - hard_stop_distance_pct / 100.0)
        vol_stop_price = m.last_close * (1.0 - vol_stop_distance_pct / 100.0)
        final_stop_price = max(hard_stop_price, vol_stop_price)

        risk_inr = (m.last_close - final_stop_price) * shares
        risk_pct = risk_inr / capital_inr * 100.0

        time_stop_weeks = int(cfg["risk"]["time_stop_weeks"])
        target_exit = (datetime.now() + timedelta(weeks=time_stop_weeks)).strftime("%Y-%m-%d")

        notes = list(m.notes)
        pead_note = pead_overlays.get(m.symbol, "")
        if pead_note:
            notes.append(pead_note)
        if abs(drift) > 1.5:
            notes.append(f"Share-rounding drift {drift:+.1f} pct points (small capital)")

        positions.append(
            Position(
                symbol=m.symbol,
                sector=m.sector,
                isin=m.isin,
                last_close=m.last_close,
                raw_weight_pct=raw_w,
                capped_weight_pct=w,
                shares=shares,
                notional_inr=notional,
                realised_weight_pct=realised_w,
                weight_drift_pct=drift,
                hard_stop_price=hard_stop_price,
                vol_stop_price=vol_stop_price,
                final_stop_price=final_stop_price,
                risk_inr=risk_inr,
                risk_pct_capital=risk_pct,
                target_exit_date=target_exit,
                pead_overlay=bool(pead_note and not pead_note.startswith("PEAD -")),
                earnings_blackout=False,
                notes=notes,
            )
        )
        deployed += notional

    return positions, deployed


# ============================================================
# Pipeline glue
# ============================================================


def compute_metrics(
    stock: Stock,
    daily: pd.DataFrame,
    fundamentals: dict,
    earnings_data: dict,
    eps_cv_median: float | None,
    cfg: dict,
) -> StockMetrics | None:
    if daily is None or daily.empty or "Close" not in daily.columns:
        return None
    last_close = float(daily["Close"].iloc[-1])
    mom = compute_momentum_12_1(daily["Close"], cfg)
    vol = compute_realised_vol_annual(
        daily["Close"], int(cfg["data"]["vol_window_weeks"])
    )
    atr = compute_atr_pct(daily, int(cfg["data"]["atr_window_days"]))
    if mom is None or vol is None:
        return None
    q_score, q_breakdown = quality_score_for(
        stock.symbol, fundamentals, eps_cv_median, cfg
    )
    pead_b, pead_note = pead_bonus_for(stock.symbol, earnings_data, cfg)
    earn_3d = is_earnings_within_3d(stock.symbol, earnings_data)
    return StockMetrics(
        symbol=stock.symbol,
        sector=stock.sector,
        yf_ticker=stock.yf_ticker,
        isin=stock.isin,
        last_close=last_close,
        momentum_12_1=mom,
        realised_vol_4w_annual=vol,
        atr_pct_14d=atr if atr is not None else 0.0,
        quality_score=q_score,
        quality_breakdown=q_breakdown,
        pead_bonus=pead_b,
        pead_note=pead_note,
        earnings_within_3d=earn_3d,
    )


def rank_candidates(metrics: list[StockMetrics], cfg: dict) -> list[StockMetrics]:
    """Rank by 12-1 momentum (descending) within quality-passing names,
    then apply PEAD bonus as a rank-shift (each +1 bonus moves a name up by 1 slot).
    """
    threshold = int(cfg["quality"]["required_score"])
    qualified = [m for m in metrics if m.quality_score >= threshold]
    qualified.sort(key=lambda x: x.momentum_12_1, reverse=True)
    for i, m in enumerate(qualified):
        m.composite_rank = float(i) - float(m.pead_bonus)
    qualified.sort(key=lambda x: x.composite_rank)
    top_n = int(cfg["momentum"]["top_n_after_quality"])
    return qualified[:top_n]
