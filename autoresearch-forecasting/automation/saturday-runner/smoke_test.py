#!/usr/bin/env python3
"""Offline smoke test for the Saturday Runner pipeline.

Generates synthetic OHLC data for a subset of the universe, runs the full
8-step playbook, and asserts the outputs are well-formed. No network needed.

Run:
    python smoke_test.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(HERE))

from lib import data as data_mod
from lib import playbook as pb
from lib import report as rpt


def synth_ohlc(start_price: float, days: int, drift_annual: float, vol_annual: float, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    daily_drift = drift_annual / 252.0
    daily_vol = vol_annual / np.sqrt(252.0)
    rets = rng.normal(daily_drift, daily_vol, size=days)
    close = start_price * np.exp(np.cumsum(rets))
    intraday_range = np.abs(rng.normal(0, daily_vol, size=days)) * close * 0.5
    high = close + intraday_range
    low = close - intraday_range
    open_ = np.concatenate([[start_price], close[:-1]])
    volume = rng.integers(100_000, 1_000_000, size=days)
    end_date = datetime.now().date()
    dates = pd.bdate_range(end=end_date, periods=days)
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=dates,
    )


def make_synthetic_universe(universe, days: int, rng):
    history: dict[str, pd.DataFrame] = {}
    for i, s in enumerate(universe):
        drift = float(rng.uniform(-0.05, 0.55))
        vol = float(rng.uniform(0.18, 0.45))
        start_price = float(rng.uniform(80, 1200))
        history[s.yf_ticker] = synth_ohlc(start_price, days, drift, vol, seed=1000 + i)
    return history


def run_branch(label: str, nifty_drift: float, cfg, universe, fundamentals, earnings, days, rng_seed: int):
    print()
    print("#" * 78)
    print(f"#  SMOKE BRANCH: {label}")
    print("#" * 78)
    rng = np.random.default_rng(rng_seed)
    history = make_synthetic_universe(universe, days, rng)
    nifty_daily = synth_ohlc(22000, days, nifty_drift, 0.16, seed=99)
    vix = synth_ohlc(14, days, 0.0, 0.20, seed=200)["Close"].clip(8, 35)
    vix_daily = pd.DataFrame(
        {"Open": vix, "High": vix * 1.05, "Low": vix * 0.95, "Close": vix, "Volume": 0.0},
        index=vix.index,
    )

    market = pb.assess_market_state(nifty_daily, vix_daily, cfg)
    print(f"[smoke] market.trend_on={market.trend_on}, vix={market.india_vix:.2f}, vol_scale={market.vol_scaling_factor}")

    eps_cvs = [
        fundamentals.get(s.symbol, {}).get("eps_cv_5y")
        for s in universe
        if fundamentals.get(s.symbol, {}).get("eps_cv_5y") is not None
    ]
    eps_cv_median = float(np.median(eps_cvs)) if eps_cvs else None

    metrics = []
    for s in universe:
        m = pb.compute_metrics(s, history.get(s.yf_ticker), fundamentals, earnings, eps_cv_median, cfg)
        if m is not None:
            metrics.append(m)

    capital = float(cfg["capital"]["amount_inr"])
    if market.trend_on:
        ranked = pb.rank_candidates(metrics, cfg)
        selected = pb.select_with_sector_cap(ranked, cfg)
        positions, deployed = pb.build_positions(
            selected, market,
            {m.symbol: m.pead_note for m in selected if m.pead_note},
            earnings, capital, cfg,
        )
    else:
        defensive_pool = sorted(
            [m for m in metrics if m.quality_score == 3], key=lambda x: -x.momentum_12_1
        )[:8]
        if len(defensive_pool) < 3:
            extra = sorted(
                [m for m in metrics if m.quality_score == 2 and m not in defensive_pool],
                key=lambda x: -x.momentum_12_1,
            )[: 8 - len(defensive_pool)]
            defensive_pool = defensive_pool + extra
        ranked = defensive_pool
        cfg_def = dict(cfg)
        cfg_def["portfolio"] = dict(cfg["portfolio"])
        cfg_def["portfolio"]["target_positions"] = 3
        cfg_def["portfolio"]["max_positions"] = 3
        cfg_def["portfolio"]["max_position_pct"] = 5.0
        cfg_def["portfolio"]["min_position_pct"] = 5.0
        selected = pb.select_with_sector_cap(ranked, cfg_def)
        positions, deployed = pb.build_positions(
            selected, market, {}, earnings, capital, cfg_def
        )

    rpt.print_console(market, ranked, selected, positions, capital, deployed, cfg)

    out = HERE / "runs" / f"_smoke_{label.lower().replace(' ', '_').replace('-', '_')}"
    out.mkdir(parents=True, exist_ok=True)
    rpt.write_markdown(out / "portfolio.md", market, ranked, selected, positions, capital, deployed, cfg)
    if positions:
        rpt.write_gtt_csv(out / "gtt_orders.csv", positions)

    if positions:
        for p in positions:
            assert p.shares >= 1
            assert p.final_stop_price < p.last_close
            assert p.risk_inr <= capital * 0.012 + 1
        from collections import Counter
        for sec, cnt in Counter(p.sector for p in positions).items():
            assert cnt <= cfg["portfolio"]["max_per_sector"], f"sector {sec} cap breach"
        assert deployed <= capital * (1.0 - cfg["portfolio"]["cash_buffer_pct_floor"] / 100.0) + 1
    return market, ranked, selected, positions, deployed


def main() -> int:
    cfg = yaml.safe_load((HERE / "config.yaml").open())
    universe = data_mod.load_universe(HERE / "universe.csv")
    fundamentals = {
        k: v
        for k, v in data_mod.load_json(HERE / "fundamentals.json").items()
        if not k.startswith("_")
    }
    earnings = data_mod.load_json(HERE / "earnings_recent.json")
    days = int(cfg["data"]["yfinance_lookback_days"])

    m_off, _, _, p_off, _ = run_branch("TREND-OFF", nifty_drift=-0.10, cfg=cfg,
                                        universe=universe, fundamentals=fundamentals,
                                        earnings=earnings, days=days, rng_seed=42)
    assert not m_off.trend_on, "TREND-OFF branch did not trigger"

    m_on, _, _, p_on, dep_on = run_branch("TREND-ON", nifty_drift=0.55, cfg=cfg,
                                            universe=universe, fundamentals=fundamentals,
                                            earnings=earnings, days=days, rng_seed=99)
    assert m_on.trend_on, "TREND-ON branch did not trigger"
    assert len(p_on) >= 3, f"TREND-ON expected >=3 positions, got {len(p_on)}"

    print()
    print("[smoke] Both branches passed. Outputs in runs/_smoke_trend_on/ and runs/_smoke_trend_off/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
