from datetime import datetime, timedelta
from loguru import logger


def optimal_temperature_calculator_node(state):
    electricity_prices_data = state.get('energy_prices_per_hour')
    weather_forecast_data = state.get('weather_forecast')
    sensor_data = state.get('sensor_data')
    bandwidth = 6  # state.get('bandwidth')
    temperature_setpoint = 21  # state.get('temperature_setpoint')

    electricity_prices = [float(item['price']) for item in electricity_prices_data]
    weather_forecast = [item['temperature'] for item in weather_forecast_data]
    current_temperature = sensor_data.get('ambient_temperature_celsius')

    setpoints = calculate_setpoints(electricity_prices, weather_forecast, temperature_setpoint,
                                    bandwidth, current_temperature)
    setpoints_with_time = add_datetime_to_setpoints_and_round_setpoints(setpoints)
    baseline_cost, optimized_cost, savings = calculate_costs(setpoints, electricity_prices, weather_forecast)

    return {
        "setpoints": setpoints_with_time,
        "baseline_cost": baseline_cost,
        "optimized_cost": optimized_cost,
        "savings": savings
    }


def calculate_setpoints(electricity_prices, weather_forecast, temperature_setpoint, bandwidth, current_temperature):
    min_setpoint = temperature_setpoint - bandwidth / 2
    max_setpoint = temperature_setpoint + bandwidth / 2

    normalized_prices = normalize_prices(electricity_prices)

    setpoints = [
        calculate_initial_setpoint(temperature_setpoint, min_setpoint, max_setpoint,
                                   normalized_prices[hour], weather_forecast[hour], current_temperature)
        for hour in range(24)
    ]

    setpoints = adjust_setpoints(setpoints, temperature_setpoint, min_setpoint, max_setpoint)

    final_average = round(sum(setpoints) / 24, 2)
    if abs(final_average - temperature_setpoint) > 0.01:
        logger.info(f"Failed to adjust setpoints to exactly meet the average setpoint requirement. {final_average} != {temperature_setpoint}")

    return setpoints


def normalize_prices(electricity_prices):
    max_price = max(electricity_prices)
    min_price = min(electricity_prices)
    return [(price - min_price) / (max_price - min_price) for price in electricity_prices]


def calculate_initial_setpoint(average_setpoint, min_setpoint, max_setpoint, price_factor,
                               outside_temp, current_temperature):
    if price_factor > 0.5:
        ideal_setpoint = average_setpoint + (max_setpoint - average_setpoint) * (price_factor - 0.5) * 2
    else:
        ideal_setpoint = average_setpoint - (average_setpoint - min_setpoint) * (0.5 - price_factor) * 2

    # Adjust setpoint based on outside temperature
    if outside_temp < average_setpoint:
        ideal_setpoint += (average_setpoint - outside_temp) * 0.1
    elif outside_temp > average_setpoint:
        ideal_setpoint -= (outside_temp - average_setpoint) * 0.1

    # Further adjust based on current ambient temperature
    if current_temperature < average_setpoint:
        ideal_setpoint += (average_setpoint - current_temperature) * 0.05
    elif current_temperature > average_setpoint:
        ideal_setpoint -= (current_temperature - average_setpoint) * 0.05

    return max(min_setpoint, min(max_setpoint, ideal_setpoint))


def adjust_setpoints(setpoints, average_setpoint, min_setpoint, max_setpoint):
    total_setpoint = sum(setpoints)
    current_average = total_setpoint / 24
    adjustment_needed = average_setpoint - current_average

    for i in range(24):
        setpoints[i] += adjustment_needed
        setpoints[i] = max(min_setpoint, min(max_setpoint, setpoints[i]))

    return setpoints


def add_datetime_to_setpoints_and_round_setpoints(setpoints):
    current_time = datetime.now()
    return [
        {'time': (current_time + timedelta(hours=hour)).strftime('%Y-%m-%d %H:%M:%S'),
         'setpoint': round(setpoints[hour], 2)}
        for hour in range(24)
    ]


def calculate_costs(setpoints, electricity_prices, outside_temperatures):
    baseline_cost = 0
    optimized_cost = 0
    average_setpoint = 20

    for hour in range(24):
        baseline_cost += abs(outside_temperatures[hour] - average_setpoint) * electricity_prices[hour]
        optimized_cost += abs(outside_temperatures[hour] - setpoints[hour]) * electricity_prices[hour]

    savings = baseline_cost - optimized_cost
    return round(baseline_cost, 2), round(optimized_cost, 2), round(savings, 2)
