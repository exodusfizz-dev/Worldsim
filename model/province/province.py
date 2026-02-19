"""Province model and intercity migration orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from model.migration import GroupMigrationEvent, Migration


@dataclass
class ProvinceParams:
    """Immutable construction parameters for a province."""

    name: str
    area: int
    cities: list


@dataclass
class ProvinceState:
    """Mutable province-level runtime state."""

    migrations: list[GroupMigrationEvent] = field(default_factory=list)


class Province:
    """Province object owning a list of cities."""

    def __init__(self, cfg: dict, rng, params: ProvinceParams) -> None:
        self.rng = rng
        self.cfg = cfg
        self.p = params
        self.state = ProvinceState()

        intercity_rate = self.cfg.get("migration", {}).get("intercity_rate", 0.0001)
        self.migration = Migration.for_intercity(
            rng=self.rng,
            intercity_rate=intercity_rate,
        )

    @classmethod
    def from_dict(cls, province_data: dict, cities, cfg, rng) -> "Province":
        return cls(
            params=ProvinceParams(
                name=province_data["name"],
                area=province_data["area"],
                cities=cities,
            ),
            cfg=cfg,
            rng=rng,
        )

    @property
    def name(self) -> str:
        return self.p.name

    @property
    def cities(self) -> list:
        return self.p.cities

    @property
    def area(self) -> int:
        return self.p.area

    @property
    def migrations(self) -> list[GroupMigrationEvent]:
        """Read-only log of intercity migration events for the latest tick."""
        return self.state.migrations

    def tick(self) -> None:
        for city in self.p.cities:
            city.tick()
        self.run_migrations()

    def run_migrations(self) -> None:
        """Run basic intercity migration from less to more attractive cities."""
        self.state.migrations = []
        if not self.cfg.get("migration", {}).get("enabled", True):
            return

        touched_cities: set = set()

        for source_city in self.p.cities:
            candidates = [
                city
                for city in self.p.cities
                if city is not source_city
                and city.migration_attractiveness > source_city.migration_attractiveness
            ]
            if not candidates:
                continue

            target_city = self.migration.choose_target_city(source_city, candidates)
            if target_city is None:
                continue
            events = self.migration.migrate_between_cities(source_city, target_city)
            if not events:
                continue

            self.state.migrations.extend(events)
            touched_cities.add(source_city)
            touched_cities.add(target_city)

        for city in touched_cities:
            city.refresh_totals()
