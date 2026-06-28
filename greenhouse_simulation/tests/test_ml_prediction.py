import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from simulation.ml_prediction import MLPrediction


def test_predict_uses_feature_names_and_returns_expected_keys():
    model = MLPrediction()
    values = {
        "temperature": 25.0,
        "air_humidity": 60.0,
        "soil_moisture": 40.0,
        "ph": 6.5,
        "npk": 100.0,
        "co2": 450.0,
    }

    prediction = model.predict(values)

    assert model.feature_names == ["temperature", "air_humidity", "soil_moisture", "ph", "npk", "co2"]
    assert set(prediction.keys()) == {"irrigation_needed", "ventilation_needed"}
    assert isinstance(prediction["irrigation_needed"], int)
    assert isinstance(prediction["ventilation_needed"], int)


def test_predict_works_without_co2_value():
    model = MLPrediction()
    values = {
        "temperature": 30.0,
        "air_humidity": 70.0,
        "soil_moisture": 25.0,
        "ph": 5.8,
        "npk": 55.0,
    }

    prediction = model.predict(values)

    assert set(prediction.keys()) == {"irrigation_needed", "ventilation_needed"}
    assert isinstance(prediction["irrigation_needed"], int)
    assert isinstance(prediction["ventilation_needed"], int)
