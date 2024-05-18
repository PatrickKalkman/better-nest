import datetime
import os
import requests
import json
from loguru import logger


ENERGY_CACHE_DIR = "cache"
API_BASE_URL = "https://enever.nl/api/"
API_ENDPOINTS = {
    "electricity_price_today": "stroomprijs_vandaag.php",
    "electricity_price_tomorrow": "stroomprijs_morgen.php",
    "electricity_price_last_30_days": "stroomprijs_laatste30dagen.php",
    "gas_price_today": "gasprijs_vandaag.php",
    "gas_price_last_30_days": "gasprijs_laatste30dagen.php"
}


def energy_prices_node(state):
    if state.get('mode') == 'demo':
        prices = load_demo_data()
    else:
        prices = get_energy_prices('electricity_price_today')

    if prices is None:
        return {"error": "Data not available"}

    energy_prices_per_hour = transform_data(prices)
    return {"energy_prices_per_hour": energy_prices_per_hour}


def get_api_url(data_type):
    token = os.getenv("ENERGY_PRIZES_TOKEN")
    return f"{API_BASE_URL}{API_ENDPOINTS[data_type]}?token={token}"


def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_cache_file_path(data_type):
    today = datetime.date.today().isoformat()
    return os.path.join(ENERGY_CACHE_DIR, f"{data_type}_{today}.json")


def load_data_from_cache(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return None


def save_data_to_cache(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file)


def fetch_data_from_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get('status') != "true":
            raise ValueError("API response was not successful")
        return data.get('data')
    except requests.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        return None
    except requests.RequestException as e:
        logger.error(f"Request exception occurred: {e}")
        return None


def get_energy_prices(data_type):
    if data_type == "electricity_price_tomorrow" and datetime.datetime.now().hour < 16:
        logger.info(f"Data for {data_type} not yet available. Skipping.")
        return None

    ensure_directory_exists(ENERGY_CACHE_DIR)
    cache_file_path = get_cache_file_path(data_type)
    cached_data = load_data_from_cache(cache_file_path)

    if cached_data:
        logger.info(f"Using cached data for {data_type}.")
        return cached_data

    url = get_api_url(data_type)
    try:
        prices = fetch_data_from_api(url)
        save_data_to_cache(cache_file_path, prices)
        return prices
    except Exception as e:
        logger.error(f"An error occurred while getting energy prices for {data_type}: {e}")
        return None


def transform_data(data):
    transformed = []
    provider_abbr = os.getenv("ENERGY_PROVIDER") or "prijsEN"
    for entry in data:
        date_obj = datetime.datetime.strptime(entry["datum"], "%Y-%m-%d %H:%M:%S")
        iso_date = date_obj.isoformat()
        transformed.append({"date": iso_date, "price": entry[provider_abbr]})
    return transformed


def load_demo_data():
    demo_file_path = os.path.join(ENERGY_CACHE_DIR, "demo_electricity_price_today.json")
    try:
        with open(demo_file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"Demo data file not found: {demo_file_path}")
        return None
