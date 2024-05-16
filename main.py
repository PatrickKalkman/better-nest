from dotenv import load_dotenv
from loguru import logger

from langgraph.graph import StateGraph, END
from agent_state import AgentState

from nodes.weather_forecast_node import weather_forecast_node
from nodes.energy_prices_node import energy_prices_node
from nodes.sensor_data_node import sensor_data_node
from nodes.optimal_temperature_calculator_node import optimal_temperature_calculator_node

load_dotenv()

logger.info("Starting better nest agent...")

workflow = StateGraph(AgentState)
workflow.add_node("energy_prices_node", energy_prices_node)
workflow.add_node("weather_forecast_node", weather_forecast_node)
workflow.add_node("sensor_data_node", sensor_data_node)
workflow.add_node("optimal_temperature_calculator_node", optimal_temperature_calculator_node)

workflow.set_entry_point("energy_prices_node")
workflow.add_edge("energy_prices_node", "weather_forecast_node")
workflow.add_edge("weather_forecast_node", "sensor_data_node")
workflow.add_edge("sensor_data_node", "optimal_temperature_calculator_node")
workflow.add_edge("optimal_temperature_calculator_node", END)
app = workflow.compile()

for s in app.stream({}):
    print(list(s.values())[0])
