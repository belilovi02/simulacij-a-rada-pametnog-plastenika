import pandas as pd
from .actuators import ActuatorModel
from .greenhouse_model import GreenhouseModel
from .sensors import SensorModel
from .weather_station import WeatherStationModel


def _apply_rules(values):
    pump1 = values["soil_moisture"] < 38 or values["npk"] < 65
    pump2 = values["soil_moisture"] < 28 and values["temperature"] > 28
    fan = values["temperature"] > 30 or values["co2"] > 700 or values["air_humidity"] > 78
    open_greenhouse = values["temperature"] > 32 and values["weather_signal"] not in {"rain", "wind"}
    led = values["co2"] > 720 or values["temperature"] < 20 or values["air_humidity"] < 38
    alarm = values["ph"] < 5.7 or values["ph"] > 7.2 or values["npk"] < 55 or values["soil_moisture"] < 18
    return {
        "pump1": pump1,
        "pump2": pump2,
        "fan": fan,
        "led": led,
        "open_greenhouse": open_greenhouse,
        "alarm": alarm,
    }


def _safe_zone(value_row):
    return (
        18 <= value_row["temperature"] <= 30
        and 30 <= value_row["soil_moisture"] <= 70
        and 300 <= value_row["co2"] <= 800
        and 5.8 <= value_row["ph"] <= 7.0
        and 80 <= value_row["npk"] <= 200
    )


def run_monte_carlo(simulations=500, steps=12):
    rows = []
    for simulation_id in range(simulations):
        sensors = SensorModel()
        weather = WeatherStationModel()
        actuators = ActuatorModel()
        greenhouse = GreenhouseModel(sensors, actuators, weather_station=weather)

        for step in range(steps):
            weather.update()
            sensor_values = sensors.current_values()
            weather_values = weather.current_values()
            values = {**sensor_values, **weather_values}
            controls = _apply_rules(values)

            actuators.pump1 = controls["pump1"]
            actuators.pump2 = controls["pump2"]
            actuators.fan = controls["fan"]
            actuators.led = controls["led"]
            actuators.greenhouse_open = controls["open_greenhouse"]
            actuators.alarm = controls["alarm"]

            row = {
                "simulation_id": simulation_id,
                "step": step,
                **sensor_values,
                "outdoor_temperature": weather_values["outdoor_temperature"],
                "outdoor_humidity": weather_values["outdoor_humidity"],
                "wind_speed": weather_values["wind_speed"],
                "rainfall_mm": weather_values["rainfall_mm"],
                "weather_signal": weather_values["weather_signal"],
                **controls,
            }
            rows.append(row)
            greenhouse.simulate_step()

    df = pd.DataFrame(rows)
    trend_df = df.groupby("step").agg(
        temperature_mean=("temperature", "mean"),
        soil_moisture_mean=("soil_moisture", "mean"),
        co2_mean=("co2", "mean"),
        ph_mean=("ph", "mean"),
        npk_mean=("npk", "mean"),
    ).reset_index()

    df["safe_zone"] = df.apply(_safe_zone, axis=1)
    weather_counts = df["weather_signal"].value_counts().to_dict()

    pump1_count = int(df["pump1"].sum())
    pump2_count = int(df["pump2"].sum())

    def confidence_statistics(column):
        """Deskriptivna statistika i 95% CI sredine (normalna aproksimacija)."""
        values = df[column]
        count = int(values.count())
        mean = float(values.mean())
        std = float(values.std(ddof=1))
        standard_error = std / (count ** 0.5)
        margin = 1.96 * standard_error
        return {
            "count": count,
            "mean": mean,
            "std": std,
            "min": float(values.min()),
            "max": float(values.max()),
            "median": float(values.median()),
            "standard_error": standard_error,
            "ci95_lower": mean - margin,
            "ci95_upper": mean + margin,
            "ci95_width": margin * 2,
        }

    summary = {
        "pump1_count": pump1_count,
        "pump2_count": pump2_count,
        "pump_count": pump1_count + pump2_count,
        "fan_count": int(df["fan"].sum()),
        "led_count": int(df["led"].sum()),
        "open_greenhouse_count": int(df["open_greenhouse"].sum()),
        "alarm_count": int(df["alarm"].sum()),
        "avg_temperature": float(df["temperature"].mean()),
        "avg_soil_moisture": float(df["soil_moisture"].mean()),
        "avg_co2": float(df["co2"].mean()),
        "avg_ph": float(df["ph"].mean()),
        "avg_npk": float(df["npk"].mean()),
        "critical_low_moisture_count": int((df["soil_moisture"] < 25).sum()),
        "critical_high_temperature_count": int((df["temperature"] > 38).sum()),
        "critical_high_co2_count": int((df["co2"] > 900).sum()),
        "safe_zone_ratio": float(df["safe_zone"].mean()),
        "weather_counts": {key: int(value) for key, value in weather_counts.items()},
        "action_summary": {
            "pump": pump1_count + pump2_count,
            "pump1": pump1_count,
            "pump2": pump2_count,
            "fan": int(df["fan"].sum()),
            "open_greenhouse": int(df["open_greenhouse"].sum()),
            "alarm": int(df["alarm"].sum()),
        },
        "uncertainty": {
            "temperature": confidence_statistics("temperature"),
            "soil_moisture": confidence_statistics("soil_moisture"),
            "ph": confidence_statistics("ph"),
            "npk": confidence_statistics("npk"),
            "co2": confidence_statistics("co2"),
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
