import json
from population import PopulationGroup
from city import City
from province import Province


class Core:
    def __init__ (self):
        self.provinces = []
        
        with open("population_groups.json") as f:
            data = json.load(f)
            for province in data["provinces"]:

                cities = []
                province_name = province["name"]
                province_area = province["area"]

                for city in province["cities"]:
                    populations = []
                    city_name = city["name"]

                    for group in city["groups"]:
                        population = PopulationGroup(size=group["size"], healthcare=group["base_healthcare"], healthcare_capacity=group["healthcare_capacity"])
                        populations.append(population)

                    city = City(populations)
                    cities.append((city, city_name))

                province = Province(cities, province_area)
                self.provinces.append((province, province_name))

    def tick(self):
        for province, _ in self.provinces:
            province.tick()
            