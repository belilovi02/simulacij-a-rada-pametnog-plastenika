import random
import pandas as pd


def _random_sensor_row():
    return {
        "temperature": random.uniform(15, 45),
        "air_humidity": random.uniform(30, 95),
        "soil_moisture": random.uniform(10, 90),
        "ph": random.uniform(4.5, 8.5),
        "npk": random.uniform(0, 250),
        "light": random.uniform(0, 1000),
    }


def _apply_rules(values):
    pump = values["soil_moisture"] < 35
    fan = values["temperature"] > 32
    open_greenhouse = values["temperature"] > 35
    alarm = values["ph"] < 5.5 or values["ph"] > 7.5 or values["npk"] < 60
    return {
        "pump": pump,
        "fan": fan,
        "open_greenhouse": open_greenhouse,
        "alarm": alarm,
    }


def run_monte_carlo(simulations=1000):
    rows = []
    for _ in range(simulations):
        values = _random_sensor_row()
        result = _apply_rules(values)
        row = {**values, **result}
        rows.append(row)

    df = pd.DataFrame(rows)
    summary = {
        "pump_count": int(df["pump"].sum()),
        "fan_count": int(df["fan"].sum()),
        "open_greenhouse_count": int(df["open_greenhouse"].sum()),
        "alarm_count": int(df["alarm"].sum()),
        "avg_temperature": float(df["temperature"].mean()),
        "avg_soil_moisture": float(df["soil_moisture"].mean()),
    }
    return summary, df
