import json
from population import PopulationGroup
from city import City
from province import Province


class Core:
    def __init__ (self):
        self.build_sim()

    def tick(self):
        for province in self.provinces:
            province.tick()
            

    def build_sim(self):
        self.provinces = []
        
        with open("population_groups.json") as f:
            data = json.load(f)
            for province in data["provinces"]:

                cities = []
                province_area = province["area"]
                province_name = province["name"]

                for city in province["cities"]:
                    populations = []
                    city_name = city["name"]

                    for group in city["groups"]:
                        population = PopulationGroup(size=group["size"], healthcare=group["base_healthcare"], healthcare_capacity=group["healthcare_capacity"])
                        populations.append(population)

                    city = City(populations, city_name)
                    cities.append(city)

                province = Province(cities, province_area, province_name)
                self.provinces.append(province)