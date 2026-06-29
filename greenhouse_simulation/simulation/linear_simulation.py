import pandas as pd


# Linearno interpolira zadane početne i završne uvjete, na svakom koraku primjenjuje
# pragove upravljanja te vraća sažetak aktivacija i potpunu tablicu rezultata.
def run_linear_simulation(
    temp_start=20.0,
    temp_end=38.0,
    moisture_start=70.0,
    moisture_end=25.0,
    npk_start=180.0,
    npk_end=50.0,
    co2_start=450.0,
    co2_end=900.0,
    steps=20,
):
    rows = []
    for step in range(steps):
        progress = step / max(steps - 1, 1)
        temperature = temp_start + (temp_end - temp_start) * progress
        soil_moisture = moisture_start + (moisture_end - moisture_start) * progress
        npk = npk_start + (npk_end - npk_start) * progress
        co2 = co2_start + (co2_end - co2_start) * progress
        ph = 6.5
        air_humidity = 55.0 - (progress * 20.0)

        pump = soil_moisture < 35.0
        fan = temperature > 32.0
        open_greenhouse = temperature > 35.0
        npk_pump = npk < 60.0
        alarm = npk < 50.0 or temperature > 42.0

        rows.append(
            {
                "step": step,
                "temperature": round(temperature, 2),
                "air_humidity": round(air_humidity, 2),
                "soil_moisture": round(soil_moisture, 2),
                "ph": round(ph, 2),
                "npk": round(npk, 2),
                "co2": round(co2, 2),
                "pump": pump,
                "fan": fan,
                "open_greenhouse": open_greenhouse,
                "npk_pump": npk_pump,
                "alarm": alarm,
            }
        )

    df = pd.DataFrame(rows)
    events = []
    for action in ["pump", "fan", "open_greenhouse", "npk_pump", "alarm"]:
        triggered = df[df[action]].head(1)
        if not triggered.empty:
            events.append(
                {
                    "action": action,
                    "step": int(triggered.iloc[0]["step"]),
                    "value": float(triggered.iloc[0][action]),
                }
            )

    summary = {
        "temperature": df["temperature"].tolist(),
        "soil_moisture": df["soil_moisture"].tolist(),
        "npk": df["npk"].tolist(),
        "co2": df["co2"].tolist(),
        "pump_count": int(df["pump"].sum()),
        "fan_count": int(df["fan"].sum()),
        "open_greenhouse_count": int(df["open_greenhouse"].sum()),
        "npk_pump_count": int(df["npk_pump"].sum()),
        "alarm_count": int(df["alarm"].sum()),
        "events": events,
        "trend_series": {
            "temperature": df["temperature"].tolist(),
            "soil_moisture": df["soil_moisture"].tolist(),
            "npk": df["npk"].tolist(),
            "co2": df["co2"].tolist(),
        },
        "steps": steps,
    }
    return summary, df
