import os
import time
import requests
import json
from loguru import logger

TOKEN_FILE = 'token_info.json'


def sensor_data_node(state):
    device_info = get_device_info()
    if device_info:
        extracted_traits = extract_device_traits(device_info)
        return {'sensor_data': extracted_traits}
    return {'error': 'Data not available'}


def save_token_info(access_token, expires_in):
    expiration_time = time.time() + expires_in - 60  # Refresh 1 minute before expiration
    token_info = {
        'access_token': access_token,
        'expiration_time': expiration_time
    }
    with open(TOKEN_FILE, 'w') as file:
        json.dump(token_info, file)


def load_token_info():
    if not os.path.exists(TOKEN_FILE):
        return None, 0
    with open(TOKEN_FILE, 'r') as file:
        token_info = json.load(file)
        return token_info.get('access_token'), token_info.get('expiration_time')


def refresh_access_token():
    logger.info('Requesting access token using refresh token...')
    response = requests.post(
        'https://oauth2.googleapis.com/token',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            'client_id': os.getenv('CLIENT_ID'),
            'client_secret': os.getenv('CLIENT_SECRET'),
            'refresh_token': os.getenv('REFRESH_TOKEN'),
            'grant_type': 'refresh_token'
        }
    )
    if response.status_code != 200:
        logger.error(f'Failed to refresh access token. Status code: {response.status_code}')
        return None

    response_data = response.json()
    access_token = response_data['access_token']
    expires_in = response_data['expires_in']
    save_token_info(access_token, expires_in)
    return access_token


def get_access_token():
    access_token, expiration_time = load_token_info()
    if time.time() > expiration_time:
        access_token = refresh_access_token()
        if access_token is None:
            raise Exception('Authentication required. Please re-authenticate.')
    return access_token


def get_device_info():
    try:
        access_token = get_access_token()
    except Exception as e:
        logger.error(f'Failed to get access token: {e}')
        return None

    device_name = os.getenv('DEVICE_NAME')
    url = f'https://smartdevicemanagement.googleapis.com/v1/{device_name}'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 401:
        logger.error('Authentication required. Please re-authenticate.')
        return None

    if response.status_code != 200:
        logger.error(f'Failed to get device info. Status code: {response.status_code}')
        return None

    return response.json()


def extract_device_traits(device_info):
    traits = device_info.get("traits", {})
    heat_celsius = traits.get("sdm.devices.traits.ThermostatEco", {}).get("heatCelsius")
    status = traits.get("sdm.devices.traits.ThermostatHvac", {}).get("status")
    ambient_temperature_celsius = traits.get("sdm.devices.traits.Temperature", {}).get("ambientTemperatureCelsius")
    thermostat_mode = traits.get("sdm.devices.traits.ThermostatMode", {}).get("mode")
    connectivity_status = traits.get("sdm.devices.traits.Connectivity", {}).get("status")
    humidity = traits.get("sdm.devices.traits.Humidity", {}).get("ambientHumidityPercent")

    return {
        "heat_celsius": heat_celsius,
        "humidity": humidity,
        "ambient_temperature_celsius": ambient_temperature_celsius,
        "thermostat_mode": thermostat_mode,
        "status": status,
        "connectivity_status": connectivity_status
    }
