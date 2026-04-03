"""Normalize Upstox option-chain JSON rows for the rule engine."""

from __future__ import annotations

import json
from typing import Any


def parse_chain_json(chain_json: str) -> list[dict[str, Any]]:
    obj = json.loads(chain_json)
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict) and "data" in obj:
        data = obj["data"]
        if not isinstance(data, list):
            raise ValueError("response 'data' must be a list")
        return data
    raise ValueError("expected a JSON array or an object with a 'data' array")


def spot_from_chain(chain: list[dict[str, Any]]) -> float:
    if not chain:
        raise ValueError("empty option chain")
    v = chain[0].get("underlying_spot_price")
    if v is None:
        raise ValueError("missing underlying_spot_price")
    return float(v)


def _f(x: Any, default: float = 0.0) -> float:
    if x is None:
        return default
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def _i(x: Any, default: int = 0) -> int:
    if x is None:
        return default
    try:
        return int(x)
    except (TypeError, ValueError):
        return default


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    """Ensure nested structures exist with numeric defaults (Upstox-shaped)."""
    co = row.get("call_options") or {}
    po = row.get("put_options") or {}
    cmd = co.get("market_data") or {}
    pmd = po.get("market_data") or {}
    cg = co.get("option_greeks") or {}
    pg = po.get("option_greeks") or {}
    return {
        "strike_price": _f(row.get("strike_price")),
        "underlying_spot_price": _f(row.get("underlying_spot_price")),
        "expiry": row.get("expiry"),
        "underlying_key": row.get("underlying_key"),
        "pcr": _f(row.get("pcr")),
        "call_options": {
            "market_data": {
                "ltp": _f(cmd.get("ltp")),
                "volume": _i(cmd.get("volume")),
                "oi": _f(cmd.get("oi")),
                "close_price": _f(cmd.get("close_price")),
                "prev_oi": _f(cmd.get("prev_oi")),
            },
            "option_greeks": {
                "vega": _f(cg.get("vega")),
                "theta": _f(cg.get("theta")),
                "gamma": _f(cg.get("gamma")),
                "delta": _f(cg.get("delta")),
                "iv": _f(cg.get("iv")),
                "pop": _f(cg.get("pop")),
            },
        },
        "put_options": {
            "market_data": {
                "ltp": _f(pmd.get("ltp")),
                "volume": _i(pmd.get("volume")),
                "oi": _f(pmd.get("oi")),
                "close_price": _f(pmd.get("close_price")),
                "prev_oi": _f(pmd.get("prev_oi")),
            },
            "option_greeks": {
                "vega": _f(pg.get("vega")),
                "theta": _f(pg.get("theta")),
                "gamma": _f(pg.get("gamma")),
                "delta": _f(pg.get("delta")),
                "iv": _f(pg.get("iv")),
                "pop": _f(pg.get("pop")),
            },
        },
    }
