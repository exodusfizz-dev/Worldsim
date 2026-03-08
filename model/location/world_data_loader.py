"""
Procedural world generation from Natural Earth data.

Loads real geographic data and generates simulation entities based on actual city/province/country attributes.
"""

from dataclasses import dataclass
import geopandas as gpd
from shapely.geometry import Point
from .load_maps import load_natural_earth_data
from model.population import PopulationGenerator
from model.economy.industry import FirmGenerator


@dataclass
class LocationMetadata:
    """Geographic metadata attached to simulation entities."""
    lat: float
    lon: float
    geometry: object
    ne_id: str


class WorldDataLoader:
    """Load Natural Earth data and procedurally generate world simulation."""

    def __init__(self, rng, city_cfg: dict, province_cfg: dict, country_cfg: dict):
        """
        Args:
            rng: numpy random generator
            *_cfg: config dicts (for generators and Core)
        """
        self.rng = rng
        self.city_cfg = city_cfg
        self.province_cfg = province_cfg
        self.country_cfg = country_cfg

        self.population_gen = PopulationGenerator(rng)
        self.firm_gen = FirmGenerator(rng)

        self.ne_data = load_natural_earth_data()
        self._prepare_indexes()

    def _prepare_indexes(self):
        """Build spatial indexes for fast lookups."""
        self.cities_gdf = self.ne_data["cities"]
        self.provinces_gdf = self.ne_data["provinces"]
        self.countries_gdf = self.ne_data["countries"]

    def load_country(self, country_name: str) -> dict:
        """Load a single country's data from Natural Earth and generate simulation."""

        country_row = self.countries_gdf[
            self.countries_gdf["NAME"].str.lower() == country_name.lower()
        ]

        if country_row.empty:
            raise ValueError(f"Country '{country_name}' not found in Natural Earth data")

        country_data = {
            "name": country_name,
            "provinces": self._load_provinces_for_country(country_name),
        }

        return country_data

    def _load_provinces_for_country(self, country_name: str) -> list[dict]:
        """Load provinces (admin_1) for a country."""

        provinces = self.provinces_gdf[
            self.provinces_gdf["admin"].str.lower() == country_name.lower()
        ]

        province_list = []
        for _, province_row in provinces.iterrows():
            province_name = province_row["name"]
            geometry = province_row.geometry

            province_data = {
                "name": province_name,
                "area": int(geometry.area * 111 * 111),  # Rough km^2 estimate
                "geometry": geometry,
                "cities": self._load_cities_for_province(country_name, province_name),
            }
            province_list.append(province_data)

        return province_list

    def _load_cities_for_province(
        self, country_name: str, province_name: str
    ) -> list[dict]:

        """Load cities (populated places) for a province."""

        cities = self.cities_gdf[
            (self.cities_gdf["ADM0NAME"].str.lower() == country_name.lower())
            & (self.cities_gdf["ADM1NAME"].str.lower() == province_name.lower())
        ]

        city_list = []
        for idx, (_, city_row) in enumerate(cities.iterrows()):
            city_name = city_row.get("NAME", f"City_{idx}")
            population = int(city_row.get("POP_MAX", 10000))
            geometry = city_row.geometry

            city_size_rank = idx / max(1, len(cities))

            city_data = {
                "name": city_name,
                "geometry": geometry,
                "groups": self.population_gen.generate_for_city(city_name, population),
                "firms": self.firm_gen.generate_for_city(
                    city_name, population, city_size_rank
                ),
            }
            city_list.append(city_data)

        return city_list

    def load_world(self, country_names: list[str]) -> list[dict]:
        """Load multiple countries and return as list compatible with Core.build_sim()."""
        countries_data = []
        for country_name in country_names:
            try:
                country_data = self.load_country(country_name)
                countries_data.append(country_data)
            except ValueError as e:
                print(f"Warning: {e}")

        return countries_data
