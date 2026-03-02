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
    def __init__(self, params: MarketParams, distance_provider, rng):
        self.p = params
        self.rng = rng

        self.distance_provider = distance_provider or NeutralDistanceProvider()

    @classmethod
    def build_from(cls,
        rng,
        distance_provider: DistanceProvider | None = None,
        ) -> "SupplyChain":

        return cls(
            params=MarketParams(),
            distance_provider=distance_provider,
            rng=rng,
        )

    def request(self):
        pass
