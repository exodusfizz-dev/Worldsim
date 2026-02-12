'''
This module calls core to run the simulation, and prints outputs
'''
from config import CONFIG
from model.core import Core


MAIN_CFG = CONFIG["main"]
REPORTER_CFG = MAIN_CFG.get("reporter", {})


def main():
    '''
    Runs whole simulation. Also handles output by calling report function
    '''
 # Core initialises whole simulation.
    core = Core(
        seed_cfg=CONFIG.get("seed"),
        city_cfg=CONFIG.get("city"),
        province_cfg=CONFIG.get("province"),
        )

    core.build_sim()

    for week in range(1, 52):

        core.tick()

        if REPORTER_CFG.get('enabled', True) and week % REPORTER_CFG.get('report_interval', 1) == 0:

            report(week, core)

def report(week, core):
    '''
    Outputs data for main
    
    :param week: week number (int)
    :param core: core object
    '''
    print(f"------\n------\nWeek {week}: ")

    for province in core.provinces:

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
                    f"employment_rate = {g['employment_rate']:.3f},"
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


if __name__ == "__main__":  # Temporary main function for testing
    main()
