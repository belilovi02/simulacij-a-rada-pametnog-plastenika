
class EnergyModel:
    def __init__(self, actuators):
        self.actuators = actuators
        self.esp32_power = 0.5
        self.arduino_power = 0.4
        self.sensors_power = 0.5
        self.pump1_power = 12.0
        self.pump2_power = 12.0
        self.pump3_power = 10.0
        self.fan_power = 8.0
        self.led_power = 10.0
        self.motor_power = 15.0
        self.panel1_power = 20.0
        self.panel2_power = 20.0
        self.battery_capacity_wh = 12 * 20
        self.battery_level_wh = self.battery_capacity_wh

    def compute_consumption(self):
        total = self.esp32_power + self.arduino_power + self.sensors_power
        total += self.pump1_power if self.actuators.pump1 else 0
        total += self.pump2_power if self.actuators.pump2 else 0
        total += self.pump3_power if self.actuators.pump3 else 0
        total += self.fan_power if self.actuators.fan else 0
        total += self.led_power if self.actuators.led else 0
        total += self.motor_power if self.actuators.greenhouse_open else 0
        return round(total, 2)

    def compute_solar_production(self):
        production = 0
        if self.actuators.led:
            production = self.panel1_power + self.panel2_power
        else:
            production = self.panel1_power + self.panel2_power
        return production

    def update_battery(self, consumption):
        production = self.compute_solar_production()
        net = production - consumption
        self.battery_level_wh = self._clamp(self.battery_level_wh + net, 0, self.battery_capacity_wh)
        return round(self.battery_level_wh, 2)

    def estimate_runtime(self, consumption):
        if consumption <= 0:
            return float("inf")
        return round(self.battery_level_wh / consumption, 2)

    def current_report(self):
        consumption = self.compute_consumption()
        production = self.compute_solar_production()
        battery = self.battery_level_wh
        runtime = self.estimate_runtime(consumption)
        net_balance = production - consumption
        battery_percentage = round((battery / self.battery_capacity_wh) * 100, 1)
        solar_coverage_pct = round((production / max(consumption, 1) * 100), 1)
        return {
            "consumption": consumption,
            "production": production,
            "battery_wh": battery,
            "runtime_h": runtime,
            "net_balance_wh": round(net_balance, 2),
            "battery_percentage": battery_percentage,
            "solar_coverage_pct": solar_coverage_pct,
        }

    @staticmethod
    def _clamp(value, minimum, maximum):
        return minimum if value < minimum else maximum if value > maximum else value
