'''Helper function to assign cities to base provinces.'''

import geopandas as gpd


def assign_cities(
    provinces: gpd.GeoDataFrame,
    cities: gpd.GeoDataFrame,
) -> dict[int, list[int]]:

    '''Assigns cities to base provinces.'''

    assignments: dict[int, list[int]] = {int(pid): [] for pid in provinces["base_id"]}
    if cities.empty:
        return assignments

    city_points = cities[["city_id", "geometry"]].copy()
    province_polys = provinces[["base_id", "geometry"]].copy()

    within_joins = gpd.sjoin(city_points, province_polys, how="left", predicate="within")

    assigned_map: dict[int, int] = {}

    for _, row in within_joins.dropna(subset=["base_id"]).iterrows():
        city_id = row["city_id"]
        # Keep first match for boundary/overlap edge-cases.
        if city_id not in assigned_map:
            assigned_map[city_id] = int(row["base_id"])

    unmatched = city_points[~city_points["city_id"].isin(list(assigned_map.keys()))]
    # ~ means not, i.e. unmatched = city points that aren't in assigned map. Numpy/pandas specific.
    if not unmatched.empty:
        nearest_joins = gpd.sjoin_nearest(
            unmatched.to_crs(epsg=3857),
            province_polys.to_crs(epsg=3857),
            how="left",
            distance_col="distance_m",
        )
        for _, row in nearest_joins.dropna(subset=["base_id"]).iterrows():
            assigned_map[int(row["city_id"])] = int(row["base_id"])

    for city_id, province_id in assigned_map.items():
        assignments[province_id].append(city_id)

    return assignments
