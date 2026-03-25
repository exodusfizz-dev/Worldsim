"""City data capture and summaries."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from model.city.city import City


class PopulationSummary(TypedDict):
    group: int
    group_type: int
    size: int
    healthcare: float
    last_births: int
    last_deaths: int
    employment_rate: float
    sick_rate: float


class FirmSummary(TypedDict):
    ownership: str
    good: str
    employed: int
    total_productivity: float


class CitySummary(TypedDict):
    population: int
    births: int
    deaths: int
    employable: float
    productivity: float


class CitySnapshot(TypedDict):
    city_data: CitySummary
    population_data: list[PopulationSummary]
    firm_data: list[FirmSummary]


@dataclass
class CityData:
    """City data handles per-tick summaries and storage."""

    city: "City"
    data: list[CitySnapshot] = field(default_factory=list)

    def update_city_data(self) -> None:
        self.data.append(self.store_data())

    def sum_population_data(self) -> list[PopulationSummary]:
        return self.city.population.summary_rows()

    def sum_firm_data(self) -> list[FirmSummary]:
        summary: list[FirmSummary] = []
        for firm in self.city.firms:
            summary.append(
                {
                    "ownership": firm.ownership,
                    "good": firm.good,
                    "employed": firm.employed,
                    "total_productivity": firm.total_productivity,
                }
            )

        return summary

    def sum_city_data(self) -> CitySummary:
        totals = self.city.population.totals()
        return {
            "population": int(totals["population"]),
            "births": int(totals["births"]),
            "deaths": int(totals["deaths"]),
            "employable": float(totals["employable"]),
            "productivity": float(sum(firm.total_productivity for firm in self.city.firms)),
        }

    def store_data(self) -> CitySnapshot:
        return {
            "city_data": self.sum_city_data(),
            "population_data": self.sum_population_data(),
            "firm_data": self.sum_firm_data(),
        }
