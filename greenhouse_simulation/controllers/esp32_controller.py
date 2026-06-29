import time
from datetime import datetime


class ESP32Controller:
    # Povezuje komunikacijski ESP32 model s glavnim Arduino kontrolerom.
    def __init__(self, arduino_controller):
        self.arduino = arduino_controller
        self.status = "Offline"
        self.last_command = "None"
        self.log_callback = None

    # Registrira funkciju kojoj će kontroler prosljeđivati tekstualne događaje.
    def set_log_callback(self, callback):
        self.log_callback = callback

    # Bilježi korisničku naredbu i prosljeđuje je Arduino kontroleru na obradu.
    def send_command(self, command):
        self.last_command = command
        self._log(f"ESP32: primljena komanda '{command}'")
        self.arduino.receive_command(command)

    # Simulira prijem Arduino stanja i njegovo slanje prema korisničkom sučelju.
    def receive_state(self, state):
        self._log("ESP32: stanje poslato na dashboard")
        return state

    # U pozadinskoj petlji periodično dohvaća stanje aktivnog Arduino kontrolera.
    def run(self):
        self.status = "Online"
        self._log("ESP32: pokrenut i u funkciji")
        while True:
            time.sleep(2)
            if self.arduino.status == "Online":
                state = self.arduino.get_status()
                self.receive_state(state)
                self._log("ESP32: prima stanje od Arduino Mega kontrolera")

    # Šalje poruku registriranom loggeru ili je ispisuje u terminal s vremenom.
    def _log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(f"{datetime.now().isoformat()} - {message}")
