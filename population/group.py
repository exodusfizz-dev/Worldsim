class PopulationGroup:
    def __init__(self, size, healthcare, healthcare_capacity):
        self.size = size

        self.base_healthcare= healthcare  # 0.0–1.0
        self.healthcare = healthcare
        self.healthcare_capacity = healthcare_capacity

        self.base_birth_rate = 0.0002
        self.base_death_rate = 0.00015
        
        self.employment_rate = 0.75 + (self.healthcare * 0.15)
        self.labour_productivity = 1.0

        self.migration_attractiveness = min(0.45 + (self.healthcare * 0.3) + (self.employment_rate * 0.2), max(0.45 + (self.healthcare * 0.3) + (self.employment_rate * 0.2), 1.0))



    def tick(self): # Simulate one time step - e.g. one week for now
        
        self.update_demographics()

        self.update_healthcare()

        self.update_employment()


    def update_healthcare(self):

        if self.size / self.healthcare_capacity <= 1.0:
            self.healthcare_modifier = 1.05
        else:
            self.healthcare_modifier = (self.healthcare_capacity / self.size) ** 1.1

        self.healthcare = self.base_healthcare * self.healthcare_modifier

        self.migration_attractiveness = min(0.45 + (self.healthcare * 0.3) + (self.employment_rate * 0.2), max(0.45 + (self.healthcare * 0.3) + (self.employment_rate * 0.2), 1.0))

    def update_demographics(self):
        
        death_rate = self.base_death_rate * (1.0 - self.healthcare)

        self.births = self.size * self.base_birth_rate
        self.deaths = self.size * death_rate

        self.size += self.births - self.deaths

        self.last_births = self.births
        self.last_deaths = self.deaths

    def update_employment(self):
        self.employment_rate = 0.75 + (self.healthcare * 0.15)
        