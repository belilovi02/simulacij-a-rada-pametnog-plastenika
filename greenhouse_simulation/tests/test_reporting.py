import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd

from simulation.actuators import ActuatorModel
from simulation.energy_model import EnergyModel
from simulation.monte_carlo import run_monte_carlo
from simulation.reporting import save_monte_carlo_report, save_prediction_event


def test_save_monte_carlo_report_creates_csv(tmp_path):
    summary, df = run_monte_carlo(simulations=20, steps=3)
    output_path = tmp_path / "monte.csv"

    saved_path = save_monte_carlo_report(summary, df, output_path=str(output_path))

    assert saved_path == str(output_path)
    assert output_path.exists()
    assert pd.read_csv(output_path).shape[0] > 0


def test_save_prediction_event_creates_csv(tmp_path):
    output_path = tmp_path / "predictions.csv"
    values = {
        "temperature": 30.0,
        "air_humidity": 65.0,
        "soil_moisture": 28.0,
        "ph": 6.0,
        "npk": 90.0,
        "co2": 800.0,
    }

    saved_path = save_prediction_event(values, {"irrigation_needed": 1, "ventilation_needed": 0}, "uključi pumpu", output_path=str(output_path))

    assert saved_path == str(output_path)
    assert output_path.exists()
    assert "timestamp" in pd.read_csv(output_path).columns


def test_monte_carlo_summary_contains_rich_metrics():
    summary, df = run_monte_carlo(simulations=12, steps=4)

    assert "avg_co2" in summary
    assert "critical_low_moisture_count" in summary
    assert "critical_high_temperature_count" in summary
    assert "critical_high_co2_count" in summary
    assert "action_summary" in summary
    assert "trend_series" in summary
    assert set(summary["action_summary"].keys()) >= {"pump", "fan", "open_greenhouse", "alarm"}
    assert set(summary["trend_series"].keys()) >= {"temperature", "soil_moisture", "co2", "ph", "npk"}
    assert len(summary["trend_series"]["temperature"]) > 0
    assert len(df) > 0


def test_energy_model_reports_balance_and_battery_percentage():
    actuators = ActuatorModel()
    actuators.pump1 = True
    actuators.fan = True

    energy_model = EnergyModel(actuators)
    report = energy_model.current_report()

    assert "net_balance_wh" in report
    assert "battery_percentage" in report
    assert "solar_coverage_pct" in report
