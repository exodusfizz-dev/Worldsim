"""Labour market matching and payroll settlement."""

from dataclasses import dataclass, field

import numpy as np


@dataclass(frozen=True)
class LabourFlow:
    """A single group->firm employment assignment."""

    group_index: int
    firm_index: int
    workers: int
    wage_rate: float
    gross_pay: float


@dataclass
class LabourClearResult:
    """Outputs of one labour market clear step."""

    total_employed: int = 0
    group_employed: list[int] = field(default_factory=list)
    firm_employed: list[int] = field(default_factory=list)
    flows: list[LabourFlow] = field(default_factory=list)
    group_income: list[float] = field(default_factory=list)
    firm_wage_bill: list[float] = field(default_factory=list)


class LabourMarket:
    """Labour market object owned by cities."""

    def __init__(self, rng, country_policy=None):
        self.rng = rng
        self.country_policy = country_policy

    def compute_supply(self, population) -> tuple[list[int], int]:
        """Return per-group labour supply and total supply."""
        size = population.sizes.astype(np.float64)
        employable = population.employable_shares.astype(np.float64)
        per_group = np.maximum((size * employable).astype(np.int64), 0)
        total_supply = int(np.sum(per_group))
        return per_group.tolist(), total_supply

    def compute_labour_demand(self, firms) -> tuple[list[int], int]:
        """Return per-firm demand and total demand."""
        per_f_demand = [max(int(firm.labour_demand()), 0) for firm in firms]
        total_demand = sum(per_f_demand)
        return per_f_demand, total_demand

    def is_eligible(self, group_education: float, firm) -> bool:
        """Eligibility hook for future education/skill constraints."""
        del group_education, firm # TODO
        return True

    def _empty_result(self, group_count: int, firm_count: int):
        return LabourClearResult(
            total_employed=0,
            group_employed=[0 for _ in range(group_count)],
            firm_employed=[0 for _ in range(firm_count)],
            flows=[],
            group_income=[0.0 for _ in range(group_count)],
            firm_wage_bill=[0.0 for _ in range(firm_count)],
        )

    def clear_market(self, population, firms) -> "LabourClearResult":
        """Assign workers to firms and settle gross wages."""
        result = self._empty_result(group_count=population.group_count, firm_count=len(firms))
        if population.group_count == 0 or not firms:
            return result

        per_g_supply, total_supply = self.compute_supply(population)
        per_f_demand, total_demand = self.compute_labour_demand(firms)
        if total_supply == 0 or total_demand == 0:
            return result

        group_education = population.education_levels.astype(np.float64)

        remaining_supply = total_supply
        remaining_demand = total_demand
        remaining_per_g_supply = per_g_supply[:]
        remaining_per_f_demand = per_f_demand[:]

        firm_order = sorted(
            range(len(firms)),
            key=lambda idx: (float(firms[idx].wage), -idx),
            reverse=True,
        )

        for _ in range(5): # TODO
            for firm_index in firm_order:
                if remaining_per_f_demand[firm_index] <= 0:
                    continue
                firm = firms[firm_index]
                if firm.state.market_capital <= 0 or firm.wage <= 0:
                    continue

                for group_index in range(population.group_count):
                    if remaining_per_f_demand[firm_index] <= 0:
                        break
                    if remaining_per_g_supply[group_index] <= 1:
                        continue

                    if not self.is_eligible(group_education[group_index], firm):
                        continue

                    p = self.calc_employment_probability(
                        remaining_supply=remaining_supply,
                        remaining_demand=remaining_demand,
                        group_education=group_education[group_index],
                        firm=firm,
                    )

                    workers = min(
                        self.draw_count(
                            supply=remaining_per_g_supply[group_index],
                            probability=p,
                        ),
                        per_f_demand[firm_index],
                    )

                    gross_pay = workers * firm.wage
                    result.flows.append(
                        LabourFlow(
                            group_index=group_index,
                            firm_index=firm_index,
                            workers=workers,
                            wage_rate=firm.wage,
                            gross_pay=gross_pay,
                        )
                    )
                    result.group_employed[group_index] += workers
                    result.firm_employed[firm_index] += workers
                    result.group_income[group_index] += gross_pay
                    result.firm_wage_bill[firm_index] += gross_pay

                    remaining_supply -= workers
                    remaining_demand -= workers
                    remaining_per_g_supply[group_index] -= workers
                    remaining_per_f_demand[firm_index] -= workers

        result.total_employed = int(sum(result.group_employed))

        for firm_index, firm in enumerate(firms):
            firm.employed = result.firm_employed[firm_index]
            firm.market_capital = max(firm.market_capital - result.firm_wage_bill[firm_index], 0.0)

        return result

    def draw_count(self, supply: float, probability: float) -> int:
        """Draw integer employees using RNG binomial when available."""
        n = max(int(supply), 0)
        p = max(min(probability, 1.0), 0.0)
        if n == 0 or p <= 0:
            return 0

        if self.rng is not None and hasattr(self.rng, "binomial"):
            return int(self.rng.binomial(n, p))

        return min(int(round(n * p)), int(supply))

    def calc_employment_probability(
        self,
        remaining_supply: float,
        remaining_demand: float,
        group_education: float,
        firm,
    ) -> float:
        """Calculate the deterministic probability of a potential employee being employed."""
        if remaining_demand <= 0 or remaining_supply <= 0:
            return 0.0
        probability = min(remaining_supply / remaining_demand, 1)

        firm_ed = getattr(firm, "education_wanted", 0)
        if firm_ed > 0 and group_education > 0:
            probability *= group_education / firm_ed * 0.1

        return min(probability, 1)
