"""Layer 1: Order Book Structure Analysis -- L2 depth imbalance, spread, walls."""

from __future__ import annotations

from typing import Any


_LEVEL_WEIGHTS = [5, 4, 3, 2, 1]


def compute_order_book_structure(quote_data: dict[str, Any]) -> dict[str, Any]:
    """Analyse 5-level bid/ask depth from a full market quote.

    *quote_data* is the per-instrument object returned by
    ``GET /market-quote/quotes`` (must contain ``depth.buy`` and
    ``depth.sell`` arrays of 5 levels each with *quantity*, *price*, *orders*).
    """
    depth = quote_data.get("depth") or {}
    bids: list[dict] = depth.get("buy") or []
    asks: list[dict] = depth.get("sell") or []

    if not bids or not asks:
        return _neutral("no_depth_data")

    best_bid_qty = _qty(bids[0])
    best_ask_qty = _qty(asks[0])
    best_bid_price = _price(bids[0])
    best_ask_price = _price(asks[0])

    # --- L1 imbalance ---
    denom = best_bid_qty + best_ask_qty
    l1_imbalance = (best_bid_qty - best_ask_qty) / denom if denom else 0.0

    # --- Weighted Book Imbalance across 5 levels ---
    weighted_bid = sum(_qty(bids[i]) * _LEVEL_WEIGHTS[i] for i in range(min(len(bids), 5)))
    weighted_ask = sum(_qty(asks[i]) * _LEVEL_WEIGHTS[i] for i in range(min(len(asks), 5)))
    wbi_denom = weighted_bid + weighted_ask
    wbi = (weighted_bid - weighted_ask) / wbi_denom if wbi_denom else 0.0

    # --- Spread ---
    midpoint = (best_ask_price + best_bid_price) / 2.0 if (best_ask_price + best_bid_price) else 1.0
    spread = best_ask_price - best_bid_price
    spread_bps = (spread / midpoint) * 10_000 if midpoint else 0.0

    # --- Walls (qty > 3x average level qty) ---
    all_bid_qtys = [_qty(b) for b in bids[:5]]
    all_ask_qtys = [_qty(a) for a in asks[:5]]
    avg_level_qty = (sum(all_bid_qtys) + sum(all_ask_qtys)) / max(len(all_bid_qtys) + len(all_ask_qtys), 1)
    wall_threshold = avg_level_qty * 3.0

    bid_walls = [
        {"price": _price(bids[i]), "quantity": _qty(bids[i])}
        for i in range(min(len(bids), 5))
        if _qty(bids[i]) > wall_threshold
    ]
    ask_walls = [
        {"price": _price(asks[i]), "quantity": _qty(asks[i])}
        for i in range(min(len(asks), 5))
        if _qty(asks[i]) > wall_threshold
    ]

    # --- Order count analysis (institutional = high qty/orders ratio) ---
    institutional_levels: list[dict] = []
    for side_label, levels in [("bid", bids[:5]), ("ask", asks[:5])]:
        for lv in levels:
            orders = _orders(lv)
            qty = _qty(lv)
            if orders > 0 and qty / orders > 50:
                institutional_levels.append(
                    {"side": side_label, "price": _price(lv), "qty_per_order": round(qty / orders, 1)}
                )

    # --- Scoring ---
    has_ask_wall_near_best = any(w["price"] <= best_ask_price * 1.002 for w in ask_walls)
    has_bid_wall_near_best = any(w["price"] >= best_bid_price * 0.998 for w in bid_walls)

    if wbi > 0.4 and l1_imbalance > 0.3 and not has_ask_wall_near_best:
        signal, points = "BULLISH", 2
    elif wbi > 0.2 or l1_imbalance > 0.3:
        signal, points = "LEAN_BULLISH", 1
    elif wbi < -0.4 and l1_imbalance < -0.3 and not has_bid_wall_near_best:
        signal, points = "BEARISH", -2
    elif wbi < -0.2 or l1_imbalance < -0.3:
        signal, points = "LEAN_BEARISH", -1
    else:
        signal, points = "NEUTRAL", 0

    return {
        "layer": "L1_ORDER_BOOK",
        "signal": signal,
        "points": points,
        "meta": {
            "l1_imbalance": round(l1_imbalance, 4),
            "weighted_book_imbalance": round(wbi, 4),
            "spread": round(spread, 2),
            "spread_bps": round(spread_bps, 2),
            "bid_walls": bid_walls,
            "ask_walls": ask_walls,
            "institutional_levels": institutional_levels,
        },
    }


def _neutral(reason: str) -> dict[str, Any]:
    return {"layer": "L1_ORDER_BOOK", "signal": "NEUTRAL", "points": 0, "meta": {"reason": reason}}


def _qty(level: dict) -> float:
    v = level.get("quantity", 0)
    if isinstance(v, dict):
        return 0.0
    return float(v or 0)


def _price(level: dict) -> float:
    v = level.get("price", 0)
    if isinstance(v, dict):
        return 0.0
    return float(v or 0)


def _orders(level: dict) -> int:
    v = level.get("orders", 0)
    if isinstance(v, dict):
        return 0
    return int(v or 0)
