class CityData:
    def __init__(self, name, populations, cfg, rng):
        self.name = name
        self.populations = populations
        self.cfg = cfg
        self.rng = rng
    
    def update_pop_data(self):
        self.total_population = sum(group.size for group in self.populations)
        self.birth_total = sum(group.births for group in self.populations)
        self.death_total = sum(group.deaths for group in self.populations)

        self.attractiveness = sum(group.migration_attractiveness for group in self.populations) / len(self.populations)

        self.employment_rate = sum(group.employment_rate for group in self.populations) / len(self.populations)

        self.productivity = sum(group.size * group.labour_productivity * group.employment_rate for group in self.populations)

    def sum_population_data(self):
        
        """Returns dictionary summary of all population groups."""
        
        summary = []

        for i, group in enumerate(self.populations, 1):
            summary.append ({
                'group': i,
                'size': group.size,
                'healthcare': group.healthcare,
                'last_births': group.births,
                'last_deaths': group.deaths,
                'employment_rate': group.employment_rate,

            })

        return summary