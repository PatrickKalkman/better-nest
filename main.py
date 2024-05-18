from dotenv import load_dotenv
from loguru import logger
from langgraph.graph import StateGraph, END
from agent_state import AgentState

from nodes.configuration_node import configuration_node
from nodes.weather_forecast_node import weather_forecast_node
from nodes.energy_prices_node import energy_prices_node
from nodes.sensor_data_node import sensor_data_node
from nodes.optimal_temperature_calculator_node import optimal_temperature_calculator_node
from nodes.decision_insight_node import decision_insight_node
from nodes.temperature_setpoint_realizer_node import temperature_setpoint_realizer_node

from generate_graph import generate_graph

load_dotenv()

logger.info("Starting better nest agent...")

workflow = StateGraph(AgentState)
workflow.add_node("configuration_node", configuration_node)
workflow.add_node("energy_prices_node", energy_prices_node)
workflow.add_node("weather_forecast_node", weather_forecast_node)
workflow.add_node("sensor_data_node", sensor_data_node)
workflow.add_node("optimal_temperature_calculator_node", optimal_temperature_calculator_node)
workflow.add_node("decision_insight_node", decision_insight_node)
workflow.add_node("temperature_setpoint_realizer_node", temperature_setpoint_realizer_node)

workflow.set_entry_point("configuration_node")
workflow.add_edge("configuration_node", "energy_prices_node")
workflow.add_edge("energy_prices_node", "weather_forecast_node")
workflow.add_edge("weather_forecast_node", "sensor_data_node")
workflow.add_edge("sensor_data_node", "optimal_temperature_calculator_node")
workflow.add_edge("optimal_temperature_calculator_node", "decision_insight_node")
workflow.add_edge("decision_insight_node", "temperature_setpoint_realizer_node")
workflow.add_edge("temperature_setpoint_realizer_node", END)
app = workflow.compile()

final_state = {
    'energy_prices_per_hour': [],
    'weather_forecast': [],
    'sensor_data': {},
    'setpoints': [],
    'temperature_setpoint': None,
    'bandwidth': None
}

for s in app.stream({}):
    result = list(s.values())[0]

    if 'energy_prices_per_hour' in result:
        final_state['energy_prices_per_hour'] = result['energy_prices_per_hour']
    elif 'weather_forecast' in result:
        final_state['weather_forecast'] = result['weather_forecast']
    elif 'sensor_data' in result:
        final_state['sensor_data'] = result['sensor_data']
    elif 'setpoints' in result:
        final_state['setpoints'] = result['setpoints']
    elif 'temperature_setpoint' in result:
        final_state['temperature_setpoint'] = result['temperature_setpoint']
        final_state['bandwidth'] = result['bandwidth']

    logger.info(result)

generate_graph(final_state)
