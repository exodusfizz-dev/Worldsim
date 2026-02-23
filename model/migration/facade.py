"""Public migration facade preserving the existing API."""

from typing import TYPE_CHECKING, Sequence

from model.migration.allocation import MigrationAllocator
from model.migration.engines import IntercityMigrationEngine, IntergroupMigrationEngine
from model.migration.options import MigrationOptions
from model.migration.protocols import DistanceProvider, NeutralDistanceProvider
from model.migration.selectors import WeightedTargetSelector
from model.migration.types import GroupMigrationEvent

if TYPE_CHECKING:
    from model.city.city import City


class Migration:
    """Migration engine supporting intracity and intercity group transfers."""

    def __init__(
        self,
        rng,
        options: MigrationOptions | None = None,
        distance_provider: DistanceProvider | None = None,
    ) -> None:
        self.rng = rng
        cfg = options or MigrationOptions()
        self.options = MigrationOptions(
            intergroup_rate=max(min(cfg.intergroup_rate, 1.0), 0.0),
            intercity_rate=max(min(cfg.intercity_rate, 1.0), 0.0),
        )
        self.distance_provider = distance_provider or NeutralDistanceProvider()

        self.selector = WeightedTargetSelector(
            rng=self.rng,
            distance_provider=self.distance_provider,
        )
        self.allocator = MigrationAllocator(rng=self.rng)
        self.intergroup_engine = IntergroupMigrationEngine(
            selector=self.selector,
            allocator=self.allocator,
        )
        self.intercity_engine = IntercityMigrationEngine(
            selector=self.selector,
            allocator=self.allocator,
        )

    @classmethod
    def for_intergroup(
        cls,
        rng,
        intergroup_rate: float,
        distance_provider: DistanceProvider | None = None,
    ) -> "Migration":
        """Create a service with only intergroup migration enabled."""
        return cls(
            rng=rng,
            options=MigrationOptions(intergroup_rate=intergroup_rate, intercity_rate=0.0),
            distance_provider=distance_provider,
        )

    @classmethod
    def for_intercity(
        cls,
        rng,
        intercity_rate: float,
        distance_provider: DistanceProvider | None = None,
    ) -> "Migration":
        """Create a service with only intercity migration enabled."""
        return cls(
            rng=rng,
            options=MigrationOptions(intergroup_rate=0.0, intercity_rate=intercity_rate),
            distance_provider=distance_provider,
        )

    @property
    def intergroup_rate(self) -> float:
        return self.options.intergroup_rate

    @property
    def intercity_rate(self) -> float:
        return self.options.intercity_rate

    def choose_target_city(self, source_city: "City", candidates: Sequence["City"]) -> "City | None":
        return self.intercity_engine.choose_target_city(source_city=source_city, candidates=candidates)

    def migrate_within_city(self, city: "City") -> list[GroupMigrationEvent]:
        return self.intergroup_engine.migrate_within_city(
            city=city,
            intergroup_rate=self.intergroup_rate,
        )

    def migrate_between_cities(self, source_city: "City", target_city: "City") -> list[GroupMigrationEvent]:
        return self.intercity_engine.migrate_between_cities(
            source_city=source_city,
            target_city=target_city,
            intercity_rate=self.intercity_rate,
        )
