'''Handles country object.'''

import networkx as nx

from .country_properties import (CountryProperties,
                                              CountryParams)
from model.economy.trade import SupplyChain

class Country(CountryProperties):
    '''
    Country object owns provinces.
    '''
    def __init__(self, params: CountryParams, cfg, rng):
        self.p = params
        self.cfg = cfg
        self.rng = rng

        self.city_distances = self._build_city_distances()

        all_firms = [
            firm
            for province in self.provinces
            for city in province.cities
            for firm in city.firms
        ]
        all_cities = [
            city
            for province in self.provinces
            for city in province.cities
        ]
        self.market = SupplyChain.build_from(rng=rng, firms=all_firms, cities=all_cities)

    @classmethod
    def from_dict(cls, country_data, provinces, rng, cfg) -> "Country":
        return cls(
            params=CountryParams(
                name=country_data["name"],
                provinces=provinces
            ),
            cfg=cfg,
            rng=rng)

    def tick(self):
        for province in self.p.provinces:
            province.tick()
        self.market.clear_chain(city_distances=self.city_distances)

    def _build_city_distances(self) -> dict[tuple[int, int], float]:
        city_distances = {}
        for province in self.p.provinces:
            for city1 in province.cities:
                for city2 in province.cities:
                    if city1 == city2:
                        continue
                    pair = tuple(sorted((city1.p.id, city2.p.id)))
                    if pair not in city_distances:
                        dist = self.distance_function(city1, city2)
                        city_distances[pair] = dist
        return city_distances

    def distance_function(self, city1, city2) -> float:
        '''Calculate distance between two cities.'''
        # Placeholder: use Euclidean distance based on city locations.
        #TODO: Replace with networkx using NE road data.

        loc1 = city1.location
        loc2 = city2.location
        return ((loc1.x - loc2.x) ** 2 + (loc1.y - loc2.y) ** 2) ** 0.5
