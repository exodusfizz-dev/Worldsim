'''Firm object owned by cities.'''
from dataclasses import dataclass, field
from model.core.random import _sample_normal

from model.economy.industry.firm_properties import (FirmParams,
                                                    FirmState,
                                                    FirmProperties)


@dataclass(frozen=True)
class GoodDemandItem:
    """Demand for a single input material."""
    good: str
    shortfall: float

@dataclass
class GoodDemandResult:
    """All input demands from a single firm."""
    firm_good: str  # What firm produces
    demands: list[GoodDemandItem] = field(default_factory=list)

    def has_demand(self) -> bool:
        return any(d.shortfall > 0 for d in self.demands)

class Firm(FirmProperties):
    def __init__(self, params: FirmParams, rng):
        self.p = params
        self.state = FirmState()

        self.rng = rng

        self.state.market_capital = self.p.capital if self.p.capital is not None else 0.0

        if self.input_mats is not None:
            for mat in self.input_mats:
                self.state.inv.setdefault(mat, 0.0)
        self.state.inv.setdefault(self.good, 0.0)

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
                input_mats=firm_data.get("input_mats"),
                education_wanted=firm_data.get("education_wanted", 1.0),
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

    def good_demand(self) -> GoodDemandResult:
        '''Returns a float demand for each material in input.'''
        result = GoodDemandResult(firm_good=self.good, demands=[])

        if self.able_to_produce == float('inf') or not self.input_mats:
            return result

        max_production = min(self.p.productivity * self.employed,
                            self.p.production_capacity)

        for mat in self.input_mats:
            shortfall = max(max_production - self.inv[mat], 0.0)
            result.demands.append(GoodDemandItem(
            good=mat,
            shortfall=shortfall,
        ))

        return result


    def update_total_productivity(self) -> float:
        self.total_productivity = max(
            min(self.p.productivity * self.employed,
                self.p.production_capacity,
                self.able_to_produce),
            0,
        )

        return self.total_productivity

    def produce(self):
        produced = min(_sample_normal(expected=self.update_total_productivity(), rng=self.rng),
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
