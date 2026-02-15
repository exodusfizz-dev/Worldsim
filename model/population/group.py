from model.core.random import _sample_normal

class PopulationGroup:
    def __init__(self, size, healthcare, healthcare_capacity, rng):
        self.rng = rng

        self.size = size

        self.base_healthcare = healthcare  # 0.0–1.0
        self.healthcare = healthcare
        self.healthcare_capacity = healthcare_capacity
        self.sick_rate = 0.02
        self.sick = 0


        self.base_birth_rate = 0.0002
        self.base_death_rate = 0.00015

        self.employable = 0.7 - self.sick_rate
        self.base_sickness_rate = 0.025
        self.labour_productivity = 1.0
        self.employed = 0
        self.employment_rate = 0

        self.migration_attractiveness = (self.healthcare * 0.3) + (self.employment_rate * 0.2)



    def tick(self): # Simulate one time step - e.g. one week for now
        
        self.update_demographics()

        self.update_sick()
        self.update_healthcare()

        self.update_employment()


    def update_healthcare(self):

        if self.sick / self.healthcare_capacity <= 1.0:
            self.healthcare_modifier = 1.05
        else:
            self.healthcare_modifier = (self.healthcare_capacity / self.size) ** 1.3

        self.healthcare = min(self.base_healthcare * self.healthcare_modifier, 1.0)

        self.migration_attractiveness = (self.healthcare * 0.3) + (self.employment_rate * 0.2)

    def update_demographics(self):

        death_rate = self.base_death_rate * (2.001 - (2 * self.healthcare))
        self.birth_rate = self.base_birth_rate * max((1.0 - (self.employment_rate * 0.15 - self.healthcare * 0.1)), 0)

        expected_births = self.size * self.birth_rate
        expected_deaths = self.size * death_rate

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
