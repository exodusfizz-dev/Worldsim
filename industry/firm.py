class Firm:
    def __init__(self, productivity, production_capacity, capital, ownership, wage, good):
        self.productivity = productivity # Output per unit of labour
        self.production_capacity = production_capacity # Maximum production capacity

        self.capital = capital # Available capital for production
        self.ownership = ownership # Placeholder for ownership structure (state, corporate, cooperative)

        self.wage = wage # Amount paid to default worker
        self.employed = 0
        self.total_productivity = 0

        self.inventory = 0 # How many of the good are stored.
        self.good = good # What good this firm produces. Each firm produces one good only. 

    def labour_demand(self):
        return min(self.production_capacity / self.productivity, self.capital / self.wage)
    
    def update_total_productivity(self):
        self.total_productivity = min(self.productivity * self.employed, self.production_capacity)

        return self.total_productivity

    def produce(self):
        self.inventory += self.total_productivity


    def tick(self):
        self.update_total_productivity()
        self.produce()

    def transfer_to_city(self):
        amount = self.inventory
        self.inventory = 0
        return amount




