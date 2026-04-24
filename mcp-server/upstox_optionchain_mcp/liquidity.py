"""Layer 3: Liquidity Assessment -- depth ratio, RVOL, visible depth."""

from __future__ import annotations

from typing import Any


def compute_liquidity(
    quote_data: dict[str, Any],
    session_volume: float,
    expected_volume: float,
) -> dict[str, Any]:
    """Assess liquidity from L2 depth and volume data.

    *quote_data* must contain ``depth.buy`` / ``depth.sell`` arrays.
    *expected_volume* is the pro-rated average daily volume for this time of day.
    """
    depth = quote_data.get("depth") or {}
    bids: list[dict] = depth.get("buy") or []
    asks: list[dict] = depth.get("sell") or []

    total_bid_depth = sum(_qty(b) for b in bids[:5])
    total_ask_depth = sum(_qty(a) for a in asks[:5])

    depth_ratio = total_bid_depth / total_ask_depth if total_ask_depth > 0 else 1.0
    rvol = session_volume / expected_volume if expected_volume > 0 else 1.0

    # Scoring
    if depth_ratio > 1.5 and rvol > 1.2:
        signal, points = "BULLISH", 2
    elif depth_ratio > 1.3 or (depth_ratio > 1.0 and rvol > 1.5):
        signal, points = "LEAN_BULLISH", 1
    elif depth_ratio < 0.67 and rvol > 1.2:
        signal, points = "BEARISH", -2
    elif depth_ratio < 0.75 or (depth_ratio < 1.0 and rvol > 1.5):
        signal, points = "LEAN_BEARISH", -1
    else:
        signal, points = "NEUTRAL", 0

    # RVOL < 0.7 cap
    if rvol < 0.7:
        points = max(-1, min(1, points))

    return {
        "layer": "L3_LIQUIDITY",
        "signal": signal,
        "points": points,
        "meta": {
            "total_bid_depth": total_bid_depth,
            "total_ask_depth": total_ask_depth,
            "depth_ratio": round(depth_ratio, 4),
            "rvol": round(rvol, 4),
            "rvol_capped": rvol < 0.7,
        },
    }


def _qty(level: dict) -> float:
    v = level.get("quantity", 0)
    if isinstance(v, dict):
        return 0.0
    return float(v or 0)
