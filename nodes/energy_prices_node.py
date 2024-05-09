import datetime
import os
import requests
import json
from loguru import logger

ENERGY_CACHE_DIR = "energy_cache"
DATA_TYPES_URLS = {
    "electricity_price_today": "https://enever.nl/api/stroomprijs_vandaag.php?token=",
    "electricity_price_tomorrow": "https://enever.nl/api/stroomprijs_morgen.php?token=",
    "electricity_price_last_30_days": "https://enever.nl/api/stroomprijs_laatste30dagen.php?token=",
    "gas_price_today": "https://enever.nl/api/gasprijs_vandaag.php?token=",
    "gas_price_last_30_days": "https://enever.nl/api/gasprijs_laatste30dagen.php?token="
}


def energy_prices_node(state):
    ensure_cache_directory_exists()
    url = DATA_TYPES_URLS['gas_price_today']
    prices = get_energy_prices('gas_price_today', url)
    if prices is None:
        return {"error": "Data not available"}
    provider_abbr = os.getenv("ENERGY_PROVIDER")
    energy_price_today = prices[0][f'prijs{provider_abbr}']
    return {"energy_price_today": energy_price_today}


def ensure_cache_directory_exists():
    if not os.path.exists(ENERGY_CACHE_DIR):
        os.makedirs(ENERGY_CACHE_DIR)


def get_cache_file_name(data_type):
    today = datetime.date.today().isoformat()
    return f'{ENERGY_CACHE_DIR}/{data_type}_{today}.json'


def load_data_from_cache(cache_file):
    try:
        with open(cache_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return None


def save_data_to_cache(cache_file, data):
    with open(cache_file, 'w') as file:
        json.dump(data, file)


def fetch_prices_from_api(url):
    token = os.getenv("ENERGY_PRIZES_TOKEN")
    full_url = f"{url}{token}"
    try:
        response = requests.get(full_url)
        response.raise_for_status()
        data = response.json()
        if data['status'] != "true":
            raise ValueError("API response was not successful")
        return data['data']
    except requests.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        return None
    except requests.RequestException as e:
        logger.error(f"Request exception occurred: {e}")
        return None


def get_energy_prices(data_type, url):
    if data_type == "electricity_price_tomorrow" and datetime.datetime.now().hour < 16:
        logger.info(f"Data for {data_type} not yet available. Skipping.")
        return None

    cache_file = get_cache_file_name(data_type)
    cached_data = load_data_from_cache(cache_file)

    if cached_data:
        logger.info(f"Using cached data for {data_type}")
        return cached_data

    try:
        prices = fetch_prices_from_api(url)
        save_data_to_cache(cache_file, prices)
        return prices
    except Exception as e:
        logger.error(f"An error occurred while getting energy prices for {data_type}: {e}")
        return None
