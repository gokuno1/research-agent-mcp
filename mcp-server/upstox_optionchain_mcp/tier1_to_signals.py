"""Map rule_engine output to OptionSignal-shaped dicts (15 Tier-1), mirroring OptionChainSignalServiceImpl.mapLegacySignals."""

from __future__ import annotations

from typing import Any


def legacy_to_signals(legacy: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    if not legacy:
        return result

    ov = legacy.get("oi_velocity")
    if ov:
        meta: dict[str, Any] = {
            "call_delta_pct": ov["call_delta_oi_pct"],
            "put_delta_pct": ov["put_delta_oi_pct"],
            "price_move": ov["price_move"],
            "atm_contraction": ov["atm_contraction_active"],
        }
        tr = ov.get("top_resistance_band")
        if tr:
            meta["resistance_from"] = tr["from"]
            meta["resistance_to"] = tr["to"]
        ts = ov.get("top_support_band")
        if ts:
            meta["support_from"] = ts["from"]
            meta["support_to"] = ts["to"]
        result.append({"name": "OI_VELOCITY", "state": ov["state"], "strength": ov["strength"], "meta": meta})

    ovc = legacy.get("opening_vs_closing")
    if ovc:
        m = {
            "positional_share": ovc["positional_volume_share"],
            "churn_share": ovc["churn_volume_share"],
        }
        mb = ovc.get("top_magnet_band")
        if mb:
            m["magnet_from"] = mb["from"]
            m["magnet_to"] = mb["to"]
        result.append({"name": "OPENING_VS_CLOSING", "state": ovc["state"], "strength": ovc["strength"], "meta": m})

    dhp = legacy.get("dealer_hedge_pressure")
    if dhp:
        result.append(
            {
                "name": "DEALER_HEDGE_PRESSURE",
                "state": dhp["state"],
                "strength": dhp["strength"],
                "meta": {
                    "net_public_call_delta": dhp["net_public_call_delta"],
                    "net_public_put_delta": dhp["net_public_put_delta"],
                    "net_dealer_delta_sensitivity": dhp["net_dealer_delta_sensitivity"],
                    "moneyness_center": dhp["moneyness_weighted_center"],
                },
            }
        )

    cog = legacy.get("oi_center_of_gravity")
    if cog:
        result.append(
            {
                "name": "OI_CENTER_OF_GRAVITY",
                "state": cog["state"],
                "strength": cog["strength"],
                "meta": {
                    "cog_strike": cog["cog_strike"],
                    "distance_from_spot": cog["distance_from_spot"],
                    "drift_points": cog["drift_points"],
                },
            }
        )

    ca = legacy.get("convexity_asymmetry")
    if ca:
        m = {
            "atm_call_share": ca["atm_call_oi_share"],
            "atm_put_share": ca["atm_put_oi_share"],
            "otm_call_share": ca["otm_call_oi_share"],
            "otm_put_share": ca["otm_put_oi_share"],
        }
        dw = ca.get("dominant_wing_band")
        if dw:
            m["dominant_wing_from"] = dw["from"]
            m["dominant_wing_to"] = dw["to"]
        result.append({"name": "CONVEXITY_ASYMMETRY", "state": ca["state"], "strength": ca["strength"], "meta": m})

    lv = legacy.get("liquidity_void")
    if lv:
        m = {}
        va = lv.get("void_above_spot")
        if va:
            m["void_above_from"] = va["from"]
            m["void_above_to"] = va["to"]
        vb = lv.get("void_below_spot")
        if vb:
            m["void_below_from"] = vb["from"]
            m["void_below_to"] = vb["to"]
        cl = lv.get("top_high_oi_cluster")
        if cl:
            m["cluster_from"] = cl["from"]
            m["cluster_to"] = cl["to"]
        result.append({"name": "LIQUIDITY_VOID", "state": lv["state"], "strength": lv["strength"], "meta": m})

    sr = legacy.get("strike_roll")
    if sr:
        result.append(
            {
                "name": "STRIKE_ROLL",
                "state": sr["state"],
                "strength": sr["strength"],
                "meta": {
                    "from_strike": sr.get("from_strike"),
                    "to_strike": sr.get("to_strike"),
                    "side": sr.get("side"),
                },
            }
        )

    cc = legacy.get("calendar_conflict")
    if cc:
        result.append({"name": "CALENDAR_CONFLICT", "state": cc["state"], "strength": cc["strength"], "meta": {}})

    sk = legacy.get("skew_responsiveness")
    if sk:
        result.append(
            {
                "name": "SKEW_RESPONSIVENESS",
                "state": sk["state"],
                "strength": sk["strength"],
                "meta": {
                    "price_move": sk["price_move"],
                    "call_skew_slope": sk["call_skew_slope"],
                    "put_skew_slope": sk["put_skew_slope"],
                },
            }
        )

    dnc = legacy.get("dealer_neutral_corridor")
    if dnc:
        result.append(
            {
                "name": "DEALER_NEUTRAL_CORRIDOR",
                "state": dnc["state"],
                "strength": dnc["strength"],
                "meta": {"lower_bound": dnc["lower_bound"], "upper_bound": dnc["upper_bound"]},
            }
        )

    idom = legacy.get("intrinsic_dominance")
    if idom:
        result.append(
            {
                "name": "INTRINSIC_DOMINANCE",
                "state": idom["state"],
                "strength": idom["strength"],
                "meta": {"intrinsic_oi_share": idom["intrinsic_oi_share"]},
            }
        )

    sdf = legacy.get("strike_defense_failure")
    if sdf:
        m = {}
        if sdf.get("failed_strike") is not None:
            m["failed_strike"] = sdf["failed_strike"]
        if sdf.get("side"):
            m["side"] = sdf["side"]
        result.append({"name": "STRIKE_DEFENSE_FAILURE", "state": sdf["state"], "strength": sdf["strength"], "meta": m})

    sfd = legacy.get("synthetic_forward_distortion")
    if sfd:
        result.append(
            {"name": "SYNTHETIC_FORWARD_DISTORTION", "state": sfd["state"], "strength": sfd["strength"], "meta": {}}
        )

    pt = legacy.get("participant_trap")
    if pt:
        m = {}
        rz = pt.get("retail_short_zone")
        if rz:
            m["retail_short_from"] = rz["from"]
            m["retail_short_to"] = rz["to"]
        iz = pt.get("institutional_wing_zone")
        if iz:
            m["inst_wing_from"] = iz["from"]
            m["inst_wing_to"] = iz["to"]
        result.append({"name": "PARTICIPANT_TRAP", "state": pt["state"], "strength": pt["strength"], "meta": m})

    vse = legacy.get("volatility_supply_exhaustion")
    if vse:
        result.append(
            {
                "name": "VOLATILITY_SUPPLY_EXHAUSTION",
                "state": vse["state"],
                "strength": vse["strength"],
                "meta": {"exhaustion_score": vse["exhaustion_score"]},
            }
        )

    return result
