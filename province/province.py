class Province:
    def __init__(self, cities, area, name, cfg, rng):
        
        self.rng = rng
        self.cfg = cfg
        self.name = name
        self.area = area  # in square kilometers
        self.cities = cities 



    def tick(self):
        for city in self.cities:
            city.tick()

    def city_migration(self, city):
        '''Handles migration between cities in the province.'''
        pass  # To be implemented in future versions