from time import time

from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from loguru import logger

MODEL_NAME = "Llama3-70b-8192"


def decision_insight_node(state):
    GROQ_LLM = ChatGroq(model=MODEL_NAME)

    if state.get('mode') == 'demo':
        return {"explanation": ("The temperature at 10:00:00 is set to 22.28 degrees because the electricity prices are"
                                "relatively low at this time, and the weather is warm with a forecasted temperature"
                                " of 18.8°C. Additionally, the average temperature over the 24-hour period should be"
                                " within the bandwidth range of 6.0°C, which allows for some flexibility in "
                                "temperature adjustments to optimize energy costs. By setting the temperature to "
                                "22.28°C, the system is taking advantage of the low energy prices while maintaining "
                                "a comfortable temperature and staying within the desired bandwidth.")}

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
    hour = round(time() / 3600) % 24
    setpoint = state["setpoints"][hour]
    explanation = explanation_generator.invoke({
        "energy_prices": state["energy_prices_per_hour"],
        "weather_forecast": state["weather_forecast"],
        "sensor_data": state["sensor_data"],
        "setpoints": state["setpoints"],
        "bandwidth": state["bandwidth"],
        "temperature_setpoint": state["temperature_setpoint"],
        "insulation_factor": state["insulation_factor"],
        "hour": hour,
        "setpoint": setpoint["setpoint"],
    })

    logger.info(f"Explanation for {hour}:00: {explanation}")

    return {"explanation": explanation}
