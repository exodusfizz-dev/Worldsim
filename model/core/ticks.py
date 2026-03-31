
import numpy as np
from model.city import PopulationGenerator
from .build_sim import build_sim as build_sim_core
from .shocks import Shock



class Core:
    def __init__(
        self,
        seed_cfg,
        city_cfg,
        province_cfg,
        country_cfg,
        location_cfg=None,
    ):

        if seed_cfg["use"]:
            self.rng = np.random.default_rng(seed_cfg["seed"])
        else:
            self.rng = np.random.default_rng()

        self.city_cfg = city_cfg or {}
        self.province_cfg = province_cfg or {}
        self.country_cfg = country_cfg or {}
        self.location_cfg = location_cfg or {}

        pop_cfg = self.city_cfg.get("population", {})
        self.population_gen = PopulationGenerator(
            rng=self.rng,
            base_group_count=int(pop_cfg.get("base_group_count", 5)),
            group_type_count=int(pop_cfg.get("group_type_count", 3)),
        )

        self.countries = []

    def tick(self):
        for country in self.countries:
            country.tick()

    def build_sim(self):
        """Build simulation from Natural Earth data."""
        build_sim_core(self)

    def to_shock_or_not_to_shock(self):
        if self.rng.choice([True, False], p=(0.01, 0.99)):
            pass
            # init a Shock
