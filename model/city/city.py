"""City domain model and per-tick simulation updates."""

from __future__ import annotations

from dataclasses import dataclass, field
from model.city.city_data import CityData
from model.economy import LabourMarket
from model.economy.labour.labour_market import LabourClearResult
from model.migration import GroupMigrationEvent, Migration


@dataclass
class CityParams:
    """Immutable construction parameters for a city."""

    name: str
    populations: list
    firms: list


@dataclass
class CityState:
    """Mutable city state updated during each simulation tick."""

    employed: int = 0
    migrations: list[GroupMigrationEvent] = field(default_factory=list)
    last_food_deficit: float | None = None
    inv: dict[str, float] = field(default_factory=dict)
    treasury: float = 0.0
    labour_result: LabourClearResult | None = None
    starving: bool = False


class City:
    """City object owned by provinces."""

    def __init__(self, cfg: dict, rng, params: CityParams) -> None:
        self.p = params
        self.rng = rng
        self.cfg = cfg

        self.state = CityState()

        intergroup_rate = self.cfg.get("migration", {}).get("intergroup_rate", 0.0005)
        self.migration = Migration.for_intergroup(
            rng=self.rng,
            intergroup_rate=intergroup_rate,
        )

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
            ),
            rng=rng,
            cfg=cfg,
        )

    @property
    def employed(self) -> int:
        return self.state.employed

    @property
    def migrations(self) -> list[GroupMigrationEvent]:
        return self.state.migrations

    @property
    def last_food_deficit(self) -> float | None:
        return self.state.last_food_deficit

    @property
    def inv(self) -> dict[str, float]:
        return self.state.inv

    @property
    def migration_attractiveness(self) -> float:
        if self.state.starving:
            return 0.0
        return sum(group.migration_attractiveness for group in self.p.populations)


    @property
    def total_population(self) -> float:
        """Canonical city population used by migration and reporting."""
        return sum(group.size for group in self.populations)

    @property
    def group_count(self) -> int:
        """Number of population groups currently in the city."""
        return len(self.p.populations)

    @property
    def name(self) -> str:
        return self.p.name

    @property
    def populations(self) -> list:
        return self.p.populations

    @property
    def firms(self) -> list:
        return self.p.firms

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
            self.state.migrations.extend(self.migration.migrate_within_city(self))

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

        market_cfg = self.cfg.get("market", {})
        food_price = max(float(market_cfg.get("food_price", 1.0)), 0.0)
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

    def tick_groups(self):
        for group in self.p.populations:
            group.tick()
