import os
import requests
from loguru import logger

from nodes.token_utils import get_access_token


def sensor_data_node(state):
    device_info = get_device_info()
    if device_info:
        extracted_traits = extract_device_traits(device_info)
        return {'sensor_data': extracted_traits}
    return {'error': 'Data not available'}


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
