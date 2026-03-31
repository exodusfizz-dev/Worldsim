import unittest
from dataclasses import dataclass
import random

import numpy as np

from model.city import CityPopulation
from model.city.population_generator import PopulationSeed
from model.migration import Migration
from model.province.province import Province, ProvinceParams


@dataclass
class StubCity:
    name: str
    population: CityPopulation

    @property
    def migration_attractiveness(self) -> float:
        return self.population.migration_attractiveness

    @property
    def total_population(self) -> int:
        return self.population.total_population


class ZeroDistance:
    def weight(self, source_key: str, target_key: str) -> float:
        return 0.0


class RngAdapter:
    def __init__(self, seed: int) -> None:
        self._rng = random.Random(seed)

    def uniform(self, a: float, b: float) -> float:
        return self._rng.uniform(a, b)

    def binomial(self, n: int, p: float) -> int:
        successes = 0
        for _ in range(n):
            if self._rng.random() < p:
                successes += 1
        return successes


def make_population(sizes: list[int], healthcare: list[float]) -> CityPopulation:
    n = len(sizes)
    seed = PopulationSeed(
        group_type=np.arange(n, dtype=np.int8) % 3,
        size=np.asarray(sizes, dtype=np.int64),
        base_healthcare=np.asarray(healthcare, dtype=np.float64),
        healthcare_capacity=np.maximum(100, np.asarray(sizes, dtype=np.int64)),
        education=np.ones(n, dtype=np.float64),
        money=np.zeros(n, dtype=np.float64),
    )
    pop = CityPopulation.from_seed(seed=seed, rng=np.random.default_rng(123))
    pop.groups["healthcare"] = np.asarray(healthcare, dtype=np.float64)
    return pop


class MigrationPhase1Tests(unittest.TestCase):
    def make_cities(self) -> tuple[StubCity, StubCity]:
        source = StubCity(
            name="A",
            population=make_population([120, 80, 50], [0.2, 0.25, 0.3]),
        )
        target = StubCity(
            name="B",
            population=make_population([100, 90], [0.7, 0.8]),
        )
        return source, target

    def test_intercity_migration_conserves_total_and_uses_ints(self):
        source, target = self.make_cities()
        migration = Migration.for_intercity(
            rng=RngAdapter(7),
            intercity_rate=0.4,
        )

        before_total = source.total_population + target.total_population
        events = migration.migrate_between_cities(source, target)
        after_total = source.total_population + target.total_population

        self.assertEqual(before_total, after_total)
        self.assertTrue(all(isinstance(event.amount, int) for event in events))
        self.assertTrue(np.all(source.population.groups["size"] >= 0))
        self.assertTrue(np.all(target.population.groups["size"] >= 0))

    def test_fallback_split_used_when_target_has_fewer_groups(self):
        source, target = self.make_cities()
        migration = Migration.for_intercity(
            rng=RngAdapter(99),
            intercity_rate=0.9,
        )

        events = migration.migrate_between_cities(source, target)
        self.assertTrue(
            any(event.source_group_index >= target.population.group_count for event in events)
        )

    def test_province_uses_intercity_rate_from_config(self):
        province = Province(
            cfg={"migration": {"enabled": True, "intercity_rate": 0.123}},
            rng=RngAdapter(1),
            params=ProvinceParams(name="P", area=100, cities=[], geometry=None),
        )
        self.assertAlmostEqual(province.migration.intercity_rate, 0.123)

    def test_distance_weight_can_zero_out_migration(self):
        source, target = self.make_cities()
        migration = Migration.for_intercity(
            rng=RngAdapter(2),
            intercity_rate=0.9,
            distance_provider=ZeroDistance(),
        )

        events = migration.migrate_between_cities(source, target)
        self.assertEqual(events, [])


if __name__ == "__main__":
    unittest.main()
