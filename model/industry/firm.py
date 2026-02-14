from model.core.random import _sample_normal

class Firm:
    def __init__(self, productivity, production_capacity, capital, ownership, wage, good, rng):
        self.productivity = productivity # Output per unit of labour
        self.production_capacity = production_capacity # Maximum production capacity

        self.capital = capital # Available capital for production
        self.ownership = ownership # Placeholder for ownership structure (state, corporate, cooperative)

        self.wage = wage # Amount paid to default worker
        self.employed = 0
        self.total_productivity = 0

        self.inventory = 0 # How many of the good are stored.
        self.good = good # What good this firm produces. Each firm produces one good only.

        self.rng = rng

    def labour_demand(self):
        '''Limiting factor of employment is either:
        The production capacity / output per worker,
        Or the capital available to pay workers'''
        return min(self.production_capacity / self.productivity, self.capital / self.wage)
    
    def update_total_productivity(self):
        self.total_productivity = max(min(self.productivity * self.employed, self.production_capacity), 0)

        return self.total_productivity

    def produce(self):
        self.inventory += _sample_normal(expected = self.total_productivity, rng = self.rng)


    def tick(self):
        self.update_total_productivity()
        self.produce()

    def transfer_to_city(self):
        amount = self.inventory
        self.inventory = 0
        return amount
