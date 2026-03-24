"""City domain model and per-tick simulation updates."""

from __future__ import annotations

from model.city.city_data import CityData
from model.economy import LabourMarket

from .city_properties import (CityParams,
                              CityState,
                              CityProperties)



class City(CityProperties):
    """City object owned by provinces."""

# TODO: move from old population group list of objects to array handled by city_population_manager.py

    def __init__(self, cfg: dict, rng, params: CityParams) -> None:
        self.p = params
        self.rng = rng
        self.cfg = cfg

        self.state = CityState()

        intergroup_rate = self.cfg.get("migration", {}).get("intergroup_rate", 0.0005)
        del intergroup_rate
        self.migration = None

        self.labour_market = LabourMarket(self.rng, country_policy=None)

        for firm in self.p.firms:
            self.state.inv.setdefault(firm.good, 0.0)
        if "food" not in self.state.inv:
            self.state.inv["food"] = 0.0

        self.city_data = CityData(self)

    @classmethod
    def from_dict(cls, city_data: dict, populations, firms, rng, cfg) -> "City":
        return cls(
            params=CityParams(
                name=city_data["name"],
                populations=populations,
                firms=firms,
                location=city_data["geometry"],
                id=city_data["city_id"],
            ),
            rng=rng,
            cfg=cfg,
        )



    def tick(self) -> None:
        self.tick_groups()

        self.state.labour_result = self.labour_market.clear_market(
            populations=self.p.populations,
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
        self.run_migrations()
        self.city_data.update_city_data()

    def run_migrations(self) -> None:
        """Run migration between groups inside this city."""
        self.state.migrations = []
        if self.cfg.get("migration", {}).get("enabled", True):
            self.state.migrations.extend(self.migration.migrate_within_city(self)
                                         if self.migration
                                         else [])

    def settle_labour_tax(self) -> None:
        """Collect labour income tax from groups."""
        if self.state.labour_result is None:
            return

        labour_tax_rate = 0.2
        if labour_tax_rate <= 0:
            return

        for group, income in zip(self.p.populations, self.state.labour_result.group_income):
            tax = max(income, 0.0) * labour_tax_rate
            paid = min(group.money, tax)
            group.money -= paid
            self.state.treasury += paid

    def consume_food(self) -> None:
        """Groups buy and consume food from city inventory."""
        if not self.p.populations:
            self.state.last_food_deficit = None
            return

        food_price = 5.0 # Placeholder pre market
        total_deficit = 0.0

        for group in self.p.populations:
            needed = group.compute_food_consumption()
            available = self.state.inv["food"]
            if available <= 0:
                purchased = 0.0
            elif food_price <= 0:
                purchased = min(needed, available)
            else:
                affordable = group.money / food_price
                purchased = min(needed, available, affordable)

            if food_price > 0 and purchased > 0:
                spent = purchased * food_price
                group.money = max(group.money - spent, 0.0)
            self.state.inv["food"] -= purchased

            deficit = max(needed - purchased, 0.0)
            total_deficit += deficit
            if deficit > 0:
                group.starve(food_deficit=deficit)

        if total_deficit > 0:
            self.state.last_food_deficit = total_deficit
            self.state.starving = True
        else:
            self.state.last_food_deficit = None

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

    def tick_groups(self):
        for group in self.p.populations:
            group.tick()
