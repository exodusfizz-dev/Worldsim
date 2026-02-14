'''
Report function is part of the visualisation module. It print data from the model, called in main.py
'''

def report(week, core):
    print(f"------\n------\nWeek {week}: ")
    for country in core.countries:
        print(f"Country: {country.name}")
        report_provinces(country)

def report_provinces(country):
    '''
    Outputs data for main
    
    :param week: week number (int)
    :param country: country object
    '''

    for province in country.provinces:

        print(f"------\nProvince: {province.name}")
        for city in province.cities:

            print(f"{city.name}: \nPopulation = {int(city.total_population)}"\
                f"\nProductivity = {city.productivity:.2f}, "\
                f"Births = {city.birth_total}, "\
                f"Deaths = {city.death_total}"
                )

            for g in city.city_data.sum_population_data():
                print(
                    f"Group {g['group']}: "
                    f"size = {int(g['size'])}, "
                    f"healthcare = {g['healthcare']:.3f}, "
                    f"employment_rate = {g['employment_rate']:.3f}, "
                    f"sick rate = {g['sick_rate']:.3f}"
                    )

            for f in city.city_data.sum_firm_data():
                print(
                    f"Ownership: {f['ownership']}, "                    
                    f"Good: {f['good']}, "
                    f"Employed = {f['employed']}, "
                    f"Total productivity = {f['total_productivity']:.0f},"         
                )

            for good, amount in city.inv.items():
                print(f"Good: {good}, Kgs: {amount:.2f}")

            if city.last_food_deficit:
                print(f"Food deficit: {city.last_food_deficit:.2f} Kgs")
            else:
                print("No food deficit")

            for migration in city.migrations: # Prints migration data

                from_group, amount, to_group = migration
                print(f"{from_group} -> {to_group}, amount: {amount:.3f}")
