'''
City data module contains class CityData, which supplies various data-related functions
'''

class CityData:
    '''
    City data handles data for cities by updating, creating summaries and storing it
    '''
    def __init__(self, city):
        self.city = city

    def update_pop_data(self):
        '''
        Updates data that is dependent on variables the city object handles
        '''
        c = self.city
        c.total_population = sum(group.size for group in c.populations)
        c.birth_total = sum(group.births for group in c.populations)
        c.death_total = sum(group.deaths for group in c.populations)

        # People of fit age and health to work as decimal.
        c.employable = sum(group.employable for group in c.populations) / len(c.populations)

        c.productivity = sum(firm.total_productivity for firm in c.firms)

    def sum_population_data(self):

        '''Returns dictionary summary of all population groups.'''
        c = self.city
        summary = []

        for i, group in enumerate(c.populations, 1):
            summary.append ({
                'group': i,
                'size': group.size,
                'healthcare': group.healthcare,
                'last_births': group.births,
                'last_deaths': group.deaths,
                'employment_rate': group.employment_rate,
                'sick_rate': group.sick_rate
            })

        return summary

    def sum_firm_data(self):

        '''Returns dictionary summary of all firms.'''

        c = self.city
        summary = []

        for firm in c.firms:
            summary.append ({
                'ownership': firm.ownership,
                'good': firm.good,
                'employed': firm.employed,
                'total_productivity': firm.total_productivity
            })

        return summary
    