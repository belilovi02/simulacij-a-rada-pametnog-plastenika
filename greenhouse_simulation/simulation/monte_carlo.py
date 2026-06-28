import random
import pandas as pd


def _random_sensor_row():
    return {
        "temperature": random.uniform(15, 45),
        "air_humidity": random.uniform(30, 95),
        "soil_moisture": random.uniform(10, 90),
        "ph": random.uniform(4.5, 8.5),
        "npk": random.uniform(0, 250),
        "co2": random.uniform(200, 1200),
    }


def _apply_rules(values):
    pump = values["soil_moisture"] < 35
    fan = values["temperature"] > 32
    open_greenhouse = values["temperature"] > 35
    led = values["co2"] > 750
    alarm = values["ph"] < 5.5 or values["ph"] > 7.5 or values["npk"] < 60
    return {
        "pump": pump,
        "fan": fan,
        "led": led,
        "open_greenhouse": open_greenhouse,
        "alarm": alarm,
    }


def _apply_effects(values, controls):
    updated = dict(values)
    if controls["pump"]:
        updated["soil_moisture"] = min(90, updated["soil_moisture"] + 2.5)
    if controls["fan"]:
        updated["temperature"] = max(15, updated["temperature"] - 0.7)
    if controls["led"]:
        updated["co2"] = max(200, updated["co2"] - 40)
    if controls["open_greenhouse"]:
        updated["temperature"] = max(15, updated["temperature"] - 0.3)

    updated["temperature"] = min(45, max(15, updated["temperature"] + random.uniform(-1.2, 1.2)))
    updated["air_humidity"] = min(95, max(30, updated["air_humidity"] + random.uniform(-2.5, 2.5)))
    updated["soil_moisture"] = min(90, max(10, updated["soil_moisture"] + random.uniform(-1.0, 1.0)))
    updated["ph"] = min(8.5, max(4.5, updated["ph"] + random.uniform(-0.15, 0.15)))
    updated["npk"] = min(250, max(0, updated["npk"] + random.uniform(-8, 8)))
    updated["co2"] = min(1200, max(200, updated["co2"] + random.uniform(-60, 60)))
    return updated


def run_monte_carlo(simulations=500, steps=12):
    rows = []
    for simulation_id in range(simulations):
        values = _random_sensor_row()
        for step in range(steps):
            controls = _apply_rules(values)
            row = {"simulation_id": simulation_id, "step": step, **values, **controls}
            rows.append(row)
            values = _apply_effects(values, controls)

    df = pd.DataFrame(rows)
    trend_df = df.groupby("step").agg(
        temperature_mean=("temperature", "mean"),
        soil_moisture_mean=("soil_moisture", "mean"),
        co2_mean=("co2", "mean"),
        ph_mean=("ph", "mean"),
        npk_mean=("npk", "mean"),
    ).reset_index()

    summary = {
        "pump_count": int(df["pump"].sum()),
        "fan_count": int(df["fan"].sum()),
        "led_count": int(df["led"].sum()),
        "open_greenhouse_count": int(df["open_greenhouse"].sum()),
        "alarm_count": int(df["alarm"].sum()),
        "avg_temperature": float(df["temperature"].mean()),
        "avg_soil_moisture": float(df["soil_moisture"].mean()),
        "avg_co2": float(df["co2"].mean()),
        "critical_low_moisture_count": int((df["soil_moisture"] < 25).sum()),
        "critical_high_temperature_count": int((df["temperature"] > 38).sum()),
        "critical_high_co2_count": int((df["co2"] > 900).sum()),
        "action_summary": {
            "pump": int(df["pump"].sum()),
            "fan": int(df["fan"].sum()),
            "open_greenhouse": int(df["open_greenhouse"].sum()),
            "alarm": int(df["alarm"].sum()),
        },
        "trend_series": {
            "temperature": trend_df["temperature_mean"].tolist(),
            "soil_moisture": trend_df["soil_moisture_mean"].tolist(),
            "co2": trend_df["co2_mean"].tolist(),
            "ph": trend_df["ph_mean"].tolist(),
            "npk": trend_df["npk_mean"].tolist(),
        },
    }
    return summary, df
