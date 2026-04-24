"""Layer 2: Order Flow Proxy -- candle-level delta, cumulative delta, divergence."""

from __future__ import annotations

from typing import Any


def compute_order_flow(candles: list[list]) -> dict[str, Any]:
    """Compute order flow proxy from intraday OHLCV candles.

    Each candle row: ``[timestamp, open, high, low, close, volume, oi]``.
    """
    if len(candles) < 2:
        return _neutral("insufficient_candles")

    deltas: list[float] = []
    prices: list[float] = []
    volumes: list[float] = []

    for c in candles:
        o, h, l, close, vol = float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5])
        prices.append(close)
        volumes.append(vol)
        if close > o:
            deltas.append(vol)
        elif close < o:
            deltas.append(-vol)
        else:
            deltas.append(0.0)

    # Cumulative delta
    cum_delta: list[float] = []
    running = 0.0
    for d in deltas:
        running += d
        cum_delta.append(running)

    # Delta trend over last 6 candles (approx 30 min at 5-min, or 6 min at 1-min)
    lookback = min(6, len(cum_delta))
    recent = cum_delta[-lookback:]
    delta_trend = "FLAT"
    if len(recent) >= 2:
        slope = recent[-1] - recent[0]
        if slope > 0:
            delta_trend = "RISING"
        elif slope < 0:
            delta_trend = "FALLING"

    # Price trend
    price_trend = "FLAT"
    if len(prices) >= 2:
        p_slope = prices[-1] - prices[0]
        if p_slope > 0:
            price_trend = "RISING"
        elif p_slope < 0:
            price_trend = "FALLING"

    # Session extremes for divergence check
    session_high = max(float(c[2]) for c in candles)
    session_low = min(float(c[3]) for c in candles)
    current_close = prices[-1]
    at_session_high = abs(current_close - session_high) / max(session_high, 1) < 0.001
    at_session_low = abs(current_close - session_low) / max(session_low, 1) < 0.001

    # Divergence overrides
    bearish_divergence = at_session_high and delta_trend == "FALLING"
    bullish_divergence = at_session_low and delta_trend == "RISING"

    # Volume-price confirmation
    avg_vol = sum(volumes) / len(volumes) if volumes else 1.0
    up_candle_high_vol = sum(
        1 for i, c in enumerate(candles) if float(c[4]) > float(c[1]) and volumes[i] > avg_vol * 1.2
    )
    down_candle_high_vol = sum(
        1 for i, c in enumerate(candles) if float(c[4]) < float(c[1]) and volumes[i] > avg_vol * 1.2
    )

    # Scoring
    if bullish_divergence:
        signal, points = "BULLISH_DIVERGENCE", 2
    elif bearish_divergence:
        signal, points = "BEARISH_DIVERGENCE", -2
    elif delta_trend == "RISING" and price_trend == "RISING":
        signal, points = "BULLISH", 2
    elif delta_trend == "RISING" and price_trend == "FLAT":
        signal, points = "LEAN_BULLISH", 1
    elif delta_trend == "FALLING" and price_trend == "FALLING":
        signal, points = "BEARISH", -2
    elif delta_trend == "FALLING" and price_trend == "FLAT":
        signal, points = "LEAN_BEARISH", -1
    else:
        signal, points = "NEUTRAL", 0

    return {
        "layer": "L2_ORDER_FLOW",
        "signal": signal,
        "points": points,
        "meta": {
            "cumulative_delta": round(cum_delta[-1], 2) if cum_delta else 0.0,
            "delta_trend": delta_trend,
            "price_trend": price_trend,
            "bearish_divergence": bearish_divergence,
            "bullish_divergence": bullish_divergence,
            "up_candles_high_vol": up_candle_high_vol,
            "down_candles_high_vol": down_candle_high_vol,
            "session_high": session_high,
            "session_low": session_low,
        },
    }


def _neutral(reason: str) -> dict[str, Any]:
    return {"layer": "L2_ORDER_FLOW", "signal": "NEUTRAL", "points": 0, "meta": {"reason": reason}}
