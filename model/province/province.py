"""Province model and intercity migration orchestration."""

from dataclasses import dataclass, field
from model.migration import Migration
from model.province.province_properties import (ProvinceParams,
                                                ProvinceState,
                                                ProvinceProperties)


class Province(ProvinceProperties):
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
        '''Build a province from input data and constructed cities.'''
        return cls(
            params=ProvinceParams(
                name=province_data["name"],
                area=province_data["area"],
                cities=cities,
            ),
            cfg=cfg,
            rng=rng,
        )


    def tick(self) -> None:
        '''Runs one time step for the province, and all cities within it.'''
        for city in self.p.cities:
            city.tick()
        self.run_migrations()

    def run_migrations(self) -> None:
        """Run basic intercity migration from less to more attractive cities."""
        self.state.migrations = []
        if not self.cfg.get("migration", {}).get("enabled", True):
            return

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
