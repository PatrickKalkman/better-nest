import os
import requests
from loguru import logger
from time import time
from nodes.token_utils import get_access_token


def temperature_setpoint_realizer_node(state):
    current_hour = round(time() / 3600) % 24
    setpoints = state['setpoints']
    temperature_setpoint = setpoints[current_hour]['setpoint']
    set_calculated_temperature(temperature_setpoint)


def set_calculated_temperature(temperature_setpoint):
    try:
        access_token = get_access_token()
    except Exception as e:
        logger.error(f'Failed to get access token: {e}')
        return None

    device_name = os.getenv('DEVICE_NAME')
    url = f'https://smartdevicemanagement.googleapis.com/v1/{device_name}:executeCommand'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    data = {
        "command": "sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat",
        "params": {
            "heatCelsius": temperature_setpoint
        }
    }

    logger.info(f'Setting temperature to {temperature_setpoint} degrees')

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 401:
        logger.error('Authentication required. Please re-authenticate.')
        return None

    if response.status_code != 200:
        logger.error(f'Failed to set temperature. Status code: {response.status_code} reason: {response.json()}')
        return None

    return response.json()
