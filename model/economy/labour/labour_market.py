'''labour_market.py holds the class LabourMarket, which handles employment.'''

class LabourMarket:
    '''
    Labour market object is owned by cities and assigns workers to firms.
    '''
    def __init__(self, rng, country_policy = None):
        self.rng = rng
        self.country_policy = country_policy

    def compute_supply(self, populations):
        '''
        Helper function for clear_market.
        
        Returns a list of individual group supplies (the number fit to be employed),
        and the total supply of labour across the city.
        '''
        group_supply = [int(group.size * max(group.employable, 0)) for group in populations]
        total_supply = sum(group_supply)
        return group_supply, total_supply

    def compute_labour_demand(self, firms):
        '''
        Helper function for clear_market.
        
        Returns a list of individual demands, and the total demand of all firms.
        '''
        firm_demands = [int(firm.labour_demand()) for firm in firms]
        total_demand = sum(firm_demands)

        return firm_demands, total_demand

    def clear_market(self, populations, firms):
        '''
        Assigns employable people to firms.
        
        :param self: labour market obj
        :param populations: groups supplying labour
        :param firms: industries demanding labour
        '''
        supply_g, total_supply = self.compute_supply(populations)
        demand_f, total_demand = self.compute_labour_demand(firms)

        if total_supply == 0 or total_demand == 0:
            return 0

        total_employed = min(total_supply, total_demand)
        hire_rate = total_employed / total_supply


        for g, supply in zip(populations, supply_g):
            employed_count = int(hire_rate * supply)
            g.employed = employed_count

        demand_fill_rate = total_employed / total_demand

        for f, demand in zip(firms, demand_f):
            workers_employed = int(demand * demand_fill_rate)
            f.employed = workers_employed
            # f.capital -= workers_employed * f.wage

        return total_employed
