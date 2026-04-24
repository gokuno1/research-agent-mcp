"""Layer 5: VWAP and Volume Profile -- VWAP, slope, HVN/LVN, LTP vs ATP."""

from __future__ import annotations

from typing import Any


def compute_vwap_profile(
    candles: list[list],
    ltp: float,
    atp: float,
    bucket_size: float = 10.0,
) -> dict[str, Any]:
    """Compute VWAP, volume profile, and related L5 signals.

    *candles*: rows of ``[ts, O, H, L, C, V, OI]``.
    *ltp*/*atp*: last traded price / average traded price from full quote.
    *bucket_size*: price range per volume-profile bucket (default 10 pts for NIFTY).
    """
    if len(candles) < 2:
        return _neutral("insufficient_candles")

    tp_vol_sum = 0.0
    vol_sum = 0.0
    volume_buckets: dict[float, float] = {}

    for c in candles:
        h, l, close, vol = float(c[2]), float(c[3]), float(c[4]), float(c[5])
        tp = (h + l + close) / 3.0
        tp_vol_sum += tp * vol
        vol_sum += vol

        bucket_key = round((tp // bucket_size) * bucket_size, 2)
        volume_buckets[bucket_key] = volume_buckets.get(bucket_key, 0.0) + vol

    vwap = tp_vol_sum / vol_sum if vol_sum > 0 else ltp

    # VWAP slope: compare VWAP at 25% vs 75% through the session
    n = len(candles)
    q1_idx = n // 4
    q3_idx = (3 * n) // 4
    if q3_idx > q1_idx:
        vwap_q1 = _partial_vwap(candles[:q1_idx + 1])
        vwap_q3 = _partial_vwap(candles[:q3_idx + 1])
        if vwap_q1 and vwap_q3:
            vwap_slope = "RISING" if vwap_q3 > vwap_q1 * 1.0005 else (
                "FALLING" if vwap_q3 < vwap_q1 * 0.9995 else "FLAT"
            )
        else:
            vwap_slope = "FLAT"
    else:
        vwap_slope = "FLAT"

    # Price vs VWAP
    price_vs_vwap = "ABOVE" if ltp > vwap * 1.001 else ("BELOW" if ltp < vwap * 0.999 else "AT_VWAP")

    # HVN / LVN
    hvn_bucket = max(volume_buckets, key=volume_buckets.get) if volume_buckets else ltp  # type: ignore[arg-type]
    lvn_bucket = min(volume_buckets, key=volume_buckets.get) if volume_buckets else ltp  # type: ignore[arg-type]

    # LTP vs ATP
    ltp_vs_atp = "ABOVE" if ltp > atp * 1.001 else ("BELOW" if ltp < atp * 0.999 else "AT_ATP")

    # Scoring
    if price_vs_vwap == "ABOVE" and vwap_slope == "RISING" and ltp_vs_atp == "ABOVE":
        signal, points = "BULLISH", 2
    elif price_vs_vwap == "ABOVE" or (price_vs_vwap == "AT_VWAP" and vwap_slope == "RISING"):
        signal, points = "LEAN_BULLISH", 1
    elif price_vs_vwap == "BELOW" and vwap_slope == "FALLING" and ltp_vs_atp == "BELOW":
        signal, points = "BEARISH", -2
    elif price_vs_vwap == "BELOW" or (price_vs_vwap == "AT_VWAP" and vwap_slope == "FALLING"):
        signal, points = "LEAN_BEARISH", -1
    else:
        signal, points = "NEUTRAL", 0

    return {
        "layer": "L5_VWAP_PROFILE",
        "signal": signal,
        "points": points,
        "meta": {
            "vwap": round(vwap, 2),
            "vwap_slope": vwap_slope,
            "price_vs_vwap": price_vs_vwap,
            "ltp_vs_atp": ltp_vs_atp,
            "hvn_price": hvn_bucket,
            "lvn_price": lvn_bucket,
            "ltp": ltp,
            "atp": atp,
        },
    }


def _partial_vwap(candles: list[list]) -> float | None:
    tp_vol = 0.0
    vol = 0.0
    for c in candles:
        h, l, close, v = float(c[2]), float(c[3]), float(c[4]), float(c[5])
        tp_vol += ((h + l + close) / 3.0) * v
        vol += v
    return tp_vol / vol if vol > 0 else None


def _neutral(reason: str) -> dict[str, Any]:
    return {"layer": "L5_VWAP_PROFILE", "signal": "NEUTRAL", "points": 0, "meta": {"reason": reason}}
