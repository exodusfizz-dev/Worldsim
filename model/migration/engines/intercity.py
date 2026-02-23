"""Intercity migration engine."""

from typing import TYPE_CHECKING, Sequence

from model.migration.types import GroupMigrationEvent

if TYPE_CHECKING:
    from model.city.city import City
    from model.migration.allocation import MigrationAllocator
    from model.migration.selectors import WeightedTargetSelector


class IntercityMigrationEngine:
    """Orchestrates migration between cities."""

    def __init__(
        self,
        selector: "WeightedTargetSelector",
        allocator: "MigrationAllocator",
    ) -> None:
        self.selector = selector
        self.allocator = allocator

    def choose_target_city(
        self,
        source_city: "City",
        candidates: Sequence["City"],
    ) -> "City | None":
        """Choose a migration target city using weighted random selection."""
        weighted = self.selector.build_weighted_candidates(
            source_attractiveness=source_city.migration_attractiveness,
            source_key=source_city.name,
            candidates=candidates,
            attractiveness_of=lambda city: city.migration_attractiveness,
            key_of=lambda city: city.name,
        )
        if not weighted:
            return None

        index = self.selector.weighted_choice_index([target.weight for target in weighted])
        if index is None:
            return None
        return weighted[index].candidate

    def migrate_between_cities(
        self,
        source_city: "City",
        target_city: "City",
        intercity_rate: float,
    ) -> list[GroupMigrationEvent]:
        """Move integer migrants from source city groups to target city groups."""
        events: list[GroupMigrationEvent] = []
        if intercity_rate <= 0:
            return events
        if not source_city.populations or not target_city.populations:
            return events
        if source_city.total_population <= 0:
            return events

        gap = target_city.migration_attractiveness - source_city.migration_attractiveness
        if gap <= 0:
            return events

        p_move = intercity_rate * gap * self.selector.distance_weight(
            source_city.name, target_city.name
        )
        if p_move <= 0:
            return events

        for source_index, source_group in enumerate(source_city.populations):
            expected_move = self.allocator.draw_count(
                population=source_group.size,
                probability=p_move,
            )
            if expected_move <= 0:
                continue

            if source_index < len(target_city.populations):
                moved = self.allocator.safe_transfer(
                    source_group=source_group,
                    target_group=target_city.populations[source_index],
                    requested_amount=expected_move,
                )
                if moved > 0:
                    events.append(
                        GroupMigrationEvent(
                            source_city=source_city.name,
                            source_group_index=source_index,
                            target_city=target_city.name,
                            target_group_index=source_index,
                            amount=moved,
                            channel="intercity",
                        )
                    )
                continue

            for target_index, chunk in self.allocator.fallback_split(
                amount=expected_move,
                destination_groups=target_city.populations,
            ):
                moved = self.allocator.safe_transfer(
                    source_group=source_group,
                    target_group=target_city.populations[target_index],
                    requested_amount=chunk,
                )
                if moved <= 0:
                    continue
                events.append(
                    GroupMigrationEvent(
                        source_city=source_city.name,
                        source_group_index=source_index,
                        target_city=target_city.name,
                        target_group_index=target_index,
                        amount=moved,
                        channel="intercity",
                    )
                )

        return events
