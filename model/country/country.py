'''Handles country object.'''

from dataclasses import dataclass

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

        self.market = SupplyChain.build_from(rng=rng)

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
