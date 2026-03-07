
from .load_maps import load_natural_earth_data

class WorldMap:
    '''Global geospatial index.'''

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self.world = load_natural_earth_data()

        self.countries = self.world["countries"]
        self.provinces = self.world["provinces"]
        self.cities = self.world["cities"]

        self.countries_index = self.countries.sindex
        self.provinces_index = self.provinces.sindex

        self._initialized = True
