"""City domain model and per-tick simulation updates."""

from __future__ import annotations

from dataclasses import dataclass, field
from model.city.city_data import CityData
from model.economy import LabourMarket
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
    migration_attractiveness: float = 0.0
    inv: dict[str, float] = field(default_factory=dict)
    total_population: float = 0.0


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

        self.refresh_totals()
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
        return self.state.migration_attractiveness

    @migration_attractiveness.setter
    def migration_attractiveness(self, value: float) -> None:
        self.state.migration_attractiveness = value

    @property
    def total_population(self) -> float:
        """Canonical city population used by migration and reporting."""
        return self.state.total_population

    @total_population.setter
    def total_population(self, value: float) -> None:
        self.state.total_population = value

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

    def refresh_totals(self) -> None:
        """Recompute derived totals needed by migration and reporting."""
        self.total_population = sum(group.size for group in self.p.populations)
        if self.p.populations:
            self.state.migration_attractiveness = (
                sum(group.migration_attractiveness for group in self.p.populations)
                / len(self.p.populations)
            )
        else:
            self.state.migration_attractiveness = 0.0

    def tick(self) -> None:
        for group in self.p.populations:
            group.tick()
        self.refresh_totals()

        self.state.employed = self.labour_market.clear_market(
            populations=self.p.populations,
            firms=self.p.firms,
        )

        for firm in self.p.firms:
            firm.tick()
            if firm.good not in self.state.inv:
                self.state.inv.setdefault(firm.good, 0.0)

            if firm.ownership == "state":
                self.state.inv[firm.good] += firm.transfer_to_city()

        self.consume_food()
        self.run_migrations()
        self.refresh_totals()
        self.city_data.update_city_data()

    def run_migrations(self) -> None:
        """Run migration between groups inside this city."""
        self.state.migrations = []
        if self.cfg.get("migration", {}).get("enabled", True):
            self.state.migrations.extend(self.migration.migrate_within_city(self))

    def consume_food(self) -> None:
        """Consume food and apply starvation effects when supply is insufficient."""
        food_needed = sum(g.compute_food_consumption() for g in self.p.populations)
        if food_needed < self.state.inv["food"]:
            self.state.inv["food"] -= food_needed
            self.state.last_food_deficit = None
            return

        self.state.last_food_deficit = food_needed - self.state.inv["food"]
        self.state.migration_attractiveness = 0.0
        self.state.inv["food"] = 0.0

        if not self.p.populations:
            return
        per_group_deficit = self.state.last_food_deficit // len(self.p.populations)
        for group in self.p.populations:
            group.starve(food_deficit=per_group_deficit)
