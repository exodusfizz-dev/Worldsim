from city import City
from population import PopulationGroup


def main():
    pop = [PopulationGroup(size=1000, healthcare=0.7, healthcare_capacity = 1100), PopulationGroup(size=500, healthcare=0.9, healthcare_capacity = 600), PopulationGroup(size=2000, healthcare=0.4, healthcare_capacity = 1900)]
    city = City(pop)
    for week in range(52):
        city.tick()
        print(f"Week {week + 1}: population = {int(round(city.total_population))}, births = {city.birth_total}, deaths = {city.death_total}") # This only prints the first group. Considering making rounding a helper function for use elsewhere

        for g in city.get_population_data():
            print(f"Group {g['group']}: size = {int(round(g['size']))}, healthcare = {g['healthcare']}")

        for migration in g['migrations']:
            from_group, amount, to_group = migration
            print(f"{from_group} -> {to_group}, amount: {amount}")

if __name__ == "__main__":
    main()
