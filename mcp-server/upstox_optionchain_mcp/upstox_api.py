"""HTTP client for Upstox v2 option chain."""

from __future__ import annotations

import os
from typing import Any
import json

import httpx

DEFAULT_BASE = "https://api.upstox.com/v2"
DEFAULT_INSTRUMENT_KEY = "NSE_INDEX|Nifty 50"

with open("/Users/aniketbi/Desktop/Aniket/project_files_backups/autoresearch-forecasting/.cursor/mcp.json") as f:
    data = json.load(f)

server = "upstox-optionchain"

def get_token() -> str:
    token = (
        data.get("mcpServers", {})
        .get(server, {})
        .get("env", {})
        .get("UPSTOX_ACCESS_TOKEN")
    ).strip()
    if not token:
        raise RuntimeError(
            "UPSTOX_ACCESS_TOKEN is not set. Add it to your MCP server env in Cursor settings (mcp.json)."
        )
    return token


def get_instrument_key() -> str:
    return (
        data.get("mcpServers", {})
        .get(server, {})
        .get("env", {})
        .get("UPSTOX_INSTRUMENT_KEY")
    ).strip() or DEFAULT_INSTRUMENT_KEY


def get_base_url() -> str:
    return (
        data.get("mcpServers", {})
        .get(server, {})
        .get("env", {})
        .get("UPSTOX_API_BASE")
    ).strip() or DEFAULT_BASE


def _headers() -> dict[str, str]:
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_token()}",
    }


def _get(path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
    url = f"{get_base_url()}{path}"
    with httpx.Client(timeout=60.0) as client:
        r = client.get(url, headers=_headers(), params=params)
        r.raise_for_status()
        return r.json()


def fetch_option_chain(expiry_date: str, instrument_key: str | None = None) -> dict[str, Any]:
    key = instrument_key or get_instrument_key()
    return _get("/option/chain", {"instrument_key": key, "expiry_date": expiry_date})


def fetch_full_market_quote(symbols: list[str]) -> dict[str, Any]:
    """GET /market-quote/quotes -- full quote with L2 depth, OHLC, volume, ATP, OI."""
    return _get("/market-quote/quotes", {"symbol": ",".join(symbols)})


def fetch_intraday_candles(instrument_key: str, interval: str = "1minute") -> dict[str, Any]:
    """GET /historical-candle/intraday/{key}/{interval} -- today's OHLCV candles."""
    encoded = instrument_key.replace("|", "%7C")
    return _get(f"/historical-candle/intraday/{encoded}/{interval}")


def fetch_historical_candles(
    instrument_key: str,
    interval: str,
    to_date: str,
    from_date: str | None = None,
) -> dict[str, Any]:
    """GET /historical-candle/{key}/{interval}/{to}/{from} -- historical OHLCV."""
    encoded = instrument_key.replace("|", "%7C")
    path = f"/historical-candle/{encoded}/{interval}/{to_date}"
    if from_date:
        path += f"/{from_date}"
    return _get(path)


def fetch_ohlc_quotes(symbols: list[str], interval: str = "1d") -> dict[str, Any]:
    """GET /market-quote/ohlc -- OHLC + LTP for up to 1000 instruments."""
    return _get("/market-quote/ohlc", {"symbol": ",".join(symbols), "interval": interval})


def fetch_ltp_quotes(symbols: list[str]) -> dict[str, Any]:
    """GET /market-quote/ltp -- LTP for up to 1000 instruments."""
    return _get("/market-quote/ltp", {"symbol": ",".join(symbols)})
