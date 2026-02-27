'''Basic first version of market. Owned by a city. Can request goods from other cities.'''

from typing import TYPE_CHECKING, Sequence, Callable

from dataclasses import dataclass
from model.protocols import DistanceProvider, NeutralDistanceProvider

if TYPE_CHECKING:
    pass


@dataclass
class MarketParams:
    city_key: str

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
        city_key: str,
        distance_provider: DistanceProvider | None = None,
        ) -> "Market":
        return cls(
            params=MarketParams(
                city_key=city_key,
            ),
            distance_provider=distance_provider,
            rng=rng,
        )
