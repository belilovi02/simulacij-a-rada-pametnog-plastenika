import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from controllers.arduino_mega_controller import ArduinoMegaController
from simulation.actuators import ActuatorModel
from simulation.sensors import SensorModel


def test_manual_pump_off_overrides_auto_control():
    sensors = SensorModel()
    actuators = ActuatorModel()
    controller = ArduinoMegaController(sensors, actuators)

    sensors.soil_moisture = 20.0
    controller.receive_command("pump1_off")
    controller._process_command()
    controller._apply_control_logic()

    assert actuators.pump1 is False
