"""Basic first version of market. Owned by a city."""

from dataclasses import dataclass
from model.protocols import DistanceProvider, NeutralDistanceProvider


@dataclass
class MarketParams:
    pass

@dataclass
class MarketState:
    pass

class SupplyChain:
    def __init__(self, params: MarketParams, firms, distance_provider, rng):
        self.p = params
        self.rng = rng
        self.firms = firms

        self.distance_provider = distance_provider or NeutralDistanceProvider()

    @classmethod
    def build_from(cls,
        rng,
        firms: list,
        distance_provider: DistanceProvider | None = None,
        ) -> "SupplyChain":

        return cls(
            params=MarketParams(),
            firms=firms,
            distance_provider=distance_provider,
            rng=rng,
        )

    def request(self):
        '''Allows firms to request goods for manufacturing from other firms/cities.'''
        for firm in self.firms:
            demand_result = firm.good_demand()
            if not demand_result.has_demand():
                continue
            for item in demand_result:
                pass

