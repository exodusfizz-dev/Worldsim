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
    
    def sum_firm_data(self):

        '''Returns dictionary summary of all firms.'''

        summary = []

        for firm in self.firms:
            summary.append ({
                'ownership': firm.ownership,
                'good': firm.good,
                'employed': firm.employed,
                'total_productivity': firm.total_productivity
            })