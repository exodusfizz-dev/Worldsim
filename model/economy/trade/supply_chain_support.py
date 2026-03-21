"""Utility helpers for supply-chain market signal and history handling."""

from __future__ import annotations

from statistics import median

from model.economy.trade.supply_chain_types import SingleHistoryItem


def build_market_signal(
    history: dict[str, list[SingleHistoryItem]],
    good: str,
    predicted_supply_risk: float,
) -> dict[str, float]:
    """Build a robust signal bundle for one good from rolling history."""
    series = history.get(good, [])
    if not series:
        return {
            "top_bid": 0.0,
            "top_ask": 0.0,
            "agreed_price": 0.0,
            "reference_price": 0.0,
            "predicted_supply_risk": predicted_supply_risk,
        }

    latest = series[-1]
    tail = series[-12:]
    refs: list[float] = []
    for item in tail:
        if item.agreed_price > 0:
            refs.append(item.agreed_price)
        elif item.top_bid > 0 and item.top_ask > 0:
            refs.append((item.top_bid + item.top_ask) / 2.0)
        elif item.top_ask > 0:
            refs.append(item.top_ask * 0.9)
        elif item.top_bid > 0:
            refs.append(item.top_bid)
    reference_price = median(refs) if refs else 0.0
    return {
        "top_bid": latest.top_bid,
        "top_ask": latest.top_ask,
        "agreed_price": latest.agreed_price,
        "reference_price": reference_price,
        "predicted_supply_risk": predicted_supply_risk,
    }


def compute_fill_ratio(
    start_quantities: dict[tuple[int, str], float],
    remaining_quantities: dict[tuple[int, str], float],
) -> dict[tuple[int, str], float]:
    """Compute fill ratio per keyed order family."""
    result: dict[tuple[int, str], float] = {}
    for key, start_qty in start_quantities.items():
        remaining = remaining_quantities.get(key, 0.0)
        filled = max(start_qty - remaining, 0.0)
        result[key] = filled / start_qty if start_qty > 0 else 1.0
    return result


def build_dense_history_entries(
    *,
    known_goods: set[str],
    buy_orders: list,
    sell_orders: list,
    market_snapshot: dict[str, dict[str, float]],
    trade_summary: dict[str, dict[str, float]],
    tick_count: int,
) -> dict[str, SingleHistoryItem]:
    """Build one history entry per known good for the current tick."""
    entries: dict[str, SingleHistoryItem] = {}
    goods = sorted(known_goods | set(market_snapshot) | set(trade_summary))
    for item in goods:
        snapshot = market_snapshot.get(item, {})
        top_bid = snapshot.get(
            "top_bid",
            max((order.price for order in buy_orders if order.item == item), default=0.0),
        )
        top_ask = snapshot.get(
            "top_ask",
            min((order.price for order in sell_orders if order.item == item), default=0.0),
        )
        summary = trade_summary.get(item, {"quantity": 0.0, "value": 0.0})
        quantity = summary["quantity"]
        agreed_price = summary["value"] / quantity if quantity > 0 else 0.0
        entries[item] = SingleHistoryItem(
            top_bid=top_bid,
            top_ask=top_ask,
            agreed_price=agreed_price,
            quantity=quantity,
            timestamp=tick_count,
        )
    return entries
