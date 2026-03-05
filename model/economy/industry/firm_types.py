from dataclasses import dataclass, field

@dataclass(frozen=True)
class GoodDemandItem:
    """Demand for a single input material."""
    good: str
    shortfall: float

@dataclass
class GoodDemandResult:
    """All input demands from a single firm."""
    firm_good: str  # What firm produces
    demands: list[GoodDemandItem] = field(default_factory=list)

    def has_demand(self) -> bool:
        return any(d.shortfall > 0 for d in self.demands)