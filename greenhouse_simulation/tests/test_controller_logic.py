import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from controllers.arduino_mega_controller import ArduinoMegaController
from simulation.actuators import ActuatorModel
from simulation.sensors import SensorModel
from simulation.weather_station import WeatherStationModel


def test_manual_pump_off_overrides_auto_control():
    sensors = SensorModel()
    actuators = ActuatorModel()
    controller = ArduinoMegaController(sensors, actuators)

    sensors.soil_moisture = 20.0
    controller.receive_command("pump1_off")
    controller._process_command()
    controller._apply_control_logic()

    assert actuators.pump1 is False


def test_recommendation_applies_auto_actions():
    sensors = SensorModel()
    actuators = ActuatorModel()
    controller = ArduinoMegaController(sensors, actuators)

    sensors.soil_moisture = 20.0
    sensors.temperature = 40.0
    sensors.co2 = 850.0

    controller.apply_recommendation({"irrigation_needed": 1, "ventilation_needed": 1}, sensors.current_values())

    assert actuators.pump1 is True
    assert actuators.fan is True
    assert actuators.greenhouse_open is True


def test_weather_station_closes_greenhouse_when_windy_or_rainy():
    sensors = SensorModel()
    actuators = ActuatorModel()
    weather = WeatherStationModel()
    controller = ArduinoMegaController(sensors, actuators, weather_station=weather)

    weather.wind_speed = 12.0
    weather.rainfall_mm = 2.0
    controller._apply_control_logic()

    assert actuators.greenhouse_open is False
