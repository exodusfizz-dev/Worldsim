"""Candidate scoring and weighted target selection helpers."""

from typing import Callable, Sequence

from model.protocols import DistanceProvider
from model.migration.types import T, WeightedTarget


class WeightedTargetSelector:
    """Build weighted candidates and draw weighted random selections."""

    def __init__(self, rng, distance_provider: DistanceProvider) -> None:
        self.rng = rng
        self.distance_provider = distance_provider

    def distance_weight(self, source_key: str, target_key: str) -> float:
        """Return non-negative distance weight."""
        return max(self.distance_provider.weight(source_key, target_key), 0.0)

    def weighted_choice_index(self, weights: Sequence[float]) -> int | None:
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

    def build_weighted_candidates(
        self,
        source_attractiveness: float,
        source_key: str,
        candidates: Sequence[T],
        attractiveness_of: Callable[[T], float],
        key_of: Callable[[T], str],
        include_candidate: Callable[[int, T], bool] | None = None,
    ) -> list[WeightedTarget[T]]:
        """Build weighted candidates from attractiveness gap and distance."""
        weighted_candidates: list[WeightedTarget[T]] = []
        for idx, candidate in enumerate(candidates):
            if include_candidate is not None and not include_candidate(idx, candidate):
                continue
            gap = attractiveness_of(candidate) - source_attractiveness
            if gap <= 0:
                continue
            weight = gap * self.distance_weight(source_key, key_of(candidate))
            if weight > 0:
                weighted_candidates.append(
                    WeightedTarget(index=idx, candidate=candidate, weight=weight)
                )
        return weighted_candidates

    def find_target_groups(
        self,
        source_attractiveness: float,
        source_city_key: str,
        groups,
        source_index: int,
    ):
        """Return eligible weighted target groups for intracity migration."""
        return self.build_weighted_candidates(
            source_attractiveness=source_attractiveness,
            source_key=source_city_key,
            candidates=groups,
            attractiveness_of=lambda group: group.migration_attractiveness,
            key_of=lambda _group: source_city_key,
            include_candidate=lambda idx, _group: idx != source_index,
        )
