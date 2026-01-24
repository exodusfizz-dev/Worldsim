class City:
    def __init__(self, populations):
        self.populations = populations

    def tick(self):
        for group in self.populations:
            group.tick()        
        self.total_population = sum(group.size for group in self.populations)
        self.birth_total = sum(group.last_births for group in self.populations)
        self.death_total = sum(group.last_deaths for group in self.populations)

    def get_population_data(self):

        """Returns dictionary summary of all population groups."""
        
        summary = []

        for i, group in enumerate(self.populations, 1):
            summary.append ({
                'group': i,
                'size': group.size,
                'healthcare': group.healthcare,
                'last_births': group.last_births,
                'last_deaths': group.last_deaths
            })

        return summary
