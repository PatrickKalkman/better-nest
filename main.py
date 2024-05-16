from dotenv import load_dotenv
from nodes.weather_forecast_node import weather_forecast_node
from nodes.energy_prices_node import energy_prices_node
from nodes.sensor_data_node import sensor_data_node
from loguru import logger

load_dotenv()

logger.info("Starting better nest agent...")

state = {}
result = energy_prices_node(state)
logger.info(f"{result}")
result = weather_forecast_node(state)
logger.info(f"{result}")
result = sensor_data_node(state)
logger.info(f"{result}")