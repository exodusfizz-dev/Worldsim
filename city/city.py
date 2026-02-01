from core import CITY_CFG
default_migration_rate = CITY_CFG['migration']['intergroup_rate']

class City:
    def __init__(self, populations, name):
        self.name = name
        self.populations = populations
        self.migrations = []
        self.base_migration_rate = default_migration_rate  # 0.05% migration rate

    def tick(self):
        for group in self.populations: # City controls tick updates of all owned population groups
            group.tick()

        self.migrations = []

        for i, group in enumerate(self.populations, 1):
            migrated, target = self.group_migration(group)

            if migrated > 0:
                target_index = self.populations.index(target) + 1
                self.migrations.append((i, migrated, target_index))
        
        self.update_pop_data()
        

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
    

    def group_migration(self, group):
        '''Migrate a small portion of a population group to a preexisting group with better healthcare.'''
        better_groups = [g for g in self.populations if g.migration_attractiveness > group.migration_attractiveness]
        if better_groups:
            target_group = better_groups[0]  # Currently selects the first better group found; selection criteria will be refined later
            migrating_size = group.size * self.base_migration_rate
            group.size -= migrating_size
            target_group.size += migrating_size


            return migrating_size, target_group
        else:
            return 0, None
        
        
    def update_pop_data(self):
        self.total_population = sum(group.size for group in self.populations)
        self.birth_total = sum(group.births for group in self.populations)
        self.death_total = sum(group.deaths for group in self.populations)

        self.attractiveness = sum(group.migration_attractiveness for group in self.populations) / len(self.populations)

        self.employment_rate = sum(group.employment_rate for group in self.populations) / len(self.populations)

        self.productivity = sum(group.size * group.labour_productivity * group.employment_rate for group in self.populations)
