import json
from model.city import City
from model.province import Province
import numpy as np
from model.industry import Firm
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

 

    def build_provinces(self, data):
        provinces = []

        for province_data in data["provinces"]:

            cities = []
            province_area = province_data["area"]
            province_name = province_data["name"]

            for city in province_data["cities"]:
                populations = []
                firms = []
                city_name = city["name"]

                for group in city["groups"]: # Creates list of population groups in city
                        population_obj = PopulationGroup(
                                                         size=group["size"], 
                                                         healthcare=group["base_healthcare"], 
                                                         healthcare_capacity=group["healthcare_capacity"], 
                                                         rng=self.rng
                                                         )
                        populations.append(population_obj)

                for firm in city["firms"]: # Creates list of firms in city
                        firm_obj = Firm(
                                        productivity = firm["productivity"],
                                        production_capacity = firm["production_capacity"],
                                        capital = firm["capital"],
                                        ownership = firm["ownership"],
                                        wage = firm["wage"],
                                        good = firm["good"],
                                        rng = self.rng
                                         )
                        firms.append(firm_obj)

                city_obj = City(populations, city_name, cfg=self.city_cfg, rng=self.rng, firms=firms)
                cities.append(city_obj)
                    
                province_obj = Province(cities, province_area, province_name, cfg=self.province_cfg, rng=self.rng)
                provinces.append(province_obj)
        
        return provinces

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
        
    