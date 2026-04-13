"""
Procedural world generation from Natural Earth data.

Loads real geographic data based on actual city/province/country attributes.
"""

# TODO: Look at efficiency - loading whole world is slow


from dataclasses import dataclass
import geopandas as gpd
from .load_maps import load_natural_earth_data
from model.economy.industry import FirmGenerator
from .assign_cities import assign_cities
from model.location.province_collator import (
    CountryPolyStrategy,
    RegionStrategy,
    ResolveProvinces,
    DefaultProvinces,
)


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
        """Initialize loader and source data."""
        self.rng = rng
        self.city_cfg = city_cfg
        self.province_cfg = province_cfg
        self.country_cfg = country_cfg
        self.location_cfg: dict = location_cfg or {}

        self.firm_gen = FirmGenerator(rng)

        self.ne_data = load_natural_earth_data()
        self._prepare_indexes()

    def _prepare_indexes(self):
        """Build reusable indexes for fast country/province/city lookups."""
        self.cities_gdf = self.ne_data["cities"].copy()
        self.provinces_gdf = self.ne_data["provinces"].copy()
        self.countries_gdf = self.ne_data["countries"].copy()

        self.countries_gdf["name_lower"] = self.countries_gdf["NAME"].str.lower()
        self.provinces_gdf["admin_lower"] = self.provinces_gdf["admin"].str.lower()
        self.cities_gdf["adm0_lower"] = self.cities_gdf["ADM0NAME"].str.lower()

        self.country_names = sorted(self.countries_gdf["NAME"].dropna().unique().tolist())
        self.country_name_set = set(self.countries_gdf["name_lower"].dropna().tolist())

        self.provinces_by_country = {
            country_name: group.drop(columns=["admin_lower"])
            for country_name, group in self.provinces_gdf.groupby("admin_lower", sort=False)
        }
        self.cities_by_country = {
            country_name: group.drop(columns=["adm0_lower"])
            for country_name, group in self.cities_gdf.groupby("adm0_lower", sort=False)
        }

    def load_country(self, country_name: str) -> dict:
        """Load a single country's data from Natural Earth and generate simulation."""
        country_key = country_name.lower()
        if country_key not in self.country_name_set:
            raise ValueError(f"Country '{country_name}' not found in Natural Earth data")

        country_data = {
            "name": country_name,
            "provinces": self._load_provinces_for_country(country_key),
        }

        return country_data

    def _select_province_collator(self, base_provinces: gpd.GeoDataFrame) -> "ResolveProvinces":
        """Pick a province collator strategy."""
        if len(base_provinces) <= self.location_cfg.get("province_collation_threshold", 5):
            return CountryPolyStrategy()
        if base_provinces["region"].nunique() > 4:
            return RegionStrategy()
        return DefaultProvinces()

    def _build_province_output(
        self,
        provinces: dict[int, dict],
        cities: gpd.GeoDataFrame,
    ) -> list[dict]:
        """Convert collated provinces based on base provinces into data for sim builder."""
        has_any_city = not cities.empty
        city_payload_by_id = self._prepare_city_payloads(cities) if has_any_city else {}
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
                    "area": int(geometry.area * 111 * 111),
                    "geometry": geometry,
                    "cities": self._load_cities_for_province(
                        city_ids=city_ids,
                        city_payload_by_id=city_payload_by_id,
                    ),
                }
            )

        return output_items

    def _load_provinces_for_country(self, country_name: str) -> list[dict]:
        """Load provinces (admin_1) for a country."""

        base_provinces = self.provinces_by_country.get(country_name)
        cities = self.cities_by_country.get(country_name)

        if base_provinces is None or base_provinces.empty:
            return []

        base_provinces = base_provinces.copy().reset_index(drop=True)
        base_provinces["base_id"] = base_provinces.index.astype(int)

        cities = cities.copy().reset_index(drop=True) if cities is not None else gpd.GeoDataFrame()
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

    def _prepare_city_payloads(self, cities_gdf: gpd.GeoDataFrame) -> dict[int, tuple]:
        """Prepare immutable city payload data indexed by city_id for fast province assembly."""
        city_count = len(cities_gdf)
        city_payload_by_id: dict[int, tuple] = {}

        for idx, city_row in enumerate(cities_gdf.itertuples(index=False)):
            city_id = int(city_row.city_id)
            city_name = getattr(city_row, "NAME", f"City_{idx}")
            pop_max = getattr(city_row, "POP_MAX", 10_000)
            population = 10_000 if pop_max is None else int(pop_max)
            city_size_rank = idx / max(1, city_count)
            city_payload_by_id[city_id] = (city_name, population, city_row.geometry, city_size_rank)

        return city_payload_by_id

    def _load_cities_for_province(
        self,
        city_ids: list[int],
        city_payload_by_id: dict[int, tuple] | None,
    ) -> list[dict]:
        """Load cities (populated places) for a province."""
        if not city_payload_by_id or not city_ids:
            return []

        city_list = []
        for city_id in city_ids:
            payload = city_payload_by_id.get(city_id)
            if payload is None:
                continue
            city_name, population, geometry, city_size_rank = payload

            city_data = {
                "name": city_name,
                "geometry": geometry,
                "population_estimate": population,
                "firms": self.firm_gen.generate_for_city(population, city_size_rank),
                "city_id": city_id,
            }
            city_list.append(city_data)

        return city_list

    def load_world(self, country_names: list[str]) -> list[dict]:
        """Load multiple countries and return as list compatible with Core.build_sim()."""
        countries_data = []
        if not country_names:
            country_names = self.country_names
        for country_name in country_names:
            try:
                country_data = self.load_country(country_name)
                countries_data.append(country_data)
            except ValueError as e:
                print(f"Warning: {e}")

        return countries_data

    def release_resources(self) -> None:
        """Drop large cached GeoDataFrames and indexes once loading is complete."""
        self.ne_data = {}
        self.cities_gdf = gpd.GeoDataFrame()
        self.provinces_gdf = gpd.GeoDataFrame()
        self.countries_gdf = gpd.GeoDataFrame()
        self.provinces_by_country = {}
        self.cities_by_country = {}
        self.country_names = []
        self.country_name_set = set()
