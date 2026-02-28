"""Basic first version of market. Owned by a city."""

from dataclasses import dataclass
from model.protocols import DistanceProvider, NeutralDistanceProvider


@dataclass
class MarketParams:
    city_id: str

    @property
    def city_key(self) -> str:
        """Compatibility alias while callers migrate from city_key."""
        return self.city_id

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
        city_key: str | None = None,
        distance_provider: DistanceProvider | None = None,
        ) -> "Market":
        resolved_city_id = city_id if city_id is not None else city_key
        if resolved_city_id is None:
            raise ValueError("Market.build_from requires city_id (or legacy city_key).")
        return cls(
            params=MarketParams(
                city_id=resolved_city_id,
            ),
            distance_provider=distance_provider,
            rng=rng,
        )
