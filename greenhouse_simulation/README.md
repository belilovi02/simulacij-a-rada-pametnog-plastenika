# Pametni plastenik - Simulacija

Ovaj projekt je Python desktop aplikacija koja simulira pametni plastenik koristeći softverski model za senzore, aktuatore, dva virtualna kontrolera i analize. Ne koristi stvarni Arduino ili ESP32 hardver; umjesto toga, oba kontrolera rade unutar same aplikacije i komuniciraju preko Python objekata.

## Šta ovaj projekat sadrži
- simulaciju senzora i aktuatora za plastenik
- dva virtualna kontrolera: ESP32 i Arduino Mega
- grafički interfejs baziran na Tkinteru
- Monte Carlo analizu ponašanja sistema
- energetsku simulaciju sa solarniim panelima i baterijom
- jednostavan ML model za predikciju navodnjavanja i ventilacije
- logovanje podataka u CSV fajl

## Komponente i kako rade
- Senzori: prate temperaturu, vlažnost zraka, vlagu zemljišta, pH, NPK i CO2.
- Aktuatori: predstavljaju pumpu, ventilator, LED, otvor plastenika i alarm.
- ESP32 kontroler: prima komande iz GUI-a i prosljeđuje ih Arduino kontroleru.
- Arduino Mega kontroler: čita stanje senzora, primjenjuje automatsku logiku i upravlja aktuatorima.
- Dashboard: prikazuje senzore, aktuatore, stanje kontrolera, energiju i rezultate Monte Carlo/ML.
- Monte Carlo: simulira veliki broj slučajnih scenarija i prikazuje koliko puta se nešto dogodilo.
- ML predikcija: procjenjuje treba li navodnjavanje ili ventilacija na osnovu trenutnih vrijednosti.
- Reporting: sprema rezultate Monte Carlo-a i sve predikcije sa vremenom u CSV datoteke u folderu data.

## Cilj projekta
- simulirati pametni plastenik
- prikazati paralelni rad dva kontrolera (ESP32 i Arduino Mega)
- simulirati senzore i aktuatorske izlaze
- provesti Monte Carlo analizu
- izračunati energetsku potrošnju s dvije solarne ploče
- trenirati jednostavan ML model za predikciju navodnjavanja/ventilacije

## Zašto simulacija
Umjesto korištenja Tinkercada i fizičkog hardvera, aplikacija izvodi sve funkcije lokalno u Pythonu. To omogućuje brzu provjeru pravila, grafova i dodavanje analize bez dodatnog hardverskog sloja.

## Uloga kontrolera
- ESP32Controller simulira komunikacijski modul, prima komande iz GUI-ja i prosljeđuje ih Arduino Mega kontroleru.
- ArduinoMegaController simulira očitavanje senzora, primjenu automatske logike i upravljanje aktuatorima.

## Senzori
Simulirani senzori uključuju:
- temperaturu zraka (°C)
- vlažnost zraka (%)
- vlažnost zemljišta (%)
- pH vrijednost
- NPK vrijednost
- intenzitet svjetlosti (lux)

## Aktuatori
Simulirani ON/OFF prikaz su za:
- pumpu 1
- pumpu 2
- ventilator
- LED svjetlo
- otvaranje / zatvaranje plastenika
- alarm

## Monte Carlo analiza
Monte Carlo modul nasumično generira senzorski dataset i računa koliko puta se uključuju pumpe, ventilator, otvaranje plastenika i alarm.

## Energetska simulacija
Energetski model računa:
- ESP32: 0.5 W
- Arduino Mega: 0.4 W
- senzori: 0.5 W
- pumpa 1/2: 12 W
- ventilator: 8 W
- LED: 10 W
- motor: 15 W
- solarne ploče: 20 W + 20 W
- baterija: 12 V, 20 Ah

## ML predikcija
Random Forest model trenira se na sintetičkom datasetu koji koristi senzorske vrijednosti za klasifikaciju:
- irrigation_needed
- ventilation_needed

## Spremanje rezultata
Aplikacija automatski zapisuje rezultate u folderu data:
- monte_carlo_report.csv - rezultat Monte Carlo simulacije za 500 pokretanja po defaultu, sa svim generiranim koracima i vremenskom oznakom
- prediction_events.csv - povijest predikcija sa vremenom, senzorskim vrijednostima i preporukama
- simulation_log.csv - tok događaja i stanja aktuatora kroz rad aplikacije

## Kako koristiti
1. Pokrenite aplikaciju sa `python main.py`.
2. U kartici Monte Carlo unesite broj simulacija ili ostavite 500.
3. Kliknite na „Pokreni Monte Carlo“.
4. Rezultati se automatski spremaju u folder data.
5. U kartici ML predikcija kliknite „Predvidi“ i svaka predikcija se zapisa u CSV datoteku sa vremenom.

## Instalacija
1. Otvorite terminal u direktoriju greenhouse_simulation
2. Instalirajte zavisnosti:
   pip install -r requirements.txt
3. Pokrenite aplikaciju:
   python main.py

## Struktura projekta
- main.py - ulazna tačka aplikacije
- simulation/reporting.py - spremanje izvještaja i predikcija
- controllers/esp32_controller.py - virtualni ESP32 kontroler
- controllers/arduino_mega_controller.py - virtualni Arduino Mega kontroler
- simulation/sensors.py - model senzora
- simulation/actuators.py - model aktuatora
- simulation/greenhouse_model.py - osnovni model plastenika
- simulation/monte_carlo.py - Monte Carlo analiza
- simulation/energy_model.py - energetska simulacija
- simulation/ml_prediction.py - ML predikcija
- ui/dashboard.py - Tkinter dashboard
- data/simulation_log.csv - CSV log podataka
