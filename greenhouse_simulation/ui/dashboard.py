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
    # Povezuje Tkinter prozor sa svim modelima i zatim gradi starije desktop sučelje.
    def __init__(self, root, esp32, arduino, sensors, actuators, ml_model, log_file, weather_station=None):
        self.root = root
        self.esp32 = esp32
        self.arduino = arduino
        self.sensors = sensors
        self.actuators = actuators
        self.ml_model = ml_model
        self.log_file = log_file
        self.weather_station = weather_station
        self.energy_model = EnergyModel(actuators)
        self.monte_last_trend = {"temperature": [], "soil_moisture": [], "co2": [], "ph": [], "npk": []}
        self.esp32.set_log_callback(self.add_log)
        self.arduino.set_log_callback(self.add_log)
        self._build_ui()
        self._refresh_loop()

    # Stvara kartice aplikacije i poziva zasebne graditelje sadržaja svake kartice.
    def _build_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.dashboard_frame = ttk.Frame(self.notebook)
        self.montecarlo_frame = ttk.Frame(self.notebook)
        self.energy_frame = ttk.Frame(self.notebook)
        self.ml_frame = ttk.Frame(self.notebook)
        self.weather_frame = ttk.Frame(self.notebook)

        self.visualization_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.notebook.add(self.montecarlo_frame, text="Monte Carlo")
        self.notebook.add(self.energy_frame, text="Energetska sim")
        self.notebook.add(self.ml_frame, text="ML predikcija")
        self.notebook.add(self.weather_frame, text="Meteo stanica")
        self.notebook.add(self.visualization_frame, text="Plastenik")

        self._build_dashboard_tab()
        self._build_montecarlo_tab()
        self._build_energy_tab()
        self._build_ml_tab()
        self._build_weather_tab()
        self._build_visualization_tab()

    # Gradi glavnu karticu sa senzorima, aktuatorima, energijom i ručnim komandama.
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
        for idx, label in enumerate(["pump1", "pump2", "fan", "greenhouse_open", "alarm"]):
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

        self.safe_zone_label = ttk.Label(self.dashboard_frame, text="Sigurna zona: ---")
        self.safe_zone_label.pack(side=tk.TOP, anchor=tk.W, padx=12, pady=4)

        log_frame = ttk.LabelFrame(self.dashboard_frame, text="Log")
        log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.log_text = tk.Text(log_frame, height=12, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    # Gradi unos broja scenarija, gumb i prostor za Monte Carlo rezultate.
    def _build_montecarlo_tab(self):
        controls = ttk.Frame(self.montecarlo_frame)
        controls.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        ttk.Label(controls, text="Broj simulacija:").pack(side=tk.LEFT, padx=4)
        self.monte_input = tk.IntVar(value=500)
        ttk.Entry(controls, textvariable=self.monte_input, width=8).pack(side=tk.LEFT, padx=4)
        ttk.Button(controls, text="Pokreni Monte Carlo", command=self.run_monte_carlo).pack(side=tk.LEFT, padx=4)

        self.monte_results = tk.Text(self.montecarlo_frame, height=10, state=tk.DISABLED)
        self.monte_results.pack(fill=tk.X, padx=8, pady=8)

        self.monte_fig = Figure(figsize=(8, 5), dpi=100)
        self.monte_canvas = FigureCanvasTkAgg(self.monte_fig, master=self.montecarlo_frame)
        self.monte_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    # Priprema tekstualni energetski izvještaj i Matplotlib graf potrošnje.
    def _build_energy_tab(self):
        self.energy_report = ttk.LabelFrame(self.energy_frame, text="Energetski izvještaj")
        self.energy_report.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        self.energy_labels = {}
        for idx, label in enumerate(["consumption", "production", "battery_wh", "runtime_h", "net_balance_wh", "battery_percentage", "solar_coverage_pct"]):
            ttk.Label(self.energy_report, text=label.replace("_", " ") + ":").grid(row=idx // 2, column=0 if idx % 2 == 0 else 2, sticky=tk.W, padx=4, pady=2)
            self.energy_labels[label] = ttk.Label(self.energy_report, text="---")
            self.energy_labels[label].grid(row=idx // 2, column=1 if idx % 2 == 0 else 3, sticky=tk.W, padx=4, pady=2)

        self.energy_fig = Figure(figsize=(8, 4), dpi=100)
        self.energy_canvas = FigureCanvasTkAgg(self.energy_fig, master=self.energy_frame)
        self.energy_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    # Stvara prikaz vanjskih meteoroloških vrijednosti i njihovih grafikona.
    def _build_weather_tab(self):
        weather_panel = ttk.LabelFrame(self.weather_frame, text="Podaci meteorološke stanice")
        weather_panel.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        self.weather_labels = {}
        for idx, label in enumerate(["outdoor_temperature", "outdoor_humidity", "wind_speed", "rainfall_mm", "weather_signal"]):
            ttk.Label(weather_panel, text=label.replace("_", " ") + ":").grid(row=idx, column=0, sticky=tk.W, padx=4, pady=2)
            self.weather_labels[label] = ttk.Label(weather_panel, text="---")
            self.weather_labels[label].grid(row=idx, column=1, sticky=tk.W, padx=4, pady=2)

        self.weather_fig = Figure(figsize=(8, 4), dpi=100)
        self.weather_canvas = FigureCanvasTkAgg(self.weather_fig, master=self.weather_frame)
        self.weather_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    # Gradi karticu s metrikama modela, predikcijom i preporukom akcije.
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

    # Priprema Canvas na kojem se crta pojednostavljeni digitalni plastenik.
    def _build_visualization_tab(self):
        canvas_frame = ttk.LabelFrame(self.visualization_frame, text="Skica 2D plastenika")
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.greenhouse_canvas = tk.Canvas(canvas_frame, width=760, height=380, bg="#f7f9f3", highlightthickness=0)
        self.greenhouse_canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self._draw_greenhouse_base()

    # Crta nepomičnu konstrukciju plastenika koja je osnova animiranog prikaza.
    def _draw_greenhouse_base(self):
        self.greenhouse_canvas.delete("all")
        self.greenhouse_canvas.create_rectangle(70, 90, 690, 330, fill="#e7f2e7", outline="#4a6a4a", width=4)
        self.greenhouse_canvas.create_polygon(70, 90, 380, 20, 690, 90, fill="#d5ead5", outline="#4a6a4a", width=4)
        self.greenhouse_canvas.create_rectangle(90, 100, 240, 280, fill="#dbe7d8", outline="#4a6a4a", width=2, tags="soil_bed")
        self.greenhouse_canvas.create_text(165, 290, text="Gredica", font=("Helvetica", 10, "bold"), fill="#2f4b2c")
        self.greenhouse_canvas.create_rectangle(310, 100, 390, 180, fill="#f9f0b9", outline="#c2aa4a", width=2, tags="led")
        self.greenhouse_canvas.create_text(350, 140, text="LED", font=("Helvetica", 10, "bold"), tags="led_label")
        self.greenhouse_canvas.create_oval(450, 110, 520, 170, fill="#b3defd", outline="#3b80c1", width=2, tags="fan")
        self.greenhouse_canvas.create_text(485, 140, text="Ventilator", font=("Helvetica", 10, "bold"), tags="fan_label")
        self.greenhouse_canvas.create_rectangle(90, 300, 160, 330, fill="#94c973", outline="#5d803f", width=2, tags="pump1")
        self.greenhouse_canvas.create_text(125, 315, text="Pumpa 1", font=("Helvetica", 9), tags="pump1_label")
        self.greenhouse_canvas.create_rectangle(170, 300, 240, 330, fill="#94c973", outline="#5d803f", width=2, tags="pump2")
        self.greenhouse_canvas.create_text(205, 315, text="Pumpa 2", font=("Helvetica", 9), tags="pump2_label")
        self.greenhouse_canvas.create_rectangle(520, 230, 640, 310, fill="#f1d8b5", outline="#9f7b3b", width=2, tags="door")
        self.greenhouse_canvas.create_text(580, 270, text="Ulaz/otvoren", font=("Helvetica", 9), tags="door_label")
        self.greenhouse_canvas.create_text(380, 40, text="Pametni plastenik", font=("Helvetica", 14, "bold"), fill="#2d5740")
        self.greenhouse_canvas.create_text(380, 360, text="Za prikaz upaljenih sustava i vremena", font=("Helvetica", 9), fill="#2f4b2c")

    # Mijenja boje i oznake digitalnog prikaza prema trenutnim aktuatorima.
    def _update_visualization(self):
        self._draw_greenhouse_base()
        if self.actuators.pump1:
            self.greenhouse_canvas.itemconfig("pump1", fill="#4caf50")
        if self.actuators.pump2:
            self.greenhouse_canvas.itemconfig("pump2", fill="#4caf50")
        if self.actuators.fan:
            self.greenhouse_canvas.itemconfig("fan", fill="#42a5f5")
        if self.actuators.led:
            self.greenhouse_canvas.itemconfig("led", fill="#fdd835")
        if self.actuators.greenhouse_open:
            self.greenhouse_canvas.itemconfig("door", fill="#aed581")
        if self.actuators.alarm:
            self.greenhouse_canvas.create_text(380, 200, text="ALARM! / Neispravne vrijednosti", font=("Helvetica", 11, "bold"), fill="#c0392b", tags="alarm_text")
        weather_text = "Vani: " + (self.weather_station.current_values().get("weather_signal", "---") if self.weather_station else "---")
        self.greenhouse_canvas.create_text(380, 60, text=weather_text, font=("Helvetica", 10, "italic"), fill="#39554b", tags="weather_text")

    # Zakazuje periodično osvježavanje Tkinter sučelja bez blokiranja glavne niti.
    def _refresh_loop(self):
        self._update_dashboard()
        self.root.after(1500, self._refresh_loop)

    # Čita modele i osvježava sve tekstualne senzore, aktuatore i energiju.
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

        safe_zone = (
            18 <= sensor_values["temperature"] <= 30
            and 30 <= sensor_values["soil_moisture"] <= 70
            and 300 <= sensor_values["co2"] <= 800
            and 5.8 <= sensor_values["ph"] <= 7.0
            and 80 <= sensor_values["npk"] <= 200
        )
        self.safe_zone_label.config(text=f"Sigurna zona: {'DA' if safe_zone else 'NE'}")

        energy_report = self.energy_model.current_report()
        for key, label in self.energy_labels.items():
            label.config(text=str(energy_report[key]))

        self._update_energy_plot(energy_report)
        self._update_ml_tab()
        self._update_weather_tab()
        self._update_visualization()
        self._write_log_to_csv(sensor_values, actuator_state, energy_report["consumption"])

    # Dodaje novo energetsko mjerenje u povijest i ponovno crta trendove.
    def _update_energy_plot(self, energy_report):
        self.energy_fig.clear()
        ax1 = self.energy_fig.add_subplot(121)
        labels = ["ESP32", "Mega", "Sensors", "Pump1", "Pump2", "Fan", "Motor"]
        power = [
            self.energy_model.esp32_power,
            self.energy_model.arduino_power,
            self.energy_model.sensors_power,
            self.energy_model.pump1_power if self.actuators.pump1 else 0,
            self.energy_model.pump2_power if self.actuators.pump2 else 0,
            self.energy_model.fan_power if self.actuators.fan else 0,
            self.energy_model.motor_power if self.actuators.greenhouse_open else 0,
        ]
        ax1.bar(labels, power, color="#4C78A8", edgecolor="black", alpha=0.9)
        ax1.set_title("Potrošnja po komponentama (W)")
        ax1.set_ylabel("W")
        ax1.tick_params(axis='x', rotation=20)

        ax2 = self.energy_fig.add_subplot(122)
        ax2.bar(["Potrošnja", "Proizvodnja", "Neto bilans"], [energy_report["consumption"], energy_report["production"], energy_report["net_balance_wh"]], color=["#F58518", "#54A24B", "#E45756"], edgecolor="black", alpha=0.9)
        ax2.set_title("Energetski bilans")
        ax2.set_ylabel("Wh")

        self.energy_fig.tight_layout()
        self.energy_canvas.draw()

    # Osvježava meteorološke oznake i grafove najnovijim vanjskim stanjem.
    def _update_weather_tab(self):
        if not self.weather_station:
            return
        values = self.weather_station.current_values()
        for key, label in self.weather_labels.items():
            label.config(text=str(values[key]))

        self.weather_fig.clear()
        ax1 = self.weather_fig.add_subplot(121)
        ax1.plot(["Temp vani", "Vjetar", "Kisa"], [values["outdoor_temperature"], values["wind_speed"], values["rainfall_mm"]], marker="o", color="#2e86de")
        ax1.set_title("Meteo trend")
        ax1.set_ylabel("Vrijednost")

        ax2 = self.weather_fig.add_subplot(122)
        ax2.bar(["Temp", "Vlaga", "Vjetar", "Kiša"], [values["outdoor_temperature"], values["outdoor_humidity"], values["wind_speed"], values["rainfall_mm"]], color=["#f39c12", "#16a085", "#8e44ad", "#3498db"])
        ax2.set_title("Aktuelni meteopodaci")
        ax2.set_ylabel("Vrijednost")
        self.weather_fig.tight_layout()
        self.weather_canvas.draw()

    # Prikazuje aktualnu točnost i ostale informacije treniranog ML modela.
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

    # Spaja unutarnje i vanjske ulaze te od modela traži trenutnu predikciju.
    def _predict_current(self):
        current = self.sensors.current_values()
        prediction = self.ml_model.predict(current)
        label = "Potrebna navodnjavanja" if prediction["irrigation_needed"] else "Nema potrebe za navodnjavanjem"
        ventilation = "Potrebna ventilacija" if prediction["ventilation_needed"] else "Ventilacija nije potrebna"
        self.prediction_label.config(text=f"{label} | {ventilation}")
        self._update_recommendation(current, prediction)
        save_prediction_event(current, prediction, self.recommendation_label.cget("text"))
        self.add_log("ESP32: pokrenuta ML predikcija na trenutnim podacima")

    # Pretvara ML odluke u korisničku preporuku i sprema događaj u CSV.
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

    # Pokreće Monte Carlo iz desktop forme, prikazuje sažetak i sprema izvještaj.
    def run_monte_carlo(self):
        simulations = max(10, self.monte_input.get())
        summary, df = run_monte_carlo(simulations)
        self.monte_results.config(state=tk.NORMAL)
        self.monte_results.delete("1.0", tk.END)
        self.monte_results.insert(tk.END, f"Simulacija: {simulations}\n")
        self.monte_results.insert(tk.END, f"Pumpa 1 uključena: {summary['pump1_count']} puta\n")
        self.monte_results.insert(tk.END, f"Pumpa 2 uključena: {summary['pump2_count']} puta\n")
        self.monte_results.insert(tk.END, f"Ventilator uključen: {summary['fan_count']} puta\n")
        self.monte_results.insert(tk.END, f"LED uključen: {summary['led_count']} puta\n")
        self.monte_results.insert(tk.END, f"Otvaranje plastenika: {summary['open_greenhouse_count']} puta\n")
        self.monte_results.insert(tk.END, f"Alarm: {summary['alarm_count']} puta\n")
        self.monte_results.insert(tk.END, f"Sigurna zona ratio: {summary['safe_zone_ratio']:.2f}\n")
        self.monte_results.insert(tk.END, f"Vrijeme signala: {summary['weather_counts']}\n")
        self.monte_results.insert(tk.END, f"Prosječna temperatura: {summary['avg_temperature']:.2f} °C\n")
        self.monte_results.insert(tk.END, f"Prosječna vlažnost zemljišta: {summary['avg_soil_moisture']:.2f}%\n")
        self.monte_results.insert(tk.END, f"Prosječni CO2: {summary['avg_co2']:.1f} ppm\n")
        self.monte_results.insert(tk.END, f"Kritično niska vlaga: {summary['critical_low_moisture_count']} koraka\n")
        self.monte_results.insert(tk.END, f"Kritično visoka temperatura: {summary['critical_high_temperature_count']} koraka\n")
        self.monte_results.insert(tk.END, f"Kritično visoki CO2: {summary['critical_high_co2_count']} koraka\n")
        self.monte_results.config(state=tk.DISABLED)
        self.monte_last_trend = summary.get("trend_series", self.monte_last_trend)
        self._plot_montecarlo(df)
        save_monte_carlo_report(summary, df)

    # Iz Monte Carlo DataFramea crta histograme, aktivacije i vremenske trendove.
    def _plot_montecarlo(self, df):
        self.monte_fig.clear()

        ax1 = self.monte_fig.add_subplot(221)
        ax1.hist(df["temperature"], bins=20, color="#2ecc71", alpha=0.75)
        ax1.set_title("Temperatura")
        ax1.set_xlabel("°C")
        ax1.set_ylabel("Broj koraka")

        ax2 = self.monte_fig.add_subplot(222)
        ax2.hist(df["soil_moisture"], bins=20, color="#3498db", alpha=0.75)
        ax2.set_title("Vlažnost zemljišta")
        ax2.set_xlabel("%")
        ax2.set_ylabel("Broj koraka")

        ax3 = self.monte_fig.add_subplot(223)
        action_counts = [df["pump1"].sum(), df["pump2"].sum(), df["fan"].sum(), df["open_greenhouse"].sum(), df["alarm"].sum()]
        ax3.bar(["Pumpa 1", "Pumpa 2", "Ventilator", "Plastenik", "Alarm"], action_counts, color=["#e67e22", "#f39c12", "#9b59b6", "#1abc9c", "#e74c3c"], edgecolor="black", alpha=0.9)
        ax3.set_title("Broj aktivacija akcija")
        ax3.set_ylabel("Ukupan broj")
        ax3.tick_params(axis='x', rotation=15)
        ax3.set_title("Broj aktivacija akcija")
        ax3.set_ylabel("Ukupan broj")

        ax4 = self.monte_fig.add_subplot(224)
        ax4.plot(list(range(len(self.monte_last_trend["temperature"]))), self.monte_last_trend["temperature"], color="#e74c3c", marker="o", linewidth=1.8, label="Temperatura")
        ax4.plot(list(range(len(self.monte_last_trend["soil_moisture"]))), self.monte_last_trend["soil_moisture"], color="#3498db", marker="s", linewidth=1.8, label="Vlažnost")
        ax4.plot(list(range(len(self.monte_last_trend["co2"]))), self.monte_last_trend["co2"], color="#f1c40f", marker="^", linewidth=1.8, label="CO2")
        ax4.plot(list(range(len(self.monte_last_trend["ph"]))), self.monte_last_trend["ph"], color="#16a085", marker="D", linewidth=1.5, label="pH")
        ax4.plot(list(range(len(self.monte_last_trend["npk"]))), self.monte_last_trend["npk"], color="#8e44ad", marker="P", linewidth=1.5, label="NPK")
        ax4.set_title("Trend kroz vrijeme")
        ax4.set_xlabel("Korak simulacije")
        ax4.set_ylabel("Vrijednost")
        ax4.legend(loc="best")

        self.monte_fig.tight_layout()
        self.monte_canvas.draw()

    # Dodaje vremenski označenu poruku u vidljivi zapis događaja.
    def add_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    # Dodaje trenutno stanje senzora, aktuatora i energije u simulacijski CSV.
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
            actuators["greenhouse_open"],
            actuators["alarm"],
            energy_consumption,
        ]
        file_exists = os.path.exists(self.log_file)
        with open(self.log_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "temperature", "air_humidity", "soil_moisture", "ph", "npk", "co2", "pump1", "pump2", "fan", "greenhouse_open", "alarm", "energy_consumption"])
            writer.writerow(row)
