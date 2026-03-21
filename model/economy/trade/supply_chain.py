"""Continuous double-auction style supply chain market.

This module maintains a persistent order book across ticks:
- Firms submit/update bids (buy orders) for input materials.
- Cities submit/update asks (sell orders) for available inventory.
- Orders are *not* wiped every tick. They are updated in place when the
  participant resubmits, and removed only when the participant no longer wants
  to quote that item (or need falls to zero).

Matching is deterministic and transport-aware. A seller's effective price for a
buyer is:
    effective_ask = quoted_ask + distance(city, firm_city) * energy_cost

History is recorded per good every tick to support adaptive quoting strategies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from model.economy.trade.supply_chain_types import (
    MarketBuyOrder,
    MarketSellOrder,
    SingleHistoryItem,
)
from model.economy.trade.supply_chain_support import (
    build_dense_history_entries,
    build_market_signal,
    compute_fill_ratio,
)

if TYPE_CHECKING:
    from model.city.city import City
    from model.economy.industry.firm import Firm


@dataclass
class MarketState:
    """Mutable market state owned by a country market instance."""

    buy_orders: list[MarketBuyOrder] = field(default_factory=list)
    sell_orders: list[MarketSellOrder] = field(default_factory=list)
    history: dict[str, list[SingleHistoryItem]] = field(default_factory=dict)


class SupplyChain:
    """Persistent-order-book market for trade of commodities."""

    def __init__(
        self,
        firms: list["Firm"],
        cities: list["City"],
        rng,
        city_distances: dict[tuple[int, int], float],
    ):
        self.state = MarketState()
        self.rng = rng
        self.firms = firms
        self.cities = cities
        self.city_distances = city_distances

        # Placeholder energy cost until an energy commodity market exists.
        self.energy_cost = 1.0
        self.distance_fallback = 1000.0
        self.tick_count = 0

        # Per-tick cache used for history writing and adaptive quoting.
        self._last_trade_summary: dict[str, dict[str, float]] = {}
        self._last_market_snapshot: dict[str, dict[str, float]] = {}
        self._last_transport_cost: dict[str, float] = {}

        # Per-agent fill success from the previous tick.
        self._firm_fill_ratio: dict[tuple[int, str], float] = {}
        self._city_fill_ratio: dict[tuple[int, str], float] = {}
        self._firm_bid_gap: dict[tuple[int, str], float] = {}
        self._city_underask_gap: dict[tuple[int, str], float] = {}
        self._known_goods: set[str] = set()

    @classmethod
    def build_from(
        cls,
        rng,
        firms: list,
        cities: list,
        city_distances: dict[tuple[int, int], float],
    ) -> "SupplyChain":
        """Create a market for one country from existing actors."""
        return cls(
            firms=firms,
            cities=cities,
            rng=rng,
            city_distances=city_distances,
        )

    def _distance_between(self, city_id_1: int, city_id_2: int) -> float:
        """Return precomputed city distance, with a conservative fallback."""
        if city_id_1 == city_id_2:
            return 0.0

        pair = tuple(sorted((city_id_1, city_id_2)))
        return self.city_distances.get(pair, self.distance_fallback)

    def _effective_sell_price(self, sell_order: MarketSellOrder, firm: "Firm") -> float:
        """Transport-adjusted ask faced by a specific buyer."""
        distance = self._distance_between(sell_order.city.id, firm.city_id)
        return max(sell_order.price + distance * self.energy_cost, 0.0)

    def _predict_supply_risk(self, good: str) -> float:
        """Return multiplicative risk for near-term supply disruption.
        `1.0` means neutral risk, values above 1.0 increase scarcity pressure.
        """
        #TODO: Replace this stub with a model using geopolitics/weather/shocks (needs these features built first)
        _ = good
        return 1.0

    def _signal_for_good(self, good: str) -> dict[str, float]:
        """Return robust market signal bundle used by buyers/sellers."""
        return build_market_signal(
            history=self.state.history,
            good=good,
            predicted_supply_risk=self._predict_supply_risk(good),
        )

    def _firm_fill_ratio_for(self, firm: "Firm", good: str) -> float:
        """Share of last tick's requested quantity that was filled."""
        return self._firm_fill_ratio.get((id(firm), good), 1.0)

    def _city_fill_ratio_for(self, city: "City", good: str) -> float:
        """Share of last tick's offered quantity that was sold."""
        return self._city_fill_ratio.get((city.id, good), 1.0)

    def _upsert_orders(self) -> None:
        """Refresh quotes while keeping order identity across ticks.

        - if a participant already has an order for an item, update price/amount
        - otherwise create a new order
        - remove quotes for items the participant no longer submits
        """
        existing_buys: dict[tuple[int, str], MarketBuyOrder] = {
            (id(order.firm), order.item): order
            for order in self.state.buy_orders
            if order.shortfall > 0
        }
        existing_sells: dict[tuple[int, str], MarketSellOrder] = {
            (order.city.id, order.item): order
            for order in self.state.sell_orders
            if order.amount > 0
        }

        seen_buy_keys: set[tuple[int, str]] = set()
        seen_sell_keys: set[tuple[int, str]] = set()

        for firm in self.firms:
            if not firm.input_mats:
                continue

            firm_signals = {
                item: self._signal_for_good(item)
                for item in firm.input_mats
            }
            firm_fill = {
                item: self._firm_fill_ratio_for(firm, item)
                for item in firm.input_mats
            }
            firm_feedback = {
                item: {
                    "required_overbid": self._firm_bid_gap.get((id(firm), item), 0.0),
                }
                for item in firm.input_mats
            }

            for intent in firm.good_demand(
                market_signals=firm_signals,
                fill_ratios=firm_fill,
                price_feedback=firm_feedback,
            ):
                key = (id(firm), intent.item)
                seen_buy_keys.add(key)
                self._known_goods.add(intent.item)

                existing = existing_buys.get(key)
                if existing is None:
                    existing_buys[key] = intent
                else:
                    existing.shortfall = intent.shortfall
                    existing.price = intent.price

        for city in self.cities:
            city_items = [item for item, amount in city.inv.items() if amount > 0]
            city_signals = {item: self._signal_for_good(item) for item in city_items}
            city_fill = {item: self._city_fill_ratio_for(city, item) for item in city_items}
            city_feedback = {
                item: {
                    "required_underask": self._city_underask_gap.get((city.id, item), 0.0),
                }
                for item in city_items
            }

            for intent in city.good_supply(
                market_signals=city_signals,
                fill_ratios=city_fill,
                price_feedback=city_feedback,
            ):
                key = (city.id, intent.item)
                seen_sell_keys.add(key)
                self._known_goods.add(intent.item)
                existing = existing_sells.get(key)
                if existing is None:
                    existing_sells[key] = intent
                else:
                    existing.amount = intent.amount
                    existing.price = intent.price

        # Orders not resubmitted are considered cancelled.
        self.state.buy_orders = [
            order for key, order in existing_buys.items()
            if key in seen_buy_keys and order.shortfall > 0
        ]
        self.state.sell_orders = [
            order for key, order in existing_sells.items()
            if key in seen_sell_keys and order.amount > 0
        ]

    def _trade_order(
        self,
        buy_order: MarketBuyOrder,
        sell_order: MarketSellOrder,
        quantity: float,
        price: float,
    ) -> None:
        """Execute one trade transfer, clamping for feasibility/safety."""
        if quantity <= 0:
            return

        available_sell = max(sell_order.amount, 0.0)
        available_buy = max(buy_order.shortfall, 0.0)
        affordable_quantity = buy_order.firm.market_capital / price if price > 0 else quantity
        quantity = min(quantity, available_sell, available_buy, max(affordable_quantity, 0.0))
        if quantity <= 0:
            return

        total_cost = quantity * price
        seller_revenue = quantity * max(sell_order.price, 0.0)
        transport_cost = max(total_cost - seller_revenue, 0.0)
        buyer_total = seller_revenue + transport_cost
        buyer = buy_order.firm
        seller = sell_order.city

        seller.inv.setdefault(sell_order.item, 0.0)
        buyer.inv.setdefault(buy_order.item, 0.0)

        seller.inv[sell_order.item] = max(seller.inv[sell_order.item] - quantity, 0.0)
        buyer.inv[buy_order.item] += quantity
        seller.state.treasury += seller_revenue
        buyer.market_capital = max(buyer.market_capital - buyer_total, 0.0)

        buy_order.shortfall = max(buy_order.shortfall - quantity, 0.0)
        sell_order.amount = max(sell_order.amount - quantity, 0.0)

        summary = self._last_trade_summary.setdefault(
            buy_order.item,
            {"quantity": 0.0, "value": 0.0},
        )
        summary["quantity"] += quantity
        summary["value"] += buyer_total
        self._last_transport_cost[buy_order.item] = self._last_transport_cost.get(buy_order.item, 0.0) + transport_cost

    def tick(self) -> None:
        """One market step: refresh quotes, match, record history, advance clock."""
        self._last_trade_summary = {}
        self._last_market_snapshot = {}
        self._last_transport_cost = {}

        self._upsert_orders()
        self.match_orders()
        self.record_history()

        self.tick_count += 1

    def match_orders(self) -> None:
        """Price-time style matching by item.

        Matching process per good:
        - sort bids descending by price
        - for each bid, sort asks by effective transport-adjusted price
        - execute whenever bid >= effective ask

        Also computes fill-ratios per participant for adaptive quoting next tick.
        """
        buy_orders_by_item: dict[str, list[MarketBuyOrder]] = {}
        sell_orders_by_item: dict[str, list[MarketSellOrder]] = {}
        self._firm_bid_gap = {}
        self._city_underask_gap = {}

        buy_start_qty: dict[tuple[int, str], float] = {}
        sell_start_qty: dict[tuple[int, str], float] = {}

        for order in self.state.buy_orders:
            if order.shortfall <= 0:
                continue
            key = (id(order.firm), order.item)
            buy_start_qty[key] = order.shortfall
            buy_orders_by_item.setdefault(order.item, []).append(order)

        for order in self.state.sell_orders:
            if order.amount <= 0:
                continue
            key = (order.city.id, order.item)
            sell_start_qty[key] = order.amount
            sell_orders_by_item.setdefault(order.item, []).append(order)

        items = sorted(set(buy_orders_by_item) | set(sell_orders_by_item))

        for item in items:
            buys = sorted(
                buy_orders_by_item.get(item, []),
                key=lambda order: (-order.price, order.firm.city_id, id(order.firm)),
            )
            sells = sell_orders_by_item.get(item, [])

            top_bid = max((order.price for order in buys), default=0.0)
            if buys and sells:
                top_ask = min(
                    self._effective_sell_price(sell_order, buy_order.firm)
                    for buy_order in buys
                    for sell_order in sells
                )
            else:
                top_ask = min((max(order.price, 0.0) for order in sells), default=0.0)

            self._last_market_snapshot[item] = {
                "top_bid": top_bid,
                "top_ask": top_ask,
            }

            for buy_order in buys:
                if buy_order.shortfall <= 0:
                    continue

                candidate_sells = sorted(
                    (sell_order for sell_order in sells if sell_order.amount > 0),
                    key=lambda sell_order: (
                        self._effective_sell_price(sell_order, buy_order.firm),
                        sell_order.city.id,
                    ),
                )
                if candidate_sells:
                    best_effective = self._effective_sell_price(candidate_sells[0], buy_order.firm)
                    key = (id(buy_order.firm), item)
                    self._firm_bid_gap[key] = max(best_effective - buy_order.price, 0.0)

                for sell_order in candidate_sells:
                    if buy_order.shortfall <= 0:
                        break

                    effective_price = self._effective_sell_price(sell_order, buy_order.firm)
                    if buy_order.price < effective_price:
                        break

                    affordable = min(
                        buy_order.shortfall,
                        sell_order.amount,
                        buy_order.firm.market_capital / effective_price if effective_price > 0 else buy_order.shortfall,
                    )
                    quantity = max(affordable, 0.0)
                    if quantity <= 0:
                        continue

                    self._trade_order(
                        buy_order=buy_order,
                        sell_order=sell_order,
                        quantity=quantity,
                        price=effective_price,
                    )

            for sell_order in sells:
                key = (sell_order.city.id, item)
                if not buys:
                    self._city_underask_gap[key] = 0.0
                    continue
                best_net_bid = max(
                    max(buy_order.price - self._distance_between(sell_order.city.id, buy_order.firm.city_id) * self.energy_cost, 0.0)
                    for buy_order in buys
                )
                self._city_underask_gap[key] = max(sell_order.price - best_net_bid, 0.0)

        # Fill ratios (previous tick outcome signal for next tick repricing).
        remaining_buy = {(id(order.firm), order.item): order.shortfall for order in self.state.buy_orders}
        remaining_sell = {(order.city.id, order.item): order.amount for order in self.state.sell_orders}

        self._firm_fill_ratio = compute_fill_ratio(buy_start_qty, remaining_buy)
        self._city_fill_ratio = compute_fill_ratio(sell_start_qty, remaining_sell)

        # Keep only active open orders on the book.
        self.state.buy_orders = [order for order in self.state.buy_orders if order.shortfall > 0]
        self.state.sell_orders = [order for order in self.state.sell_orders if order.amount > 0]

    def record_history(self) -> None:
        """Write one history item per known good, every tick.

        This produces a dense time series for easier plotting and downstream
        analysis, even when there is zero volume/liquidity.
        """
        self._known_goods.update(order.item for order in self.state.buy_orders)
        self._known_goods.update(order.item for order in self.state.sell_orders)
        entries = build_dense_history_entries(
            known_goods=self._known_goods,
            buy_orders=self.state.buy_orders,
            sell_orders=self.state.sell_orders,
            market_snapshot=self._last_market_snapshot,
            trade_summary=self._last_trade_summary,
            tick_count=self.tick_count,
        )
        for item, entry in entries.items():
            self.state.history.setdefault(item, []).append(entry)
