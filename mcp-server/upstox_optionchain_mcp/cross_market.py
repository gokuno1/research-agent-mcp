"""Layer 6: Cross-Market Divergence -- relative strength, sector alignment, futures premium."""

from __future__ import annotations

from typing import Any


def compute_cross_market(
    ohlc_data: dict[str, Any],
    primary_symbol: str,
) -> dict[str, Any]:
    """Score cross-market divergence from OHLC quotes of related instruments.

    *ohlc_data* is the ``data`` dict from ``GET /market-quote/ohlc`` keyed by
    symbol.  *primary_symbol* is the instrument being traded (its % change is
    compared against the others).
    """
    if not ohlc_data:
        return _neutral("no_ohlc_data")

    changes: dict[str, float] = {}
    for sym, info in ohlc_data.items():
        ohlc = info.get("ohlc") or {}
        close = float(ohlc.get("close", 0) or 0)
        last = float(info.get("last_price", 0) or 0)
        if close > 0 and last > 0:
            changes[sym] = (last - close) / close * 100.0

    primary_change = changes.get(primary_symbol)
    if primary_change is None:
        return _neutral("primary_symbol_missing_in_data")

    # Relative strength vs each related instrument
    others = {s: c for s, c in changes.items() if s != primary_symbol}
    if not others:
        return _neutral("no_related_instruments")

    confirming = 0
    diverging = 0
    for sym, chg in others.items():
        same_direction = (chg > 0 and primary_change > 0) or (chg < 0 and primary_change < 0)
        if same_direction:
            confirming += 1
        else:
            diverging += 1

    total = confirming + diverging
    confirm_ratio = confirming / total if total > 0 else 0.5

    # Futures premium (heuristic: look for a symbol ending with a futures-like key)
    futures_premium: float | None = None
    for sym, info in ohlc_data.items():
        if sym != primary_symbol and primary_symbol.split("|")[1] in sym:
            spot_price = changes.get(primary_symbol, 0)
            fut_ohlc = info.get("ohlc") or {}
            fut_close = float(fut_ohlc.get("close", 0) or 0)
            fut_last = float(info.get("last_price", 0) or 0)
            if fut_close > 0:
                primary_ohlc = ohlc_data.get(primary_symbol, {}).get("ohlc", {})
                spot_last = float(ohlc_data.get(primary_symbol, {}).get("last_price", 0) or 0)
                if spot_last > 0 and fut_last > 0:
                    futures_premium = (fut_last - spot_last) / spot_last * 100.0
            break

    # Scoring
    premium_healthy = futures_premium is None or (futures_premium is not None and futures_premium > 0.03)

    if confirm_ratio >= 0.8 and premium_healthy:
        signal, points = "CONFIRMING", 2
    elif confirm_ratio >= 0.6:
        signal, points = "MOSTLY_CONFIRMING", 1
    elif confirm_ratio <= 0.2:
        signal, points = "CONTRADICTING", -2
    elif confirm_ratio <= 0.4:
        signal, points = "WARNING", -1
    else:
        signal, points = "DIVERGENT", 0

    return {
        "layer": "L6_CROSS_MARKET",
        "signal": signal,
        "points": points,
        "meta": {
            "primary_change_pct": round(primary_change, 4),
            "instrument_changes": {s: round(c, 4) for s, c in changes.items()},
            "confirming_count": confirming,
            "diverging_count": diverging,
            "confirm_ratio": round(confirm_ratio, 4),
            "futures_premium_pct": round(futures_premium, 4) if futures_premium is not None else None,
        },
    }


def _neutral(reason: str) -> dict[str, Any]:
    return {"layer": "L6_CROSS_MARKET", "signal": "NEUTRAL", "points": 0, "meta": {"reason": reason}}
