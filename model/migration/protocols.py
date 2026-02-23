"""Distance weighting protocols for migration."""

from typing import Protocol


class DistanceProvider(Protocol):
    """Interface for optional distance/friction weighting."""

    def weight(self, source_key: str, target_key: str) -> float:
        """Return multiplicative distance weight for a source->target pair."""


class NeutralDistanceProvider:
    """Default distance provider with no friction."""

    def weight(self, source_key: str, target_key: str) -> float:
        return 1.0
