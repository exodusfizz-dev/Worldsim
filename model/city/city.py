"""City domain model and per-tick simulation updates."""

from __future__ import annotations

from model.city.city_data import CityData
from model.economy import LabourMarket

from .city_properties import CityParams, CityState, CityProperties


class City(CityProperties):
    """City object owned by provinces."""

    def __init__(self, cfg: dict, rng, params: CityParams) -> None:
        self.p = params
        self.population = params.population
        self.rng = rng
        self.cfg = cfg

        self.state = CityState()


        self.labour_market = LabourMarket(self.rng, country_policy=None)

        for firm in self.p.firms:
            self.state.inv.setdefault(firm.good, 0.0)
        if "food" not in self.state.inv:
            self.state.inv["food"] = 0.0

        self.city_data = CityData(self)

    @classmethod
    def from_dict(cls, city_data: dict, population, firms, rng, cfg) -> "City":
        return cls(
            params=CityParams(
                name=city_data["name"],
                population=population,
                firms=firms,
                location=city_data["geometry"],
                id=city_data["city_id"],
            ),
            rng=rng,
            cfg=cfg,
        )

    def tick(self) -> None:
        self.population.tick()

        self.state.labour_result = self.labour_market.clear_market(
            population=self.population,
            firms=self.p.firms,
        )
        self.state.employed = self.state.labour_result.total_employed
        self.settle_labour_tax()

        for firm in self.p.firms:
            if firm.good not in self.state.inv:
                self.state.inv.setdefault(firm.good, 0.0)
            firm.tick()

            if firm.ownership == "state":
                transfer = firm.transfer_to_city()
                self.state.inv[firm.good] += transfer
                firm.market_capital += transfer * (1 / firm.p.productivity) * 30

        self.consume_food()
        self.city_data.update_city_data()


    def settle_labour_tax(self) -> None:
        """Collect labour income tax from groups."""
        if self.state.labour_result is None:
            return

        labour_tax_rate = self.cfg.get("economy", {}).get("labour_tax_rate", 0.2)
        self.state.treasury += self.population.apply_labour_result(
            labour_result=self.state.labour_result,
            labour_tax_rate=labour_tax_rate,
        )

    def consume_food(self) -> None:
        """Groups buy and consume food from city inventory."""
        if self.population.group_count <= 0:
            self.state.last_food_deficit = None
            self.state.starving = False
            return

        food_price = self.cfg.get("economy", {}).get("food_price", 5.0)
        consumed, total_deficit = self.population.apply_food_allocation(
            available_food=float(self.state.inv.get("food", 0.0)),
            food_price=food_price,
        )
        self.state.inv["food"] = max(float(self.state.inv.get("food", 0.0)) - consumed, 0.0)

        if total_deficit > 0:
            self.state.last_food_deficit = total_deficit
            self.state.starving = True
        else:
            self.state.last_food_deficit = None
            self.state.starving = False

    def sell_to_firm(self, firm, item, amount, price) -> None:
        available = self.state.inv.get(item, 0.0)
        to_sell = min(available, amount)
        if to_sell <= 0:
            return

        revenue = to_sell * price
        self.state.inv[item] -= to_sell
        firm.inv[item] = firm.inv.get(item, 0.0) + to_sell
        self.state.treasury += revenue
        firm.market_capital -= revenue
