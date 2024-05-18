from time import time

from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from loguru import logger

MODEL_NAME = "Llama3-70b-8192"


def decision_insight_node(state):
    GROQ_LLM = ChatGroq(model=MODEL_NAME)

    explain_calculated_setpoints_prompt = PromptTemplate(
        template="""\
        system
        You are an expert in energy management and explaining the calculated temperature setpoints.

        user
        Given the following data:
        - Energy prices per hour: {energy_prices}
        - Weather forecast: {weather_forecast}
        - Sensor data: {sensor_data}
        - Calculated setpoints: {setpoints}
        - Bandwidth: {bandwidth}
        - Temperature setpoint: {temperature_setpoint}
        - Insulation factor: {insulation_factor}

        Explain why the temperature at {hour}:00 is set to {setpoint} degrees. Give a brief explanation. 
        For example, 'The temperature is set the lower limit of {setpoint} degrees celcius because the electricity
        prices are high and the weather is cold.' Or
        'The temperature is set to the higher limit of {setpoint} degrees celcius because the electricity prices are 
        low and the weather is warm.'
        Also consider that the average temperature should be within the bandwidth range over 24 hours.

        assistant""",
        input_variables=["energy_prices", "weather_forecast", "sensor_data",
                         "setpoints", "bandwidth", "temperature_setpoint",
                         "insulation_factor", "hour", "setpoint"],
    )

    explanation_generator = explain_calculated_setpoints_prompt | GROQ_LLM | StrOutputParser()
    hour = f'{round(time() / 3600)} % 24:00'
    setpoint_at_10 = state["setpoints"][10]
    explanation = explanation_generator.invoke({
        "energy_prices": state["energy_prices_per_hour"],
        "weather_forecast": state["weather_forecast"],
        "sensor_data": state["sensor_data"],
        "setpoints": state["setpoints"],
        "bandwidth": state["bandwidth"],
        "temperature_setpoint": state["temperature_setpoint"],
        "insulation_factor": state["insulation_factor"],
        "hour": hour,
        "setpoint": setpoint_at_10["setpoint"],
    })

    logger.info(f"Explanation for {10}:00: {explanation}")

    return {"explanation": explanation}
