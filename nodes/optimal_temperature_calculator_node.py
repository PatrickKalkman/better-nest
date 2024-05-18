from datetime import datetime, timedelta
from loguru import logger
import numpy as np


def optimal_temperature_calculator_node(state):

    electricity_prices_data = state['energy_prices_per_hour']
    weather_forecast_data = state['weather_forecast']
    sensor_data = state['sensor_data']
    bandwidth = state['bandwidth']
    temperature_setpoint = state['temperature_setpoint']
    insulation_factor = state['insulation_factor']

    electricity_prices = np.array([float(item['price']) for item in electricity_prices_data])
    weather_forecast = np.array([item['temperature'] for item in weather_forecast_data])
    current_temperature = sensor_data.get('ambient_temperature_celsius')

    setpoints = calculate_setpoints(electricity_prices, weather_forecast, temperature_setpoint,
                                    bandwidth, current_temperature, insulation_factor)
    setpoints_with_time = add_datetime_to_setpoints_and_round_setpoints(setpoints)

    baseline_cost, optimized_cost, savings = calculate_costs(setpoints, electricity_prices,
                                                             weather_forecast, temperature_setpoint)

    return {
        "setpoints": setpoints_with_time,
        "baseline_cost": baseline_cost,
        "optimized_cost": optimized_cost,
        "savings": savings
    }


def calculate_setpoints(electricity_prices, weather_forecast, temperature_setpoint,
                        bandwidth, current_temperature, insulation_factor):

    volatility = np.std(electricity_prices) / np.mean(electricity_prices)
    dynamic_bandwidth = bandwidth * (1 + volatility)

    min_setpoint = temperature_setpoint - dynamic_bandwidth / 2
    max_setpoint = temperature_setpoint + dynamic_bandwidth / 2

    normalized_prices = normalize_prices(electricity_prices)

    setpoints = np.array([
        calculate_initial_setpoint(temperature_setpoint, min_setpoint, max_setpoint,
                                   normalized_prices[hour], weather_forecast[hour],
                                   current_temperature, insulation_factor)
        for hour in range(24)
    ])

    setpoints = adjust_setpoints(setpoints, temperature_setpoint, min_setpoint, max_setpoint)

    final_average = round(np.mean(setpoints), 2)
    if abs(final_average - temperature_setpoint) > 0.5:
        logger.info(f"Adjusted setpoints outside ±0.5°C range. {final_average} != {temperature_setpoint}")

    return setpoints


def normalize_prices(electricity_prices):
    min_price = np.min(electricity_prices)
    max_price = np.max(electricity_prices)
    return (electricity_prices - min_price) / (max_price - min_price)


def calculate_initial_setpoint(average_setpoint, min_setpoint, max_setpoint, price_factor,
                               outside_temp, current_temperature, insulation_factor):

    ideal_setpoint = average_setpoint + (max_setpoint - min_setpoint) * (0.75 - price_factor) * 2
    temp_adjustment = insulation_factor * (0.1 * (average_setpoint - outside_temp)
                                           if outside_temp < average_setpoint
                                           else -0.1 * (outside_temp - average_setpoint))

    ambient_adjustment = (
        0.05 * (average_setpoint - current_temperature)
        if current_temperature < average_setpoint
        else -0.05 * (current_temperature - average_setpoint)
    )

    ideal_setpoint += temp_adjustment + ambient_adjustment
    return np.clip(ideal_setpoint, min_setpoint, max_setpoint)


def adjust_setpoints(setpoints, average_setpoint, min_setpoint, max_setpoint):
    current_average = np.mean(setpoints)
    adjustment_needed = average_setpoint - current_average

    adjusted_setpoints = setpoints + adjustment_needed
    return np.clip(adjusted_setpoints, min_setpoint, max_setpoint)


def add_datetime_to_setpoints_and_round_setpoints(setpoints):
    current_time = datetime.now()
    return [
        {'time': (current_time + timedelta(hours=hour)).strftime('%Y-%m-%d %H:%M:%S'),
         'setpoint': round(setpoint, 2)}
        for hour, setpoint in enumerate(setpoints)
    ]


def calculate_costs(setpoints, electricity_prices, outside_temperatures, baseline_setpoint):
    baseline_cost = np.sum(np.abs(outside_temperatures - baseline_setpoint) * electricity_prices)
    optimized_cost = np.sum(np.abs(outside_temperatures - setpoints) * electricity_prices)
    savings = baseline_cost - optimized_cost
    return round(baseline_cost, 2), round(optimized_cost, 2), round(savings, 2)
