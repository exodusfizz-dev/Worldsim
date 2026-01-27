import json
from population import PopulationGroup
from city import City


class Core:
    def __init__ (self):
        self.cities = []
        
        with open("population_groups.json") as f:
            data = json.load(f)
        
        for city in data["cities"]:
            populations = []
            city_name = city["name"]

            for group in city["groups"]:
                populations.append(PopulationGroup(size=group["size"], healthcare=group["base_healthcare"], healthcare_capacity=group["healthcare_capacity"]))
            
            city = City(populations)
            self.cities.append((city, city_name))



    def tick(self):
        for city, _ in self.cities:
            city.tick()

            