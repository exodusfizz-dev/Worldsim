from dataclasses import dataclass, field

from model.migration import GroupMigrationEvent
from model.economy.labour.labour_market import LabourClearResult


@dataclass
class CityParams:
    """Immutable construction parameters for a city."""

    name: str
    population: object
    firms: list
    location: object
    id: int


@dataclass
class CityState:
    """Mutable city state updated during each simulation tick."""

    employed: int = 0
    last_food_deficit: float | None = None
    inv: dict[str, float] = field(default_factory=dict)
    treasury: float = 0.0
    labour_result: LabourClearResult | None = None
    starving: bool = False


class CityProperties:
    """Property handler for city class."""

    @property
    def employed(self) -> int:
        return self.state.employed


    @property
    def last_food_deficit(self) -> float | None:
        return self.state.last_food_deficit

    @property
    def inv(self) -> dict[str, float]:
        return self.state.inv

    @property
    def migration_attractiveness(self) -> float:
        if self.state.starving:
            return 0.0
        return self.population.migration_attractiveness

    @property
    def total_population(self) -> int:
        """Canonical city population used by migration and reporting."""
        return self.population.total_population

    @property
    def group_count(self) -> int:
        """Number of population groups currently in the city."""
        return self.population.group_count

    @property
    def name(self) -> str:
        return self.p.name

    @property
    def firms(self) -> list:
        return self.p.firms

    @property
    def location(self) -> object:
        return self.p.location

    @property
    def id(self) -> int:
        return self.p.id
