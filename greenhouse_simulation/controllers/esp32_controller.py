import time
from datetime import datetime


class ESP32Controller:
    def __init__(self, arduino_controller):
        self.arduino = arduino_controller
        self.status = "Offline"
        self.last_command = "None"
        self.log_callback = None

    def set_log_callback(self, callback):
        self.log_callback = callback

    def send_command(self, command):
        self.last_command = command
        self._log(f"ESP32: primljena komanda '{command}'")
        self.arduino.receive_command(command)

    def receive_state(self, state):
        self._log("ESP32: stanje poslato na dashboard")
        return state

    def run(self):
        self.status = "Online"
        self._log("ESP32: pokrenut i u funkciji")
        while True:
            time.sleep(2)
            if self.arduino.status == "Online":
                state = self.arduino.get_status()
                self.receive_state(state)
                self._log("ESP32: prima stanje od Arduino Mega kontrolera")

    def _log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(f"{datetime.now().isoformat()} - {message}")
