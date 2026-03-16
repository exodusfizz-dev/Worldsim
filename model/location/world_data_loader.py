"""
Procedural world generation from Natural Earth data.

Loads real geographic data based on actual city/province/country attributes.
"""

from dataclasses import dataclass
import geopandas as gpd
from .load_maps import load_natural_earth_data
from model.population import PopulationGenerator
from model.economy.industry import FirmGenerator
from .assign_cities import assign_cities
from model.location.province_collator import CountryPolyStrategy, RegionStrategy, ResolveProvinces, DefaultProvinces


@dataclass
class LocationMetadata:
    """Geographic metadata attached to simulation entities."""
    lat: float
    lon: float
    geometry: object
    ne_id: str


class WorldDataLoader:
    """Load Natural Earth data and procedurally generate world simulation."""

    def __init__(self, rng, city_cfg: dict, province_cfg: dict, country_cfg: dict, location_cfg: dict):
        """
        Args:
            rng: numpy random generator
            *_cfg: config dicts (for generators and Core)
        """
        self.rng = rng
        self.city_cfg = city_cfg
        self.province_cfg = province_cfg
        self.country_cfg = country_cfg
        self.location_cfg: dict = location_cfg or {}

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

    def _select_province_collator(self, base_provinces: gpd.GeoDataFrame) -> "ResolveProvinces":
        """Pick a province collator strategy."""
        if len(base_provinces) <= self.location_cfg.get("province_collation_threshold", 5):
            return CountryPolyStrategy()
        if base_provinces["region"].nunique() > 4:  # Arbitrary threshold for "many" regions
            return RegionStrategy()
        return DefaultProvinces()

    def _build_province_output(
        self,
        provinces: dict[int, dict],
        cities: gpd.GeoDataFrame,
    ) -> list[dict]:
        """Convert collated provinces based on base provinces into data for sim builder."""
        has_any_city = not cities.empty
        output_items: list[dict] = []

        for province in provinces.values():
            city_ids = list(province.get("city_ids", []))
            if has_any_city and not city_ids:
                continue

            province_name = province.get("name") or f"Province_{len(output_items)}"
            geometry: object = province.get("geometry")

            output_items.append(
                {
                    "name": province_name,
                    "area": int(geometry.area * 111 * 111),  # Rough km^2 estimate
                    "geometry": geometry,
                    "cities": self._load_cities_for_province(city_ids=city_ids, cities_gdf=cities),
                }
            )

        return output_items

    def _load_provinces_for_country(self, country_name: str) -> list[dict]:
        """Load provinces (admin_1) for a country."""

        base_provinces = self.provinces_gdf[
            self.provinces_gdf["admin"].str.lower() == country_name.lower()
        ].copy()
        cities = self.cities_gdf[
            self.cities_gdf["ADM0NAME"].str.lower() == country_name.lower()
        ].copy()

        if base_provinces.empty:
            return []

        base_provinces = base_provinces.reset_index(drop=True)
        base_provinces["base_id"] = base_provinces.index.astype(int)

        cities = cities.reset_index(drop=True)
        cities["city_id"] = cities.index.astype(int)

        city_assignments = assign_cities(base_provinces, cities)

        min_cities = int(self.location_cfg.get("min_cities_per_province", 5))

        collator = self._select_province_collator(base_provinces)

        provinces = collator.collate_provinces(
            base_provinces=base_provinces,
            city_assignments=city_assignments,
            min_cities=min_cities,
        )

        return self._build_province_output(
            provinces=provinces,
            cities=cities,
        )

    def _load_cities_for_province(
        self, city_ids: list[int], cities_gdf: gpd.GeoDataFrame
    ) -> list[dict]:

        """Load cities (populated places) for a province."""

        cities = cities_gdf[cities_gdf['city_id'].isin(city_ids)]

        city_list = []
        for idx, (_, city_row) in enumerate(cities.iterrows()):
            city_name = city_row.get("NAME", f"City_{idx}")
            population = int(city_row.get("POP_MAX", 10000))
            geometry = city_row.geometry
            city_id = int(city_row["city_id"])

            city_size_rank = idx / max(1, len(cities))

            city_data = {
                "name": city_name,
                "geometry": geometry,
                "groups": self.population_gen.generate_for_city(city_name, population),
                "firms": self.firm_gen.generate_for_city(population, city_size_rank),
                "city_id": city_id
            }
            city_list.append(city_data)

        return city_list

    def load_world(self, country_names: list[str] ) -> list[dict]:
        """Load multiple countries and return as list compatible with Core.build_sim()."""
        countries_data = []
        if not country_names:
            country_names = self.ne_data["countries"]["NAME"].tolist()
        for country_name in country_names:
            try:
                country_data = self.load_country(country_name)
                countries_data.append(country_data)
            except ValueError as e:
                print(f"Warning: {e}")

        return countries_data
