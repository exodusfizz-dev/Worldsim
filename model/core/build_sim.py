"""Simulation build orchestration for Core."""

from model.city import City, CityPopulation
from model.economy import Firm
from model.country import Country
from model.province import Province
from model.location.world_data_loader import WorldDataLoader


def build_firms(core, firms, city_id: int):
    return [Firm.from_dict(firm_data, rng=core.rng, city_id=city_id) for firm_data in firms]


def build_city(core, city_data):
    pop_seed = core.population_gen.generate_for_city(
        city_name=city_data["name"],
        population=int(city_data.get("population_estimate", 0)),
    )
    population = CityPopulation.from_seed(
        seed=pop_seed,
        rng=core.rng,
        cfg=core.city_cfg.get("population", {}),
    )

    firms = build_firms(core, city_data["firms"], city_id=city_data["city_id"])

    return City.from_dict(
        city_data,
        population,
        firms,
        rng=core.rng,
        cfg=core.city_cfg,
    )


def build_province(core, province_data):
    cities = [build_city(core, city_data) for city_data in province_data["cities"]]
    return Province.from_dict(province_data, cities, cfg=core.province_cfg, rng=core.rng)


def build_provinces(core, data):
    return [build_province(core, province_data) for province_data in data["provinces"]]


def build_sim(core, countries_to_load=None):
    """Build simulation entities from Natural Earth-derived world data."""
    loader = WorldDataLoader(
        rng=core.rng,
        city_cfg=core.city_cfg,
        province_cfg=core.province_cfg,
        country_cfg=core.country_cfg,
        location_cfg=core.location_cfg,
    )

    if countries_to_load is None:
        countries_to_load = []

    data = {"countries": loader.load_world(countries_to_load)}

    for country_data in data["countries"]:
        provinces = build_provinces(core, data=country_data)
        country_obj = Country.from_dict(
            country_data,
            provinces,
            cfg=core.country_cfg,
            rng=core.rng,
        )
        core.countries.append(country_obj)
