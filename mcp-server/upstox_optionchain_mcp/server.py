"""
Stdio MCP server: Upstox option chain + 15 Tier-1 signals + trade-signal prompt builder.

Configure in Cursor via MCP settings: set env UPSTOX_ACCESS_TOKEN (and optionally
UPSTOX_INSTRUMENT_KEY, UPSTOX_API_BASE, UPSTOX_INDEX_LABEL).
"""

from __future__ import annotations

import json
import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from upstox_optionchain_mcp.date_utils import get_expiry_string_like_java
from upstox_optionchain_mcp.feature_pipeline import compute_features_json_string
from upstox_optionchain_mcp.signal_prompt import build_trade_signal_prompt
from upstox_optionchain_mcp.upstox_api import fetch_option_chain

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


def run_stdio() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_stdio()
