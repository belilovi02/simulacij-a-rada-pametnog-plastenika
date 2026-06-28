import random


class SensorModel:
    def __init__(self):
        self.temperature = random.uniform(18, 28)
        self.air_humidity = random.uniform(40, 70)
        self.soil_moisture = random.uniform(25, 55)
        self.ph = random.uniform(5.8, 7.0)
        self.npk = random.uniform(80, 180)
        self.co2 = random.uniform(300, 800)

    def update(self):
        self.temperature = self._clamp(self.temperature + random.uniform(-1.5, 1.5), 15, 45)
        self.air_humidity = self._clamp(self.air_humidity + random.uniform(-4, 4), 30, 95)
        self.soil_moisture = self._clamp(self.soil_moisture + random.uniform(-5, 4), 10, 90)
        self.ph = self._clamp(self.ph + random.uniform(-0.2, 0.2), 4.5, 8.5)
        self.npk = self._clamp(self.npk + random.uniform(-10, 10), 0, 250)
        self.co2 = self._clamp(self.co2 + random.uniform(-80, 80), 200, 1200)

    def current_values(self):
        return {
            "temperature": round(self.temperature, 1),
            "air_humidity": round(self.air_humidity, 1),
            "soil_moisture": round(self.soil_moisture, 1),
            "ph": round(self.ph, 2),
            "npk": round(self.npk, 1),
            "co2": round(self.co2, 1),
        }

    @staticmethod
    def _clamp(value, minimum, maximum):
        if value < minimum:
            return minimum
        if value > maximum:
            return maximum
        return value
