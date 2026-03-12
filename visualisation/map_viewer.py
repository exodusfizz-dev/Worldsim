"""Simple map display using merged province geometries from the simulation core."""

import geopandas as gpd
import matplotlib.pyplot as plt


def show_merged_provinces_map(core) -> None:
    """Display country outlines with merged province boundaries from core.countries."""
    province_rows = []
    country_rows = []

    for country in core.countries:
        country_geoms = []
        for province in country.provinces:
            if province.geometry is None:
                continue
            country_geoms.append(province.geometry)
            province_rows.append(
                {
                    "country": country.name,
                    "province": province.name,
                    "geometry": province.geometry,
                }
            )

        if country_geoms:
            country_rows.append(
                {
                    "country": country.name,
                    "geometry": gpd.GeoSeries(country_geoms).union_all(),
                }
            )

    if not province_rows:
        raise ValueError("No province geometries found in core.countries")

    provinces_gdf = gpd.GeoDataFrame(province_rows, geometry="geometry", crs="EPSG:4326")
    countries_gdf = gpd.GeoDataFrame(country_rows, geometry="geometry", crs="EPSG:4326")

    fig, ax = plt.subplots(figsize=(14, 8))

    if not countries_gdf.empty:
        countries_gdf.boundary.plot(ax=ax, color="#222222", linewidth=1.2)
    provinces_gdf.boundary.plot(ax=ax, color="#1f77b4", linewidth=0.6, alpha=0.95)

    ax.set_title("Merged Simulation Provinces")
    ax.set_axis_off()
    plt.tight_layout()
    plt.show()
