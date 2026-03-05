'''Population group properties to improve readability and maintainability.'''

from dataclasses import dataclass

@dataclass
class PopulationGroupParams:
    size: int
    base_healthcare: float
    healthcare_capacity: int
    education_level: str | None = None

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
    money: float = 0.0
    education: float = 1.0

@dataclass
class PopulationGroupProperties:
    '''Property accessors for population groups.'''

    @property
    def size(self):
        return self.state.size

    @size.setter
    def size(self, value):
        self.state.size = value

    @property
    def healthcare_capacity(self):
        return self.p.healthcare_capacity

    @property
    def education_level(self):
        return self.p.education_level

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

    @property
    def money(self):
        return self.state.money
    @money.setter
    def money(self, value):
        self.state.money = value

    @property
    def healthcare(self):
        return self.state.healthcare
    @healthcare.setter
    def healthcare(self, value):
        self.state.healthcare = value

    @property
    def sick(self):
        return self.state.sick
    @sick.setter
    def sick(self, value):
        self.state.sick = value

    @property
    def migration_attractiveness(self):
        return (self.state.healthcare * 0.3) + (self.employment_rate * 0.2)

    @property
    def employment_rate(self):
        return self.state.employed / self.size


    @property
    def employable(self):
        return self.state.employable
    @employable.setter
    def employable(self, value):
        self.state.employable = value

    @property
    def employed(self):
        return self.state.employed

    @employed.setter
    def employed(self, value):
        self.state.employed = value

    @property
    def education(self):
        return self.state.education
