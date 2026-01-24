from city import City
from population import PopulationGroup


def main():
    pop = [PopulationGroup(size=1000, healthcare=0.5), PopulationGroup(size=500, healthcare=0.9)]
    city = City(pop)
    for week in range(52):
        city.tick()
        print(f"Week {week + 1}: population = {int(round(city.total_population))}, births = {city.birth_total}, deaths = {city.death_total}") # This only prints the first group. Considering making rounding a helper function for use elsewhere

        for g in city.get_population_data():
            print(f"Group {g['group']}: size = {int(round(g['size']))}, healthcare = {g['healthcare']}")
            
if __name__ == "__main__":
    main()
