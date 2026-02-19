"""Migration service used by city and province simulation steps.

The service is configured with explicit channels (intergroup/intercity) so each
owner only enables the migration modes it needs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Protocol, Sequence, TypeVar

if TYPE_CHECKING:
    from model.city.city import City
    from model.population.group import PopulationGroup

T = TypeVar("T")


class DistanceProvider(Protocol):
    """Interface for optional distance/friction weighting."""

    def weight(self, source_key: str, target_key: str) -> float:
        """Return multiplicative distance weight for a source->target pair."""


class NeutralDistanceProvider:
    """Default distance provider with no friction."""

    def weight(self, source_key: str, target_key: str) -> float:
        return 1.0


@dataclass(frozen=True)
class MigrationConfig:
    """Migration channel configuration.

    Rates are probabilities in [0, 1] and are clamped by ``Migration``.
    """

    intergroup_rate: float = 0.0
    intercity_rate: float = 0.0


@dataclass(frozen=True)
class GroupMigrationEvent:
    """Record of a single group-to-group transfer."""

    source_city: str
    source_group_index: int
    target_city: str
    target_group_index: int
    amount: int
    channel: str


class Migration:
    """Migration engine supporting intracity and intercity group transfers."""

    def __init__(
        self,
        rng,
        config: MigrationConfig | None = None,
        distance_provider: DistanceProvider | None = None,
    ) -> None:

        self.rng = rng
        cfg = config or MigrationConfig()
        self.config = MigrationConfig(
            intergroup_rate=max(min(cfg.intergroup_rate, 1.0), 0.0),
            intercity_rate=max(min(cfg.intercity_rate, 1.0), 0.0),
        )
        self.distance_provider = distance_provider or NeutralDistanceProvider()

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
            config=MigrationConfig(intergroup_rate=intergroup_rate, intercity_rate=0.0),
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
            config=MigrationConfig(intergroup_rate=0.0, intercity_rate=intercity_rate),
            distance_provider=distance_provider,
        )

    @property
    def intergroup_rate(self) -> float:
        return self.config.intergroup_rate

    @property
    def intercity_rate(self) -> float:
        return self.config.intercity_rate

    def _distance_weight(self, source_key: str, target_key: str) -> float:
        """Return non-negative distance weight."""
        return max(self.distance_provider.weight(source_key, target_key), 0.0)

    def _draw_count(self, population: float, probability: float) -> int:
        """Draw integer migrants using RNG binomial when available."""
        n = max(int(population), 0)
        p = max(min(probability, 1.0), 0.0)
        if n == 0 or p <= 0:
            return 0

        if self.rng is not None and hasattr(self.rng, "binomial"):
            return int(self.rng.binomial(n, p))
        return int(round(n * p))

    def _safe_transfer(
        self,
        source_group: PopulationGroup,
        target_group: PopulationGroup,
        requested_amount: int,
    ) -> int:
        """Move integer population safely between groups."""
        if requested_amount <= 0:
            return 0
        available = max(int(source_group.size), 0)
        moved = min(requested_amount, available)
        if moved <= 0:
            return 0
        source_group.size -= moved
        target_group.size += moved
        return moved

    def _weighted_choice_index(self, weights: Sequence[float]) -> int | None:
        """Select index from non-negative weights using RNG."""
        total = sum(weights)
        if total <= 0:
            return None
        if self.rng is not None and hasattr(self.rng, "uniform"):
            threshold = float(self.rng.uniform(0.0, total))
        else:
            threshold = total / 2.0
        running = 0.0
        for idx, weight in enumerate(weights):
            running += weight
            if threshold <= running:
                return idx
        return len(weights) - 1

    def _build_weighted_candidates(
        self,
        source_attractiveness: float,
        source_key: str,
        candidates: Sequence[T],
        attractiveness_of: Callable[[T], float],
        key_of: Callable[[T], str],
        include_candidate: Callable[[int, T], bool] | None = None,
    ) -> list[tuple[int, T, float]]:

        """Build weighted candidates from attractiveness gap and distance weight."""
        weighted_candidates: list[tuple[int, T, float]] = []
        for idx, candidate in enumerate(candidates):
            if include_candidate is not None and not include_candidate(idx, candidate):
                continue
            gap = attractiveness_of(candidate) - source_attractiveness
            if gap <= 0:
                continue
            distance_weight = self._distance_weight(source_key, key_of(candidate))
            weight = gap * distance_weight
            if weight > 0:
                weighted_candidates.append((idx, candidate, weight))
        return weighted_candidates

    def _candidate_groups(
        self,
        source_attractiveness: float,
        source_city_key: str,
        groups: Sequence[PopulationGroup],
        source_index: int,
    ) -> list[tuple[int, PopulationGroup, float]]:

        """Return eligible target groups for intracity migration."""
        return self._build_weighted_candidates(
            source_attractiveness=source_attractiveness,
            source_key=source_city_key,
            candidates=groups,
            attractiveness_of=lambda group: group.migration_attractiveness,
            key_of=lambda _group: source_city_key,
            include_candidate=lambda idx, _group: idx != source_index,
        )

    def _fallback_split(
        self,
        amount: int,
        destination_groups: Sequence[PopulationGroup],
    ) -> list[tuple[int, int]]:
        """Split integer amount across destination groups by size share."""
        if amount <= 0 or not destination_groups:
            return []

        total_size = sum(max(int(group.size), 0) for group in destination_groups)
        if total_size <= 0:
            base = amount // len(destination_groups)
            rem = amount % len(destination_groups)
            out = [(idx, base) for idx in range(len(destination_groups))]
            for idx in range(rem):
                out[idx] = (out[idx][0], out[idx][1] + 1)
            return out

        # Largest remainder allocation for integer conservation.
        alloc: list[int] = []
        remainders: list[tuple[int, float]] = []
        assigned = 0
        for idx, group in enumerate(destination_groups):
            exact = amount * (max(int(group.size), 0) / total_size)
            floor_val = int(exact)
            alloc.append(floor_val)
            assigned += floor_val
            remainders.append((idx, exact - floor_val))
        remainders.sort(key=lambda x: x[1], reverse=True)
        for i in range(amount - assigned):
            alloc[remainders[i][0]] += 1
        return [(idx, val) for idx, val in enumerate(alloc) if val > 0]

    def choose_target_city(self, source_city: City, candidates: Sequence[City]) -> City | None:
        """Choose a migration target city using weighted random selection."""
        weighted = self._build_weighted_candidates(
            source_attractiveness=source_city.migration_attractiveness,
            source_key=source_city.name,
            candidates=candidates,
            attractiveness_of=lambda city: city.migration_attractiveness,
            key_of=lambda city: city.name,
        )
        if not weighted:
            return None

        index = self._weighted_choice_index([weight for _, _, weight in weighted])
        if index is None:
            return None
        _, chosen_city, _ = weighted[index]
        return chosen_city

    def migrate_within_city(self, city: City) -> list[GroupMigrationEvent]:
        """Move integer migrants between groups inside one city."""
        events: list[GroupMigrationEvent] = []
        if self.intergroup_rate <= 0:
            return events

        for source_index, source_group in enumerate(city.populations):
            targets = self._candidate_groups(
                source_attractiveness=source_group.migration_attractiveness,
                source_city_key=city.name,
                source_index=source_index,
                groups=city.populations,
            )
            if not targets:
                continue

            target_choice = self._weighted_choice_index([weight for _, _, weight in targets])
            if target_choice is None:
                continue
            target_index, target_group, _ = targets[target_choice]

            moved = self._safe_transfer(
                source_group=source_group,
                target_group=target_group,
                requested_amount=self._draw_count(source_group.size, self.intergroup_rate),
            )
            if moved <= 0:
                continue

            events.append(
                GroupMigrationEvent(
                    source_city=city.name,
                    source_group_index=source_index,
                    target_city=city.name,
                    target_group_index=target_index,
                    amount=moved,
                    channel="intergroup",
                )
            )

        return events

    def migrate_between_cities(self, source_city: City, target_city: City) -> list[GroupMigrationEvent]:
        """Move integer migrants from source city groups to target city groups."""
        events: list[GroupMigrationEvent] = []
        if self.intercity_rate <= 0:
            return events
        if not source_city.populations or not target_city.populations:
            return events
        if source_city.total_population <= 0:
            return events

        gap = target_city.migration_attractiveness - source_city.migration_attractiveness
        if gap <= 0:
            return events

        p_move = self.intercity_rate * gap * self._distance_weight(source_city.name, target_city.name)
        if p_move <= 0: # p_move is probability per person to move
            return events

        for source_index, source_group in enumerate(source_city.populations):
            expected_move = self._draw_count(population=source_group.size, probability=p_move)
            if expected_move <= 0:
                continue

            if source_index < len(target_city.populations):
                moved = self._safe_transfer(
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

            for target_index, chunk in self._fallback_split(amount=expected_move,
                                    destination_groups=target_city.populations):
                moved = self._safe_transfer(
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
