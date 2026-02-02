from config import CONFIG
from core import Core

MAIN_CFG = CONFIG["main"]


def main():

    core = Core(
    seed_cfg=CONFIG["seed"],
    city_cfg=CONFIG["city"],
    province_cfg=CONFIG["province"]
    )

    for week in range(52):

        core.tick()

        if MAIN_CFG['reporter']['enabled'] and week % MAIN_CFG['reporter']['save_interval'] == 0:
            report(week, core)


def report(week, core):
        print(f"Week {week+1}: ")

        for province in core.provinces:

            print(f"Province: {province.name}")
            for city in province.cities:

                print(f"{city.name}: \nPopulation = {int(city.total_population)} \nProductivity = {city.productivity:.2f}, Births = {city.birth_total}, Deaths = {city.death_total}")

                for g in city.sum_population_data():
                    print(
                        f"Group {g['group']}: "
                        f"size = {int(g['size'])}, "
                        f"healthcare = {g['healthcare']:.3f}, "
                        f"employment_rate = {g['employment_rate']:.3f},"
                    )

                for migration in city.migrations: # Prints migration data

                    from_group, amount, to_group = migration
                    print(f"{from_group} -> {to_group}, amount: {amount:.3f}")
                    

if __name__ == "__main__":  # Temporary main function for testing
    main()
