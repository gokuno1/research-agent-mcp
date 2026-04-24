"""Layer 4: PCR, Max Pain, OI Concentration, ATM Straddle."""

from __future__ import annotations

from typing import Any


def compute_pcr_maxpain(chain: list[dict[str, Any]], spot: float) -> dict[str, Any]:
    """Standard Layer-4 option chain positioning metrics.

    *chain* is the list of normalized option chain rows (same shape used by
    ``rule_engine.evaluate``).  *spot* is the underlying spot price.
    """
    if not chain:
        return _neutral("empty_chain")

    total_call_oi = 0.0
    total_put_oi = 0.0
    max_call_oi = 0.0
    max_call_oi_strike = spot
    max_put_oi = 0.0
    max_put_oi_strike = spot
    strikes: list[float] = []
    call_ois: dict[float, float] = {}
    put_ois: dict[float, float] = {}

    for row in chain:
        k = float(row["strike_price"])
        strikes.append(k)
        c_oi = float((row.get("call_options") or {}).get("market_data", {}).get("oi", 0) or 0)
        p_oi = float((row.get("put_options") or {}).get("market_data", {}).get("oi", 0) or 0)
        call_ois[k] = c_oi
        put_ois[k] = p_oi
        total_call_oi += c_oi
        total_put_oi += p_oi
        if c_oi > max_call_oi:
            max_call_oi = c_oi
            max_call_oi_strike = k
        if p_oi > max_put_oi:
            max_put_oi = p_oi
            max_put_oi_strike = k

    # PCR (OI-based)
    pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 1.0

    # Max Pain -- strike minimizing total option pain
    strikes_sorted = sorted(set(strikes))
    max_pain_strike = spot
    min_pain = float("inf")
    for k in strikes_sorted:
        call_pain = sum(call_ois.get(s, 0) * max(0.0, k - s) for s in strikes_sorted if s < k)
        put_pain = sum(put_ois.get(s, 0) * max(0.0, s - k) for s in strikes_sorted if s > k)
        total_pain = call_pain + put_pain
        if total_pain < min_pain:
            min_pain = total_pain
            max_pain_strike = k

    # OI change at highest-OI strikes
    call_oi_change = 0.0
    put_oi_change = 0.0
    for row in chain:
        k = float(row["strike_price"])
        cmd = (row.get("call_options") or {}).get("market_data", {})
        pmd = (row.get("put_options") or {}).get("market_data", {})
        if abs(k - max_call_oi_strike) < 0.01:
            call_oi_change = float(cmd.get("oi", 0) or 0) - float(cmd.get("prev_oi", 0) or 0)
        if abs(k - max_put_oi_strike) < 0.01:
            put_oi_change = float(pmd.get("oi", 0) or 0) - float(pmd.get("prev_oi", 0) or 0)

    # ATM straddle price
    atm_strike = min(strikes_sorted, key=lambda k: abs(k - spot)) if strikes_sorted else spot
    atm_call_ltp = 0.0
    atm_put_ltp = 0.0
    for row in chain:
        if abs(float(row["strike_price"]) - atm_strike) < 0.01:
            atm_call_ltp = float((row.get("call_options") or {}).get("market_data", {}).get("ltp", 0) or 0)
            atm_put_ltp = float((row.get("put_options") or {}).get("market_data", {}).get("ltp", 0) or 0)
            break
    atm_straddle = atm_call_ltp + atm_put_ltp

    # Scoring
    above_max_pain = spot > max_pain_strike
    below_call_resistance = spot < max_call_oi_strike
    above_put_support = spot > max_put_oi_strike
    approaching_put_support = abs(spot - max_put_oi_strike) / max(spot, 1) < 0.005

    bonus = 0
    if spot > max_call_oi_strike:
        bonus += 1
    if spot < max_put_oi_strike:
        bonus -= 1

    if pcr > 1.2 and above_max_pain and below_call_resistance:
        signal, points = "BULLISH", 2
    elif pcr > 1.0 and above_put_support:
        signal, points = "LEAN_BULLISH", 1
    elif pcr < 0.8 and approaching_put_support:
        signal, points = "BEARISH", -2
    elif pcr < 0.8 and not above_max_pain and above_put_support:
        signal, points = "LEAN_BEARISH", -1
    elif abs(pcr - 1.0) <= 0.2 and abs(spot - max_pain_strike) / max(spot, 1) < 0.005:
        signal, points = "NEUTRAL", 0
    else:
        signal, points = "NEUTRAL", 0

    points += bonus
    points = max(-3, min(3, points))

    return {
        "layer": "L4_OPTION_CHAIN",
        "signal": signal,
        "points": points,
        "meta": {
            "pcr_oi": round(pcr, 4),
            "max_pain_strike": max_pain_strike,
            "highest_call_oi_strike": max_call_oi_strike,
            "highest_call_oi": max_call_oi,
            "highest_put_oi_strike": max_put_oi_strike,
            "highest_put_oi": max_put_oi,
            "call_oi_change_at_resistance": call_oi_change,
            "put_oi_change_at_support": put_oi_change,
            "atm_straddle_price": round(atm_straddle, 2),
            "atm_strike": atm_strike,
        },
    }


def _neutral(reason: str) -> dict[str, Any]:
    return {"layer": "L4_OPTION_CHAIN", "signal": "NEUTRAL", "points": 0, "meta": {"reason": reason}}
