"""Data fetching layer.

Default source: yfinance (free, NSE EOD via the `.NS` suffix).
Optional: replace `fetch_history()` with an Upstox SDK call for live use.
Caching: in-memory only; the script is one-shot per weekend run.
"""

from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
import yfinance as yf


@dataclass(frozen=True)
class Stock:
    symbol: str
    sector: str
    yf_ticker: str
    isin: str


def load_universe(csv_path: Path) -> list[Stock]:
    out: list[Stock] = []
    with csv_path.open() as f:
        for row in csv.DictReader(f):
            out.append(
                Stock(
                    symbol=row["symbol"].strip(),
                    sector=row["sector"].strip(),
                    yf_ticker=row["yf_ticker"].strip(),
                    isin=row.get("isin", "").strip(),
                )
            )
    return out


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def fetch_history(
    tickers: Iterable[str],
    days: int,
    *,
    retries: int = 2,
    sleep_between_retries: float = 2.0,
) -> dict[str, pd.DataFrame]:
    """Download daily OHLCV for each ticker. Returns dict[ticker -> dataframe]."""
    tickers = list(tickers)
    out: dict[str, pd.DataFrame] = {}
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        try:
            data = yf.download(
                tickers=tickers,
                period=f"{days}d",
                interval="1d",
                group_by="ticker",
                auto_adjust=True,
                threads=True,
                progress=False,
            )
            if isinstance(data.columns, pd.MultiIndex):
                for t in tickers:
                    if t in data.columns.get_level_values(0):
                        df = data[t].dropna(how="all").copy()
                        if not df.empty:
                            out[t] = df
            else:
                if not data.empty:
                    out[tickers[0]] = data.dropna(how="all").copy()
            return out
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(sleep_between_retries)
    raise RuntimeError(f"yfinance download failed after {retries + 1} attempts: {last_err}")


def fetch_index_and_vix(days: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """NIFTY 50 spot and INDIA VIX history."""
    raw = yf.download(
        tickers=["^NSEI", "^INDIAVIX"],
        period=f"{days}d",
        interval="1d",
        group_by="ticker",
        auto_adjust=True,
        threads=True,
        progress=False,
    )
    nifty = raw["^NSEI"].dropna(how="all").copy()
    vix = raw["^INDIAVIX"].dropna(how="all").copy()
    return nifty, vix
