from dataclasses import dataclass, field

from migration import GroupMigrationEvent
from model.economy.labour.labour_market import LabourClearResult



@dataclass
class CityParams:
    """Immutable construction parameters for a city."""

    name: str
    populations: list
    firms: list
    location: object
    id: int


@dataclass
class CityState:
    """Mutable city state updated during each simulation tick."""

    employed: int = 0
    migrations: list[GroupMigrationEvent] = field(default_factory=list)
    last_food_deficit: float | None = None
    inv: dict[str, float] = field(default_factory=dict)
    treasury: float = 0.0
    labour_result: LabourClearResult | None = None
    starving: bool = False


class CityProperties:
    '''Property handler for city class.'''
    @property
    def employed(self) -> int:
        return self.state.employed

    @property
    def migrations(self) -> list[GroupMigrationEvent]:
        return self.state.migrations

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
        return sum(group.migration_attractiveness for group in self.p.populations)


    @property
    def total_population(self) -> float:
        """Canonical city population used by migration and reporting."""
        return sum(group.size for group in self.populations)

    @property
    def group_count(self) -> int:
        """Number of population groups currently in the city."""
        return len(self.p.populations)

    @property
    def name(self) -> str:
        return self.p.name

    @property
    def populations(self) -> list:
        return self.p.populations

    @property
    def firms(self) -> list:
        return self.p.firms

    @property
    def location(self) -> object:
        return self.p.location

    @property
    def id(self) -> int:
        return self.p.id
