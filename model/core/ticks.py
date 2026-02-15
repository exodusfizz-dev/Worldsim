import json
from model.city import City
from model.province import Province
import numpy as np
from model.economy import Firm
from model.population import PopulationGroup
from model.country import Country


class Core:
    def __init__(self, seed_cfg, city_cfg, province_cfg, country_cfg):

        if seed_cfg['use']:
            self.rng = np.random.default_rng(seed_cfg['seed'])
        else:
            self.rng = np.random.default_rng()

        self.city_cfg = city_cfg
        self.province_cfg = province_cfg
        self.country_cfg = country_cfg

    def tick(self):
        for country in self.countries:
            country.tick()

    def _build_population_groups(self, groups):
        return [
            PopulationGroup(
                size=group["size"],
                healthcare=group["base_healthcare"],
                healthcare_capacity=group["healthcare_capacity"],
                rng=self.rng,
            )
            for group in groups
        ]

    def _build_firms(self, firms):
        return [Firm(productivity = firm_data["productivity"],
                production_capacity = firm_data["production_capacity"],
                capital = firm_data["capital"],
                ownership = firm_data["ownership"],
                wage = firm_data["wage"],
                good = firm_data["good"],
                rng = self.rng) for firm_data in firms]

    def _build_city(self, city_data):
        populations = self._build_population_groups(city_data["groups"])
        firms = self._build_firms(city_data["firms"])
        return City(populations, city_data["name"], cfg=self.city_cfg, rng=self.rng, firms=firms)

    def _build_province(self, province_data):
        cities = [self._build_city(city_data) for city_data in province_data["cities"]]
        return Province(
            cities,
            province_data["area"],
            province_data["name"],
            cfg=self.province_cfg,
            rng=self.rng,
        )

    def build_provinces(self, data):
        return [self._build_province(province_data) for province_data in data["provinces"]]

    def build_sim(self):
        self.countries = []

        with open("input_data.json") as f:
            data = json.load(f)

        for country_data in data["countries"]:
            provinces = self.build_provinces(data=country_data)

            name = country_data["name"]
            cfg = self.country_cfg
            country_obj = Country(provinces, name, cfg, rng=self.rng)

            self.countries.append(country_obj)
        
    
