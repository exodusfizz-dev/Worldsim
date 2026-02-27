from model.core.random import _sample_normal

from dataclasses import dataclass

@dataclass
class PopulationGroupParams:
    size: int
    base_healthcare: float
    healthcare_capacity: int

@dataclass
class PopulationGroupState:
    size: int = 0
    healthcare: float = 0.0
    healthcare_capacity: int = 0
    sick_rate: float = 0.0
    sick: int = 0
    births: int = 0
    deaths: int = 0
    employable: float = 0.0
    employed: int = 0
    employment_rate: float = 0.0
    migration_attractiveness: float = 0.0

class PopulationGroup:
    def __init__(self, params, rng):
        self.rng = rng
        self.p = params

        self.state = PopulationGroupState()

        self.healthcare = self.p.base_healthcare  # 0.0–1.0

        self.sick_rate = 0.02
        self.sick = 0

        self.base_birth_rate = 0.0002
        self.base_death_rate = 0.00015

        self.employable = 0.7 - self.sick_rate
        self.base_sickness_rate = 0.025
        self.employed = 0
        self.employment_rate = 0

        self.migration_attractiveness = (self.healthcare * 0.3) + (self.employment_rate * 0.2)

    @classmethod
    def from_dict(cls, group_data: dict, rng) -> "PopulationGroup":
        return cls(
            params=PopulationGroupParams(
                size=group_data["size"],
                base_healthcare=group_data["base_healthcare"],
                healthcare_capacity=group_data["healthcare_capacity"]
            ),
            rng=rng,
        )

    @property
    def size(self):
        return self.p.size

    @size.setter
    def size(self, value):
        self.p.size = value

    @property
    def healthcare_capacity(self):
        return self.p.healthcare_capacity

    @property
    def births(self):
        return self.state.births
    @births.setter
    def births(self, value):
        self.state.births = value

    @property
    def deaths(self):
        return self.state.deaths
    @deaths.setter
    def deaths(self, value):
        self.state.deaths = value

    def tick(self): # Simulate one time step - e.g. one week for now
        
        self.update_demographics()

        self.update_sick()
        self.update_healthcare()

        self.update_employment()


    def update_healthcare(self):

        if self.sick / self.p.healthcare_capacity <= 1.0:
            healthcare_modifier = 1.05
        else:
            healthcare_modifier = (self.p.healthcare_capacity / self.size) ** 1.3

        self.healthcare = min(self.p.base_healthcare * healthcare_modifier, 1.0)

        self.migration_attractiveness = (self.healthcare * 0.3) + (self.employment_rate * 0.2)

    def update_demographics(self):

        death_rate = self.base_death_rate * (2.001 - (2 * self.healthcare))
        birth_rate = self.base_birth_rate * max((1.0 - (self.employment_rate * 0.15 - self.healthcare * 0.1)), 0)

        expected_births = self.p.size * birth_rate
        expected_deaths = self.p.size * death_rate

        self.births = _sample_normal(expected=expected_births, rng=self.rng)
        self.deaths = _sample_normal(expected=expected_deaths, rng=self.rng)

        self.size = max(0, self.size + self.births - self.deaths)

    def update_sick(self):
        self.sick = min(self.size * self.base_sickness_rate * (1-self.healthcare), self.size)
        self.sick_rate = self.sick / self.size if self.size > 0 else 0

    def update_employment(self):
        self.employable = 0.7 - self.sick_rate

        self.employment_rate = self.employed / self.size if self.size > 0 else 0

    def compute_food_consumption(self):
        food_consumption = self.size * (3 - self.sick_rate)
        return food_consumption
    
    def starve(self, food_deficit):
        if self.size <= 0:
            return
        self.sick = self.sick * (food_deficit / (self.size * 3))
