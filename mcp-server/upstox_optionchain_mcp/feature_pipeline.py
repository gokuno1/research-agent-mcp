"""End-to-end: option-chain JSON -> Tier-1 feature bundle JSON string."""

from __future__ import annotations

import json
import math
from typing import Any

from upstox_optionchain_mcp.chain_parse import normalize_row, parse_chain_json, spot_from_chain
from upstox_optionchain_mcp.rule_engine import evaluate
from upstox_optionchain_mcp.tier1_to_signals import legacy_to_signals


def _sanitize_for_json(obj: Any) -> Any:
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_for_json(v) for v in obj]
    return obj


def compute_feature_bundle(chain_json: str) -> dict[str, Any]:
    raw_rows = parse_chain_json(chain_json)
    chain = [normalize_row(r) for r in raw_rows]
    if not chain:
        raise ValueError("option chain has no rows")
    spot = spot_from_chain(chain)
    legacy = evaluate(chain, spot)
    signals = legacy_to_signals(legacy)
    strikes = sorted({float(r["strike_price"]) for r in chain})
    return {
        "underlying_spot_price": spot,
        "underlying_key": chain[0].get("underlying_key"),
        "expiry": chain[0].get("expiry"),
        "strike_prices_available": strikes,
        "atm_strike_hint": min(strikes, key=lambda k: abs(k - spot)) if strikes else None,
        "tier1_signals": signals,
        "legacy_rule_engine": legacy,
    }


def compute_features_json_string(chain_json: str) -> str:
    bundle = _sanitize_for_json(compute_feature_bundle(chain_json))
    return json.dumps(bundle, indent=2, allow_nan=False)
