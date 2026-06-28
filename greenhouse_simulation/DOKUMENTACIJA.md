# Dokumentacija projekta: Pametni plastenik

## 1. Opis projekta
Ovaj projekat predstavlja autonomnu simulaciju pametnog plastenika u Pythonu. Cilj sistema je da samostalno upravlja radom plastenika bez stalnog korisničkog intervencija, koristeći senzore, meteorološku stanicu, ML predikciju i realistične simulacijske modele.

U okviru aplikacije implementirani su:
- senzori za temperaturu, vlažnost zraka, vlagu zemljišta, pH, NPK i CO2
- aktuatori kao što su pumpa, ventilator, otvor plastenika i alarm
- meteorološka stanica sa podacima o temperaturi vani, vlažnosti vani, brzini vjetra i količini kiše
- virtualni kontroleri ESP32 i Arduino Mega
- grafički dashboard u Tkinter-u
- Monte Carlo simulacija sa trend grafovima i sažetkom akcija
- ML predikcija za navodnjavanje, ventilaciju i procjenu uvjeta u plasteniku
- automatsko upravljanje na osnovu senzora, vremena i preporuka
- spremanje rezultata u CSV datoteke

## 2. Struktura projekta
### Root folder
- main.py — ulazna tačka aplikacije. Pokreće kontrolere, pravi GUI i starta simulaciju.
- requirements.txt — lista Python zavisnosti potrebnih za rad projekta.
- README.md — kratka dokumentacija projekta.
- DOKUMENTACIJA.md — detaljna dokumentacija projekta.

### Folder controllers
- controllers/arduino_mega_controller.py — virtualni Arduino Mega kontroler. Očitava senzore, obrađuje vremenske uslove, primjenjuje automatska pravila i upravlja aktuatorima.
- controllers/esp32_controller.py — virtualni ESP32 kontroler. Prima komande iz GUI-a i prenosi ih Arduino kontroleru.
- controllers/__init__.py — Python paket marker.

### Folder simulation
- simulation/sensors.py — model senzora. Generira i ažurira trenutne senzorske vrijednosti.
- simulation/actuators.py — model aktuatora. Čuva stanje pumpe, ventilatora, plastenika i alarma.
- simulation/greenhouse_model.py — osnovni model plastenika. Ažurira stanje sistema na osnovu aktivnih aktuatora.
- simulation/ml_prediction.py — ML model za predikciju potrebe za navodnjavanjem i ventilacijom. Koristi i vanjske vremenske podatke.
- simulation/monte_carlo.py — Monte Carlo simulator. Generira veliki broj scenarija i računa broj aktivacija akcija, kritične uvjete i trendove kroz vrijeme.
- simulation/energy_model.py — energetski model. Izračunava potrošnju, proizvodnju solarnih panela, neto bilans i stanje baterije.
- simulation/reporting.py — modul za spremanje rezultata Monte Carlo-a, predikcija i logova u CSV datoteke.
- simulation/weather_station.py — meteorološka stanica. Simulira vanjsku temperaturu, vlagu, vjetar i kišu.
- simulation/__init__.py — Python paket marker.

### Folder ui
- ui/dashboard.py — Tkinter dashboard. Prikazuje stanje senzora i aktuatora, kontrolere, energiju, Monte Carlo rezultate, ML predikcije i meteorološke podatke.
- ui/__init__.py — Python paket marker.

### Folder data
- data/simulation_log.csv — log svih događaja i stanja sistema kroz vrijeme.
- data/monte_carlo_report.csv — izveštaj sa rezultatima Monte Carlo simulacije.
- data/prediction_events.csv — istorija predikcija sa vremenom, vrijednostima senzora i preporukama.

### Folder tests
- tests/test_controller_logic.py — testovi za automatsku kontrolu, pumpu na osnovu NPK-a i reakciju na vremenske uvjete.
- tests/test_ml_prediction.py — testovi za ML predikciju i ulazne značajke uključujući meteorološke podatke.
- tests/test_reporting.py — testovi za spremanje izvještaja i predikcija u CSV.

## 3. Komponente sistema
### Senzori
Senzori prate sljedeće vrijednosti:
- temperatura unutar plastenika (°C)
- vlažnost zraka (%)
- vlažnost zemljišta (%)
- pH
- NPK
- CO2

### Meteorološka stanica
Meteorološka stanica dodaje vanjske uvjete:
- vanjska temperatura (°C)
- vanjska vlažnost (%)
- brzina vjetra (km/h)
- količina kiše (mm)
- signal vremena: sunny, hot, wind ili rain

### Aktuatori
Aktuatori predstavljaju:
- pumpu 1
- ventilator
- otvor/zatvaranje plastenika
- alarm

### Kontroleri
- ESP32 kontroler prima komande iz GUI-a i prenosi ih Arduino kontroleru.
- Arduino Mega kontroler čita senzore, uzima u obzir vremenske uvjete, primjenjuje automatska pravila i upravlja aktuatorima.

### Dashboard
Dashboard prikazuje:
- trenutne senzore
- stanje aktuatora
- status kontrolera
- energetsku potrošnju i bateriju
- rezultate Monte Carlo simulacije
- ML predikciju i preporuku akcije
- meteorološke podatke i njihove grafove

## 4. Funkcionalnosti
- potpuno autonomno upravljanje plastenikom bez potrebe za ručnim intervencijama
- automatska kontrola na osnovu senzora, NPK-a, temperature, CO2 i vremena
- zatvaranje plastenika kada je jak vjetar ili kada pada kiša
- pumpa se uključuje kada je niska vlaga zemljišta ili NPK premalen
- Monte Carlo analiza sa više stotina simulacija po defaultu
- predikcija potrebe za navodnjavanjem i ventilacijom
- prikaz trendova kroz vrijeme za temperaturu, vlagu, CO2, pH i NPK
- prikaz grafika za energiju, akcije, vremenske uslove i odabrane trendove
- automatsko spremanje rezultata u folderu data

## 5. Tok izvršavanja aplikacije
1. Pokretanjem [main.py](main.py) se kreira folder data ukoliko ne postoji.
2. Inicijaliziraju se senzori, aktuatori, meteorološka stanica, ML model i kontroleri.
3. Pokreće se GUI dashboard.
4. ESP32 i Arduino Mega kontroleri rade u posebnim nitima.
5. Arduino kontroler periodično čita senzore i vremenske podatke te primjenjuje automatska pravila.
6. Ako je potrebno, sistem samostalno uključuje pumpu, ventilator ili zatvara plastenik.
7. Dashboard prikazuje stanje sistema i ažurira grafove.
8. Monte Carlo i ML predikcija se mogu pokrenuti iz interfejsa.
9. Rezultati se automatski spremaju u CSV fajlove.

## 6. Detaljan opis ključnih modula
### controllers/arduino_mega_controller.py
- __init__(...) — inicijalizira senzore, aktuatore, meteorološku stanicu, status i log callback.
- receive_command(...) — prima komandu od ESP32 kontrolera.
- get_status() — vraća trenutni status senzora, aktuatora i zadnje komande.
- run() — petlja kontrolera u kojoj se periodično očitavaju senzori, ažurira meteorološka stanica i primjenjuje kontrolna logika.
- _process_command() — obrađuje ručne komande kao pump1_on, pump1_off, fan_on i sl.
- _apply_control_logic() — automatski odlučuje kada uključiti pumpu, ventilator, plastenik ili alarm.
- apply_recommendation(...) — primjenjuje preporuke direktno na aktuatore, čime sistem djeluje autonomno.
- _apply_recommendation_logic() — generiše automatske preporuke na osnovu trenutnih vrijednosti i primjenjuje ih.
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

### simulation/weather_station.py
- __init__() — postavlja početne vrijednosti za temperaturu, vlagu, vjetar i kišu.
- update() — mijenja meteorološke uvjete u realističnim okvirima.
- current_values() — vraća trenutne meteopodatke i signal vremena.
- _classify_weather() — određuje da li je vrijeme sunny, hot, wind ili rain.

### simulation/actuators.py
- __init__() — inicijalizira sve aktuatorske izlaze na OFF.
- state — svojstvo koje vraća stanje svih aktuatora kao rječnik.

### simulation/greenhouse_model.py
- __init__(...) — povezuje senzore i aktuatore.
- simulate_step() — simulira jedan korak sistema i mijenja senzore na osnovu trenutno uključenih aktuatora.

### simulation/ml_prediction.py
- __init__() — inicijalizira model i trenira ga nad realističnim sintetičkim podacima.
- _generate_dataset() — pravi dataset za treniranje sa temperaturama, vlagom, CO2, pH, NPK i meteorološkim parametrima.
- _train_model() — trenira Random Forest klasifikator za predikciju navodnjavanja i ventilacije.
- predict() — vraća predikciju za trenutne vrijednosti senzora i vremena.

### simulation/monte_carlo.py
- _random_sensor_row() — generira jedinstveni skup senzorskih vrijednosti.
- _apply_rules() — određuje koje akcije treba pokrenuti na osnovu trenutnih podataka.
- _apply_effects() — primjenjuje efekte akcija na vrijednosti senzora za sljedeći korak.
- run_monte_carlo() — pokreće simulaciju kroz više koraka i vraća sažetak, DataFrame i trend serije za temperaturu, vlagu, CO2, pH i NPK.

### simulation/energy_model.py
- __init__(...) — postavlja snage komponenti i stanje baterije.
- compute_consumption() — računa ukupnu potrošnju.
- compute_solar_production() — računa proizvodnju solarnih panela.
- update_battery() — ažurira stanje baterije na osnovu proizvodnje i potrošnje.
- estimate_runtime() — procjenjuje koliko sati sistem može raditi na trenutnoj bateriji.
- current_report() — vraća kompletan energetski izvještaj sa neto bilansom, postotkom baterije i pokrivenošću solarnom energijom.

### simulation/reporting.py
- save_monte_carlo_report() — sprema rezultate Monte Carlo simulacije u CSV.
- save_prediction_event() — sprema predikcije sa vremenom, senzorskim vrijednostima i preporukom akcije.

### ui/dashboard.py
- __init__(...) — postavlja kontrolere, model, meteorološku stanicu i grafički interfejs.
- _build_ui() — gradi sve tabove: Dashboard, Monte Carlo, Energetska simulacija, ML predikcija i Meteo stanica.
- _build_dashboard_tab() — prikazuje senzore, aktuatore i ručne komande.
- _build_montecarlo_tab() — prikazuje unos za broj simulacija, rezultate i grafike.
- _build_energy_tab() — prikazuje energetski izvještaj i grafike potrošnje.
- _build_ml_tab() — prikazuje ML statistiku i preporuku akcije.
- _build_weather_tab() — prikazuje podatke meteorološke stanice i odgovarajuće grafove.
- _refresh_loop() — periodično osvježava dashboard.
- _update_dashboard() — ažurira sve widgete na ekranu.
- _predict_current() — pokreće ML predikciju za trenutne vrijednosti.
- _update_recommendation() — formira preporuku akcije.
- run_monte_carlo() — pokreće Monte Carlo simulaciju i sprema rezultate.
- _plot_montecarlo() — prikazuje više grafika: distribucije i trendove.
- add_log() — dodaje poruku u log.
- _write_log_to_csv() — zapisuje trenutni status u CSV log.

## 7. Rezultati i izvještaji
Aplikacija automatski sprema sljedeće datoteke:
- data/monte_carlo_report.csv
- data/prediction_events.csv
- data/simulation_log.csv

Pored toga, dashboard prikazuje:
- trendove temperature, vlage, CO2, pH i NPK kroz vrijeme
- broj aktivacija pumpi, ventilatora, plastenika i alarma
- energetski bilans i stanje baterije
- meteorološke grafove za vanjsku temperaturu, vjetar i kišu

## 8. Kako pokrenuti projekt
1. Otvorite terminal u folderu projekta.
2. Instalirajte zavisnosti:
   `pip install -r requirements.txt`
3. Pokrenite aplikaciju:
   `python main.py`

## 9. Testovi
Projekt uključuje testove za kontroler, ML predikciju, reporting i meteorološku logiku:
- tests/test_controller_logic.py
- tests/test_ml_prediction.py
- tests/test_reporting.py

## 10. Napomena
Ovo je softverska simulacija pametnog plastenika koja djeluje autonomno i koristi realistične sintetičke podatke kako bi prikazala kako bi takav sistem mogao funkcionirati u praksi.
