
from core import Core


def main():

    core = Core()

    for week in range(52):

        core.tick()

        print(f"Week {week+1}: ")
        for province, provincename in core.provinces:
            print(f"Province: {provincename}")
            for city, cityname in province.cities:
                print(f"{cityname}: \nPopulation = {int(city.total_population)} \nProductivity = {city.productivity:.2f}")

                for g in city.sum_population_data():
                    print(
                        f"Group {g['group']}: "
                        f"size = {int(g['size'])}, "
                        f"healthcare = {g['healthcare']:.3f}, "
                        f"employment_rate = {g['employment_rate']:.3f}, "
                    )

                for migration in city.migrations: # Prints migration data
                    
                    from_group, amount, to_group = migration
                    print(f"{from_group} -> {to_group}, amount: {amount:.3f}")


if __name__ == "__main__":  # Temporary main function for testing
    main()
