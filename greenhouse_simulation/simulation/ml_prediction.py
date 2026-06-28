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
        self._train_model()

    def _generate_dataset(self, rows=1200):
        data = []
        for _ in range(rows):
            temperature = np.random.uniform(15, 45)
            air_humidity = np.random.uniform(30, 95)
            soil_moisture = np.random.uniform(10, 90)
            ph = np.random.uniform(4.5, 8.5)
            npk = np.random.uniform(0, 250)
            light = np.random.uniform(0, 1000)
            irrigation_needed = int(soil_moisture < 35 or temperature > 32)
            ventilation_needed = int(temperature > 32 or light > 900)
            data.append({
                "temperature": temperature,
                "air_humidity": air_humidity,
                "soil_moisture": soil_moisture,
                "ph": ph,
                "npk": npk,
                "light": light,
                "irrigation_needed": irrigation_needed,
                "ventilation_needed": ventilation_needed,
            })
        return pd.DataFrame(data)

    def _train_model(self):
        df = self._generate_dataset()
        X = df[["temperature", "air_humidity", "soil_moisture", "ph", "npk", "light"]]
        y_irrigation = df["irrigation_needed"]
        y_ventilation = df["ventilation_needed"]

        X_train, X_test, y_train, y_test = train_test_split(X, y_irrigation, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        self.model = model
        self.accuracy = accuracy_score(y_test, y_pred)
        self.confusion = confusion_matrix(y_test, y_pred)
        self.feature_importances_ = model.feature_importances_

    def predict(self, values):
        feature_names = ["temperature", "air_humidity", "soil_moisture", "ph", "npk", "light"]
        X = pd.DataFrame([
            [
                values["temperature"],
                values["air_humidity"],
                values["soil_moisture"],
                values["ph"],
                values["npk"],
                values["light"],
            ]
        ], columns=feature_names)
        predicted = self.model.predict(X)[0]
        return {
            "irrigation_needed": int(predicted),
            "ventilation_needed": int(values["temperature"] > 32 or values["light"] > 900),
        }
