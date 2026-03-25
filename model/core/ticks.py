from model.city import City, CityPopulation, PopulationGenerator
from model.province import Province
import numpy as np
from model.economy import Firm
from model.country import Country
from model.location.world_data_loader import WorldDataLoader


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

    def _build_firms(self, firms, city_id: int):
        return [Firm.from_dict(firm_data, rng=self.rng, city_id=city_id) for firm_data in firms]

    def _build_city(self, city_data):
        pop_seed = self.population_gen.generate_for_city(
            city_name=city_data["name"],
            population=int(city_data.get("population_estimate", 0)),
        )
        population = CityPopulation.from_seed(
            seed=pop_seed,
            rng=self.rng,
            cfg=self.city_cfg.get("population", {}),
        )

        firms = self._build_firms(city_data["firms"], city_id=city_data["city_id"])

        return City.from_dict(
            city_data,
            population,
            firms,
            rng=self.rng,
            cfg=self.city_cfg,
        )

    def _build_province(self, province_data):
        cities = [self._build_city(city_data) for city_data in province_data["cities"]]
        return Province.from_dict(province_data, cities, cfg=self.province_cfg, rng=self.rng)

    def build_provinces(self, data):
        return [self._build_province(province_data) for province_data in data["provinces"]]

    def build_sim(self):
        """Build simulation from Natural Earth data."""
        loader = WorldDataLoader(
            rng=self.rng,
            city_cfg=self.city_cfg,
            province_cfg=self.province_cfg,
            country_cfg=self.country_cfg,
            location_cfg=self.location_cfg,
        )

        countries_to_load = ["United Kingdom"]
        data = {"countries": loader.load_world(countries_to_load)}

        for country_data in data["countries"]:
            provinces = self.build_provinces(data=country_data)

            cfg = self.country_cfg

            country_obj = Country.from_dict(
                country_data,
                provinces,
                cfg=cfg,
                rng=self.rng,
            )

            self.countries.append(country_obj)
