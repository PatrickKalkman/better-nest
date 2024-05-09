import os
import datetime
from loguru import logger
import swagger_client
from swagger_client.rest import ApiException


def initialize_api_client():
    configuration = swagger_client.Configuration()
    configuration.api_key['key'] = os.getenv("WEATHER_API_KEY")
    return swagger_client.APIsApi(swagger_client.ApiClient(configuration))


def weather_forecast_node(state):
    api_instance = initialize_api_client()
    solar = get_solar_information(api_instance)
    forecast = get_forecast_information(api_instance)
    return {'solar': solar, 'forecast': forecast}


def get_forecast_information(api_instance):
    try:
        location = os.getenv("LOCATION")
        logger.info(f"Getting forecast information for {location}")
        current_date = datetime.date.today() + datetime.timedelta(days=1)
        formatted_date = current_date.strftime('%Y-%m-%d')
        forecast = api_instance.forecast_weather(location, days=1, dt=formatted_date, alerts='no', aqi='no', tp=24)
        return forecast
    except ApiException as e:
        logger.error(f"Exception when calling forecast: {e}")
        return None


def get_solar_information(api_instance):
    try:
        location = os.getenv("LOCATION")
        current_date = datetime.date.today()
        formatted_date = current_date.strftime('%Y-%m-%d')
        logger.info(f"Getting astronomy information for {location} on {formatted_date}")
        api_response = api_instance.astronomy(location, formatted_date)
        sunrise = api_response['astronomy']['astro']['sunrise']
        sunset = api_response['astronomy']['astro']['sunset']
        logger.info(f"Sunrise: {sunrise}, Sunset: {sunset}")
        return {"sunrise": sunrise, "sunset": sunset}
    except ApiException as e:
        logger.error(f"Exception when calling astronomy: {e}")
        return None
