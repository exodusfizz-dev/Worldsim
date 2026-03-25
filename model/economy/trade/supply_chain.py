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
    item: str
    amount: float
    price: float

class SupplyChain:
    def __init__(self, params: MarketParams, firms, cities, distance_provider, rng):
        self.p = params
        self.state = MarketState()
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

    def demand(self) -> list[MarketBuyOrder]:
        '''Allows firms to request goods for manufacturing from other firms/cities.'''
        market_buyers: list[MarketBuyOrder] = []
        for firm in self.firms:
            demand_result = firm.good_demand()
            if not demand_result.has_demand():
                continue
            for demand in demand_result.demands:
                market_buyers.append(MarketBuyOrder(firm, demand.good, demand.shortfall))
        return market_buyers

    def clear_chain(self, city_distances: dict[tuple[int, int], float]):
        '''Clears the supply chain by matching demand and supply.
        May have continual contracts in the future.'''
        demands = self.demand()
        per_good_suppliers = self.supply()

        for demand in demands:
            valid_suppliers = per_good_suppliers.get(demand.item, [])
            if not valid_suppliers:
                continue
            for supplier in valid_suppliers:
                if supplier.amount <= 0:
                    valid_suppliers.remove(supplier)
                    continue
                if supplier.city.p.id == demand.firm.p.id:
                    valid_suppliers.remove(supplier)
                    continue

            self.match_demand_supply(valid_suppliers, demand, city_distances)

    def supply(self) -> dict[str, list[MarketSellOrder]]:
        '''Allows cities (and eventually firms) to offer goods for sale.'''
        per_good_suppliers: dict[str, list[MarketSellOrder]] = {}
        for city in self.cities:
            for item in city.inv:
                if item not in per_good_suppliers:
                    per_good_suppliers[item] = []
                price = 100 # Placeholder for testing.
                per_good_suppliers[item].append(MarketSellOrder(city, item, city.inv[item], price))

        return per_good_suppliers

    def match_demand_supply(self,
                            valid_suppliers: list[MarketSellOrder],
                            demand: MarketBuyOrder,
                            city_distances: dict[tuple[int, int], float]):
        '''Matches a single demand and supply order.'''

        energy_price = 1.0
        valid_suppliers.sort(
            key=lambda s: (
            city_distances.get((s.city.p.id, demand.firm.p.id), 1000)
            * energy_price
            + s.price
            )
        )
        best_supplier = valid_suppliers[0]
        to_buy = min(demand.shortfall, best_supplier.amount)
        best_supplier.city.sell_to_firm(demand.firm, demand.item, to_buy, best_supplier.price)
        best_supplier.amount -= to_buy
