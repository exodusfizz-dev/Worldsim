'''Handles province collation.'''

from typing import Protocol


from shapely import union_all

class ResolveProvinces(Protocol):
    def collate_provinces(self, base_provinces, city_assignments, min_cities) -> dict[int, dict]:
        raise NotImplementedError


class CountryPolyStrategy(ResolveProvinces):
    '''The intended strategy for micro state generation. 
    Simply merges all provinces into one, and assigns all cities to it.'''
    def collate_provinces(self,
                          base_provinces,
                          city_assignments,
                          min_cities) -> dict[int, dict]:
        provinces: dict[int, dict] = {}
        flattened_city_ids = [city_id
                         for city_id_list in city_assignments.values()
                         for city_id in city_id_list]
        # Get a single country name from the series (all should be the same)
        country_name = base_provinces["admin"].iloc[0]
        provinces[0] = {
            "name": country_name,
            "geometry": union_all(base_provinces.geometry),
            "city_ids": flattened_city_ids,
            "province_ids": list(base_provinces["base_id"]),
            }
        return provinces

class RegionStrategy(ResolveProvinces):
    '''Default strategy for larger countries. Uses natural earth regions.'''
    def collate_provinces(self,
                          base_provinces,
                          city_assignments,
                          min_cities) -> dict[int, dict]:
        provinces: dict[int, dict] = {}
        for _, row in base_provinces.iterrows():
            base_id = int(row["base_id"])
            region = row.get("region", "Unknown")
            if region not in provinces:
                provinces[region] = {
                    "name": region,
                    "geometry": None,
                    "city_ids": [],
                    "province_ids": [],
                }
            provinces[region]["city_ids"].extend(city_assignments.get(base_id, []))
            provinces[region]["province_ids"].append(base_id)
            if provinces[region]["geometry"] is None:
                provinces[region]["geometry"] = row["geometry"]
            else:
                provinces[region]["geometry"] = provinces[region]["geometry"].union(row["geometry"])
        return provinces

class DefaultProvinces(ResolveProvinces):
    '''Uses default provinces for countries that have few or no regions.'''
    def collate_provinces(self,
                          base_provinces,
                          city_assignments,
                          min_cities) -> dict[int, dict]:
        provinces: dict[int, dict] = {}
        for _, row in base_provinces.iterrows():
            base_id = int(row["base_id"])
            province_name = row.get("name", f"Province_{base_id}")
            provinces[base_id] = {
                "name": province_name,
                "geometry": row["geometry"],
                "city_ids": city_assignments.get(base_id, []),
                "province_ids": [base_id],
            }
        return provinces
    