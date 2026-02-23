"""Shared migration event and generic typing models."""

from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class GroupMigrationEvent:
    """Record of a single group-to-group transfer."""

    source_city: str
    source_group_index: int
    target_city: str
    target_group_index: int
    amount: int
    channel: str


@dataclass(frozen=True)
class WeightedTarget(Generic[T]):
    """Weighted candidate used by target selection."""

    index: int
    candidate: T
    weight: float
