"""Intergroup migration engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from model.migration.types import GroupMigrationEvent

if TYPE_CHECKING:
    from model.city.city import City
    from model.migration.allocation import MigrationAllocator
    from model.migration.selectors import WeightedTargetSelector


class IntergroupMigrationEngine:
    """Orchestrates within-city migration between population groups."""

    def __init__(
        self,
        selector: "WeightedTargetSelector",
        allocator: "MigrationAllocator",
    ) -> None:
        self.selector = selector
        self.allocator = allocator

    def migrate_within_city(self, city: "City", intergroup_rate: float) -> list[GroupMigrationEvent]:
        """Move integer migrants between groups inside one city."""

        events: list[GroupMigrationEvent] = []
        if intergroup_rate <= 0:
            return events

        for source_index, source_group in enumerate(city.populations):
            targets = self.selector.find_target_groups(
                source_attractiveness=source_group.migration_attractiveness,
                source_city_key=city.name,
                source_index=source_index,
                groups=city.populations,
            )
            if not targets:
                continue

            target_choice = self.selector.weighted_choice_index(
                [target.weight for target in targets]
            )
            if target_choice is None:
                continue
            target = targets[target_choice]

            moved = self.allocator.safe_transfer(
                source_group=source_group,
                target_group=target.candidate,
                requested_amount=self.allocator.draw_count(source_group.size, intergroup_rate),
            )
            if moved <= 0:
                continue

            events.append(
                GroupMigrationEvent(
                    source_city=city.name,
                    source_group_index=source_index,
                    target_city=city.name,
                    target_group_index=target.index,
                    amount=moved,
                    channel="intergroup",
                )
            )

        return events
