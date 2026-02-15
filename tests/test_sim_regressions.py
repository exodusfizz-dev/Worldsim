import unittest

from config import CONFIG
from model.core.ticks import Core
from model.core.invariants import assert_core_invariants


class SimulationRegressionTests(unittest.TestCase):
    def make_core(self):
        core = Core(
            seed_cfg=CONFIG.get("seed"),
            city_cfg=CONFIG.get("city"),
            province_cfg=CONFIG.get("province"),
            country_cfg=CONFIG.get("country"),
        )
        core.build_sim()
        return core

    def test_build_provinces_keeps_expected_structure(self):
        core = self.make_core()
        country = core.countries[0]

        self.assertEqual(len(country.provinces), 2)
        self.assertEqual(len(country.provinces[0].cities), 1)
        self.assertEqual(len(country.provinces[1].cities), 1)

    def test_invariants_hold_for_first_12_ticks(self):
        core = self.make_core()
        for _ in range(12):
            core.tick()
            assert_core_invariants(core)

    def test_seeded_run_is_deterministic(self):
        core_a = self.make_core()
        core_b = self.make_core()
        path_a = []
        path_b = []

        for _ in range(12):
            core_a.tick()
            core_b.tick()
            city_a = core_a.countries[0].provinces[0].cities[0]
            city_b = core_b.countries[0].provinces[0].cities[0]
            path_a.append(round(city_a.total_population, 6))
            path_b.append(round(city_b.total_population, 6))

        self.assertEqual(path_a, path_b)


if __name__ == "__main__":
    unittest.main()
