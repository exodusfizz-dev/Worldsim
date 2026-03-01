"""Basic first version of market. Owned by a city."""

from dataclasses import dataclass
from model.protocols import DistanceProvider, NeutralDistanceProvider


@dataclass
class MarketParams:
    city_id: str

@dataclass
class MarketState:
    pass

class Market:
    def __init__(self, params: MarketParams, distance_provider, rng):
        self.p = params
        self.rng = rng

        self.distance_provider = distance_provider or NeutralDistanceProvider()

    @classmethod
    def build_from(cls,
        rng,
        city_id: str | None = None,
        distance_provider: DistanceProvider | None = None,
        ) -> "Market":

        return cls(
            params=MarketParams(
                city_id=city_id,
            ),
            distance_provider=distance_provider,
            rng=rng,
        )
