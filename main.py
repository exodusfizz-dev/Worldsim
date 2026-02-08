from config import CONFIG
from core import Core
from city import CityData


MAIN_CFG = CONFIG["main"]
REPORTER_CFG = MAIN_CFG.get("reporter", {})


def main(): 
    try: # Core initialises whole simulation.
        core = Core(
            seed_cfg=CONFIG.get("seed"),
            city_cfg=CONFIG.get("city"),
            province_cfg=CONFIG.get("province"),
        )
    except Exception as e:
        print(f"Failed to load config: {e}")
        return

    for week in range(1, 52):

        core.tick()

        if REPORTER_CFG.get('enabled', True) and week % REPORTER_CFG.get('report_interval', 1) == 0:
            
            report(week, core)

def report(week, core):
    print(f"------\n------\nWeek {week}: ")

    for province in core.provinces:

        print(f"------\nProvince: {province.name}")
        for city in province.cities:

            print(f"{city.name}: \nPopulation = {int(city.total_population)} \nProductivity = {city.productivity:.2f}, Births = {city.birth_total}, Deaths = {city.death_total}")

            for g in CityData.sum_population_data(city):
                print(
                    f"Group {g['group']}: "
                    f"size = {int(g['size'])}, "
                    f"healthcare = {g['healthcare']:.3f}, "
                    f"employment_rate = {g['employment_rate']:.3f},"
                    )

            for f in CityData.sum_firm_data(city):
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

