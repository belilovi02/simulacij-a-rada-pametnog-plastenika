import time
from datetime import datetime


class ArduinoMegaController:
    # Sprema reference modela, komunikacijsko stanje i trajne ručne postavke.
    def __init__(self, sensors, actuators, weather_station=None, greenhouse_model=None):
        self.sensors = sensors
        self.actuators = actuators
        self.weather_station = weather_station
        self.greenhouse_model = greenhouse_model
        self.status = "Offline"
        self.log_callback = None
        self.received_command = None
        self.manual_overrides = {}

    # Čita privremenu ručnu postavku i uklanja je ako joj je istekao rok.
    def _get_override(self, key):
        override = self.manual_overrides.get(key)
        if not override:
            return None
        if override["expires_at"] < time.time():
            self.manual_overrides.pop(key, None)
            return None
        return override["state"]

    # Postavlja vremenski ograničenu ručnu vrijednost za odabrani aktuator.
    def _set_override(self, key, state, duration=12):
        self.manual_overrides[key] = {
            "state": state,
            "expires_at": time.time() + duration,
        }

    # Registrira funkciju za centralizirani prikaz i spremanje događaja.
    def set_log_callback(self, callback):
        self.log_callback = callback

    # Prima tekstualnu naredbu koju će sljedeća obrada pretvoriti u stanje uređaja.
    def receive_command(self, command):
        self.received_command = command
        self._log(f"Arduino Mega: primljena komanda '{command}'")

    # Vraća objedinjeni status kontrolera, senzora, aktuatora i zadnje naredbe.
    def get_status(self):
        return {
            "status": self.status,
            "sensors": self.sensors.current_values(),
            "actuators": self.actuators.state,
            "last_command": self.received_command,
        }

    # Pokreće stalni ciklus simulacije, vremena, naredbi i autonomnih odluka.
    def run(self):
        self.status = "Online"
        self._log("Arduino Mega: pokrenut i u funkciji")
        while True:
            time.sleep(1.5)
            self._log("Arduino Mega: očitavam senzore")
            if self.greenhouse_model:
                self._apply_greenhouse_simulation()
            else:
                self.sensors.update()
            if self.weather_station:
                self.weather_station.update()
            self._process_command()
            self._apply_control_logic()
            self._apply_recommendation_logic()
            self._log("Arduino Mega: stanje poslato ESP32 modulu")

    # Mapira naredbe poput pump1_on na konkretne aktuatore i ručno ih zaključava.
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
            self._log("Arduino Mega: pumpa NPK uključena")
        elif command == "pump2_off":
            self.actuators.pump2 = False
            self.manual_overrides["pump2"] = False
            self._log("Arduino Mega: pumpa NPK isključena")
        elif command == "pump3_on":
            self.actuators.pump3 = True
            self.manual_overrides["pump3"] = True
            self._log("Arduino Mega: pumpa 3 uključena")
        elif command == "pump3_off":
            self.actuators.pump3 = False
            self.manual_overrides["pump3"] = False
            self._log("Arduino Mega: pumpa 3 isključena")
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

    # Primjenjuje pragove senzora i vremena samo na uređaje bez ručne postavke.
    def _apply_control_logic(self):
        values = self.sensors.current_values()

        if self.manual_overrides.get("pump1") is not None:
            self.actuators.pump1 = self.manual_overrides["pump1"]
        elif values["soil_moisture"] < 35:
            self.actuators.pump1 = True
            self._log("Arduino Mega: vlaga zemljišta niska, pumpa za vodu uključena")
        else:
            self.actuators.pump1 = False

        if self.manual_overrides.get("fan") is not None:
            self.actuators.fan = self.manual_overrides["fan"]
        elif values["temperature"] > 32:
            self.actuators.fan = True
            self._log("Arduino Mega: temperatura visoka, ventilator uključen")
        elif values["co2"] > 750:
            self.actuators.fan = True
            self._log("Arduino Mega: CO2 visok, ventilator uključen")
        else:
            self.actuators.fan = False

        if self.manual_overrides.get("greenhouse_open") is not None:
            self.actuators.greenhouse_open = self.manual_overrides["greenhouse_open"]
        elif self.weather_station and (self.weather_station.wind_speed > 10 or self.weather_station.rainfall_mm > 2):
            self.actuators.greenhouse_open = False
            self._log("Arduino Mega: vjetar ili kiša, plastenik zatvoren")
        elif values["temperature"] > 35:
            self.actuators.greenhouse_open = True
            self._log("Arduino Mega: temperatura vrlo visoka, plastenik otvoren")
        elif values["temperature"] < 22:
            self.actuators.greenhouse_open = False
            self._log("Arduino Mega: temperatura niska, plastenik zatvoren")

        if self.manual_overrides.get("led") is not None:
            self.actuators.led = self.manual_overrides["led"]

        if self.manual_overrides.get("pump2") is not None:
            self.actuators.pump2 = self.manual_overrides["pump2"]
        elif values["soil_moisture"] < 28 and values["temperature"] > 28:
            self.actuators.pump2 = True
            self._log("Arduino Mega: NPK nizak, pumpa za hranjivo uključena")
        else:
            self.actuators.pump2 = False

        if self.manual_overrides.get("pump3") is not None:
            self.actuators.pump3 = self.manual_overrides["pump3"]
        elif values["npk"] < 60:
            self.actuators.pump3 = True
            self._log("Arduino Mega: pumpa 3 uključena zbog visoke temperature i niske vlažnosti")
        else:
            self.actuators.pump3 = False

        if values["ph"] < 5.5 or values["ph"] > 7.5 or values["npk"] < 50:
            self.actuators.alarm = True
            self._log("Arduino Mega: alarm aktiviran zbog neprihvatljivih vrijednosti")
        else:
            self.actuators.alarm = False

    # Pretvara vanjsku ML preporuku u stanja navodnjavanja, ventilacije i krova.
    def apply_recommendation(self, prediction, current_values=None):
        values = current_values or self.sensors.current_values()
        if prediction.get("irrigation_needed"):
            self.actuators.pump1 = True
            self.manual_overrides["pump1"] = True
            self._log("Arduino Mega: preporuka za navodnjavanje primijenjena")
        else:
            self.actuators.pump1 = False
            self.manual_overrides["pump1"] = False

        if prediction.get("ventilation_needed"):
            self.actuators.fan = True
            self.manual_overrides["fan"] = True
            self._log("Arduino Mega: preporuka za ventilaciju primijenjena")
        else:
            self.actuators.fan = False
            self.manual_overrides["fan"] = False

        if self.weather_station and (self.weather_station.wind_speed > 10 or self.weather_station.rainfall_mm > 2):
            self.actuators.greenhouse_open = False
            self.manual_overrides["greenhouse_open"] = False
            self._log("Arduino Mega: preporuka za zatvaranje plastenika zbog vremena primijenjena")
        elif values.get("temperature", 0) > 35:
            self.actuators.greenhouse_open = True
            self.manual_overrides["greenhouse_open"] = True
            self._log("Arduino Mega: preporuka za otvaranje plastenika primijenjena")
        elif values.get("temperature", 0) < 22:
            self.actuators.greenhouse_open = False
            self.manual_overrides["greenhouse_open"] = False

    # Iz trenutnih senzora gradi jednostavnu autonomnu preporuku uz zaštitu ručnih stanja.
    def _apply_recommendation_logic(self):
        values = self.sensors.current_values()
        prediction = {
            "irrigation_needed": int(values["soil_moisture"] < 35 or values["npk"] < 60 or values["temperature"] > 32),
            "ventilation_needed": int(values["temperature"] > 32 or values["co2"] > 750 or values["air_humidity"] < 40),
        }
        # Automatska preporuka ne smije prepisati trajnu rucnu postavku.
        if "pump1" not in self.manual_overrides:
            self.actuators.pump1 = bool(prediction["irrigation_needed"])
        if "fan" not in self.manual_overrides:
            self.actuators.fan = bool(prediction["ventilation_needed"])

    # Sigurno poziva digitalni model, a pri grešci koristi osnovno ažuriranje senzora.
    def _apply_greenhouse_simulation(self):
        try:
            self.greenhouse_model.simulate_step()
        except Exception:
            self.sensors.update()

    # Usmjerava poruku prema callbacku ili terminalu i dodaje vremensku oznaku.
    def _log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(f"{datetime.now().isoformat()} - {message}")
