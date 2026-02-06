import numpy as np
import math
from migration import Migration
from .city_data import CityData
from labour import LabourMarket


class City:
    def __init__(self, populations, name, cfg, rng, firms):
        self.rng = rng
        self.cfg = cfg
        DEFAULT_MIGRATION_RATE = self.cfg.get('intergroup_rate', 0.0005)
        self.migration = Migration(self.rng, DEFAULT_MIGRATION_RATE)

        self.labour_market = LabourMarket(self.rng, country_policy = None)
        self.firms = firms

        self.name = name
        self.populations = populations
        self.migrations = []
        self.base_migration_rate = DEFAULT_MIGRATION_RATE  # 0.05% migration rate

        self.inv = {}
        for firm in firms:
            self.inv.setdefault(firm.good, 0)

    def tick(self):
        for group in self.populations: # City controls tick updates of all owned population groups
            group.tick()
        
        self.employed = self.labour_market.clear_market(
            populations = self.populations,
            firms = self.firms
        )

        for firm in self.firms:
            firm.tick()

            if firm.ownership == "state":
                self.inv[firm.good] += firm.transfer_to_city()
                    

        
        self.run_migrations()
        CityData.update_pop_data(self)
        


    def run_migrations(self):
        if self.cfg.get('migration', {}).get('enabled', True):

            self.migrations = []

            for i, group in enumerate(self.populations, 1):
                migrated_amount, target = self.migration.migrate(group, self.populations)

                if migrated_amount > 0:
                    target_index = self.populations.index(target) + 1
                    self.migrations.append((i, migrated_amount, target_index))
    

