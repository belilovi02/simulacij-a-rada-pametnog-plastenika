import random


class WeatherStationModel:
    def __init__(self):
        self.outdoor_temperature = random.uniform(10, 35)
        self.outdoor_humidity = random.uniform(30, 95)
        self.wind_speed = random.uniform(0, 15)
        self.rainfall_mm = random.uniform(0, 8)
        self.weather_signal = "sunny"

    def update(self):
        self.outdoor_temperature = self._clamp(self.outdoor_temperature + random.uniform(-2.5, 2.5), -10, 45)
        self.outdoor_humidity = self._clamp(self.outdoor_humidity + random.uniform(-6, 6), 20, 100)
        self.wind_speed = self._clamp(self.wind_speed + random.uniform(-3, 3), 0, 25)
        self.rainfall_mm = self._clamp(self.rainfall_mm + random.uniform(-2.5, 2.5), 0, 20)
        self.weather_signal = self._classify_weather()

    def current_values(self):
        return {
            "outdoor_temperature": round(self.outdoor_temperature, 1),
            "outdoor_humidity": round(self.outdoor_humidity, 1),
            "wind_speed": round(self.wind_speed, 1),
            "rainfall_mm": round(self.rainfall_mm, 1),
            "weather_signal": self.weather_signal,
        }

    def _classify_weather(self):
        if self.rainfall_mm > 2.0:
            return "rain"
        if self.wind_speed > 10.0:
            return "wind"
        if self.outdoor_temperature > 30.0:
            return "hot"
        return "sunny"

    @staticmethod
    def _clamp(value, minimum, maximum):
        if value < minimum:
            return minimum
        if value > maximum:
            return maximum
        return value
