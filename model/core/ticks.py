import json
from model.city import City
from model.province import Province
import numpy as np
from model.economy import Firm
from model.population import PopulationGroup
from model.country import Country
from model.location.world_data_loader import WorldDataLoader


class Core:
    def __init__(self, seed_cfg, city_cfg, province_cfg, country_cfg):

        if seed_cfg['use']:
            self.rng = np.random.default_rng(seed_cfg['seed'])
        else:
            self.rng = np.random.default_rng()

        self.city_cfg = city_cfg
        self.province_cfg = province_cfg
        self.country_cfg = country_cfg

        self.countries = []

    def tick(self):
        for country in self.countries:
            country.tick()




    def _build_population_groups(self, groups):
        return [
            PopulationGroup.from_dict(group_data=group,
                rng=self.rng,)
            for group in groups
        ]

    def _build_firms(self, firms):
        return [Firm.from_dict(firm_data, rng=self.rng) for firm_data in firms]

    def _build_city(self, city_data):

        populations = self._build_population_groups(city_data["groups"])

        firms = self._build_firms(city_data["firms"])

        return City.from_dict(city_data,
                              populations,
                              firms,
                              rng=self.rng,
                              cfg=self.city_cfg)

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
        )

        countries_to_load = ["United Kingdom"]
        data = {"countries": loader.load_world(countries_to_load)}

        for country_data in data["countries"]:
            provinces = self.build_provinces(data=country_data)

            cfg = self.country_cfg

            country_obj = Country.from_dict(country_data,
                                            provinces,
                                            cfg=cfg,
                                            rng=self.rng)

            self.countries.append(country_obj)
