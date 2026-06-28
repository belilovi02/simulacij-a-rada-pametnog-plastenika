import csv
import os
import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from simulation.monte_carlo import run_monte_carlo
from simulation.energy_model import EnergyModel
from simulation.reporting import save_monte_carlo_report, save_prediction_event


class GreenhouseDashboard:
    def __init__(self, root, esp32, arduino, sensors, actuators, ml_model, log_file):
        self.root = root
        self.esp32 = esp32
        self.arduino = arduino
        self.sensors = sensors
        self.actuators = actuators
        self.ml_model = ml_model
        self.log_file = log_file
        self.energy_model = EnergyModel(actuators)
        self.esp32.set_log_callback(self.add_log)
        self.arduino.set_log_callback(self.add_log)
        self._build_ui()
        self._refresh_loop()

    def _build_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.dashboard_frame = ttk.Frame(self.notebook)
        self.montecarlo_frame = ttk.Frame(self.notebook)
        self.energy_frame = ttk.Frame(self.notebook)
        self.ml_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.notebook.add(self.montecarlo_frame, text="Monte Carlo")
        self.notebook.add(self.energy_frame, text="Energetska sim")
        self.notebook.add(self.ml_frame, text="ML predikcija")

        self._build_dashboard_tab()
        self._build_montecarlo_tab()
        self._build_energy_tab()
        self._build_ml_tab()

    def _build_dashboard_tab(self):
        values_frame = ttk.LabelFrame(self.dashboard_frame, text="Senzori")
        values_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        self.sensor_labels = {}
        for idx, label in enumerate(["temperature", "air_humidity", "soil_moisture", "ph", "npk", "co2"]):
            ttk.Label(values_frame, text=label.replace("_", " ") + ":").grid(row=idx, column=0, sticky=tk.W, padx=4, pady=2)
            self.sensor_labels[label] = ttk.Label(values_frame, text="---")
            self.sensor_labels[label].grid(row=idx, column=1, sticky=tk.W, padx=4, pady=2)

        actuators_frame = ttk.LabelFrame(self.dashboard_frame, text="Aktuatori")
        actuators_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        self.actuator_labels = {}
        for idx, label in enumerate(["pump1", "pump2", "fan", "led", "greenhouse_open", "alarm"]):
            ttk.Label(actuators_frame, text=label.replace("_", " ") + ":").grid(row=idx, column=0, sticky=tk.W, padx=4, pady=2)
            self.actuator_labels[label] = ttk.Label(actuators_frame, text="OFF")
            self.actuator_labels[label].grid(row=idx, column=1, sticky=tk.W, padx=4, pady=2)

        commands_frame = ttk.LabelFrame(self.dashboard_frame, text="Ručno upravljanje")
        commands_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        buttons = [
            ("Pumpa 1 ON", "pump1_on"),
            ("Pumpa 1 OFF", "pump1_off"),
            ("Pumpa 2 ON", "pump2_on"),
            ("Pumpa 2 OFF", "pump2_off"),
            ("Ventilator ON", "fan_on"),
            ("Ventilator OFF", "fan_off"),
            ("LED ON", "led_on"),
            ("LED OFF", "led_off"),
            ("Otvoreni plastenik", "greenhouse_open"),
            ("Zatvoreni plastenik", "greenhouse_close"),
        ]
        for idx, (text, command) in enumerate(buttons):
            btn = ttk.Button(commands_frame, text=text, command=lambda c=command: self.esp32.send_command(c))
            btn.grid(row=idx // 2, column=idx % 2, padx=4, pady=4, sticky=tk.EW)

        status_frame = ttk.LabelFrame(self.dashboard_frame, text="Status kontrolera")
        status_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)
        self.esp32_status_label = ttk.Label(status_frame, text="ESP32: Offline")
        self.esp32_status_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.arduino_status_label = ttk.Label(status_frame, text="Arduino Mega: Offline")
        self.arduino_status_label.pack(side=tk.LEFT, padx=4, pady=4)

        log_frame = ttk.LabelFrame(self.dashboard_frame, text="Log")
        log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.log_text = tk.Text(log_frame, height=12, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _build_montecarlo_tab(self):
        controls = ttk.Frame(self.montecarlo_frame)
        controls.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        ttk.Label(controls, text="Broj simulacija:").pack(side=tk.LEFT, padx=4)
        self.monte_input = tk.IntVar(value=500)
        ttk.Entry(controls, textvariable=self.monte_input, width=8).pack(side=tk.LEFT, padx=4)
        ttk.Button(controls, text="Pokreni Monte Carlo", command=self.run_monte_carlo).pack(side=tk.LEFT, padx=4)

        self.monte_results = tk.Text(self.montecarlo_frame, height=10, state=tk.DISABLED)
        self.monte_results.pack(fill=tk.X, padx=8, pady=8)

        self.monte_fig = Figure(figsize=(5, 3), dpi=100)
        self.monte_axis = self.monte_fig.add_subplot(111)
        self.monte_canvas = FigureCanvasTkAgg(self.monte_fig, master=self.montecarlo_frame)
        self.monte_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def _build_energy_tab(self):
        self.energy_report = ttk.LabelFrame(self.energy_frame, text="Energetski izvještaj")
        self.energy_report.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        self.energy_labels = {}
        for idx, label in enumerate(["consumption", "production", "battery_wh", "runtime_h"]):
            ttk.Label(self.energy_report, text=label.replace("_", " ") + ":").grid(row=idx, column=0, sticky=tk.W, padx=4, pady=2)
            self.energy_labels[label] = ttk.Label(self.energy_report, text="---")
            self.energy_labels[label].grid(row=idx, column=1, sticky=tk.W, padx=4, pady=2)

        self.energy_fig = Figure(figsize=(5, 3), dpi=100)
        self.energy_axis = self.energy_fig.add_subplot(111)
        self.energy_canvas = FigureCanvasTkAgg(self.energy_fig, master=self.energy_frame)
        self.energy_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def _build_ml_tab(self):
        info = ttk.LabelFrame(self.ml_frame, text="Model statistika")
        info.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        ttk.Label(info, text=f"Accuracy: {self.ml_model.accuracy:.2f}").pack(side=tk.LEFT, padx=4)

        self.confusion_text = tk.Text(self.ml_frame, height=5, state=tk.DISABLED)
        self.confusion_text.pack(fill=tk.X, padx=8, pady=4)
        self.feature_fig = Figure(figsize=(5, 3), dpi=100)
        self.feature_axis = self.feature_fig.add_subplot(111)
        self.feature_canvas = FigureCanvasTkAgg(self.feature_fig, master=self.ml_frame)
        self.feature_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        predict_frame = ttk.LabelFrame(self.ml_frame, text="Predikcija na trenutnim vrijednostima")
        predict_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)
        ttk.Button(predict_frame, text="Predvidi", command=self._predict_current).pack(side=tk.LEFT, padx=4)
        self.prediction_label = ttk.Label(predict_frame, text="---")
        self.prediction_label.pack(side=tk.LEFT, padx=4)

        recommendation_frame = ttk.LabelFrame(self.ml_frame, text="Preporuka akcije")
        recommendation_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)
        self.recommendation_label = ttk.Label(recommendation_frame, text="Čekam na podatke...")
        self.recommendation_label.pack(anchor=tk.W, padx=4, pady=4)

    def _refresh_loop(self):
        self._update_dashboard()
        self.root.after(1500, self._refresh_loop)

    def _update_dashboard(self):
        state = self.arduino.get_status()
        sensor_values = state["sensors"]
        actuator_state = state["actuators"]

        for key, label in self.sensor_labels.items():
            label.config(text=str(sensor_values[key]))

        for key, label in self.actuator_labels.items():
            label.config(text="ON" if actuator_state[key] else "OFF")

        self.esp32_status_label.config(text=f"ESP32: {self.esp32.status}")
        self.arduino_status_label.config(text=f"Arduino Mega: {self.arduino.status}")

        energy_report = self.energy_model.current_report()
        for key, label in self.energy_labels.items():
            label.config(text=str(energy_report[key]))

        self._update_energy_plot(energy_report)
        self._update_ml_tab()
        self._write_log_to_csv(sensor_values, actuator_state, energy_report["consumption"])

    def _update_energy_plot(self, energy_report):
        self.energy_axis.clear()
        labels = ["ESP32", "Mega", "Sensors", "Pump1", "Pump2", "Fan", "LED", "Motor"]
        power = [
            self.energy_model.esp32_power,
            self.energy_model.arduino_power,
            self.energy_model.sensors_power,
            self.energy_model.pump1_power if self.actuators.pump1 else 0,
            self.energy_model.pump2_power if self.actuators.pump2 else 0,
            self.energy_model.fan_power if self.actuators.fan else 0,
            self.energy_model.led_power if self.actuators.led else 0,
            self.energy_model.motor_power if self.actuators.greenhouse_open else 0,
        ]
        self.energy_axis.bar(labels, power, color="skyblue")
        self.energy_axis.set_title("Potrošnja po komponentama (W)")
        self.energy_axis.set_ylabel("W")
        self.energy_fig.tight_layout()
        self.energy_canvas.draw()

    def _update_ml_tab(self):
        self.confusion_text.config(state=tk.NORMAL)
        self.confusion_text.delete("1.0", tk.END)
        self.confusion_text.insert(tk.END, f"Confusion matrix:\n{self.ml_model.confusion}")
        self.confusion_text.config(state=tk.DISABLED)

        self.feature_axis.clear()
        names = self.ml_model.feature_names
        values = self.ml_model.feature_importances_
        self.feature_axis.bar(names, values, color="#f39c12")
        self.feature_axis.set_title("Važnost značajki za predikciju")
        self.feature_axis.set_ylabel("Važnost")
        self.feature_axis.tick_params(axis='x', rotation=20)
        self.feature_fig.tight_layout()
        self.feature_canvas.draw()

    def _predict_current(self):
        current = self.sensors.current_values()
        prediction = self.ml_model.predict(current)
        label = "Potrebna navodnjavanja" if prediction["irrigation_needed"] else "Nema potrebe za navodnjavanjem"
        ventilation = "Potrebna ventilacija" if prediction["ventilation_needed"] else "Ventilacija nije potrebna"
        self.prediction_label.config(text=f"{label} | {ventilation}")
        self._update_recommendation(current, prediction)
        save_prediction_event(current, prediction, self.recommendation_label.cget("text"))
        self.add_log("ESP32: pokrenuta ML predikcija na trenutnim podacima")

    def _update_recommendation(self, current, prediction):
        actions = []
        if prediction["irrigation_needed"]:
            actions.append("uključi pumpu")
        if prediction["ventilation_needed"]:
            actions.append("uključi ventilaciju")
        if current.get("temperature", 0) > 35:
            actions.append("otvori plastenik")
        if current.get("soil_moisture", 0) >= 70:
            actions.append("isključi pumpu")
        if not actions:
            actions.append("ostavi sustav u miru")

        self.recommendation_label.config(text="Preporuka: " + ", ".join(actions))

    def run_monte_carlo(self):
        simulations = max(10, self.monte_input.get())
        summary, df = run_monte_carlo(simulations)
        self.monte_results.config(state=tk.NORMAL)
        self.monte_results.delete("1.0", tk.END)
        self.monte_results.insert(tk.END, f"Simulacija: {simulations}\n")
        self.monte_results.insert(tk.END, f"Pumpa uključena: {summary['pump_count']} puta\n")
        self.monte_results.insert(tk.END, f"Ventilator uključen: {summary['fan_count']} puta\n")
        self.monte_results.insert(tk.END, f"LED uključen: {summary['led_count']} puta\n")
        self.monte_results.insert(tk.END, f"Otvaranje plastenika: {summary['open_greenhouse_count']} puta\n")
        self.monte_results.insert(tk.END, f"Alarm: {summary['alarm_count']} puta\n")
        self.monte_results.insert(tk.END, f"Prosječna temperatura: {summary['avg_temperature']:.2f} °C\n")
        self.monte_results.insert(tk.END, f"Prosječna vlažnost zemljišta: {summary['avg_soil_moisture']:.2f}%\n")
        self.monte_results.config(state=tk.DISABLED)
        self._plot_montecarlo(df)
        save_monte_carlo_report(summary, df)

    def _plot_montecarlo(self, df):
        self.monte_axis.clear()
        self.monte_axis.hist(df["temperature"], bins=20, color="#2ecc71", alpha=0.7)
        self.monte_axis.set_title("Distribucija temperature u Monte Carlo simulaciji")
        self.monte_axis.set_xlabel("Temperatura (°C)")
        self.monte_axis.set_ylabel("Broj simulacija")
        self.monte_canvas.draw()

    def add_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _write_log_to_csv(self, sensors, actuators, energy_consumption):
        timestamp = datetime.now().isoformat()
        row = [
            timestamp,
            sensors["temperature"],
            sensors["air_humidity"],
            sensors["soil_moisture"],
            sensors["ph"],
            sensors["npk"],
            sensors["co2"],
            actuators["pump1"],
            actuators["pump2"],
            actuators["fan"],
            actuators["led"],
            actuators["greenhouse_open"],
            actuators["alarm"],
            energy_consumption,
        ]
        file_exists = os.path.exists(self.log_file)
        with open(self.log_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "temperature", "air_humidity", "soil_moisture", "ph", "npk", "co2", "pump1", "pump2", "fan", "led", "greenhouse_open", "alarm", "energy_consumption"])
            writer.writerow(row)
