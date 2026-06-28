

class GreenhouseModel:
    def __init__(self, sensors, actuators):
        self.sensors = sensors
        self.actuators = actuators

    def simulate_step(self):
        current = self.sensors.current_values()
        if self.actuators.fan:
            self.sensors.temperature = max(15, self.sensors.temperature - 0.5)
        if self.actuators.led:
            self.sensors.light = min(1000, self.sensors.light + 10)
        if self.actuators.pump1 or self.actuators.pump2:
            self.sensors.soil_moisture = min(90, self.sensors.soil_moisture + 1.5)
        return self.sensors.current_values()
