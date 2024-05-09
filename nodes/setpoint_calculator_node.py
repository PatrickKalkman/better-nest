# def calculate_setpoint(current_temp, comfort_temp, forecast_temp, gas_price):
#     # Constants for weighting how much each factor influences the setpoint
#     WEIGHT_CURRENT_TEMP = 0.3
#     WEIGHT_FORECAST_TEMP = 0.4
#     WEIGHT_GAS_PRICE = 0.3

#     # Calculate how off the current and forecast temperatures are from the comfort temperature
#     current_temp_diff = abs(comfort_temp - current_temp)
#     forecast_temp_diff = abs(comfort_temp - forecast_temp)

#     # Normalize the gas price impact (assuming you know the typical range of gas prices)
#     # This is a placeholder. Adjust the normalization based on actual gas price data
#     normalized_gas_price = (gas_price - min_gas_price) / (max_gas_price - min_gas_price)

#     # Calculate the setpoint adjustment
#     # Negative values in adjustments suggest cooling, positive suggest heating
#     adjustment = (WEIGHT_CURRENT_TEMP * current_temp_diff +
#                   WEIGHT_FORECAST_TEMP * forecast_temp_diff -
#                   WEIGHT_GAS_PRICE * normalized_gas_price)

#     # Adjust the setpoint based on the adjustment calculation
#     new_setpoint = comfort_temp + adjustment

#     return new_setpoint

# # Example usage
# current_temp = 22  # current temperature in degrees Celsius
# comfort_temp = 20  # comfortable temperature in degrees Celsius
# forecast_temp = 18  # forecast temperature in degrees Celsius
# gas_price = 1.5    # current gas price, normalized between 0 and 2 for example

# setpoint = calculate_setpoint(current_temp, comfort_temp, forecast_temp, gas_price)
# print(f"Recommended setpoint: {setpoint}°C")