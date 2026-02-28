"""Labour market matching and payroll settlement."""

from dataclasses import dataclass, field


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

    def compute_supply(self, populations):
        """Return per-group labour supply and total supply."""
        group_supply = [int(group.size * max(group.employable, 0)) for group in populations]
        total_supply = sum(group_supply)
        return group_supply, total_supply

    def compute_labour_demand(self, firms):
        """Return per-firm demand and total demand."""
        firm_demands = [max(int(firm.labour_demand()), 0) for firm in firms]
        total_demand = sum(firm_demands)
        return firm_demands, total_demand

    def is_eligible(self, group, firm):
        """Eligibility hook for future education/skill constraints."""
        del group, firm
        return True

    def _empty_result(self, populations, firms):
        return LabourClearResult(
            total_employed=0,
            group_employed=[0 for _ in populations],
            firm_employed=[0 for _ in firms],
            flows=[],
            group_income=[0.0 for _ in populations],
            firm_wage_bill=[0.0 for _ in firms],
        )

    def clear_market(self, populations, firms) -> "LabourClearResult":
        """Assign workers to firms and settle gross wages."""
        result = self._empty_result(populations=populations, firms=firms)
        if not populations or not firms:
            return result

        per_g_supply, total_supply = self.compute_supply(populations)
        per_f_demand, total_demand = self.compute_labour_demand(firms)
        if total_supply == 0 or total_demand == 0:
            return result

        remaining_supply = per_g_supply[:]
        remaining_demand = per_f_demand[:]

        firm_order = sorted(
            range(len(firms)),
            key=lambda idx: (float(firms[idx].wage), -idx),
            reverse=True,
        )

        for firm_index in firm_order:
            if remaining_demand[firm_index] <= 0:
                continue
            firm = firms[firm_index]
            if firm.state.market_capital <= 0 or firm.wage <= 0:
                continue

            for group_index, group in enumerate(populations):
                if remaining_demand[firm_index] <= 0:
                    break
                if remaining_supply[group_index] <= 0:
                    continue
                if not self.is_eligible(group, firm):
                    continue

                workers = min(remaining_supply[group_index], remaining_demand[firm_index])
                if workers <= 0:
                    continue

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

                remaining_supply[group_index] -= workers
                remaining_demand[firm_index] -= workers

        result.total_employed = sum(result.group_employed)

        for group_index, group in enumerate(populations):
            group.employed = result.group_employed[group_index]
            group.money += result.group_income[group_index]

        for firm_index, firm in enumerate(firms):
            firm.employed = result.firm_employed[firm_index]
            firm.market_capital = max(firm.market_capital - result.firm_wage_bill[firm_index], 0.0)

        return result
