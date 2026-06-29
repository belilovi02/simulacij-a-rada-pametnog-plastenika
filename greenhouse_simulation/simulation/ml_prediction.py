import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier


class MLPrediction:
    def __init__(self):
        self.model = None
        self.accuracy = 0.0
        self.accuracy_scores = {}
        self.confusion = None
        self.feature_importances_ = None
        self.feature_names = [
            "temperature",
            "air_humidity",
            "soil_moisture",
            "ph",
            "npk",
            "co2",
            "outdoor_temperature",
            "outdoor_humidity",
            "wind_speed",
            "rainfall_mm",
        ]
        self._train_model()

    def _generate_dataset(self, rows=2400):
        data = []
        for _ in range(rows):
            outdoor_temperature = np.random.normal(22, 6)
            outdoor_humidity = np.random.normal(65, 15)
            wind_speed = np.random.uniform(0, 18)
            rainfall_mm = max(0.0, np.random.normal(1.2, 2.0))
            temperature = self._clamp(np.random.normal(24 + (outdoor_temperature - 20) * 0.35, 4.5), 12, 45)
            air_humidity = self._clamp(np.random.normal(55 + (outdoor_humidity - 60) * 0.25, 12), 25, 100)
            soil_moisture = self._clamp(np.random.normal(46 - (temperature - 24) * 0.5 + (rainfall_mm - 1) * 2.0, 14), 8, 90)
            ph = self._clamp(np.random.normal(6.8, 0.4), 4.5, 8.5)
            npk = self._clamp(np.random.normal(130 + (soil_moisture - 45) * 0.5, 40), 20, 250)
            co2 = self._clamp(np.random.normal(520 + (temperature - 24) * 9 - (wind_speed - 6) * 4, 115), 200, 1200)
            irrigation_needed = int(soil_moisture < 34 or temperature > 30 or rainfall_mm < 1)
            ventilation_needed = int(temperature > 28 or co2 > 700 or air_humidity > 80 or wind_speed > 11)
            if np.random.random() < 0.08:
                irrigation_needed = 1 - irrigation_needed
            if np.random.random() < 0.06:
                ventilation_needed = 1 - ventilation_needed
            data.append(
                {
                    "temperature": temperature,
                    "air_humidity": air_humidity,
                    "soil_moisture": soil_moisture,
                    "ph": ph,
                    "npk": npk,
                    "co2": co2,
                    "outdoor_temperature": outdoor_temperature,
                    "outdoor_humidity": outdoor_humidity,
                    "wind_speed": wind_speed,
                    "rainfall_mm": rainfall_mm,
                    "irrigation_needed": irrigation_needed,
                    "ventilation_needed": ventilation_needed,
                }
            )
        return pd.DataFrame(data)

    def _train_model(self):
        df = self._generate_dataset()
        X = df[self.feature_names]
        y = df[["irrigation_needed", "ventilation_needed"]]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        base_model = RandomForestClassifier(n_estimators=140, random_state=42)
        model = MultiOutputClassifier(base_model)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        self.model = model
        irrigation_accuracy = accuracy_score(y_test["irrigation_needed"], y_pred[:, 0])
        ventilation_accuracy = accuracy_score(y_test["ventilation_needed"], y_pred[:, 1])
        self.accuracy_scores = {
            "irrigation": round(float(irrigation_accuracy), 3),
            "ventilation": round(float(ventilation_accuracy), 3),
        }
        self.accuracy = round(float((y_pred == y_test.to_numpy()).all(axis=1).mean()), 3)
        self.confusion = {
            "irrigation": confusion_matrix(y_test["irrigation_needed"], y_pred[:, 0]).tolist(),
            "ventilation": confusion_matrix(y_test["ventilation_needed"], y_pred[:, 1]).tolist(),
        }
        self.feature_importances_ = np.mean(
            [est.feature_importances_ for est in model.estimators_], axis=0
        )

    def predict(self, values):
        feature_values = [values.get(name, 0) for name in self.feature_names]
        X = pd.DataFrame([feature_values], columns=self.feature_names)
        predicted = self.model.predict(X)[0]
        return {
            "irrigation_needed": int(predicted[0]),
            "ventilation_needed": int(predicted[1]),
        }

    @staticmethod
    def _clamp(value, minimum, maximum):
        return minimum if value < minimum else maximum if value > maximum else value
