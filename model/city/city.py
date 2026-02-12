import numpy as np
import math
from migration import Migration
from .city_data import CityData
from labour import LabourMarket


class City:
    def __init__(self, populations, name, cfg, rng, firms):
        self.rng = rng
        self.cfg = cfg
        DEFAULT_MIGRATION_RATE = self.cfg.get('intergroup_rate', 0.0005) # Decimal percentage that population groups will migrate each tick
        self.migration = Migration(self.rng, DEFAULT_MIGRATION_RATE) # Init migration object for this city

        self.labour_market = LabourMarket(self.rng, country_policy = None) # Init labour market object for this city
        self.firms = firms

        self.name = name
        self.populations = populations

        self.migration_attractiveness = sum(group.migration_attractiveness for group in self.populations) / len(self.populations)

        self.inv = {}
        for firm in firms:
            self.inv.setdefault(firm.good, 0) # Add each good that firms produce for this city to a dictionary

        self.city_data = CityData(self)

    def tick(self):
        for group in self.populations: # City controls tick updates of all owned population groups
            group.tick()
        self.migration_attractiveness = sum(group.migration_attractiveness for group in self.populations) / len(self.populations)
        
        self.employed = self.labour_market.clear_market(
            populations = self.populations,
            firms = self.firms
        )

        for firm in self.firms: 
            firm.tick() # Tick updates productivity after employement and makes the firm produce goods.
            if firm.good not in self.inv: # Make sure the good is in the city before transferring it
                self.inv.setdefault(firm.good, 0)

            if firm.ownership == "state":
                self.inv[firm.good] += firm.transfer_to_city() # SOEs transfer their inventory to the city.


        food_needed = sum(g.compute_food_consumption() for g in self.populations)

        if food_needed < self.inv["food"]:
            self.inv["food"] -= food_needed
            self.last_food_deficit = None
        else:
            self.last_food_deficit = food_needed - self.inv["food"] # To be used for imports later
            self.migration_attractiveness = 0 # No one wants to migrate to a starving city. They aren't allowed in anyway.
            self.inv["food"] = 0
                    
        
        self.run_migrations() # Runs migrations between population groups
        self.city_data.update_pop_data() 
        


    def run_migrations(self):
        if self.cfg.get('migration', {}).get('enabled', True):

            self.migrations = []

            for i, group in enumerate(self.populations, 1):
                migrated_amount, target = self.migration.migrate(group, self.populations)

                if migrated_amount > 0:
                    target_index = self.populations.index(target) + 1
                    self.migrations.append((i, migrated_amount, target_index))
    

