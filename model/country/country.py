class Country:
    '''
    Country object owns provinces.
    '''
    def __init__(self, provinces, name, cfg, rng):
        self.provinces = provinces
        self.name = name
        self.CFG = cfg
        self.rng = rng

    def tick(self):
        for province in self.provinces:
            province.tick()