import numpy as np
import math

class PopulationGroup:
    def __init__(self, size, healthcare, healthcare_capacity, rng):
        self.rng = rng

        self.size = size

        self.base_healthcare = healthcare  # 0.0–1.0
        self.healthcare = healthcare
        self.healthcare_capacity = healthcare_capacity

        self.base_birth_rate = 0.0002
        self.base_death_rate = 0.00015
        
        self.employable = 0.75 + (self.healthcare * 0.15)
        self.labour_productivity = 1.0
        self.employed = 0
        self.employment_rate = 0

        self.migration_attractiveness = (self.healthcare * 0.3) + (self.employment_rate * 0.2)



    def tick(self): # Simulate one time step - e.g. one week for now
        
        self.update_demographics()

        self.update_healthcare()

        self.update_employment()


    def update_healthcare(self):

        if self.size / self.healthcare_capacity <= 1.0:
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

        self.births = self._sample_count(expected_births)
        self.deaths = self._sample_count(expected_deaths)

        self.size = max(0, self.size + self.births - self.deaths)



    def update_employment(self):
        self.employable = 0.7 + (self.healthcare * 0.15)

        self.employment_rate = self.employed / self.size
        
    def _sample_count(self, expected_count):
        '''Samples a count based on normal distribution around expected count. Uses numpy normal distribution.'''
        stddev = math.sqrt(expected_count)
        sample = self.rng.normal(loc=expected_count, scale=stddev)
        return max(0, int(sample))
    
    def compute_food_consumption(self):
        food_consumption = self.size * (3 - self.healthcare)
        return food_consumption