import os
import threading
import tkinter as tk
from controllers.esp32_controller import ESP32Controller
from controllers.arduino_mega_controller import ArduinoMegaController
from ui.dashboard import GreenhouseDashboard
from simulation.sensors import SensorModel
from simulation.actuators import ActuatorModel
from simulation.ml_prediction import MLPrediction

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(DATA_DIR, "simulation_log.csv")


def ensure_data_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("timestamp,temperature,air_humidity,soil_moisture,ph,npk,co2,pump1,pump2,fan,led,greenhouse_open,alarm,energy_consumption\n")


if __name__ == "__main__":
    ensure_data_file()

    sensors = SensorModel()
    actuators = ActuatorModel()
    ml_model = MLPrediction()

    arduino = ArduinoMegaController(sensors, actuators)
    esp32 = ESP32Controller(arduino)

    root = tk.Tk()
    root.title("Pametni plastenik - Simulacija")
    app = GreenhouseDashboard(root, esp32, arduino, sensors, actuators, ml_model, LOG_FILE)

    esp_thread = threading.Thread(target=esp32.run, daemon=True)
    mega_thread = threading.Thread(target=arduino.run, daemon=True)
    esp_thread.start()
    mega_thread.start()

    root.mainloop()