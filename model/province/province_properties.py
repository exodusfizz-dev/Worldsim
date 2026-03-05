'''Property accessors, state and params for province objects'''

from dataclasses import dataclass, field
from model.migration import GroupMigrationEvent

@dataclass
class ProvinceParams:
    """Immutable construction parameters for a province."""

    name: str
    area: int
    cities: list


@dataclass
class ProvinceState:
    """Mutable province-level runtime state."""

    migrations: list[GroupMigrationEvent] = field(default_factory=list)

@dataclass
class ProvinceProperties:
    @property
    def name(self) -> str:
        return self.p.name

    @property
    def cities(self) -> list:
        return self.p.cities

    @property
    def area(self) -> int:
        return self.p.area

    @property
    def migrations(self) -> list[GroupMigrationEvent]:
        """Read-only log of intercity migration events for the latest tick."""
        return self.state.migrations
