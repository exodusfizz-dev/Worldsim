class PopulationGroup:
    def __init__(self, size, healthcare):
        self.size = size
        self.healthcare = healthcare  # 0.0–1.0

        self.base_birth_rate = 0.0002
        self.base_death_rate = 0.00015

    def tick(self): # Simulate one time step - e.g. one week for now
        death_rate = self.base_death_rate * (1.0 - self.healthcare)

        births = self.size * self.base_birth_rate
        deaths = self.size * death_rate

        self.size += births - deaths