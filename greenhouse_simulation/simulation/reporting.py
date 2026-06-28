import csv
import os
from datetime import datetime

import pandas as pd


def save_monte_carlo_report(summary, df, output_path=None):
    if output_path is None:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        output_dir = os.path.join(base_dir, "data")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "monte_carlo_report.csv")

    export_df = df.copy()
    export_df["timestamp"] = datetime.now().isoformat()
    export_df.to_csv(output_path, index=False)
    return output_path


def save_prediction_event(values, prediction, recommendation, output_path=None):
    if output_path is None:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        output_dir = os.path.join(base_dir, "data")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "prediction_events.csv")

    row = {
        "timestamp": datetime.now().isoformat(),
        "temperature": values.get("temperature"),
        "air_humidity": values.get("air_humidity"),
        "soil_moisture": values.get("soil_moisture"),
        "ph": values.get("ph"),
        "npk": values.get("npk"),
        "co2": values.get("co2"),
        "irrigation_needed": prediction.get("irrigation_needed"),
        "ventilation_needed": prediction.get("ventilation_needed"),
        "recommendation": recommendation,
    }

    if os.path.exists(output_path):
        existing = pd.read_csv(output_path)
        updated = pd.concat([existing, pd.DataFrame([row])], ignore_index=True)
        updated.to_csv(output_path, index=False)
    else:
        pd.DataFrame([row]).to_csv(output_path, index=False)

    return output_path
