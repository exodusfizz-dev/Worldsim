"""Distance weighting protocols for migration."""

from typing import Protocol

class DistanceProvider(Protocol):
    """Interface for distance/friction weighting."""

    def weight(self, source_key: str, target_key: str) -> float:
        """Return multiplicative distance weight for a source->target pair."""


class NeutralDistanceProvider(DistanceProvider):
    """Default distance provider with no friction."""

    def weight(self, source_key: str, target_key: str) -> float:
        return 1.0

class EuclideanDistanceProvider(DistanceProvider):
    def __init__(self, location_service):
        self.location_service = location_service

    def distance(self, from_entity: str, to_entity: str) -> float:
        pass
