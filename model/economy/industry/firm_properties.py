'''Firm properties to improve readability and maintainability.'''

from dataclasses import dataclass, field

@dataclass
class FirmParams:
    productivity: float
    production_capacity: int
    ownership: str
    good: str
    education_wanted: float = 1.0
    input_mats: list | None = field(default_factory=list)

    # This is a placeholder that will allow labour_market to work before education is implemented.

    # transitional: optional in input_data.json
    capital: float | None = None
    wage: float | None = None
    required_skill: str | None = None
    country_policy: dict | None = None

@dataclass
class FirmState:
    employed: int = 0
    total_productivity: float = 0.0
    market_capital: float = 0.0
    inv: dict = field(default_factory=dict)


class FirmProperties:
    '''Property accessors for firms.'''
    @property
    def employed(self):
        return self.state.employed
    @employed.setter
    def employed(self, value):
        self.state.employed = value

    @property
    def total_productivity(self):
        return self.state.total_productivity
    @total_productivity.setter
    def total_productivity(self, value):
        self.state.total_productivity = value

    @property
    def market_capital(self):
        return self.state.market_capital
    @market_capital.setter
    def market_capital(self, value):
        self.state.market_capital = value

    @property
    def good(self):
        return self.p.good

    @property
    def ownership(self):
        return self.p.ownership

    @property
    def wage(self):
        return self.p.wage if self.p.wage is not None else 0.0

    @property
    def education_wanted(self):
        return self.p.education_wanted

    @property
    def input_mats(self):
        return self.p.input_mats

    @property
    def inv(self):
        return self.state.inv

    @property
    def able_to_produce(self):
        able_to_produce = float('inf')
        if self.input_mats is not None:
            for mat in self.input_mats:
                able_to_produce = min(able_to_produce, self.inv[mat])
        return able_to_produce
