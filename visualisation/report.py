"""Reporting helpers for console output."""


def report(week, core, spr) -> None:
    """Output simulation data for the current week."""
    print(f"------\n------\nWeek {week}: ")
    countries_to_report = [
        country
        for country in core.countries
        if country.name in core.country_cfg.get("report_countries", ["United Kingdom", "China"])
    ]
    for country in countries_to_report:
        print(f"Country: {country.name}")
        if spr:
            report_provinces(country, week)


def report_provinces(country, week):
    """Output province + city data."""

    for province in country.provinces:
        print(f"------\nProvince: {province.name}")
        for city in province.cities:
            snapshot = city.city_data.data[week - 1]
            city_data = snapshot["city_data"]

            print(
                f"{city.name}: \nPopulation = {int(city_data['population'])}"
                f"\nProductivity = {city_data['productivity']:.2f}, "
                f"Births = {city_data['births']}, "
                f"Deaths = {city_data['deaths']}"
            )

            for g in snapshot["population_data"]:
                print(
                    f"Group {g['group']} (type {g['group_type']}): "
                    f"size = {int(g['size'])}, "
                    f"healthcare = {g['healthcare']:.3f}, "
                    f"employment_rate = {g['employment_rate']:.3f}, "
                    f"sick rate = {g['sick_rate']:.3f}"
                )

            for f in snapshot["firm_data"]:
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
            print(f"City treasury: {city.state.treasury:.2f}")

            for migration in city.migrations:
                from_group = migration.source_group_index + 1
                to_group = migration.target_group_index + 1
                amount = migration.amount
                print(f"{from_group} -> {to_group}, amount: {amount:.3f}")
