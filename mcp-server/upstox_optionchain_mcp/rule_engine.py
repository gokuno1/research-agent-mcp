"""
Port of com.tradebot.upstox.service.impl.OptionChainRuleEngine (15 Tier-1 signals).
Chain rows must be normalized (see chain_parse.normalize_row).
"""

from __future__ import annotations

import math
from typing import Any


def _cmd(d: dict[str, Any]) -> dict[str, Any]:
    return d["call_options"]["market_data"]


def _pmd(d: dict[str, Any]) -> dict[str, Any]:
    return d["put_options"]["market_data"]


def _cg(d: dict[str, Any]) -> dict[str, Any]:
    return d["call_options"]["option_greeks"]


def _pg(d: dict[str, Any]) -> dict[str, Any]:
    return d["put_options"]["option_greeks"]


def _find_closest_strike(chain: list[dict[str, Any]], spot: float) -> float:
    if not chain:
        return spot
    best = min(chain, key=lambda o: abs(o["strike_price"] - spot))
    return float(best["strike_price"])


def _same_strike(a: float, b: float, eps: float = 1e-6) -> bool:
    return abs(a - b) < eps


def evaluate(chain: list[dict[str, Any]], spot_price: float) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if not chain:
        return out
    out["oi_velocity"] = _compute_oi_velocity(chain, spot_price)
    out["opening_vs_closing"] = _compute_opening_vs_closing(chain, spot_price)
    out["dealer_hedge_pressure"] = _compute_dealer_hedge_pressure(chain, spot_price)
    out["oi_center_of_gravity"] = _compute_oi_center_of_gravity(chain, spot_price)
    out["convexity_asymmetry"] = _compute_convexity_asymmetry(chain, spot_price)
    out["liquidity_void"] = _compute_liquidity_void(chain, spot_price)
    out["strike_roll"] = _compute_strike_roll(chain)
    out["calendar_conflict"] = _compute_calendar_conflict(chain, spot_price)
    out["skew_responsiveness"] = _compute_skew_responsiveness(chain, spot_price)
    out["dealer_neutral_corridor"] = _compute_dealer_neutral_corridor(chain, spot_price)
    out["intrinsic_dominance"] = _compute_intrinsic_dominance(chain, spot_price)
    out["strike_defense_failure"] = _compute_strike_defense_failure(chain, spot_price)
    out["synthetic_forward_distortion"] = _compute_synthetic_forward_distortion(chain, spot_price)
    out["participant_trap"] = _compute_participant_trap(chain, spot_price)
    out["volatility_supply_exhaustion"] = _compute_volatility_supply_exhaustion(chain, spot_price)
    return out


def _band(f: float | None, t: float | None) -> dict[str, float] | None:
    if f is None or t is None or (isinstance(f, float) and math.isnan(f)):
        return None
    return {"from": float(f), "to": float(t)}


def _compute_oi_velocity(chain: list[dict[str, Any]], spot_price: float) -> dict[str, Any]:
    call_delta_oi_sum = 0.0
    put_delta_oi_sum = 0.0
    call_oi_sum = 0.0
    put_oi_sum = 0.0
    for data in chain:
        call_md = _cmd(data)
        put_md = _pmd(data)
        call_delta_oi_sum += call_md["oi"] - call_md["prev_oi"]
        put_delta_oi_sum += put_md["oi"] - put_md["prev_oi"]
        call_oi_sum += call_md["oi"]
        put_oi_sum += put_md["oi"]
    call_delta_pct = (call_delta_oi_sum / call_oi_sum) if call_oi_sum != 0.0 else 0.0
    put_delta_pct = (put_delta_oi_sum / put_oi_sum) if put_oi_sum != 0.0 else 0.0
    first_close = _cmd(chain[0])["close_price"]
    und = float(chain[0].get("underlying_spot_price") or spot_price)
    if und - first_close > 0:
        price_move = "UP"
    elif und - first_close < 0:
        price_move = "DOWN"
    else:
        price_move = "FLAT"
    state = "NEUTRAL"
    if price_move == "UP":
        if call_delta_pct > 0.05:
            state = "RESISTANCE_FORMATION"
        elif call_delta_pct < -0.05:
            state = "SHORT_COVERING"
    elif price_move == "DOWN":
        if put_delta_pct > 0.05:
            state = "BEARISH_POSITIONING"
        elif put_delta_pct < -0.05:
            state = "FLOOR_REMOVAL"
    strength = min(1.0, abs(call_delta_pct) + abs(put_delta_pct))
    atm_strike = _find_closest_strike(chain, spot_price)
    atm_call_delta_oi = 0.0
    atm_put_delta_oi = 0.0
    for data in chain:
        if _same_strike(data["strike_price"], atm_strike):
            atm_call_delta_oi = _cmd(data)["oi"] - _cmd(data)["prev_oi"]
            atm_put_delta_oi = _pmd(data)["oi"] - _pmd(data)["prev_oi"]
            break
    max_call_delta_oi = float("-inf")
    max_put_delta_oi = float("-inf")
    res_strike = atm_strike
    sup_strike = atm_strike
    for data in chain:
        call_delta_oi = _cmd(data)["oi"] - _cmd(data)["prev_oi"]
        put_delta_oi = _pmd(data)["oi"] - _pmd(data)["prev_oi"]
        if call_delta_oi > max_call_delta_oi:
            max_call_delta_oi = call_delta_oi
            res_strike = data["strike_price"]
        if put_delta_oi > max_put_delta_oi:
            max_put_delta_oi = put_delta_oi
            sup_strike = data["strike_price"]
    return {
        "call_delta_oi_pct": call_delta_pct,
        "put_delta_oi_pct": put_delta_pct,
        "price_move": price_move,
        "state": state,
        "strength": strength,
        "atm_contraction_active": atm_call_delta_oi < 0 and atm_put_delta_oi < 0,
        "top_resistance_band": _band(res_strike, res_strike),
        "top_support_band": _band(sup_strike, sup_strike),
    }


def _compute_opening_vs_closing(chain: list[dict[str, Any]], spot_price: float) -> dict[str, Any]:
    positional_volume = 0.0
    churn_volume = 0.0
    for data in chain:
        call_md = _cmd(data)
        put_md = _pmd(data)
        call_vol = int(call_md["volume"])
        put_vol = int(put_md["volume"])
        call_delta_oi = call_md["oi"] - call_md["prev_oi"]
        put_delta_oi = put_md["oi"] - put_md["prev_oi"]
        eff_call = (abs(call_delta_oi) / call_vol) if call_vol > 0 else 0.0
        eff_put = (abs(put_delta_oi) / put_vol) if put_vol > 0 else 0.0
        if eff_call > 0.2:
            positional_volume += call_vol
        else:
            churn_volume += call_vol
        if eff_put > 0.2:
            positional_volume += put_vol
        else:
            churn_volume += put_vol
    total = positional_volume + churn_volume
    pos_share = (positional_volume / total) if total > 0 else 0.0
    churn_share = (churn_volume / total) if total > 0 else 0.0
    strength = min(1.0, abs(pos_share - churn_share))
    state = "MIXED"
    if pos_share > 0.6:
        state = "POSITIONAL_DOMINANT"
    elif churn_share > 0.6:
        state = "CHURN_DOMINANT"
    best_score = float("-inf")
    best_strike = _find_closest_strike(chain, spot_price)
    for data in chain:
        call_delta_oi = max(0.0, _cmd(data)["oi"] - _cmd(data)["prev_oi"])
        put_delta_oi = max(0.0, _pmd(data)["oi"] - _pmd(data)["prev_oi"])
        score = call_delta_oi + put_delta_oi
        if score > best_score:
            best_score = score
            best_strike = data["strike_price"]
    return {
        "positional_volume_share": pos_share,
        "churn_volume_share": churn_share,
        "strength": strength,
        "state": state,
        "top_magnet_band": _band(best_strike, best_strike),
    }


def _compute_dealer_hedge_pressure(chain: list[dict[str, Any]], spot_price: float) -> dict[str, Any]:
    net_call_delta = 0.0
    net_put_delta = 0.0
    weighted_strike_sum = 0.0
    weight_sum = 0.0
    s = max(spot_price, 1.0)
    for data in chain:
        strike = data["strike_price"]
        call_g = _cg(data)
        put_g = _pg(data)
        call_md = _cmd(data)
        put_md = _pmd(data)
        moneyness_weight = math.exp(-abs(strike - spot_price) / s)
        net_call_delta += call_md["oi"] * call_g["delta"] * moneyness_weight
        net_put_delta += put_md["oi"] * put_g["delta"] * moneyness_weight
        weighted_strike_sum += strike * moneyness_weight
        weight_sum += moneyness_weight
    net_exposure = net_call_delta + net_put_delta
    if net_exposure > 0:
        state = "MOMENTUM_REINFORCEMENT_UP"
    elif net_exposure < 0:
        state = "MOMENTUM_REINFORCEMENT_DOWN"
    else:
        state = "LOW_HEDGE_PRESSURE"
    return {
        "net_public_call_delta": net_call_delta,
        "net_public_put_delta": net_put_delta,
        "net_dealer_delta_sensitivity": abs(net_exposure),
        "moneyness_weighted_center": (weighted_strike_sum / weight_sum) if weight_sum > 0.0 else spot_price,
        "state": state,
        "strength": min(1.0, abs(net_exposure) / max(spot_price, 1.0)),
    }


def _compute_oi_center_of_gravity(chain: list[dict[str, Any]], spot_price: float) -> dict[str, Any]:
    total_oi = 0.0
    weighted_strike = 0.0
    for data in chain:
        t = _cmd(data)["oi"] + _pmd(data)["oi"]
        total_oi += t
        weighted_strike += t * data["strike_price"]
    cog = (weighted_strike / total_oi) if total_oi > 0.0 else spot_price
    distance = cog - spot_price
    if distance > 0:
        state = "COG_ABOVE_SPOT"
    elif distance < 0:
        state = "COG_BELOW_SPOT"
    else:
        state = "STATIC"
    return {
        "cog_strike": cog,
        "distance_from_spot": distance,
        "drift_points": abs(distance),
        "state": state,
        "strength": min(1.0, abs(distance) / max(spot_price, 1.0)),
    }


def _compute_convexity_asymmetry(chain: list[dict[str, Any]], spot_price: float) -> dict[str, Any]:
    atm_call_oi = 0.0
    atm_put_oi = 0.0
    otm_call_oi = 0.0
    otm_put_oi = 0.0
    total_call_oi = 0.0
    total_put_oi = 0.0
    atm_band = spot_price * 0.01
    for data in chain:
        strike = data["strike_price"]
        call_oi = _cmd(data)["oi"]
        put_oi = _pmd(data)["oi"]
        total_call_oi += call_oi
        total_put_oi += put_oi
        if abs(strike - spot_price) <= atm_band:
            atm_call_oi += call_oi
            atm_put_oi += put_oi
        elif strike < spot_price:
            otm_put_oi += put_oi
        else:
            otm_call_oi += call_oi
    atm_call_share = (atm_call_oi / total_call_oi) if total_call_oi > 0.0 else 0.0
    atm_put_share = (atm_put_oi / total_put_oi) if total_put_oi > 0.0 else 0.0
    otm_call_share = (otm_call_oi / total_call_oi) if total_call_oi > 0.0 else 0.0
    otm_put_share = (otm_put_oi / total_put_oi) if total_put_oi > 0.0 else 0.0
    state = "BALANCED"
    strength = 0.0
    if otm_put_share > 0.25:
        state = "TAIL_RISK_PUT_DEMAND"
        strength = otm_put_share
    elif atm_call_share > 0.4 and otm_call_share < 0.2:
        state = "ATM_CALL_DOMINANCE"
        strength = atm_call_share
    farthest = max(chain, key=lambda o: abs(o["strike_price"] - spot_price))
    return {
        "atm_call_oi_share": atm_call_share,
        "atm_put_oi_share": atm_put_share,
        "otm_call_oi_share": otm_call_share,
        "otm_put_oi_share": otm_put_share,
        "state": state,
        "strength": min(1.0, strength),
        "dominant_wing_band": _band(farthest["strike_price"], farthest["strike_price"]),
    }


def _compute_liquidity_void(chain: list[dict[str, Any]], spot_price: float) -> dict[str, Any]:
    max_oi = 0.0
    for data in chain:
        total_oi = _cmd(data)["oi"] + _pmd(data)["oi"]
        if total_oi > max_oi:
            max_oi = total_oi
    void_above_from = float("nan")
    void_above_to = float("nan")
    void_below_from = float("nan")
    void_below_to = float("nan")
    cluster_from = float("nan")
    cluster_to = float("nan")
    for data in chain:
        strike = data["strike_price"]
        total_oi = _cmd(data)["oi"] + _pmd(data)["oi"]
        pct = (total_oi / max_oi) if max_oi > 0.0 else 0.0
        if pct < 0.2:
            if strike > spot_price:
                if math.isnan(void_above_from):
                    void_above_from = strike
                void_above_to = strike
            else:
                if math.isnan(void_below_from):
                    void_below_from = strike
                void_below_to = strike
        elif pct > 0.7:
            if math.isnan(cluster_from):
                cluster_from = strike
            cluster_to = strike
    if not math.isnan(void_above_from):
        vstate = "VOID_ABOVE_SPOT"
    elif not math.isnan(void_below_from):
        vstate = "VOID_BELOW_SPOT"
    else:
        vstate = "NO_SIGNIFICANT_VOID"
    return {
        "state": vstate,
        "strength": 0.5,
        "void_above_spot": _band(void_above_from, void_above_to) if not math.isnan(void_above_from) else None,
        "void_below_spot": _band(void_below_from, void_below_to) if not math.isnan(void_below_from) else None,
        "top_high_oi_cluster": _band(cluster_from, cluster_to) if not math.isnan(cluster_from) else None,
    }


def _compute_strike_roll(chain: list[dict[str, Any]]) -> dict[str, Any]:
    best_from = float("nan")
    best_to = float("nan")
    best_magnitude = 0.0
    for i, from_row in enumerate(chain):
        from_delta_oi = _cmd(from_row)["oi"] - _cmd(from_row)["prev_oi"]
        if from_delta_oi < -0.0:
            for j, to_row in enumerate(chain):
                if i == j:
                    continue
                to_delta_oi = _cmd(to_row)["oi"] - _cmd(to_row)["prev_oi"]
                if to_delta_oi > 0.0:
                    mag = min(abs(from_delta_oi), to_delta_oi)
                    if mag > best_magnitude:
                        best_magnitude = mag
                        best_from = from_row["strike_price"]
                        best_to = to_row["strike_price"]
    if best_magnitude == 0.0:
        return {"state": "NONE", "strength": 0.0, "from_strike": None, "to_strike": None, "side": "CALL"}
    return {
        "from_strike": best_from,
        "to_strike": best_to,
        "state": "UPWARD_CALL_ROLL" if best_to > best_from else "DOWNWARD_CALL_ROLL",
        "side": "CALL",
        "strength": min(1.0, best_magnitude / 100000.0),
    }


def _compute_skew_responsiveness(chain: list[dict[str, Any]], spot_price: float) -> dict[str, Any]:
    sum_call_num = 0.0
    sum_call_den = 0.0
    sum_put_num = 0.0
    sum_put_den = 0.0
    s = max(spot_price, 1.0)
    for data in chain:
        m = (data["strike_price"] - spot_price) / s
        sum_call_num += m * _cg(data)["iv"]
        sum_call_den += m * m
        sum_put_num += m * _pg(data)["iv"]
        sum_put_den += m * m
    call_slope = (sum_call_num / sum_call_den) if sum_call_den != 0.0 else 0.0
    put_slope = (sum_put_num / sum_put_den) if sum_put_den != 0.0 else 0.0
    price_change = float(chain[0].get("underlying_spot_price") or spot_price) - _cmd(chain[0])["close_price"]
    if price_change > 0:
        price_move = "UP"
    elif price_change < 0:
        price_move = "DOWN"
    else:
        price_move = "FLAT"
    state = "NEUTRAL"
    if price_move == "DOWN" and put_slope > 0.05:
        state = "CONFIRMING"
    elif price_move == "DOWN" and put_slope <= 0.0:
        state = "DIVERGING"
    elif price_move == "UP" and call_slope > 0.05:
        state = "CHASE_RISK"
    return {
        "call_skew_slope": call_slope,
        "put_skew_slope": put_slope,
        "price_move": price_move,
        "state": state,
        "strength": min(1.0, abs(call_slope) + abs(put_slope)),
    }


def _compute_dealer_neutral_corridor(chain: list[dict[str, Any]], spot_price: float) -> dict[str, Any]:
    lower = spot_price
    upper = spot_price
    for data in chain:
        net = _cg(data)["delta"] + _pg(data)["delta"]
        if abs(net) < 0.05:
            k = data["strike_price"]
            if k < lower:
                lower = k
            if k > upper:
                upper = k
    return {
        "lower_bound": lower,
        "upper_bound": upper,
        "state": "NARROW" if (upper - lower) <= (spot_price * 0.02) else "WIDE",
        "strength": min(1.0, (upper - lower) / spot_price if spot_price > 0 else 0.0),
    }


def _compute_intrinsic_dominance(chain: list[dict[str, Any]], spot_price: float) -> dict[str, Any]:
    intrinsic_oi = 0.0
    total_oi = 0.0
    for data in chain:
        strike = data["strike_price"]
        call_intrinsic = max(0.0, spot_price - strike)
        put_intrinsic = max(0.0, strike - spot_price)
        coi = _cmd(data)["oi"]
        poi = _pmd(data)["oi"]
        if call_intrinsic > 0.15 * strike:
            intrinsic_oi += coi
        if put_intrinsic > 0.15 * strike:
            intrinsic_oi += poi
        total_oi += coi + poi
    share = (intrinsic_oi / total_oi) if total_oi > 0.0 else 0.0
    return {
        "intrinsic_oi_share": share,
        "state": "INTRINSIC_DOMINANT" if share > 0.4 else "PREMIUM_DOMINANT",
        "strength": min(1.0, share),
    }


def _compute_strike_defense_failure(chain: list[dict[str, Any]], spot_price: float) -> dict[str, Any]:
    max_call_oi = 0.0
    level_strike = spot_price
    level_md: dict[str, Any] | None = None
    for data in chain:
        call_md = _cmd(data)
        if call_md["oi"] > max_call_oi:
            max_call_oi = call_md["oi"]
            level_strike = data["strike_price"]
            level_md = call_md
    if level_md is None:
        return {"state": "NONE", "strength": 0.0, "failed_strike": None, "side": None}
    delta_oi = level_md["oi"] - level_md["prev_oi"]
    if spot_price > level_strike and delta_oi < 0:
        return {
            "state": "RESISTANCE_FAILURE",
            "failed_strike": level_strike,
            "side": "CALL",
            "strength": min(1.0, abs(delta_oi) / max(max_call_oi, 1.0)),
        }
    if spot_price < level_strike and delta_oi < 0:
        return {
            "state": "SUPPORT_FAILURE",
            "failed_strike": level_strike,
            "side": "PUT",
            "strength": min(1.0, abs(delta_oi) / max(max_call_oi, 1.0)),
        }
    return {"state": "NONE", "strength": 0.0, "failed_strike": None, "side": None}


def _compute_participant_trap(chain: list[dict[str, Any]], spot_price: float) -> dict[str, Any]:
    upper_from = float("nan")
    upper_to = float("nan")
    lower_from = float("nan")
    lower_to = float("nan")
    for data in chain:
        strike = data["strike_price"]
        call_delta_oi = _cmd(data)["oi"] - _cmd(data)["prev_oi"]
        put_delta_oi = _pmd(data)["oi"] - _pmd(data)["prev_oi"]
        if strike > spot_price * 1.03 and call_delta_oi > 0:
            if math.isnan(upper_from):
                upper_from = strike
            upper_to = strike
        if strike < spot_price * 0.97 and put_delta_oi > 0:
            if math.isnan(lower_from):
                lower_from = strike
            lower_to = strike
    if not math.isnan(upper_from):
        state = "RETAIL_SHORT_OTM_TRAP_UP"
    elif not math.isnan(lower_from):
        state = "RETAIL_SHORT_OTM_TRAP_DOWN"
    else:
        state = "NONE"
    return {
        "state": state,
        "strength": 0.5,
        "retail_short_zone": _band(upper_from, upper_to) if not math.isnan(upper_from) else None,
        "institutional_wing_zone": _band(lower_from, lower_to) if not math.isnan(lower_from) else None,
    }


def _compute_volatility_supply_exhaustion(chain: list[dict[str, Any]], spot_price: float) -> dict[str, Any]:
    atm_strike = _find_closest_strike(chain, spot_price)
    atm_call_delta_oi = 0.0
    atm_put_delta_oi = 0.0
    for data in chain:
        if _same_strike(data["strike_price"], atm_strike):
            atm_call_delta_oi = _cmd(data)["oi"] - _cmd(data)["prev_oi"]
            atm_put_delta_oi = _pmd(data)["oi"] - _pmd(data)["prev_oi"]
            break
    exhaustion_score = (
        0.7
        if (
            abs(atm_call_delta_oi) < 0.05 * max(1.0, atm_call_delta_oi)
            and abs(atm_put_delta_oi) < 0.05 * max(1.0, atm_put_delta_oi)
        )
        else 0.0
    )
    return {
        "exhaustion_score": exhaustion_score,
        "state": "POTENTIAL_VOL_BREAKOUT" if exhaustion_score > 0.5 else "SUPPLY_INTACT",
        "strength": exhaustion_score,
    }


def _compute_calendar_conflict(chain: list[dict[str, Any]], spot_price: float) -> dict[str, Any]:
    """Near-ATM vs far-OTM OI positioning asymmetry (single-expiry proxy)."""
    near_call_oi = 0.0
    near_put_oi = 0.0
    far_call_oi = 0.0
    far_put_oi = 0.0
    near_band = spot_price * 0.02
    far_threshold = spot_price * 0.03

    for data in chain:
        strike = data["strike_price"]
        dist = abs(strike - spot_price)
        c_oi = _cmd(data)["oi"]
        p_oi = _pmd(data)["oi"]
        if dist <= near_band:
            near_call_oi += c_oi
            near_put_oi += p_oi
        elif dist >= far_threshold:
            far_call_oi += c_oi
            far_put_oi += p_oi

    near_total = near_call_oi + near_put_oi
    far_total = far_call_oi + far_put_oi
    if near_total == 0 or far_total == 0:
        return {"state": "INCONCLUSIVE", "strength": 0.0}

    near_call_share = near_call_oi / near_total
    far_call_share = far_call_oi / far_total

    divergence = abs(near_call_share - far_call_share)
    near_bullish = near_put_oi > near_call_oi
    far_bullish = far_put_oi > far_call_oi

    if (near_bullish and far_bullish) or (not near_bullish and not far_bullish):
        state = "ALIGNED"
    elif divergence > 0.15:
        state = "CONFLICTING"
    else:
        state = "INCONCLUSIVE"

    return {
        "state": state,
        "strength": min(1.0, divergence * 2),
        "near_call_share": round(near_call_share, 4),
        "far_call_share": round(far_call_share, 4),
    }


def _compute_synthetic_forward_distortion(chain: list[dict[str, Any]], spot_price: float) -> dict[str, Any]:
    """Put-call parity check: synthetic forward vs spot at ATM strikes."""
    atm_strike = _find_closest_strike(chain, spot_price)
    atm_band = spot_price * 0.01

    distortions: list[float] = []
    for data in chain:
        strike = data["strike_price"]
        if abs(strike - atm_strike) <= atm_band:
            call_ltp = _cmd(data)["ltp"]
            put_ltp = _pmd(data)["ltp"]
            if call_ltp > 0 or put_ltp > 0:
                synthetic_fwd = call_ltp - put_ltp + strike
                distortion = (synthetic_fwd - spot_price) / spot_price if spot_price > 0 else 0.0
                distortions.append(distortion)

    if not distortions:
        return {"state": "NEAR_PARITY", "strength": 0.0, "avg_distortion": 0.0}

    avg_distortion = sum(distortions) / len(distortions)

    if avg_distortion > 0.002:
        state = "FORWARD_PREMIUM"
    elif avg_distortion < -0.002:
        state = "FORWARD_DISCOUNT"
    else:
        state = "NEAR_PARITY"

    return {
        "state": state,
        "strength": min(1.0, abs(avg_distortion) * 100),
        "avg_distortion": round(avg_distortion, 6),
        "samples": len(distortions),
    }
