"""Quick utility to inspect Natural Earth GeoDataFrame columns.

Run before the simulation to verify available fields:
    python3 model/location/inspect_gdf_columns.py
    python3 model/location/inspect_gdf_columns.py --only cities
"""

# TODO: consider removing this file after inspection, as it was primarily for development and debugging purposes that are done now.

import argparse
from pathlib import Path

import geopandas as gpd


GDF_LABELS = {
    "cities": "city_gdf",
    "provinces": "provinces_gdf",
    "countries": "country_gdf",
}

SHAPEFILES = {
    "cities": "ne_10m_populated_places/ne_10m_populated_places.shp",
    "provinces": "ne_10m_admin_1_states_provinces/ne_10m_admin_1_states_provinces.shp",
    "countries": "ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp",
}


def _load_local_data(base_dir: Path) -> dict:
    data = {}
    missing = []

    for key, rel_path in SHAPEFILES.items():
        shp_path = base_dir / rel_path
        if not shp_path.exists():
            missing.append(str(shp_path))
            continue
        data[key] = gpd.read_file(shp_path)

    if missing:
        missing_list = "\n".join(f"- {m}" for m in missing)
        raise FileNotFoundError(
            "Missing shapefiles. Download/load Natural Earth first. Missing:\n"
            f"{missing_list}"
        )

    return data


def _print_columns(key: str, gdf: gpd.GeoDataFrame) -> None:
    label = GDF_LABELS[key]
    cols = list(gdf.columns)
    print(f"\n{label} ({key}) columns [{len(cols)}]:")
    for col in cols:
        print(f"- {col}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect Natural Earth GDF columns.")
    parser.add_argument(
        "--only",
        choices=("cities", "provinces", "countries", "all"),
        default="all",
        help="Inspect only one GeoDataFrame.",
    )
    parser.add_argument(
        "--data-dir",
        default="data/map_data",
        help="Base directory containing extracted Natural Earth shapefiles.",
    )
    args = parser.parse_args()

    data = _load_local_data(Path(args.data_dir))

    selected = (
        [args.only] if args.only != "all" else ["cities", "provinces", "countries"]
    )
    for key in selected:
        _print_columns(key, data[key])


if __name__ == "__main__":
    main()
