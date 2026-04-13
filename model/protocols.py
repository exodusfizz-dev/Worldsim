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
    """Distance provider using Euclidean distance.
    
    TODO: Not yet implemented. Will be replaced with networkx road-based routing.
    Consider removing this class until road network distance calculation is ready.
    """
    
    def __init__(self, location_service):
        self.location_service = location_service

    def weight(self, source_key: str, target_key: str) -> float:
        """Return distance weight (not implemented)."""
        raise NotImplementedError(
            "EuclideanDistanceProvider.weight() is not implemented. "
            "Scheduled for replacement with networkx-based road routing."
        )
