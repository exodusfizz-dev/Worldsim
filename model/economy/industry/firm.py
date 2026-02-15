from model.core.random import _sample_normal
from dataclasses import dataclass

@dataclass
class FirmParams:
    productivity: float
    production_capacity: int
    ownership: str
    good: str
    # transitional: optional in input_data.json
    capital: float | None = None
    wage: float | None = None

@dataclass
class FirmState:
    employed: int = 0
    total_productivity: float = 0.0
    inventory: float = 0.0
    market_capital: float | None = None

class Firm:
    def __init__(self, params: FirmParams, rng):
        self.p = params
        self.state = FirmState()

        self.rng = rng

    @classmethod
    def from_dict(cls, firm_data: dict, rng):
        return cls(
            params=FirmParams(
                productivity=firm_data["productivity"],
                production_capacity=firm_data["production_capacity"],
                ownership=firm_data["ownership"],
                good=firm_data["good"],
                capital=firm_data.get("capital"),
                wage=firm_data.get("wage"),
            ),
            rng=rng,
        )


    @property
    def employed(self):
        return self.state.employed
    @employed.setter
    def employed(self, value):
        self.state.employed = value

    @property
    def total_productivity(self):
        return self.state.total_productivity
    @total_productivity.setter
    def total_productivity(self, value):
        self.state.total_productivity = value

    @property
    def inventory(self):
        return self.state.inventory
    @inventory.setter
    def inventory(self, value):
        self.state.inventory = value

    @property
    def good(self):
        return self.p.good

    @property
    def ownership(self):
        return self.p.ownership

    def labour_demand(self, market_capital: float | None = None, market_wage: float | None = None):
        '''Limiting factor of employment is either:
        The production capacity / output per worker,
        Or the capital available to pay workers'''
        cap = market_capital if market_capital is not None else self.p.capital
        wage = market_wage if market_wage is not None else self.p.wage

        cap_limit = float("inf") if cap is None else cap / wage
        prod_limit = self.p.production_capacity / self.p.productivity
        return min(prod_limit, cap_limit)


    def update_total_productivity(self):

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
