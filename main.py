from city import City
from population import PopulationGroup


def main():
    pop = [PopulationGroup(size=1000, healthcare=0.7, healthcare_capacity = 1100), PopulationGroup(size=500, healthcare=0.9, healthcare_capacity = 600), PopulationGroup(size=2000, healthcare=0.4, healthcare_capacity = 1900)] # Example population groups.

    city = City(pop)

    for week in range(52): # Simulate one year, weekly ticks
        city.tick()
        print(f"Week {week + 1}: population = {int(round(city.total_population))}, births = {city.birth_total:.3f}, deaths = {city.death_total:.3f}") # This only prints totals. Considering making rounding a helper function for use elsewhere

        for g in city.get_population_data(): # Prints data for all groups in city
            print(f"Group {g['group']}: size = {int(round(g['size']))}, healthcare = {g['healthcare']:.2f}")

        for migration in g['migrations']: # Prints migration data
            from_group, amount, to_group = migration
            print(f"{from_group} -> {to_group}, amount: {amount:.3f}")

if __name__ == "__main__":  # Temporary main function for testing
    main()
