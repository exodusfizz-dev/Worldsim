from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.city.city import City
    from model.economy.industry.firm import Firm

@dataclass
class MarketBuyOrder:
    """Single bid from a firm for one input good."""
    firm: "Firm"
    item: str
    shortfall: float
    price: float

@dataclass
class MarketSellOrder:
    """Single ask from a city for one good."""
    city: "City"
    item: str
    amount: float
    price: float

@dataclass
class SingleHistoryItem:
    """Per-tick market snapshot for one good."""
    top_bid: float
    top_ask: float
    agreed_price: float
    quantity: float
    timestamp: int
