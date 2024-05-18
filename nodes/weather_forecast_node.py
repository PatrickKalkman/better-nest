import os
import datetime
from loguru import logger
import requests
import json

API_BASE_URL = "https://api.weatherapi.com/v1/forecast.json"
WEATHER_CACHE_DIR = "cache"


def weather_forecast_node(state):
    if state.get('mode') == 'demo':
        transformed_forecast = load_demo_weather_forecast()
    else:
        url = get_api_url()
        forecast = fetch_data_from_api(url)
        if forecast is None:
            return {"error": "Data not available"}
        transformed_forecast = transform_forecast_data(forecast)
    return {"weather_forecast": transformed_forecast}


def fetch_data_from_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['forecast']['forecastday'][0]['hour']
    except requests.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        return None
    except requests.RequestException as e:
        logger.error(f"Request exception occurred: {e}")
        return None


def transform_forecast_data(forecast):
    transformed_data = []
    for entry in forecast:
        date_iso = datetime.datetime.strptime(entry["time"], "%Y-%m-%d %H:%M").isoformat()
        transformed_data.append({
            "date": date_iso,
            "temperature": entry["temp_c"]
        })
    return transformed_data


def get_api_url():
    api_key = os.getenv("WEATHER_API_KEY")
    location = os.getenv("LOCATION")
    current_date = datetime.date.today()  # + datetime.timedelta(days=1)
    formatted_date = current_date.strftime('%Y-%m-%d')
    return f"{API_BASE_URL}?q={location}&days=1&dt={formatted_date}&key={api_key}"


def load_demo_weather_forecast():
    demo_file_path = os.path.join(WEATHER_CACHE_DIR, "demo_weather_forecast.json")
    try:
        with open(demo_file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"Demo data file not found: {demo_file_path}")
        return None
