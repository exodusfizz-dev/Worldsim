"""City population manager that owns a single NumPy structured array."""

from __future__ import annotations

import numpy as np

from model.city.population_generator import PopulationSeed


POP_DTYPE = np.dtype(
    [
        ("group_type", np.int16),
        ("size", np.int64),
        ("employed", np.int64),
        ("money", np.float64),
        ("base_healthcare", np.float64),
        ("healthcare", np.float64),
        ("healthcare_capacity", np.int64),
        ("sick", np.float64),
        ("sick_rate", np.float64),
        ("births", np.int64),
        ("deaths", np.int64),
        ("employable", np.float64),
        ("education", np.float64),
    ]
)


class CityPopulation:
    """Owns and updates all population group state for one city."""

    def __init__(self, groups: np.ndarray, rng, cfg: dict | None = None) -> None:
        self.rng = rng
        self.cfg = cfg or {}
        self.groups = groups.astype(POP_DTYPE, copy=False)

        self.base_birth_rate = 0.0002
        self.base_death_rate = 0.00015
        self.base_sickness_rate = 0.025

    @classmethod
    def from_seed(
        cls,
        seed: PopulationSeed,
        rng,
        cfg: dict | None = None,
    ) -> "CityPopulation":
        group_count = len(seed.size)
        groups = np.zeros(group_count, dtype=POP_DTYPE)
        groups["group_type"] = seed.group_type.astype(np.int16, copy=False)
        groups["size"] = seed.size.astype(np.int64, copy=False)
        groups["money"] = seed.money.astype(np.float64, copy=False)
        groups["base_healthcare"] = seed.base_healthcare.astype(np.float64, copy=False)
        groups["healthcare"] = seed.base_healthcare.astype(np.float64, copy=False)
        groups["healthcare_capacity"] = seed.healthcare_capacity.astype(np.int64, copy=False)
        groups["education"] = seed.education.astype(np.float64, copy=False)

        # Mirrors previous defaults from PopulationGroup
        groups["employable"] = 0.68
        groups["employed"] = 0
        groups["sick"] = 0.0
        groups["sick_rate"] = 0.02

        return cls(groups=groups, rng=rng, cfg=cfg)

    @property
    def total_population(self) -> int:
        return int(np.sum(self.groups["size"]))

    @property
    def group_count(self) -> int:
        return int(len(self.groups))

    @property
    def migration_attractiveness(self) -> float:
        if self.group_count == 0:
            return 0.0
        employment_rate = self.employment_rates()
        scores = (self.groups["healthcare"] * 0.3) + (employment_rate * 0.2)
        return float(np.sum(scores))

    @property
    def group_migration_attractiveness(self) -> np.ndarray:
        employment_rate = self.employment_rates()
        return (self.groups["healthcare"] * 0.3) + (employment_rate * 0.2)

    @property
    def sizes(self) -> np.ndarray:
        return self.groups["size"]

    @property
    def employable_shares(self) -> np.ndarray:
        return np.maximum(self.groups["employable"], 0.0)

    @property
    def education_levels(self) -> np.ndarray:
        return self.groups["education"]

    def employment_rates(self) -> np.ndarray:
        size = self.groups["size"].astype(np.float64)
        employed = self.groups["employed"].astype(np.float64)
        return np.divide(employed, size, out=np.zeros_like(size), where=size > 0)

    def tick(self) -> None:

        self._update_demographics()
        self._update_sick()
        self._update_healthcare()
        self._update_employment_supply()

    def _update_demographics(self) -> None:
        healthcare = self.groups["healthcare"]
        death_rate = self.base_death_rate * (2.001 - (2 * healthcare))

        employment_rate = self.employment_rates()
        birth_rate = self.base_birth_rate * np.maximum(
            1.0 - (employment_rate * 0.15 - healthcare * 0.1),
            0.0,
        )

        size = self.groups["size"].astype(np.float64)
        expected_births = size * birth_rate
        expected_deaths = size * death_rate

        births = self._sample_normal_counts(expected_births)
        deaths = self._sample_normal_counts(expected_deaths)

        self.groups["births"] = births
        self.groups["deaths"] = deaths
        self.groups["size"] = np.maximum(self.groups["size"] + births - deaths, 0)

    def _sample_normal_counts(self, expected: np.ndarray) -> np.ndarray:
        positive = expected > 0
        out = np.zeros_like(expected, dtype=np.int64)
        if not np.any(positive):
            return out

        sample = self.rng.normal(loc=expected[positive], scale=np.sqrt(expected[positive]))
        out[positive] = np.maximum(sample.astype(np.int64), 0)
        return out

    def _update_sick(self) -> None:
        size = self.groups["size"].astype(np.float64)
        healthcare = self.groups["healthcare"]
        sick = np.minimum(size * self.base_sickness_rate * (1.0 - healthcare), size)
        self.groups["sick"] = sick
        self.groups["sick_rate"] = np.divide(sick, size, out=np.zeros_like(size), where=size > 0)

    def _update_healthcare(self) -> None:
        size = self.groups["size"].astype(np.float64)
        cap = self.groups["healthcare_capacity"].astype(np.float64)
        sick = self.groups["sick"]

        with np.errstate(divide="ignore", invalid="ignore"):
            cap_load = np.divide(sick, cap, out=np.zeros_like(sick), where=cap > 0)

        over_capacity = cap_load > 1.0
        modifier = np.full(self.group_count, 1.05, dtype=np.float64)
        modifier[over_capacity] = np.power(
            np.divide(cap[over_capacity], size[over_capacity], out=np.zeros_like(cap[over_capacity]), where=size[over_capacity] > 0),
            1.3,
        )
        self.groups["healthcare"] = np.minimum(self.groups["base_healthcare"] * modifier, 1.0)

    def _update_employment_supply(self) -> None:
        self.groups["employable"] = 0.7 - self.groups["sick_rate"]

    def compute_food_demand(self) -> np.ndarray:
        return self.groups["size"].astype(np.float64) * (3.0 - self.groups["sick_rate"])

    def apply_food_allocation(self, available_food: float, food_price: float) -> tuple[float, float]:
        """Allocate city food inventory across groups and apply starvation effects.

        Returns:
            consumed_food, total_deficit
        """

        demand = self.compute_food_demand()
        consumed_total = 0.0
        deficit_total = 0.0

        for idx in range(self.group_count):
            needed = float(demand[idx])
            if available_food <= 0.0:
                purchased = 0.0
            elif food_price <= 0.0:
                purchased = min(needed, available_food)
            else:
                affordable = float(self.groups["money"][idx]) / food_price
                purchased = min(needed, available_food, affordable)

            if food_price > 0.0 and purchased > 0.0:
                spent = purchased * food_price
                self.groups["money"][idx] = max(float(self.groups["money"][idx]) - spent, 0.0)

            available_food -= purchased
            consumed_total += purchased

            deficit = max(needed - purchased, 0.0)
            deficit_total += deficit
            if deficit > 0.0:
                self._apply_starvation(idx=idx, food_deficit=deficit)

        return consumed_total, deficit_total

    def _apply_starvation(self, idx: int, food_deficit: float) -> None:
        size = float(self.groups["size"][idx])
        if size <= 0.0:
            return
        self.groups["sick"][idx] = self.groups["sick"][idx] * (food_deficit / (size * 3.0))

    def apply_labour_result(self, labour_result, labour_tax_rate: float) -> float:
        """Apply labour clear outputs to group employment/money and settle labour tax."""

        employed = np.asarray(labour_result.group_employed, dtype=np.int64)
        income = np.asarray(labour_result.group_income, dtype=np.float64)

        self.groups["employed"] = employed
        self.groups["money"] += income

        tax_rate = max(min(float(labour_tax_rate), 1.0), 0.0)
        if tax_rate <= 0.0:
            return 0.0

        tax_due = np.maximum(income, 0.0) * tax_rate
        paid = np.minimum(self.groups["money"], tax_due)
        self.groups["money"] -= paid
        return float(np.sum(paid))

    def totals(self) -> dict[str, float]:

        return {
            "population": int(np.sum(self.groups["size"])),
            "births": int(np.sum(self.groups["births"])),
            "deaths": int(np.sum(self.groups["deaths"])),
            "employable": float(np.mean(self.groups["employable"])),
        }

    def summary_rows(self) -> list[dict]:
        rates = self.employment_rates()
        out: list[dict] = []
        for idx in range(self.group_count):
            out.append(
                {
                    "group": idx + 1,
                    "group_type": int(self.groups["group_type"][idx]),
                    "size": int(self.groups["size"][idx]),
                    "healthcare": float(self.groups["healthcare"][idx]),
                    "last_births": int(self.groups["births"][idx]),
                    "last_deaths": int(self.groups["deaths"][idx]),
                    "employment_rate": float(rates[idx]),
                    "sick_rate": float(self.groups["sick_rate"][idx]),
                }
            )
        return out
