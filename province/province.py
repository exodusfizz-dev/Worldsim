class Province:
    def __init__(self, cities, area):

        self.area = area  # in square kilometers
        self.cities = cities 


    def tick(self):
        for city, _ in self.cities:
            city.tick()

    def city_migration(self, city):
        '''Handles migration between cities in the province.'''
        pass  # To be implemented in future versions