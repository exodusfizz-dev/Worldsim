from model.core.random import _sample_normal
from dataclasses import dataclass

from model.economy.industry.firm_properties import (FirmParams,
                                                    FirmState,
                                                    FirmProperties)

class Firm(FirmProperties):
    def __init__(self, params: FirmParams, rng):
        self.p = params
        self.state = FirmState()

        self.rng = rng

        self.state.market_capital = self.p.capital if self.p.capital is not None else 0.0

    @classmethod
    def from_dict(cls, firm_data: dict, rng, country_policy: None = None) -> "Firm":
        '''Create a new firm instance from dictionary data.'''
        return cls(
            params=FirmParams(
                productivity=firm_data["productivity"],
                production_capacity=firm_data["production_capacity"],
                ownership=firm_data["ownership"],
                good=firm_data["good"],
                capital=firm_data.get("capital"),
                wage=firm_data.get("wage"),
                required_skill=firm_data.get("required_skill"),
                country_policy=country_policy,
            ),
            rng=rng,
        )

    def labour_demand(self, market_capital: float | None = None, market_wage: float | None = None) -> int:
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


    def update_total_productivity(self) -> float:

        self.total_productivity = max(
            min(self.p.productivity * self.employed, self.p.production_capacity),
            0,
        )

        return self.total_productivity

    def produce(self):
        self.inventory += _sample_normal(expected=self.update_total_productivity(), rng=self.rng)

    def tick(self):
        self.produce()

    def transfer_to_city(self):
        '''For moving inventory to city. Only called if state owned.'''
        amount = self.inventory
        self.inventory = 0
        return amount
