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
        source_group_count = source_city.population.group_count
        target_group_count = target_city.population.group_count

        gap = target_city.migration_attractiveness - source_city.migration_attractiveness
        if gap <= 0:
            return events

        p_move = intercity_rate * gap * self.selector.distance_weight(
            source_city.name,
            target_city.name,
        )
        if p_move <= 0:
            return events

        source_sizes = source_city.population.sizes
        target_sizes = target_city.population.sizes

        for source_index in range(source_group_count):
            amount = self.allocator.draw_count(
                population=source_sizes[source_index],
                probability=p_move,
            )
            if amount <= 0:
                continue

            if source_index < target_group_count:
                source_city.population.sizes[source_index] -= amount
                target_city.population.sizes[source_index] += amount

                events.append(
                GroupMigrationEvent(
                    source_city=source_city.name,
                    source_group_index=source_index,
                    target_city=target_city.name,
                    target_group_index=source_index,
                    amount=int(amount),
                    channel="intercity",
                )
            )

                continue
            # If the migrants cannot move to the equivalent index group, then the fallback is used.
            for target_index, split_amount in self.allocator.fallback_split(
                amount=amount,
                destination_sizes=target_sizes,
            ):
                source_city.population.sizes[source_index] -= amount
                target_city.population.sizes[target_index] += amount

                events.append(
                GroupMigrationEvent(
                    source_city=source_city.name,
                    source_group_index=source_index,
                    target_city=target_city.name,
                    target_group_index=target_index,
                    amount=int(split_amount),
                    channel="intercity",
                )
            )


        return events
