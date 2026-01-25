class City:
    def __init__(self, populations):
        self.populations = populations
        self.migrations = []
        self.base_migration_rate = 0.0005  # 0.05% migration rate

    def tick(self):
        for group in self.populations: # City controls tick updates of all owned population groups
            group.tick()

        self.migrations = []

        for i, group in enumerate(self.populations, 1):
            migrated, target = self.group_migration(group, group.healthcare)

            if migrated > 0:
                target_index = self.populations.index(target) + 1
                self.migrations.append((i, migrated, target_index))
        
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
                'last_deaths': group.last_deaths,
                'migrations': self.migrations 
            })

        return summary
    

    def group_migration(self, group, healthcare):
        '''Migrate a small portion of a population group to a preexisting group with better healthcare.'''
        better_groups = [g for g in self.populations if g.healthcare > healthcare * group.healthcare_modifier]
        if better_groups:
            target_group = better_groups[0]  # Currently selects the first better group found; selection criteria will be refined later
            migrating_size = group.size * self.base_migration_rate
            group.size -= migrating_size
            target_group.size += migrating_size


            return migrating_size, target_group
        else:
            return 0, None