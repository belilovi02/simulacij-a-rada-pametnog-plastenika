import time
from datetime import datetime


class ArduinoMegaController:
    def __init__(self, sensors, actuators):
        self.sensors = sensors
        self.actuators = actuators
        self.status = "Offline"
        self.log_callback = None
        self.received_command = None
        self.manual_overrides = {}

    def set_log_callback(self, callback):
        self.log_callback = callback

    def receive_command(self, command):
        self.received_command = command
        self._log(f"Arduino Mega: primljena komanda '{command}'")

    def get_status(self):
        return {
            "status": self.status,
            "sensors": self.sensors.current_values(),
            "actuators": self.actuators.state,
            "last_command": self.received_command,
        }

    def run(self):
        self.status = "Online"
        self._log("Arduino Mega: pokrenut i u funkciji")
        while True:
            time.sleep(1.5)
            self._log("Arduino Mega: očitavam senzore")
            self.sensors.update()
            self._process_command()
            self._apply_control_logic()
            self._log("Arduino Mega: stanje poslato ESP32 modulu")

    def _process_command(self):
        command = self.received_command
        if not command:
            return

        if command == "pump1_on":
            self.actuators.pump1 = True
            self.manual_overrides["pump1"] = True
            self._log("Arduino Mega: pumpa 1 uključena")
        elif command == "pump1_off":
            self.actuators.pump1 = False
            self.manual_overrides["pump1"] = False
            self._log("Arduino Mega: pumpa 1 isključena")
        elif command == "pump2_on":
            self.actuators.pump2 = True
            self.manual_overrides["pump2"] = True
            self._log("Arduino Mega: pumpa 2 uključena")
        elif command == "pump2_off":
            self.actuators.pump2 = False
            self.manual_overrides["pump2"] = False
            self._log("Arduino Mega: pumpa 2 isključena")
        elif command == "fan_on":
            self.actuators.fan = True
            self.manual_overrides["fan"] = True
            self._log("Arduino Mega: ventilator uključen")
        elif command == "fan_off":
            self.actuators.fan = False
            self.manual_overrides["fan"] = False
            self._log("Arduino Mega: ventilator isključen")
        elif command == "led_on":
            self.actuators.led = True
            self.manual_overrides["led"] = True
            self._log("Arduino Mega: LED svjetlo uključeno")
        elif command == "led_off":
            self.actuators.led = False
            self.manual_overrides["led"] = False
            self._log("Arduino Mega: LED svjetlo isključeno")
        elif command == "greenhouse_open":
            self.actuators.greenhouse_open = True
            self.manual_overrides["greenhouse_open"] = True
            self._log("Arduino Mega: plastenik otvoren")
        elif command == "greenhouse_close":
            self.actuators.greenhouse_open = False
            self.manual_overrides["greenhouse_open"] = False
            self._log("Arduino Mega: plastenik zatvoren")

        self.received_command = None

    def _apply_control_logic(self):
        values = self.sensors.current_values()

        if self.manual_overrides.get("pump1") is not None:
            self.actuators.pump1 = self.manual_overrides["pump1"]
        elif values["soil_moisture"] < 35:
            self.actuators.pump1 = True
            self._log("Arduino Mega: vlaga zemljišta niska, pumpa uključena")
        else:
            self.actuators.pump1 = False

        if self.manual_overrides.get("fan") is not None:
            self.actuators.fan = self.manual_overrides["fan"]
        elif values["temperature"] > 32:
            self.actuators.fan = True
            self._log("Arduino Mega: temperatura visoka, ventilator uključen")
        else:
            self.actuators.fan = False

        if self.manual_overrides.get("greenhouse_open") is not None:
            self.actuators.greenhouse_open = self.manual_overrides["greenhouse_open"]
        elif values["temperature"] > 35:
            self.actuators.greenhouse_open = True
            self._log("Arduino Mega: temperatura vrlo visoka, plastenik otvoren")
        elif values["temperature"] < 22:
            self.actuators.greenhouse_open = False
            self._log("Arduino Mega: temperatura niska, plastenik zatvoren")

        if self.manual_overrides.get("led") is not None:
            self.actuators.led = self.manual_overrides["led"]
        if values["co2"] > 750:
            self.actuators.fan = True
            self._log("Arduino Mega: CO2 visok, ventilacija uključenja")
        elif values["co2"] < 450:
            self.actuators.fan = False

        if values["ph"] < 5.5 or values["ph"] > 7.5 or values["npk"] < 60:
            self.actuators.alarm = True
            self._log("Arduino Mega: alarm aktiviran zbog neprihvatljivih vrijednosti")
        else:
            self.actuators.alarm = False

    def _log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(f"{datetime.now().isoformat()} - {message}")
