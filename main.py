'''
This module calls core to run the simulation, and prints outputs
'''
from config import CONFIG
from model.core import Core
from visualisation.report import report
from visualisation.graph import graph_total_pop


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
        country_cfg=CONFIG.get("country")
        )

    core.build_sim()

    for week in range(1, 52):

        core.tick()

        if REPORTER_CFG.get('enabled', True) and week % REPORTER_CFG.get('report_interval', 1) == 0:
            spr = REPORTER_CFG.get('sub_province_report', False)

            report(week, core, spr)

    graph_total_pop(city_data=core.countries[0].provinces[0].cities[0].city_data)


if __name__ == "__main__":  # Temporary main function for testing
    main()
