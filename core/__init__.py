

from config import CONFIG

CONFIG = CONFIG


SEED_CFG = CONFIG.get('seed', {})
CITY_CFG = CONFIG.get('city', {})
PROVINCE_CFG = CONFIG.get('province', {})
MAIN_CFG = CONFIG.get('main', {})

from .ticks import Core