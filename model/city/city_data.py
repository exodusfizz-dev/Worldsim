'''
City data module contains class CityData, which supplies various data-related functions
'''

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from model.city.city import City


class PopulationSummary(TypedDict):
    group: int
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
    '''
    City data handles data for cities by updating, creating summaries and storing it
    '''
    city: "City"
    data: list[CitySnapshot] = field(default_factory=list)

    def update_city_data(self):
        '''
        Updates data that is dependent on variables the city object handles
        '''
        c = self.city
        c.total_population = sum(group.size for group in c.populations)
        c.birth_total = sum(group.births for group in c.populations)
        c.death_total = sum(group.deaths for group in c.populations)

        # People of fit age and health to work as decimal.
        c.employable = sum(group.employable for group in c.populations) / len(c.populations)

        c.productivity = sum(firm.total_productivity for firm in c.firms)

        self.data.append(self.store_data())

    def sum_population_data(self) -> list[PopulationSummary]:

        '''
        Helper function for store_data
        Returns a list dictionary summary of all population groups.
        '''

        c = self.city
        summary: list[PopulationSummary] = []

        for i, group in enumerate(c.populations, 1):
            summary.append ({
                'group': i,
                'size': group.size,
                'healthcare': group.healthcare,
                'last_births': group.births,
                'last_deaths': group.deaths,
                'employment_rate': group.employment_rate,
                'sick_rate': group.sick_rate
            })

        return summary

    def sum_firm_data(self) -> list[FirmSummary]:

        '''
        Helper function for store_data
        Returns list dictionary summary of all firms.
        '''

        c = self.city
        summary: list[FirmSummary] = []

        for firm in c.firms:
            summary.append ({
                'ownership': firm.ownership,
                'good': firm.good,
                'employed': firm.employed,
                'total_productivity': firm.total_productivity
            })

        return summary

    def sum_city_data(self) -> CitySummary:

        '''
        Helper function for store_data.
        Returns a dictionary.
        '''
        c = self.city

        summary = {
            'population': c.total_population,
            'births': c.birth_total,
            'deaths': c.death_total,
            'employable': c.employable,
            'productivity': c.productivity,
        }

        return summary

    def store_data(self) -> CitySnapshot:
        full_summary = ({
            'city_data':
                self.sum_city_data(),

            'population_data':
                self.sum_population_data(),

            'firm_data':
                self.sum_firm_data()

        }
        )

        return full_summary
