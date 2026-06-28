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
- prikaz preporuke akcije na osnovu trenutnih vrijednosti

## 5. Tok izvršavanja aplikacije
1. Pokretanjem [main.py](main.py) se kreira folder data ukoliko ne postoji.
2. Inicijaliziraju se senzori, aktuatori, ML model i kontroleri.
3. Pokreće se GUI dashboard.
4. ESP32 i Arduino Mega kontroleri rade u posebnim nitima.
5. Korisnik može ručno slati komande kroz dashboard.
6. Arduino kontroler periodično čita senzore i primjenjuje automatska pravila.
7. Dashboard prikazuje stanje sistema i ažurira grafove.
8. Monte Carlo i ML predikcija se mogu pokrenuti iz interfejsa.
9. Rezultati se automatski spremaju u CSV fajlove.

## 6. Detaljan opis ključnih modula
### controllers/arduino_mega_controller.py
- __init__(...) — inicijalizira senzore, aktuatore, status i log callback.
- receive_command(...) — prima komandu od ESP32 kontrolera.
- get_status() — vraća trenutni status senzora, aktuatora i zadnje komande.
- run() — petlja kontrolera u kojoj se periodično očitavaju senzori i primjenjuje kontrolna logika.
- _process_command() — obrađuje ručne komande kao pump1_on, pump1_off, fan_on i sl.
- _apply_control_logic() — automatski odlučuje kada uključiti pumpu, ventilator, plastenik ili alarm.
- _log(...) — šalje poruke u log ili ispisuje ih u konzolu.

### controllers/esp32_controller.py
- __init__(...) — čuva referencu na Arduino kontroler i status sistema.
- send_command(...) — prima komandu iz GUI-a i prosljeđuje je Arduino-u.
- receive_state(...) — prima stanje sistema i vraća ga dashboard-u.
- run() — periodično čita stanje od Arduino kontrolera.
- _log(...) — beleži događaje.

### simulation/sensors.py
- __init__() — postavlja početne vrijednosti senzora.
- update() — nasumično mijenja senzorske vrijednosti u realističnim granicama.
- current_values() — vraća trenutne vrijednosti kao rječnik.
- _clamp(...) — ograničava vrijednosti u dozvoljeni raspon.

### simulation/actuators.py
- __init__() — inicijalizira sve aktuatorske izlaze na OFF.
- state — svojstvo koje vraća stanje svih aktuatora kao rječnik.

### simulation/greenhouse_model.py
- __init__(...) — povezuje senzore i aktuatore.
- simulate_step() — simulira jedan korak sistema i mijenja senzore na osnovu trenutno uključenih aktuatora.

### simulation/ml_prediction.py
- __init__() — inicijalizira model i trenira ga nad sintetičkim podacima.
- _generate_dataset() — pravi sintetičke podatke za treniranje.
- _train_model() — trenira Random Forest klasifikator za predikciju navodnjavanja.
- predict() — vraća predikciju za trenutne vrijednosti senzora.

### simulation/monte_carlo.py
- _random_sensor_row() — generira jedinstveni skup senzorskih vrijednosti.
- _apply_rules() — određuje koje akcije treba pokrenuti na osnovu trenutnih podataka.
- _apply_effects() — primjenjuje efekte akcija na vrijednosti senzora za sljedeći korak.
- run_monte_carlo() — pokreće simulaciju kroz više koraka i vraća sažetak plus DataFrame.

### simulation/energy_model.py
- __init__(...) — postavlja snage komponenti i stanje baterije.
- compute_consumption() — računa ukupnu potrošnju.
- compute_solar_production() — računa proizvodnju solarnih panela.
- update_battery() — ažurira stanje baterije na osnovu proizvodnje i potrošnje.
- estimate_runtime() — procjenjuje koliko sati sistem može raditi na trenutnoj bateriji.
- current_report() — vraća kompletan energetski izvještaj.

### simulation/reporting.py
- save_monte_carlo_report() — sprema rezultate Monte Carlo simulacije u CSV.
- save_prediction_event() — sprema predikcije sa vremenom, senzorskim vrijednostima i preporukom akcije.

### ui/dashboard.py
- __init__(...) — postavlja kontrolere, model i grafički interfejs.
- _build_ui() — gradi sve tabove: Dashboard, Monte Carlo, Energetska simulacija i ML predikcija.
- _build_dashboard_tab() — prikazuje senzore, aktuatore i ručne komande.
- _build_montecarlo_tab() — prikazuje unos za broj simulacija i rezultate.
- _build_energy_tab() — prikazuje energetski izvještaj.
- _build_ml_tab() — prikazuje ML statistiku i preporuku akcije.
- _refresh_loop() — periodično osvježava dashboard.
- _update_dashboard() — ažurira sve widgete na ekranu.
- _predict_current() — pokreće ML predikciju za trenutne vrijednosti.
- _update_recommendation() — formira preporuku akcije.
- run_monte_carlo() — pokreće Monte Carlo simulaciju i sprema rezultate.
- _plot_montecarlo() — prikazuje histogram temperature.
- add_log() — dodaje poruku u log.
- _write_log_to_csv() — zapisuje trenutni status u CSV log.

## 7. Rezultati i izvještaji
Aplikacija automatski sprema sljedeće datoteke:
- data/monte_carlo_report.csv
- data/prediction_events.csv
- data/simulation_log.csv

## 8. Kako pokrenuti projekt
1. Otvorite terminal u folderu projekta.
2. Instalirajte zavisnosti:
   `pip install -r requirements.txt`
3. Pokrenite aplikaciju:
   `python main.py`

## 9. Testovi
Projekt uključuje testove za kontroler, ML predikciju i reporting:
- tests/test_controller_logic.py
- tests/test_ml_prediction.py
- tests/test_reporting.py

## 10. Napomena
Ovo je softverska simulacija i ne koristi stvarni hardver.
