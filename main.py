'''
This module calls core to run the simulation, and prints outputs
'''
from config import CONFIG
from model.core import Core
from visualisation.report import report
from visualisation.graph import graph_total_pop
from visualisation.map_viewer import show_merged_provinces_map


MAIN_CFG = CONFIG["main"]
REPORTER_CFG = MAIN_CFG.get("reporter", {})
MAP_DISPLAY_CFG = MAIN_CFG.get("map_display", {})


def main():
    '''
    Runs whole simulation. Also handles output by calling report function
    '''
    # Core initialises whole simulation.
    # TODO: Check entire repo for dead code, especially in city_data.py and protocols.py (to be replaced by networkx distances).
    # TODO: Move all place modules (province, country, city) to a larger encompassing module.
    # TODO: Assert consistecy of typehints, documentation, and naming conventions across the repo for maintainability and readability.
    core = Core(
        seed_cfg=CONFIG.get("seed"),
        city_cfg=CONFIG.get("city"),
        province_cfg=CONFIG.get("province"),
        country_cfg=CONFIG.get("country"),
        location_cfg=CONFIG.get("location")
        )

    core.build_sim()

    if MAP_DISPLAY_CFG.get("enabled", False):
        show_merged_provinces_map(core)

    for week in range(1, 52):

        core.tick()

        if REPORTER_CFG.get('enabled', True) and week % REPORTER_CFG.get('report_interval', 1) == 0:
            spr = REPORTER_CFG.get('sub_province_report', False)

            report(week, core, spr)

    if MAIN_CFG['pop_graph']['enabled']:
        graph_total_pop(city=core.countries[0].provinces[0].cities[0])


if __name__ == "__main__":  # Temporary main function for testing
    main()
