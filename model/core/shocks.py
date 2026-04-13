'''Shocks encompass natural disasters and economic shocks.'''

from typing import Protocol

# TODO: Implement economic shocks, which are caused by rng and spawned by core.


class Shock(Protocol):
    '''The framework for any kind of shock.
    Shocks arise as a class-instantiated object spawned by core, so they can affect anywhere in the world.'''
    def __init__(self):
        pass

class NaturalDisaster(Shock):
    '''Natural disasters are caused by rng and spawned by core.
    They have coordinates, a size and a magnitude.'''
    def __init__(self,
                 coordinates,
                 magnitude,
                 radius,
                 affected_provinces: list):
        self.coordinates = coordinates
        self.mag = magnitude
        self.rad = radius
        self.a_provs = affected_provinces
        self.type = "natural_disaster"
        self.a_cities = [city for prov in self.a_provs for city in prov.cities]

    def tick(self):
        # Do something to affected provinces.
        # The effect is increased by magnitude and the affected place closer relative to radius.
        # TODO: Implement effects of natural disasters.
        pass
