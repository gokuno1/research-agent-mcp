#!/usr/bin/env python3
"""Saturday Runner — weekly orchestrator.

Run this every Saturday (or Sunday) to produce the upcoming week's
NIFTY 50 swing-trading portfolio per the evidence-based playbook in:

    docs/research-runs/2026-05-02-systematic-swing-trading-evidence-based-playbook.md

Usage:
    python run.py
    python run.py --capital 100000 --dry-run
    python run.py --config config.yaml --output-dir runs/
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import yaml

from lib import data as data_mod
from lib import playbook as pb
from lib import report as rpt


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    here = Path(__file__).parent.resolve()
    p.add_argument("--config", type=Path, default=here / "config.yaml")
    p.add_argument("--universe", type=Path, default=here / "universe.csv")
    p.add_argument("--fundamentals", type=Path, default=here / "fundamentals.json")
    p.add_argument("--earnings", type=Path, default=here / "earnings_recent.json")
    p.add_argument("--output-dir", type=Path, default=here / "runs")
    p.add_argument(
        "--capital",
        type=float,
        default=None,
        help="Override capital_inr from config (₹). Default reads config.yaml.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pipeline and print to console; do not write report files.",
    )
    return p.parse_args()


def load_config(path: Path) -> dict:
    with path.open() as f:
        return yaml.safe_load(f)


def main() -> int:
    args = parse_args()
    if not args.config.exists():
        print(f"Config not found: {args.config}", file=sys.stderr)
        return 2

    cfg = load_config(args.config)
    if args.capital is not None:
        cfg["capital"]["amount_inr"] = float(args.capital)
    capital = float(cfg["capital"]["amount_inr"])

    print(f"[1/5] Loading universe + fundamentals + earnings…")
    universe = data_mod.load_universe(args.universe)
    fundamentals = {
        k: v
        for k, v in data_mod.load_json(args.fundamentals).items()
        if not k.startswith("_")
    }
    earnings = data_mod.load_json(args.earnings)

    print(f"      Universe size: {len(universe)} stocks")
    print(f"      Fundamentals entries: {sum(1 for k in fundamentals if not k.startswith('_'))}")
    print(f"      Recent earnings entries: {len(earnings.get('announcements', []))}")

    print(f"[2/5] Fetching EOD data from yfinance…")
    days = int(cfg["data"]["yfinance_lookback_days"])
    tickers = [s.yf_ticker for s in universe]
    history = data_mod.fetch_history(tickers, days)
    nifty_daily, vix_daily = data_mod.fetch_index_and_vix(days)
    print(f"      Got history for {len(history)}/{len(tickers)} tickers")
    print(f"      NIFTY history: {len(nifty_daily)} days, VIX: {len(vix_daily)} days")

    print(f"[3/5] Step 1 — assessing market state…")
    market = pb.assess_market_state(nifty_daily, vix_daily, cfg)

    print(f"[4/5] Steps 2–4 — computing per-stock metrics…")
    eps_cvs = [
        fundamentals.get(s.symbol, {}).get("eps_cv_5y")
        for s in universe
        if fundamentals.get(s.symbol, {}).get("eps_cv_5y") is not None
    ]
    import numpy as _np  # local to keep the orchestrator small
    eps_cv_median = float(_np.median(eps_cvs)) if eps_cvs else None

    metrics: list[pb.StockMetrics] = []
    skipped_no_data = 0
    for s in universe:
        df = history.get(s.yf_ticker)
        m = pb.compute_metrics(s, df, fundamentals, earnings, eps_cv_median, cfg)
        if m is None:
            skipped_no_data += 1
            continue
        metrics.append(m)
    print(f"      Metrics computed for {len(metrics)}/{len(universe)} (skipped {skipped_no_data} for missing data)")

    print(f"[5/5] Steps 5–7 — ranking, sector cap, sizing, stops…")

    if not market.trend_on:
        print("      TREND-OFF: switching to defensive sub-mode (top-3 quality, 5% each).")
        # Pull a wider pool (top 8) so the selector has room after sector-cap and earnings-blackout skips.
        defensive_pool = sorted(
            [m for m in metrics if m.quality_score == 3],
            key=lambda x: -x.momentum_12_1,
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
            selected,
            market,
            {m.symbol: m.pead_note for m in selected if m.pead_note},
            earnings,
            capital,
            cfg_def,
        )
    else:
        ranked = pb.rank_candidates(metrics, cfg)
        selected = pb.select_with_sector_cap(ranked, cfg)
        positions, deployed = pb.build_positions(
            selected,
            market,
            {m.symbol: m.pead_note for m in selected if m.pead_note},
            earnings,
            capital,
            cfg,
        )

    if cfg["output"]["print_to_console"]:
        rpt.print_console(market, ranked, selected, positions, capital, deployed, cfg)

    if args.dry_run:
        print("Dry run; no files written.")
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    run_dir = args.output_dir / today
    run_dir.mkdir(exist_ok=True)

    md_path = run_dir / "portfolio.md"
    csv_path = run_dir / "gtt_orders.csv"

    rpt.write_markdown(md_path, market, ranked, selected, positions, capital, deployed, cfg)
    if cfg["output"]["generate_gtt_csv"] and positions:
        rpt.write_gtt_csv(csv_path, positions)

    print()
    print(f"Wrote: {md_path}")
    if positions and cfg["output"]["generate_gtt_csv"]:
        print(f"Wrote: {csv_path}")

    if cfg["output"]["email_enabled"]:
        sent = rpt.send_email(
            subject=f"Portfolio for week starting {today}",
            body=md_path.read_text(),
            attachments=[md_path] + ([csv_path] if csv_path.exists() else []),
            cfg=cfg,
        )
        print(f"Email sent: {sent}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
