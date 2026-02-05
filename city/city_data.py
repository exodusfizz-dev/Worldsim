from industry import firm

class CityData:
    def __init__(self, name, populations, cfg, rng, firms):
        self.name = name
        self.populations = populations
        self.cfg = cfg
        self.rng = rng
        self.firms = firms
    
    def update_pop_data(self):
        self.total_population = sum(group.size for group in self.populations)
        self.birth_total = sum(group.births for group in self.populations)
        self.death_total = sum(group.deaths for group in self.populations)

        self.attractiveness = sum(group.migration_attractiveness for group in self.populations) / len(self.populations)

        self.employable = sum(group.employable for group in self.populations) / len(self.populations) # People of fit age and health to work
        
        for firm in self.firms:
            firm.update_total_productivity()
        self.productivity = sum(firm.total_productivity for firm in self.firms)

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