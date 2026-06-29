

class ActuatorModel:
    def __init__(self):
        self.pump1 = False
        self.pump2 = False
        self.pump3 = False
        self.fan = False
        self.led = False
        self.greenhouse_open = False
        self.alarm = False

    @property
    def state(self):
        return {
            "pump1": self.pump1,
            "pump2": self.pump2,
            "pump3": self.pump3,
            "water_pump_2": self.pump2,
            "npk_pump": self.pump3,
            "fan": self.fan,
            "led": self.led,
            "greenhouse_open": self.greenhouse_open,
            "alarm": self.alarm,
        }
