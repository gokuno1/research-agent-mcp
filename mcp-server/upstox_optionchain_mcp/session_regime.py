"""Layer 7: Session Regime and Context -- RVOL, regime, time-of-day multiplier."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any

IST = timezone(timedelta(hours=5, minutes=30))

# Cumulative share of daily volume by IST hour boundary.
# Used to pro-rate expected volume: first hour ~30%, midday ~10% each, last hour ~25%.
_HOUR_CUM_SHARE: list[tuple[int, int, float]] = [
    (9, 15, 0.00),
    (10, 15, 0.30),
    (11, 15, 0.40),
    (12, 15, 0.50),
    (13, 0, 0.60),
    (14, 0, 0.70),
    (15, 0, 0.85),
    (15, 30, 1.00),
]


def _expected_volume_share(now: datetime) -> float:
    """Return the fraction of daily volume expected to have traded by *now* IST."""
    hm = now.hour * 60 + now.minute
    prev_share = 0.0
    for h, m, share in _HOUR_CUM_SHARE:
        boundary = h * 60 + m
        if hm < boundary:
            break
        prev_share = share
    return max(prev_share, 0.01)


def compute_session_regime(
    candles: list[list],
    avg_daily_volume: float,
    current_time_ist: str | None = None,
) -> dict[str, Any]:
    """Classify session regime and compute time-of-day multiplier.

    *candles*: intraday ``[ts, O, H, L, C, V, OI]`` rows.
    *avg_daily_volume*: mean daily volume from historical data.
    *current_time_ist*: ISO-format time string; defaults to now IST.
    """
    if len(candles) < 3:
        return {
            "layer": "L7_SESSION_REGIME",
            "multiplier": 0.5,
            "regime": "INSUFFICIENT_DATA",
            "meta": {"reason": "fewer_than_3_candles"},
        }

    # Parse current time
    if current_time_ist:
        try:
            now = datetime.fromisoformat(current_time_ist)
        except ValueError:
            now = datetime.now(IST)
    else:
        now = datetime.now(IST)

    # Session volume
    session_volume = sum(float(c[5]) for c in candles)
    vol_share = _expected_volume_share(now)
    expected_volume = avg_daily_volume * vol_share
    rvol = session_volume / expected_volume if expected_volume > 0 else 1.0

    # Regime from candle structure (using ~30-min groups or raw candles)
    highs = [float(c[2]) for c in candles]
    lows = [float(c[3]) for c in candles]
    closes = [float(c[4]) for c in candles]

    # Simple swing detection: look at first, mid, last thirds
    n = len(candles)
    third = max(n // 3, 1)
    seg_highs = [max(highs[i * third: (i + 1) * third]) for i in range(3)]
    seg_lows = [min(lows[i * third: (i + 1) * third]) for i in range(3)]

    hh_hl = seg_highs[2] > seg_highs[0] and seg_lows[2] > seg_lows[0]
    lh_ll = seg_highs[2] < seg_highs[0] and seg_lows[2] < seg_lows[0]

    session_range = max(highs) - min(lows)
    avg_candle_range = sum(highs[i] - lows[i] for i in range(n)) / n if n else 0
    atr_contracting = n > 6 and (
        sum(highs[i] - lows[i] for i in range(n - 3, n)) / 3
        < sum(highs[i] - lows[i] for i in range(3)) / 3 * 0.6
    )

    if rvol < 0.5 and not hh_hl and not lh_ll:
        regime = "DEAD_DRIFT"
    elif hh_hl:
        regime = "TRENDING_UP"
    elif lh_ll:
        regime = "TRENDING_DOWN"
    elif atr_contracting:
        regime = "RANGE_BOUND"
    elif session_range > avg_candle_range * n * 0.4 and rvol > 1.5:
        regime = "VOLATILE"
    else:
        regime = "RANGE_BOUND"

    # Time-of-day multiplier
    hm = now.hour * 60 + now.minute
    if hm < 9 * 60 + 30:
        tod_reliability = "LOW"
        tod_mult = 0.5
    elif hm < 10 * 60 + 30:
        tod_reliability = "HIGH"
        tod_mult = 1.0
    elif hm < 13 * 60:
        tod_reliability = "MODERATE"
        tod_mult = 0.75
    elif hm < 14 * 60:
        tod_reliability = "LOW"
        tod_mult = 0.5
    elif hm < 15 * 60 + 15:
        tod_reliability = "HIGH"
        tod_mult = 1.0
    else:
        tod_reliability = "LOW"
        tod_mult = 0.5

    # Final multiplier
    if regime == "DEAD_DRIFT":
        multiplier = 0.0
    else:
        multiplier = tod_mult

    return {
        "layer": "L7_SESSION_REGIME",
        "multiplier": multiplier,
        "regime": regime,
        "meta": {
            "rvol": round(rvol, 4),
            "session_volume": session_volume,
            "expected_volume": round(expected_volume, 0),
            "time_of_day": tod_reliability,
            "tod_multiplier": tod_mult,
            "session_range": round(session_range, 2),
        },
    }
