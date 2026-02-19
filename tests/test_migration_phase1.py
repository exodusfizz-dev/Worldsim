import unittest
from dataclasses import dataclass
import random

from model.migration import Migration
from model.province.province import Province, ProvinceParams


@dataclass
class StubGroup:
    size: int
    migration_attractiveness: float


@dataclass
class StubCity:
    name: str
    populations: list[StubGroup]
    migration_attractiveness: float

    @property
    def total_population(self) -> int:
        return sum(group.size for group in self.populations)

    def refresh_totals(self) -> None:
        return


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


class MigrationPhase1Tests(unittest.TestCase):
    def make_cities(self) -> tuple[StubCity, StubCity]:
        source = StubCity(
            name="A",
            populations=[StubGroup(120, 0.2), StubGroup(80, 0.25), StubGroup(50, 0.3)],
            migration_attractiveness=0.25,
        )
        target = StubCity(
            name="B",
            populations=[StubGroup(100, 0.7), StubGroup(90, 0.8)],
            migration_attractiveness=0.75,
        )
        return source, target

    def test_intergroup_migration_conserves_population_and_uses_ints(self):
        city = StubCity(
            name="A",
            populations=[StubGroup(100, 0.1), StubGroup(70, 0.4), StubGroup(40, 0.7)],
            migration_attractiveness=0.0,
        )
        migration = Migration.for_intergroup(
            rng=RngAdapter(42),
            intergroup_rate=0.2,
        )

        before = city.total_population
        events = migration.migrate_within_city(city)
        after = city.total_population

        self.assertEqual(before, after)
        self.assertTrue(all(isinstance(event.amount, int) for event in events))
        self.assertTrue(all(group.size >= 0 for group in city.populations))

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
        self.assertTrue(all(group.size >= 0 for group in source.populations + target.populations))

    def test_fallback_split_used_when_target_has_fewer_groups(self):
        source, target = self.make_cities()
        migration = Migration.for_intercity(
            rng=RngAdapter(99),
            intercity_rate=0.9,
        )

        events = migration.migrate_between_cities(source, target)
        self.assertTrue(any(event.source_group_index >= len(target.populations) for event in events))

    def test_province_uses_intercity_rate_from_config(self):
        province = Province(
            cfg={"migration": {"enabled": True, "intercity_rate": 0.123}},
            rng=RngAdapter(1),
            params=ProvinceParams(name="P", area=100, cities=[]),
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
