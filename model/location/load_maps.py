import os
import requests
import zipfile
import geopandas as gpd


def get_natural_earth(category, name, res="10m", data_dir="./data/map_data"):
    """
    Downloads, unzips, and loads Natural Earth vector data.
    Categories: 'cultural', 'physical'
    """
    os.makedirs(data_dir, exist_ok=True)


    base_url = f"https://naciscdn.org/naturalearth/{res}/{category}/"
    filename = f"ne_{res}_{name}.zip"
    url = base_url + filename

    zip_path = os.path.join(data_dir, filename)
    extract_dir = os.path.join(data_dir, f"ne_{res}_{name}")


    if not os.path.exists(extract_dir):
        print(f"Downloading {name} ({res})...")
        r = requests.get(url, stream=True, timeout=10)
        with open(zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        os.remove(zip_path)


    shp_file = os.path.join(extract_dir, f"ne_{res}_{name}.shp")
    return gpd.read_file(shp_file)


def load_natural_earth_data():
    '''Loads data for world.py.'''

    countries = get_natural_earth("cultural", "admin_0_countries")
    provinces = get_natural_earth("cultural", "admin_1_states_provinces")
    cities = get_natural_earth("cultural", "populated_places")

    return {"countries": countries, "provinces": provinces, "cities": cities}
