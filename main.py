
from calendar import week
from core import Core
import core


def main():

    core = Core()

    for week in range(52):

        core.tick()

        print(f"Week {week+1}: ")

        for city, cityname in core.cities:
            print(f"{cityname}: \nPopulation = {int(city.total_population)}")

            for g in city.get_population_data():
                print(
                    f"Group {g['group']}: "
                    f"size = {int(g['size'])}, "
                    f"healthcare = {g['healthcare']:.3f}"
                )

        for migration in g['migrations']: # Prints migration data
            from_group, amount, to_group = migration
            print(f"{from_group} -> {to_group}, amount: {amount:.3f}")


if __name__ == "__main__":  # Temporary main function for testing
    main()
