# Dokumentacija projekta: Pametni plastenik

## 1. Opis projekta
Ovaj projekat predstavlja simulaciju pametnog plastenika u Pythonu. U okviru aplikacije implementirani su:
- senzori za temperaturu, vlažnost zraka, vlagu zemljišta, pH, NPK i CO2
- aktuatori kao što su pumpa, ventilator, LED, otvor plastenika i alarm
- virtualni kontroleri ESP32 i Arduino Mega
- grafički dashboard u Tkinter-u
- Monte Carlo simulacija
- ML predikcija za navodnjavanje i ventilaciju
- spremanje rezultata u CSV datoteke

## 2. Struktura projekta
### Root folder
- main.py — ulazna tačka aplikacije. Pokreće kontrolere, pravi GUI i starta simulaciju.
- requirements.txt — liste svih Python zavisnosti potrebnih za rad projekta.
- README.md — kratka dokumentacija projekta.
- DOKUMENTACIJA.md — detaljna dokumentacija projekta.

### Folder controllers
- controllers/arduino_mega_controller.py — virtualni Arduino Mega kontroler. Očitava senzore, primjenjuje automatska pravila i upravlja aktuatorima.
- controllers/esp32_controller.py — virtualni ESP32 kontroler. Prima komande iz GUI-a i prenosi ih Arduino kontroleru.
- controllers/__init__.py — Python paket marker.

### Folder simulation
- simulation/sensors.py — model senzora. Generira i ažurira trenutne senzorske vrijednosti.
- simulation/actuators.py — model aktuatora. Čuva stanje pumpe, ventilatora, LED-a, plastenika i alarma.
- simulation/greenhouse_model.py — osnovni model plastenika. Ažurira stanje sistema na osnovu aktivnih aktuatora.
- simulation/ml_prediction.py — ML model za predikciju potrebe za navodnjavanjem i ventilacijom.
- simulation/monte_carlo.py — Monte Carlo simulator. Generira veliki broj scenarija i računa koliko puta se događaju određene akcije.
- simulation/energy_model.py — energetski model. Izračunava potrošnju, proizvodnju solarnih panela i stanje baterije.
- simulation/reporting.py — modul za spremanje rezultata Monte Carlo-a i predikcija u CSV datoteke.
- simulation/__init__.py — Python paket marker.

### Folder ui
- ui/dashboard.py — Tkinter dashboard. Prikazuje stanje senzora i aktuatora, kontrolere, energiju, Monte Carlo rezultate i ML predikcije.
- ui/__init__.py — Python paket marker.

### Folder data
- data/simulation_log.csv — log svih događaja i stanja sistema kroz vrijeme.
- data/monte_carlo_report.csv — izveštaj sa rezultatima Monte Carlo simulacije.
- data/prediction_events.csv — istorija predikcija sa vremenom, vrijednostima senzora i preporukama.

### Folder tests
- tests/test_controller_logic.py — test koji provjerava da ručno isključivanje pumpe ne bude prepisano automatskom logikom.
- tests/test_ml_prediction.py — test koji provjerava ML predikciju i njene ulazne značajke.
- tests/test_reporting.py — test koji provjerava da se izvještaji i predikcije pravilno spremaju u CSV.

## 3. Komponente sistema
### Senzori
Senzori prate sljedeće vrijednosti:
- temperatura (°C)
- vlažnost zraka (%)
- vlažnost zemljišta (%)
- pH
- NPK
- CO2

### Aktuatori
Aktuatori predstavljaju:
- pumpu 1
- pumpu 2
- ventilator
- LED
- otvor/zatvaranje plastenika
- alarm

### Kontroleri
- ESP32 kontroler prima komande iz GUI-a i prenosi ih Arduino kontroleru.
- Arduino Mega kontroler čita senzore, primjenjuje automatska pravila i upravlja aktuatorima.

### Dashboard
Dashboard prikazuje:
- trenutne senzore
- stanje aktuatora
- status kontrolera
- energetsku potrošnju
- rezultate Monte Carlo simulacije
- ML predikciju i preporuku akcije

## 4. Funkcionalnosti
- rukovno upravljanje aktuatorima
- automatska kontrola na osnovu senzora
- Monte Carlo analiza sa 500 simulacija po defaultu
- predikcija potrebe za navodnjavanjem i ventilacijom
- automatsko spremanje rezultata u folderu data

## 5. Rezultati i izvještaji
Aplikacija automatski sprema sljedeće datoteke:
- data/monte_carlo_report.csv
- data/prediction_events.csv
- data/simulation_log.csv

## 6. Kako pokrenuti projekt
1. Otvorite terminal u folderu projekta.
2. Instalirajte zavisnosti:
   `pip install -r requirements.txt`
3. Pokrenite aplikaciju:
   `python main.py`

## 7. Testovi
Projekt uključuje testove za kontroler, ML predikciju i reporting:
- tests/test_controller_logic.py
- tests/test_ml_prediction.py
- tests/test_reporting.py

## 8. Napomena
Ovo je softverska simulacija i ne koristi stvarni hardver.
