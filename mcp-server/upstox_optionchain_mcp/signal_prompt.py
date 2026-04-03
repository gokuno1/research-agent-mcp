"""Prompt assembly for Cursor agent to emit the trade JSON schema."""

from __future__ import annotations

import json
from typing import Any

SCHEMA_INSTRUCTIONS = """
You are an expert NIFTY-style index options analyst. You MUST respond with ONLY a single JSON object
(no markdown fences, no extra text) matching exactly this shape:

{
  "direction_bias": "bullish" | "bearish" | "neutral",
  "volatility_expectation": "low" | "moderate" | "high",
  "key_levels": [number, ...],
  "trade_strike": "e.g. 24500 CE" or "NO_TRADE",
  "instrument_type": "CE" | "PE" or "" when NO_TRADE,
  "strike_price": number or 0 when NO_TRADE,
  "target_percent": number,
  "stop_percent": number,
  "reasoning": "short explanation",
  "confidence": "low" | "medium" | "high"
}

Rules:
- Only recommend buying CE or PE (long options). Use NO_TRADE when edge is weak or signals conflict.
- Choose strike_price using underlying spot and strike_prices_available / ATM hint; prefer liquid near-ATM unless signals justify OTM.
- target_percent and stop_percent are percent moves on the option premium (intraday-style), not on spot.
- key_levels: include support/resistance or notable strikes from signals (numbers only).
- When in doubt, NO_TRADE with neutral bias and confidence low.
"""


def build_trade_signal_prompt(
    index_label: str,
    expiry: str,
    features_json: str,
) -> str:
    try:
        bundle = json.loads(features_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"features_json is not valid JSON: {e}") from e
    spot = bundle.get("underlying_spot_price")
    lines = [
        SCHEMA_INSTRUCTIONS.strip(),
        "",
        f"Underlying label: {index_label}",
        f"Expiry: {expiry}",
        f"Spot (from chain): {spot}",
        "",
        "Feature bundle (Tier-1 signals + context):",
        json.dumps(bundle, indent=2, default=str),
    ]
    return "\n".join(lines)
