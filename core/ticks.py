import json
from population import PopulationGroup
from city import City
from province import Province
import numpy as np

class Core:
    def __init__(self, seed_cfg, city_cfg, province_cfg):

        if seed_cfg['use']:
            self.rng = np.random.default_rng(seed_cfg['seed'])

        self.city_cfg = city_cfg
        self.province_cfg = province_cfg
        self.build_sim()

    def tick(self):
        for province in self.provinces:
            province.tick()
            

    def build_sim(self):
        self.provinces = []
        
        with open("population_groups.json") as f:
            data = json.load(f)
            for province_data in data["provinces"]:

                cities = []
                province_area = province_data["area"]
                province_name = province_data["name"]

                for city in province_data["cities"]:
                    populations = []
                    city_name = city["name"]

                    for group in city["groups"]:
                        population_obj = PopulationGroup(size=group["size"], healthcare=group["base_healthcare"], healthcare_capacity=group["healthcare_capacity"], rng=self.rng)
                        populations.append(population_obj)

                    city_obj = City(populations, city_name, cfg=self.city_cfg, rng=self.rng)
                    cities.append(city_obj)

                province_obj = Province(cities, province_area, province_name, cfg=self.province_cfg, rng=self.rng)
                self.provinces.append(province_obj)