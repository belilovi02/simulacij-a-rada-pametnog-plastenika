
import random


class GreenhouseModel:
    def __init__(self, sensors, actuators, weather_station=None):
        self.sensors = sensors
        self.actuators = actuators
        self.weather_station = weather_station

    def simulate_step(self):
        self._apply_actuator_effects()
        self._apply_environmental_drift()
        self._apply_weather_influence()
        return self.sensors.current_values()

    def _apply_actuator_effects(self):
        if self.actuators.fan:
            self.sensors.temperature = max(15, self.sensors.temperature - random.uniform(0.6, 1.4))
            self.sensors.co2 = max(200, self.sensors.co2 - random.uniform(20, 35))
            self.sensors.air_humidity = max(30, self.sensors.air_humidity - random.uniform(1.0, 3.0))
        if self.actuators.led:
            self.sensors.co2 = max(200, self.sensors.co2 - random.uniform(10, 22))
            self.sensors.air_humidity = min(95, self.sensors.air_humidity + random.uniform(0.5, 2.0))
        if self.actuators.pump1 or self.actuators.pump2:
            moisture_gain = 0.0
            if self.actuators.pump1:
                moisture_gain += random.uniform(1.0, 1.8)
            if self.actuators.pump2:
                moisture_gain += random.uniform(0.8, 1.6)
            self.sensors.soil_moisture = min(90, self.sensors.soil_moisture + moisture_gain)
        if self.actuators.greenhouse_open:
            self.sensors.temperature = max(15, self.sensors.temperature - random.uniform(0.2, 0.6))
            self.sensors.co2 = max(200, self.sensors.co2 - random.uniform(5, 15))
            self.sensors.air_humidity = min(95, self.sensors.air_humidity + random.uniform(0.5, 2.0))
            self.sensors.soil_moisture = max(10, self.sensors.soil_moisture - random.uniform(0.1, 0.5))
        if self.actuators.alarm:
            self.sensors.temperature = self._clamp(self.sensors.temperature + random.uniform(-0.3, 0.3), 15, 45)

    def _apply_environmental_drift(self):
        self.sensors.temperature = self._clamp(self.sensors.temperature + random.uniform(-1.0, 1.0), 15, 45)
        self.sensors.air_humidity = self._clamp(self.sensors.air_humidity + random.uniform(-3, 3), 30, 95)
        self.sensors.soil_moisture = self._clamp(self.sensors.soil_moisture + random.uniform(-1.2, 1.2), 10, 90)
        self.sensors.ph = self._clamp(self.sensors.ph + random.uniform(-0.1, 0.1), 4.5, 8.5)
        self.sensors.npk = self._clamp(self.sensors.npk + random.uniform(-7, 7), 0, 250)
        self.sensors.co2 = self._clamp(self.sensors.co2 + random.uniform(-45, 45), 200, 1200)

    def _apply_weather_influence(self):
        if not self.weather_station:
            return
        weather = self.weather_station.current_values()
        if self.actuators.greenhouse_open:
            self.sensors.temperature = self._clamp(
                self.sensors.temperature + (weather["outdoor_temperature"] - self.sensors.temperature) * 0.1,
                15,
                45,
            )
            self.sensors.air_humidity = self._clamp(
                self.sensors.air_humidity + (weather["outdoor_humidity"] - self.sensors.air_humidity) * 0.05,
                20,
                100,
            )
            if weather["weather_signal"] == "rain":
                self.sensors.soil_moisture = min(90, self.sensors.soil_moisture + random.uniform(0.2, 1.0))
        else:
            if weather["outdoor_temperature"] > 30 and self.sensors.temperature < 26:
                self.sensors.temperature = min(45, self.sensors.temperature + random.uniform(0.1, 0.3))
        if weather["wind_speed"] > 12:
            self.sensors.co2 = min(1200, self.sensors.co2 + random.uniform(5, 20))

    @staticmethod
    def _clamp(value, minimum, maximum):
        return minimum if value < minimum else maximum if value > maximum else value
