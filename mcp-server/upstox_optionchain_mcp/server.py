"""
Stdio MCP server: Upstox option chain + 7-layer microstructure analysis.

Configure in Cursor via MCP settings: set env UPSTOX_ACCESS_TOKEN (and optionally
UPSTOX_INSTRUMENT_KEY, UPSTOX_API_BASE, UPSTOX_INDEX_LABEL).
"""

from __future__ import annotations

import json
import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from upstox_optionchain_mcp.chain_parse import normalize_row, parse_chain_json, spot_from_chain
from upstox_optionchain_mcp.cross_market import compute_cross_market
from upstox_optionchain_mcp.date_utils import get_expiry_string_like_java
from upstox_optionchain_mcp.feature_pipeline import compute_features_json_string
from upstox_optionchain_mcp.liquidity import compute_liquidity
from upstox_optionchain_mcp.microstructure_scan import run_scan
from upstox_optionchain_mcp.order_book import compute_order_book_structure
from upstox_optionchain_mcp.order_flow import compute_order_flow
from upstox_optionchain_mcp.pcr_maxpain import compute_pcr_maxpain
from upstox_optionchain_mcp.session_regime import compute_session_regime
from upstox_optionchain_mcp.signal_prompt import build_trade_signal_prompt
from upstox_optionchain_mcp.upstox_api import (
    fetch_full_market_quote,
    fetch_historical_candles,
    fetch_intraday_candles,
    fetch_ltp_quotes,
    fetch_ohlc_quotes,
    fetch_option_chain,
)
from upstox_optionchain_mcp.vwap_profile import compute_vwap_profile

mcp = FastMCP("upstox-optionchain")


def _index_label() -> str:
    return os.environ.get("UPSTOX_INDEX_LABEL", "Nifty 50").strip() or "Nifty 50"


@mcp.tool()
def get_option_chain(expiry_date: str | None = None) -> str:
    """
    Fetch a fresh put/call option chain from Upstox (GET /v2/option/chain).
    Uses Bearer token from env UPSTOX_ACCESS_TOKEN. If expiry_date is empty, uses the same
    next-weekday rule as Java DateUtils.getThursdayDateStringFormat() (Tuesday-based).
    Underlying instrument_key defaults to NSE_INDEX|Nifty 50 (override with UPSTOX_INSTRUMENT_KEY).
    Returns the full JSON response as a string (status + data).
    """
    exp = (expiry_date or "").strip() or get_expiry_string_like_java()
    payload = fetch_option_chain(exp)
    return json.dumps(payload, indent=2, default=str)


@mcp.tool()
def compute_features(option_chain_json: str) -> str:
    """
    Run the 15 Tier-1 microstructure signals (Java OptionChainRuleEngine port) on option-chain JSON.
    Pass the string returned by get_option_chain (full API response) or a JSON array of strike rows.
    Returns a JSON string: spot, strikes list, ATM hint, tier1_signals[], and raw legacy engine output.
    """
    return compute_features_json_string(option_chain_json)


@mcp.tool()
def generate_trade_signal(features_json: str, index_label: str | None = None, expiry: str | None = None) -> str:
    """
    Build the analyst prompt for the Cursor agent: paste Tier-1 features and output ONLY the trade JSON schema.
    features_json: output of compute_features. Optional index_label and expiry override display strings.
    The model in chat should answer with the JSON object (this tool does not call an LLM).
    """
    label = (index_label or "").strip() or _index_label()
    exp = (expiry or "").strip()
    if not exp:
        try:
            bundle = json.loads(features_json)
            exp = str(bundle.get("expiry") or get_expiry_string_like_java())
        except json.JSONDecodeError:
            exp = get_expiry_string_like_java()
    return build_trade_signal_prompt(label, exp, features_json)


@mcp.tool()
def place_order_sample(
    instrument_token: str,
    quantity: int,
    transaction_type: str = "BUY",
    order_type: str = "MARKET",
    product: str = "I",
) -> str:
    """
    STUB for future Upstox order placement (POST /v2/order/place). Not implemented.
    Returns a JSON description of the intended request shape. Do not use for live trading yet.
    """
    stub: dict[str, Any] = {
        "status": "not_implemented",
        "message": "Order placement will call Upstox v2 place-order API when implemented.",
        "planned_request": {
            "instrument_token": instrument_token,
            "quantity": quantity,
            "transaction_type": transaction_type,
            "order_type": order_type,
            "product": product,
            "validity": "DAY",
        },
        "defaults_note": "instrument_token is NSE_FO|... from option chain call_options.instrument_key or put_options.instrument_key",
    }
    return json.dumps(stub, indent=2)


# ---------------------------------------------------------------------------
# API tools
# ---------------------------------------------------------------------------


@mcp.tool()
def get_full_market_quote(symbols: str) -> str:
    """
    Fetch full market quotes with L2 depth (5-level bid/ask), OHLC, LTP, volume,
    average price (ATP), OI, and circuit limits.
    symbols: comma-separated instrument keys, e.g. "NSE_EQ|INE848E01016,NSE_FO|..."
    Returns full JSON response (up to 500 instruments).
    """
    sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
    payload = fetch_full_market_quote(sym_list)
    return json.dumps(payload, indent=2, default=str)


@mcp.tool()
def get_intraday_candles(instrument_key: str, interval: str = "1minute") -> str:
    """
    Fetch intraday OHLCV candles for the current trading session.
    instrument_key: e.g. "NSE_EQ|INE848E01016"
    interval: "1minute" or "30minute"
    Returns candle array [[timestamp, O, H, L, C, volume, OI], ...].
    """
    payload = fetch_intraday_candles(instrument_key, interval)
    return json.dumps(payload, indent=2, default=str)


@mcp.tool()
def get_historical_candles(
    instrument_key: str,
    interval: str,
    to_date: str,
    from_date: str | None = None,
) -> str:
    """
    Fetch historical OHLCV candles.
    interval: "1minute", "30minute", "day", "week", "month"
    to_date / from_date: yyyy-mm-dd format.
    Durations: 1minute=1 month, 30minute/day=1 year, week/month=10 years.
    """
    payload = fetch_historical_candles(instrument_key, interval, to_date, from_date)
    return json.dumps(payload, indent=2, default=str)


@mcp.tool()
def get_ohlc_quotes(symbols: str, interval: str = "1d") -> str:
    """
    Fetch OHLC + LTP quotes for up to 1000 instruments in one call.
    symbols: comma-separated instrument keys.
    interval: "1d" (default).
    """
    sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
    payload = fetch_ohlc_quotes(sym_list, interval)
    return json.dumps(payload, indent=2, default=str)


@mcp.tool()
def get_ltp_quotes(symbols: str) -> str:
    """
    Fetch last traded price for up to 1000 instruments.
    symbols: comma-separated instrument keys.
    """
    sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
    payload = fetch_ltp_quotes(sym_list)
    return json.dumps(payload, indent=2, default=str)


# ---------------------------------------------------------------------------
# Computation tools
# ---------------------------------------------------------------------------


@mcp.tool()
def compute_order_book_analysis(market_quote_json: str) -> str:
    """
    Layer 1: Order Book Structure -- compute L1 imbalance, weighted book imbalance,
    spread, walls, and institutional order detection from full market quote JSON.
    Input: JSON string from get_full_market_quote (single instrument object or full response).
    """
    raw = json.loads(market_quote_json)
    quote = _extract_first_quote(raw)
    result = compute_order_book_structure(quote)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
def compute_order_flow_proxy(intraday_candles_json: str) -> str:
    """
    Layer 2: Order Flow Proxy -- compute candle-level delta, cumulative delta,
    delta-price divergence from intraday candle JSON.
    Input: JSON string from get_intraday_candles.
    """
    raw = json.loads(intraday_candles_json)
    candles = (raw.get("data") or {}).get("candles") or raw if isinstance(raw, list) else []
    if isinstance(raw, list):
        candles = raw
    result = compute_order_flow(candles)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
def compute_liquidity_assessment(
    market_quote_json: str,
    session_volume: float,
    expected_volume: float,
) -> str:
    """
    Layer 3: Liquidity -- compute depth ratio, RVOL, and visible depth.
    market_quote_json: full market quote JSON for one instrument.
    session_volume: total volume traded in current session.
    expected_volume: pro-rated average daily volume for this time of day.
    """
    raw = json.loads(market_quote_json)
    quote = _extract_first_quote(raw)
    result = compute_liquidity(quote, session_volume, expected_volume)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
def compute_pcr_and_max_pain(option_chain_json: str) -> str:
    """
    Layer 4: PCR, Max Pain, OI Concentration, ATM straddle price.
    Input: option chain JSON (full API response or array of strike rows).
    """
    raw_rows = parse_chain_json(option_chain_json)
    chain = [normalize_row(r) for r in raw_rows]
    spot = spot_from_chain(chain)
    result = compute_pcr_maxpain(chain, spot)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
def compute_vwap_and_volume_profile(intraday_candles_json: str, market_quote_json: str) -> str:
    """
    Layer 5: VWAP, VWAP slope, volume profile HVN/LVN, LTP vs ATP.
    intraday_candles_json: from get_intraday_candles.
    market_quote_json: from get_full_market_quote (for LTP and ATP).
    """
    candle_raw = json.loads(intraday_candles_json)
    candles = (candle_raw.get("data") or {}).get("candles") or (candle_raw if isinstance(candle_raw, list) else [])
    if isinstance(candle_raw, list):
        candles = candle_raw

    quote_raw = json.loads(market_quote_json)
    quote = _extract_first_quote(quote_raw)
    ltp = float(quote.get("last_price", 0) or 0)
    atp = float(quote.get("average_price", 0) or 0)

    result = compute_vwap_profile(candles, ltp, atp)
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
def compute_cross_market_divergence(ohlc_quotes_json: str, primary_symbol: str) -> str:
    """
    Layer 6: Cross-market divergence -- relative strength, sector alignment,
    futures premium.
    ohlc_quotes_json: from get_ohlc_quotes (must include primary + related symbols).
    primary_symbol: the instrument being traded.
    """
    raw = json.loads(ohlc_quotes_json)
    data = raw.get("data") or raw
    result = compute_cross_market(data, primary_symbol)
    return json.dumps(result, indent=2, default=str)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


@mcp.tool()
def run_full_microstructure_scan(
    instrument_key: str,
    expiry_date: str | None = None,
    related_symbols: str | None = None,
) -> str:
    """
    Run the complete 7-layer microstructure scan in one call.
    Fetches option chain, full market quote, intraday & historical candles,
    and (if related_symbols provided) cross-market OHLC quotes.

    Returns JSON with per-layer signals, raw/adjusted score, verdict,
    and Tier-1 option chain features.

    instrument_key: e.g. "NSE_INDEX|Nifty 50"
    expiry_date: yyyy-mm-dd (defaults to next weekly expiry)
    related_symbols: comma-separated keys for cross-market check
      e.g. "NSE_INDEX|Nifty Bank,NSE_INDEX|Nifty IT"
    """
    related = (
        [s.strip() for s in related_symbols.split(",") if s.strip()]
        if related_symbols
        else None
    )
    result = run_scan(instrument_key, expiry_date, related)
    return json.dumps(result, indent=2, default=str)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_first_quote(raw: dict[str, Any]) -> dict[str, Any]:
    """Pull the first instrument's quote from a market-quote response."""
    data = raw.get("data") or raw
    if isinstance(data, dict):
        for val in data.values():
            if isinstance(val, dict):
                return val
    return raw


def run_stdio() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_stdio()
