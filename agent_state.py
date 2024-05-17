from typing_extensions import TypedDict
from typing import List


class EnergyPrice(TypedDict):
    date: str
    price: str


class WeatherForecast(TypedDict):
    date: str
    temperature: float


class SensorData(TypedDict):
    heat_celsius: float
    humidity: int
    ambient_temperature_celsius: float
    thermostat_mode: str
    status: str
    connectivity_status: str


class OptimalTemperature(TypedDict):
    time: str
    setpoint: float


class AgentState(TypedDict):
    energy_prices_per_hour: List[EnergyPrice]
    weather_forecast: List[WeatherForecast]
    sensor_data: SensorData
    temperature_setpoint: float
    bandwidth: float
    insulation_factor: float
    setpoints: List[OptimalTemperature]
    baseline_cost: float
    optimized_cost: float
    savings: float
