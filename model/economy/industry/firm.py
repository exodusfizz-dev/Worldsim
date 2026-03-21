'''Firm object owned by cities.'''

from __future__ import annotations

from statistics import median

from model.core.random import _sample_normal

from model.economy.industry.firm_properties import (FirmParams,
                                                    FirmState,
                                                    FirmProperties)

from model.economy.trade.supply_chain_types import MarketBuyOrder

class Firm(FirmProperties):
    def __init__(self, params: FirmParams, rng, city_id: int):
        self.p = params
        self.state = FirmState()

        self.rng = rng
        self.city_id = city_id

        self.state.market_capital = self.p.capital if self.p.capital is not None else 0.0

        if self.input_mats is not None:
            for mat in self.input_mats:
                self.state.inv.setdefault(mat, 0.0)
        self.state.inv.setdefault(self.good, 0.0)

    @classmethod
    def from_dict(cls, firm_data: dict, rng, city_id: int) -> "Firm":
        '''Create a new firm instance from dictionary data.'''
        return cls(
            params=FirmParams(
                productivity=firm_data["productivity"],
                production_capacity=firm_data["production_capacity"],
                ownership=firm_data["ownership"],
                good=firm_data["good"],
                capital=firm_data.get("capital"),
                wage=firm_data.get("wage"),
                input_mats=firm_data.get("input_mats"),
                education_wanted=firm_data.get("education_wanted", 1.0),
                desired_stock_weeks=firm_data.get("desired_stock_weeks", 5.0),
            ),
            rng=rng,
            city_id=city_id,
        )

    def labour_demand(self,
                      market_capital: float | None = None,
                      market_wage: float | None = None
                      ) -> int:
        '''Limiting factor of employment is either:
        The production capacity / output per worker,
        Or the capital available to pay workers'''
        cap = market_capital if market_capital is not None else self.p.capital
        wage = market_wage if market_wage is not None else self.p.wage

        if self.p.productivity <= 0:
            return 0

        if wage is None or wage <= 0:
            cap_limit = float("inf")
        else:
            cap_limit = float("inf") if cap is None else cap / wage

        prod_limit = self.p.production_capacity / self.p.productivity
        return int(max(min(prod_limit, cap_limit), 0))

    def good_demand(
        self,
        market_signals: dict[str, dict[str, float]],
        fill_ratios: dict[str, float],
        price_feedback: dict[str, dict[str, float]],
    ) -> list[MarketBuyOrder]:
        """Create bid intents for input materials.

        Firms target a stockpile of `desired_stock_weeks` worth of expected
        production inputs. Bid prices adapt to:
        - urgency (how far below target stock we are),
        - recent fill success (low fill => bid more aggressively),
        - robust market context (rolling reference + spread),
        - predicted supply risk (stub hook from market signal).
        - required overbid feedback from previous clearing attempts.
        """

        result = []

        if not self.input_mats:
            return result

        max_production = min(self.p.productivity * self.employed,
                            self.p.production_capacity)
        if max_production <= 0:
            return result

        for mat in self.input_mats:
            weekly_need = max_production
            target_stock = max(weekly_need * self.p.desired_stock_weeks, 0.0)
            current_stock = self.inv.get(mat, 0.0)
            shortfall = max(target_stock - current_stock, 0.0)
            if shortfall <= 0:
                continue

            signal = market_signals.get(mat, {})
            feedback = price_feedback.get(mat, {})
            top_bid = max(signal.get("top_bid", 0.0), 0.0)
            top_ask = max(signal.get("top_ask", 0.0), 0.0)
            agreed = max(signal.get("agreed_price", 0.0), 0.0)
            reference = max(signal.get("reference_price", 0.0), 0.0)
            predicted_supply_risk = max(signal.get("predicted_supply_risk", 1.0), 0.0)
            required_overbid = max(feedback.get("required_overbid", 0.0), 0.0)

            candidates = [price for price in (reference, agreed, top_ask * 0.9, top_bid) if price > 0]
            base_price = median(candidates) if candidates else 1.0
            spread = max(top_ask - top_bid, 0.0) if top_ask > 0 and top_bid > 0 else 0.0
            urgency_ratio = min(shortfall / max(weekly_need, 1e-9), self.p.desired_stock_weeks)
            urgency = min(urgency_ratio / max(self.p.desired_stock_weeks, 1.0), 1.0)

            fill_ratio = min(max(fill_ratios.get(mat, 1.0), 0.0), 1.0)
            miss_penalty = 1.0 - fill_ratio

            # Higher urgency / poor fills / expected scarcity => higher bids.
            scarcity_premium = max(predicted_supply_risk - 1.0, 0.0)
            price_multiplier = 1.0 + (0.35 * urgency) + (0.20 * miss_penalty) + (0.15 * scarcity_premium)
            adaptive_price = max(base_price * price_multiplier + (0.10 * spread) + (0.5 * required_overbid), 0.01)

            result.append(MarketBuyOrder(
                firm=self,
                item=mat,
                shortfall=shortfall,
                price=adaptive_price,
            ))

        return result

    def produce(self):
        produced = min(_sample_normal(expected=self.total_productivity, rng=self.rng),
                       self.able_to_produce)
        if self.input_mats is not None:
            for mat in self.input_mats:
                self.state.inv[mat] = max(self.state.inv[mat] - produced, 0)
        self.inv[self.good] += produced


    def tick(self):
        self.produce()

    def transfer_to_city(self):
        '''For moving inventory to city. Only called if state owned.'''
        amount = self.inv[self.good]
        self.inv[self.good] = 0
        return amount
