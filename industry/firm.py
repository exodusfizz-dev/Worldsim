class Firm:
    def __init__(self, productivity, production_capacity, capital, ownership, wage):
        self.productivity = productivity # Output per unit of labour
        self.production_capacity = production_capacity # Maximum production capacity
        self.capital = capital # Available capital for production
        self.ownership = ownership # Placeholder for ownership structure (state, corporate, cooperative)
        self.wage = wage # Amount paid to default worker
        self.employed = 0
        self.total_productivity = 0

    def labour_demand(self):
        return min(self.production_capacity, self.capital / self.wage)
    
    def update_total_productivity(self):
        self.total_productivity = self.productivity * self.employed

        
        return self.total_productivity



