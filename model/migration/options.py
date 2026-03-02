"""Runtime options for migration channels."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MigrationOptions:
    """Per-service migration rates, clamped by ``Migration``.

    These are runtime channel options (not application config loading).
    """

    intergroup_rate: float = 0.0
    intercity_rate: float = 0.0

