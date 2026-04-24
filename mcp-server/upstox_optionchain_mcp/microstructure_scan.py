"""Orchestrator: full 7-layer microstructure scan in a single call."""

from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Any

from upstox_optionchain_mcp.chain_parse import normalize_row, parse_chain_json, spot_from_chain
from upstox_optionchain_mcp.cross_market import compute_cross_market
from upstox_optionchain_mcp.date_utils import get_expiry_string_like_java
from upstox_optionchain_mcp.feature_pipeline import compute_feature_bundle
from upstox_optionchain_mcp.liquidity import compute_liquidity
from upstox_optionchain_mcp.order_book import compute_order_book_structure
from upstox_optionchain_mcp.order_flow import compute_order_flow
from upstox_optionchain_mcp.pcr_maxpain import compute_pcr_maxpain
from upstox_optionchain_mcp.session_regime import compute_session_regime
from upstox_optionchain_mcp.upstox_api import (
    fetch_full_market_quote,
    fetch_historical_candles,
    fetch_intraday_candles,
    fetch_ohlc_quotes,
    fetch_option_chain,
)
from upstox_optionchain_mcp.vwap_profile import compute_vwap_profile


def _sanitize(obj: Any) -> Any:
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    return obj


def _extract_candles(resp: dict[str, Any]) -> list[list]:
    return (resp.get("data") or {}).get("candles") or []


def _first_quote(resp: dict[str, Any]) -> dict[str, Any]:
    """Return the first instrument's quote from a market-quote response."""
    data = resp.get("data") or {}
    if isinstance(data, dict):
        for val in data.values():
            if isinstance(val, dict):
                return val
    return {}


def run_scan(
    instrument_key: str,
    expiry_date: str | None = None,
    related_symbols: list[str] | None = None,
) -> dict[str, Any]:
    """Execute the full 7-layer microstructure scan.

    Returns a dict with per-layer results, raw/adjusted scores, and the Tier-1
    feature bundle.
    """
    expiry = (expiry_date or "").strip() or get_expiry_string_like_java()
    layers: dict[str, Any] = {}
    errors: list[str] = []

    # --- 1. Option chain (Layer 4 + existing Tier-1) ---
    try:
        chain_resp = fetch_option_chain(expiry, instrument_key)
        import json
        chain_json = json.dumps(chain_resp, default=str)
        tier1_bundle = compute_feature_bundle(chain_json)

        raw_rows = parse_chain_json(chain_json)
        chain = [normalize_row(r) for r in raw_rows]
        spot = spot_from_chain(chain)

        l4 = compute_pcr_maxpain(chain, spot)
        layers["L4"] = l4
    except Exception as e:
        errors.append(f"option_chain: {e}")
        chain_json = ""
        tier1_bundle = {}
        spot = 0.0
        chain = []
        layers["L4"] = {"layer": "L4_OPTION_CHAIN", "signal": "NEUTRAL", "points": 0, "meta": {"error": str(e)}}

    # --- 2. Full market quote (Layer 1 + Layer 3 depth) ---
    quote_data: dict[str, Any] = {}
    try:
        quote_resp = fetch_full_market_quote([instrument_key])
        quote_data = _first_quote(quote_resp)
        l1 = compute_order_book_structure(quote_data)
        layers["L1"] = l1
    except Exception as e:
        errors.append(f"market_quote: {e}")
        layers["L1"] = {"layer": "L1_ORDER_BOOK", "signal": "NEUTRAL", "points": 0, "meta": {"error": str(e)}}

    # --- 3. Intraday candles (Layer 2 + Layer 5 + Layer 7 input) ---
    intraday_candles: list[list] = []
    try:
        intraday_resp = fetch_intraday_candles(instrument_key, "1minute")
        intraday_candles = _extract_candles(intraday_resp)

        l2 = compute_order_flow(intraday_candles)
        layers["L2"] = l2

        ltp = float(quote_data.get("last_price", 0) or 0)
        atp = float(quote_data.get("average_price", 0) or 0)
        l5 = compute_vwap_profile(intraday_candles, ltp, atp)
        layers["L5"] = l5
    except Exception as e:
        errors.append(f"intraday_candles: {e}")
        layers.setdefault("L2", {"layer": "L2_ORDER_FLOW", "signal": "NEUTRAL", "points": 0, "meta": {"error": str(e)}})
        layers.setdefault("L5", {"layer": "L5_VWAP_PROFILE", "signal": "NEUTRAL", "points": 0, "meta": {"error": str(e)}})

    # --- 4. Historical candles -> avg daily volume for RVOL ---
    avg_daily_volume = 0.0
    try:
        today = date.today()
        from_dt = (today - timedelta(days=30)).isoformat()
        to_dt = today.isoformat()
        hist_resp = fetch_historical_candles(instrument_key, "day", to_dt, from_dt)
        hist_candles = _extract_candles(hist_resp)
        if hist_candles:
            avg_daily_volume = sum(float(c[5]) for c in hist_candles) / len(hist_candles)
    except Exception as e:
        errors.append(f"historical_candles: {e}")

    # --- Layer 3: Liquidity (needs depth + volumes) ---
    try:
        session_volume = sum(float(c[5]) for c in intraday_candles) if intraday_candles else 0
        vol_share = 0.3  # rough first-hour default
        expected_vol = avg_daily_volume * vol_share if avg_daily_volume > 0 else max(session_volume, 1)
        l3 = compute_liquidity(quote_data, session_volume, expected_vol)
        layers["L3"] = l3
    except Exception as e:
        errors.append(f"liquidity: {e}")
        layers.setdefault("L3", {"layer": "L3_LIQUIDITY", "signal": "NEUTRAL", "points": 0, "meta": {"error": str(e)}})

    # --- 5. Cross-market divergence (Layer 6) ---
    if related_symbols:
        try:
            all_syms = [instrument_key] + related_symbols
            ohlc_resp = fetch_ohlc_quotes(all_syms)
            ohlc_data = ohlc_resp.get("data") or {}
            l6 = compute_cross_market(ohlc_data, instrument_key)
            layers["L6"] = l6
        except Exception as e:
            errors.append(f"cross_market: {e}")
            layers["L6"] = {"layer": "L6_CROSS_MARKET", "signal": "NEUTRAL", "points": 0, "meta": {"error": str(e)}}
    else:
        layers["L6"] = {"layer": "L6_CROSS_MARKET", "signal": "NEUTRAL", "points": 0, "meta": {"reason": "no_related_symbols_provided"}}

    # --- 6. Session regime (Layer 7) ---
    try:
        l7 = compute_session_regime(intraday_candles, avg_daily_volume)
        layers["L7"] = l7
    except Exception as e:
        errors.append(f"session_regime: {e}")
        layers["L7"] = {"layer": "L7_SESSION_REGIME", "multiplier": 0.75, "regime": "UNKNOWN", "meta": {"error": str(e)}}

    # --- Aggregate ---
    raw_score = sum(layers.get(k, {}).get("points", 0) for k in ["L1", "L2", "L3", "L4", "L5", "L6"])
    multiplier = layers.get("L7", {}).get("multiplier", 1.0)
    adjusted_score = round(raw_score * multiplier, 2)

    if adjusted_score >= 8:
        verdict = "STRONG_BULLISH"
    elif adjusted_score >= 5:
        verdict = "BULLISH"
    elif adjusted_score >= 3:
        verdict = "LEAN_BULLISH"
    elif adjusted_score <= -8:
        verdict = "STRONG_BEARISH"
    elif adjusted_score <= -5:
        verdict = "BEARISH"
    elif adjusted_score <= -3:
        verdict = "LEAN_BEARISH"
    else:
        verdict = "NO_SETUP"

    return _sanitize({
        "instrument_key": instrument_key,
        "expiry": expiry,
        "spot": spot,
        "raw_score": raw_score,
        "adjusted_score": adjusted_score,
        "multiplier": multiplier,
        "verdict": verdict,
        "layers": layers,
        "tier1_signals": tier1_bundle.get("tier1_signals") if tier1_bundle else [],
        "errors": errors if errors else None,
    })
