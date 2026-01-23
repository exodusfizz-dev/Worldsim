from city import City
from population import PopulationGroup


def main():
    pop = PopulationGroup(size=1000, healthcare=0.7)
    city = City([pop])

    for week in range(52):
        city.tick()
        print(f"Week {week + 1}: population = {int(round(pop.size))}") # This only prints the first group. Considering making rounding a helper function for use elsewhere


if __name__ == "__main__":
    main()
