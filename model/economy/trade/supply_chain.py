"""Basic first version of market. Owned by a city."""

from dataclasses import dataclass
from model.protocols import DistanceProvider, NeutralDistanceProvider

@dataclass
class MarketParams:
    pass

@dataclass
class MarketState:
    pass

@dataclass
class MarketBuyOrder:
    '''Single request from a firm. '''
    firm: "Firm"
    item: str
    shortfall: float

@dataclass
class MarketSellOrder:
    '''Single offer from a city (or firm in the future).'''
    city: "City"
    item: list[str]
    amount: list[float]

class SupplyChain:
    def __init__(self, params: MarketParams, firms, cities, distance_provider, rng):
        self.p = params
        self.rng = rng
        self.firms = firms
        self.cities = cities

        self.distance_provider = distance_provider or NeutralDistanceProvider()

    @classmethod
    def build_from(cls,
        rng,
        firms: list,
        cities: list,
        distance_provider: DistanceProvider | None = None,
        ) -> "SupplyChain":

        return cls(
            params=MarketParams(),
            firms=firms,
            cities=cities,
            distance_provider=distance_provider,
            rng=rng,
        )

    def request(self) -> list[MarketBuyOrder]:
        '''Allows firms to request goods for manufacturing from other firms/cities.'''
        market_buyers: list[MarketBuyOrder] = []
        for firm in self.firms:
            demand_result = firm.good_demand()
            if not demand_result.has_demand():
                continue
            for item in demand_result:
                market_buyers.append(MarketBuyOrder(firm, item, demand_result.shortfall))
        return market_buyers

    def clear_chain(self):
        requests = self.request()
        suppliers = self.offer()

        for request in requests:
            for supply in suppliers:
                pass

    def offer(self) -> list[MarketSellOrder]:
        market_sellers: list[MarketSellOrder] = []
        for city in self.cities:
            for item in city.inv:
                pass

        return market_sellers
