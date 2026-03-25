"""Population generation for city-owned NumPy group tables."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PopulationSeed:
    """Generated per-group arrays used to initialize ``CityPopulation``."""

    group_type: np.ndarray
    size: np.ndarray
    base_healthcare: np.ndarray
    healthcare_capacity: np.ndarray
    education: np.ndarray
    money: np.ndarray


class PopulationGenerator:
    """Generate city population groups as NumPy-ready arrays."""

    def __init__(
        self,
        rng,
        base_group_count: int = 5,
        group_type_count: int = 3,
    ) -> None:
        self.rng = rng
        self.base_group_count = max(int(base_group_count), 1)
        self.group_type_count = max(int(group_type_count), 1)

    def generate_for_city(self, city_name: str, population: int) -> PopulationSeed:
        """Generate grouped population data for one city.

        ``city_name`` is currently unused but kept in signature for future customization hooks.
        """
        del city_name
        # TODO: Resolve unused param.

        pop = max(int(population), 0)
        if pop > 1_000_000:
            group_count = max(1, self.base_group_count * (pop // 1_000_000))
        else:
            group_count = self.base_group_count

        if pop == 0:
            return PopulationSeed(
                group_type=np.zeros(group_count, dtype=np.int8),
                size=np.zeros(group_count, dtype=np.int32),
                base_healthcare=np.full(group_count, 0.3, dtype=np.float64),
                healthcare_capacity=np.full(group_count, 100, dtype=np.int32),
                education=np.full(group_count, 1.0, dtype=np.float64),
                money=np.zeros(group_count, dtype=np.float64),
            )

        type_ids = np.arange(group_count, dtype=np.int64) % self.group_type_count
        self.rng.shuffle(type_ids)

        size_weights = self.rng.uniform(0.5, 1.5, size=group_count)
        raw_sizes = np.floor((size_weights / np.sum(size_weights)) * pop).astype(np.int64)
        remainder = pop - int(np.sum(raw_sizes))
        if remainder > 0:
            raw_sizes[:remainder] += 1

        development = min(max(pop / 1_000_000.0, 0.0), 1.0)
        healthcare_center = 0.3 + development * 0.6
        base_healthcare = self.rng.uniform(
            max(0.2, healthcare_center - 0.2),
            min(0.99, healthcare_center + 0.2),
            size=group_count,
        )

        type_bonus = (type_ids - (self.group_type_count - 1) / 2.0) / max(self.group_type_count, 1)
        education = np.clip(1.0 + 0.6 * type_bonus + self.rng.normal(0.0, 0.05, size=group_count), 0.3, 2.0)
        money = np.clip((1_000.0 + 900.0 * type_bonus) * raw_sizes, 0.0, None)

        return PopulationSeed(
            group_type=type_ids.astype(np.int8),
            size=raw_sizes,
            base_healthcare=base_healthcare.astype(np.float64),
            healthcare_capacity=np.maximum(100, (raw_sizes * 0.1).astype(np.int64)),
            education=education.astype(np.float64),
            money=money.astype(np.float64),
        )
