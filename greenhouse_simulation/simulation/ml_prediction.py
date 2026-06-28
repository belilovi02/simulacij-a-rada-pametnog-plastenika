import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split


class MLPrediction:
    def __init__(self):
        self.model = None
        self.accuracy = 0.0
        self.confusion = None
        self.feature_importances_ = None
        self.feature_names = ["temperature", "air_humidity", "soil_moisture", "ph", "npk", "co2"]
        self._train_model()

    def _generate_dataset(self, rows=1200):
        data = []
        for _ in range(rows):
            temperature = np.random.uniform(15, 45)
            air_humidity = np.random.uniform(30, 95)
            soil_moisture = np.random.uniform(10, 90)
            ph = np.random.uniform(4.5, 8.5)
            npk = np.random.uniform(0, 250)
            co2 = np.random.uniform(250, 900)
            irrigation_needed = int(soil_moisture < 35 or temperature > 32)
            ventilation_needed = int(temperature > 32 or co2 > 700 or air_humidity < 40)
            data.append({
                "temperature": temperature,
                "air_humidity": air_humidity,
                "soil_moisture": soil_moisture,
                "ph": ph,
                "npk": npk,
                "co2": co2,
                "irrigation_needed": irrigation_needed,
                "ventilation_needed": ventilation_needed,
            })
        return pd.DataFrame(data)

    def _train_model(self):
        df = self._generate_dataset()
        X = df[self.feature_names]
        y_irrigation = df["irrigation_needed"]

        X_train, X_test, y_train, y_test = train_test_split(X, y_irrigation, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=120, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        self.model = model
        self.accuracy = accuracy_score(y_test, y_pred)
        self.confusion = confusion_matrix(y_test, y_pred)
        self.feature_importances_ = model.feature_importances_

    def predict(self, values):
        feature_values = []
        for name in self.feature_names:
            feature_values.append(values.get(name, 0))

        X = pd.DataFrame([feature_values], columns=self.feature_names)
        predicted = self.model.predict(X)[0]
        return {
            "irrigation_needed": int(predicted),
            "ventilation_needed": int(values.get("temperature", 0) > 32 or values.get("co2", 0) > 700 or values.get("air_humidity", 0) < 40),
        }
