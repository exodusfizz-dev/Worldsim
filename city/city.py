import numpy as np
import math
from migration import Migration
from .city_data import CityData


class City:
    def __init__(self, populations, name, cfg, rng):
        self.rng = rng
        self.cfg = cfg
        DEFAULT_MIGRATION_RATE = self.cfg.get('intergroup_rate', 0.0005)
        self.migration = Migration(self.rng, DEFAULT_MIGRATION_RATE)

        self.name = name
        self.populations = populations
        self.migrations = []
        self.base_migration_rate = DEFAULT_MIGRATION_RATE  # 0.05% migration rate

    def tick(self):
        for group in self.populations: # City controls tick updates of all owned population groups
            group.tick()

        if self.cfg.get('migration', {}).get('enabled', True):

            self.migrations = []

            for i, group in enumerate(self.populations, 1):
                migrated_amount, target = self.migration.migrate(group, self.populations)

                if migrated_amount > 0:
                    target_index = self.populations.index(target) + 1
                    self.migrations.append((i, migrated_amount, target_index))
        
        CityData.update_pop_data(self)
        

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
    

