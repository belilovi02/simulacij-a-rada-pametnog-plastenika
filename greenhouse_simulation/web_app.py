import csv
import io
import json
import os
import threading
import time
from collections import deque
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, make_response
from simulation.monte_carlo import run_monte_carlo
from simulation.linear_simulation import run_linear_simulation
from simulation.ml_prediction import MLPrediction
from simulation.sensors import SensorModel
from simulation.actuators import ActuatorModel
from simulation.weather_station import WeatherStationModel
from simulation.energy_model import EnergyModel
from controllers.arduino_mega_controller import ArduinoMegaController
from controllers.esp32_controller import ESP32Controller
from simulation.greenhouse_model import GreenhouseModel

BASE_DIR = os.path.dirname(__file__)
app = Flask(__name__, template_folder="templates", static_folder="static")

ml_model = MLPrediction()

sensors = SensorModel()
actuators = ActuatorModel()
weather_station = WeatherStationModel()
greenhouse_model = GreenhouseModel(sensors, actuators, weather_station=weather_station)
energy_model = EnergyModel(actuators)
arduino_controller = ArduinoMegaController(
    sensors, actuators, weather_station=weather_station, greenhouse_model=greenhouse_model
)
esp32_controller = ESP32Controller(arduino_controller)

running_state = {
    "sensors": sensors.current_values(),
    "actuators": actuators.state,
    "weather": weather_station.current_values(),
    "energy": energy_model.current_report(),
    "prediction": {},
    "recommendation": "---",
}
history = deque(maxlen=300)
state_lock = threading.Lock()

def snapshot():
    return {"timestamp": datetime.now().isoformat(timespec="seconds"),
            "sensors": sensors.current_values(), "actuators": actuators.state,
            "weather": weather_station.current_values(), "energy": energy_model.current_report(),
            "manual": dict(arduino_controller.manual_overrides)}

def background_loop():
    while True:
        time.sleep(1.5)
        weather_station.update()
        greenhouse_model.simulate_step()
        arduino_controller._apply_control_logic()
        arduino_controller._apply_recommendation_logic()
        energy_model.update_battery(energy_model.compute_consumption())
        with state_lock:
            history.append(snapshot())

@app.route("/")
def index():
    return render_template("index.html", model_accuracy=ml_model.accuracy, feature_names=ml_model.feature_names)

@app.route("/api/state")
def api_state():
    state = snapshot()
    with state_lock:
        state["history"] = list(history)
    return jsonify(state)

@app.route("/api/forecast")
def api_forecast():
    import math
    current = sensors.current_values(); points = []
    for hour in range(25):
        sun = max(0, math.sin((hour - 6) * math.pi / 12))
        points.append({"hour": hour, "temperature": round(current["temperature"] + 5*sun - 1.5, 1),
            "air_humidity": round(max(30, min(95, current["air_humidity"] - 8*sun + 3)), 1),
            "soil_moisture": round(max(10, current["soil_moisture"] - hour*.22), 1),
            "energy_consumption": round(1.4 + (12 if current["soil_moisture"]-hour*.22 < 35 else 0) + (8 if sun > .7 else 0), 1),
            "solar_production": round(40*sun, 1)})
    return jsonify({"date": (datetime.now()+timedelta(days=1)).date().isoformat(), "points": points})

@app.route("/api/export_all")
def api_export_all():
    output = io.StringIO(); writer = csv.writer(output)
    writer.writerow(["timestamp","temperature","air_humidity","soil_moisture","ph","npk","co2","outdoor_temperature","wind_speed","pump1","pump2","npk_pump","fan","greenhouse_open","consumption","production","battery_percentage"])
    with state_lock:
        rows = list(history) or [snapshot()]
    for x in rows:
        writer.writerow([x["timestamp"],x["sensors"]["temperature"],x["sensors"]["air_humidity"],x["sensors"]["soil_moisture"],x["sensors"]["ph"],x["sensors"]["npk"],x["sensors"]["co2"],x["weather"]["outdoor_temperature"],x["weather"]["wind_speed"],x["actuators"]["pump1"],x["actuators"]["pump2"],x["actuators"]["npk_pump"],x["actuators"]["fan"],x["actuators"]["greenhouse_open"],x["energy"]["consumption"],x["energy"]["production"],x["energy"]["battery_percentage"]])
    response=make_response(output.getvalue()); response.headers["Content-Disposition"]="attachment; filename=greenhouse_all_values.csv"; response.headers["Content-Type"]="text/csv; charset=utf-8"; return response

@app.route("/api/export_state")
def api_export_state():
    state = {
        **sensors.current_values(),
        **weather_station.current_values(),
        **actuators.state,
        **energy_model.current_report(),
    }
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["key", "value"])
    for key, value in state.items():
        writer.writerow([key, value])
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=greenhouse_report.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

@app.route("/api/predict", methods=["POST"])
def api_predict():
    payload = request.get_json(force=True)
    values = payload.get("values", {})
    prediction = ml_model.predict(values)
    recommendation = _build_recommendation(values, prediction)
    running_state["prediction"] = prediction
    running_state["recommendation"] = recommendation
    return jsonify({"prediction": prediction, "recommendation": recommendation})

@app.route("/api/montecarlo", methods=["POST"])
def api_montecarlo():
    req = request.get_json(force=True)
    simulations = int(req.get("simulations", 200))
    steps = int(req.get("steps", 12))
    summary, df = run_monte_carlo(simulations=simulations, steps=steps)
    chart_df = df.sample(min(len(df), 3000), random_state=42)
    return jsonify({"summary": summary, "sample": df.head(20).to_dict(orient="records"),
        "distributions": {"temperature": chart_df["temperature"].tolist(),
                          "soil_moisture": chart_df["soil_moisture"].tolist()}})

@app.route("/api/linear_simulation", methods=["POST"])
def api_linear_simulation():
    req = request.get_json(force=True)
    temp_start = float(req.get("temp_start", 20.0))
    temp_end = float(req.get("temp_end", 38.0))
    moisture_start = float(req.get("moisture_start", 70.0))
    moisture_end = float(req.get("moisture_end", 25.0))
    npk_start = float(req.get("npk_start", 180.0))
    npk_end = float(req.get("npk_end", 50.0))
    co2_start = float(req.get("co2_start", 450.0))
    co2_end = float(req.get("co2_end", 900.0))
    steps = int(req.get("steps", 20))
    summary, df = run_linear_simulation(
        temp_start=temp_start,
        temp_end=temp_end,
        moisture_start=moisture_start,
        moisture_end=moisture_end,
        npk_start=npk_start,
        npk_end=npk_end,
        co2_start=co2_start,
        co2_end=co2_end,
        steps=steps,
    )
    return jsonify({"summary": summary, "sample": df.to_dict(orient="records")})

@app.route("/api/control", methods=["POST"])
def api_control():
    payload = request.get_json(force=True)
    command = payload.get("command")
    if command:
        esp32_controller.send_command(command)
        arduino_controller._process_command()
        arduino_controller._apply_control_logic()
        energy_model.update_battery(energy_model.compute_consumption())
        return jsonify({"status": "ok", "command": command, "actuators": actuators.state, "energy": energy_model.current_report()})
    return jsonify({"status": "error", "message": "Missing command"}), 400

@app.route("/api/train")
def api_train():
    ml_model._train_model()
    return jsonify({"status": "ok", "accuracy": ml_model.accuracy, "accuracy_scores": ml_model.accuracy_scores})

@app.route("/api/random_forest")
def api_random_forest():
    values = {**sensors.current_values(), **weather_station.current_values()}
    return jsonify({
        "model": "Random Forest (140 stabala)", "training_rows": 2400,
        "accuracy": ml_model.accuracy, "accuracy_scores": ml_model.accuracy_scores,
        "confusion": ml_model.confusion, "feature_names": ml_model.feature_names,
        "feature_importances": [round(float(v), 5) for v in ml_model.feature_importances_],
        "current_values": values, "current_prediction": ml_model.predict(values),
    })

def _build_recommendation(values, prediction):
    actions = []
    if prediction.get("irrigation_needed"):
        actions.append("Uključi pumpu")
    if prediction.get("ventilation_needed"):
        actions.append("Uključi ventilaciju")
    if values.get("temperature", 0) > 35:
        actions.append("Otvoriti plastenik")
    if not actions:
        actions.append("Nema potrebe za promjenom")
    return ", ".join(actions)

if __name__ == "__main__":
    thread = threading.Thread(target=background_loop, daemon=True)
    thread.start()
    app.run(host="0.0.0.0", port=5000, debug=True)
