# Modeliranje, simulacija i predikcija mikroklimatskih uslova u pametnom plasteniku primjenom različitih metoda

## 1. Uvod

Ovaj projekt predstavlja softverski model pametnog plastenika koji objedinjuje modeliranje mikroklime, autonomno upravljanje, ručnu kontrolu, energetsku analizu, Monte Carlo metodu, linearnu simulaciju i predikciju pomoću Random Forest algoritma.

Sustav ne zahtijeva fizički Arduino ili ESP32 uređaj. Senzori, aktuatori, kontroleri i okoliš predstavljeni su Python objektima. Time je omogućeno ispitivanje ponašanja plastenika u velikom broju uvjeta bez rizika za stvarne biljke i opremu.

Glavna web-aplikacija prikazuje:

- temperaturu i vlagu zraka;
- vlagu tla, pH, NPK i koncentraciju CO₂;
- vanjsku temperaturu, vlagu, vjetar, oborine i vremenski signal;
- dvije odvojene pumpe za vodu i zasebnu NPK pumpu;
- ventilator, otvor plastenika i alarm;
- potrošnju, solarnu proizvodnju i stanje baterije;
- digitalni prikaz plastenika;
- prognozu za sljedeća 24 sata;
- deset grafikona trenutnog rada;
- rezultate Monte Carlo i linearne simulacije;
- rezultate Random Forest modela;
- izvoz prikupljenih vrijednosti u CSV.

## 2. Ciljevi projekta

Glavni cilj je pokazati kako se različite računalne metode mogu koristiti za analizu istog sustava.

1. **Modeliranje** opisuje senzore, aktuatore, vremenske uvjete i njihove međusobne utjecaje.
2. **Autonomno upravljanje** uključuje opremu kada vrijednosti prijeđu definirane pragove.
3. **Linearna simulacija** ispituje reakciju sustava na kontroliranu promjenu od početnog do završnog stanja.
4. **Monte Carlo metoda** ispituje tisuće nasumičnih scenarija i procjenjuje stabilnost sustava.
5. **Random Forest** iz podataka predviđa potrebu za navodnjavanjem i ventilacijom.
6. **Energetski model** procjenjuje potrošnju uređaja, solarnu proizvodnju i autonomiju baterije.

## 3. Arhitektura sustava

Sustav je podijeljen u pet logičkih slojeva:

1. **Sloj modela** – senzori, aktuatori, vrijeme, mikroklima i energija.
2. **Upravljački sloj** – Arduino Mega donosi odluke, a ESP32 prenosi naredbe i stanje.
3. **Analitički sloj** – linearna simulacija, Monte Carlo i Random Forest.
4. **Aplikacijski sloj** – Flask API povezuje modele s web-sučeljem.
5. **Prezentacijski sloj** – HTML, CSS, JavaScript i Plotly grafikoni.

Tok podataka je sljedeći:

`senzori + vrijeme → upravljačka pravila / ML → aktuatori → promjena mikroklime → energija → API → grafikoni`

Pozadinska petlja web-aplikacije radi svakih 1,5 sekundi. Najprije ažurira vrijeme, zatim simulira promjenu mikroklime, primjenjuje upravljačka pravila, ažurira bateriju i sprema snimku stanja u povijest.

## 4. Struktura projekta i opis svake datoteke

### 4.1. Datoteke u korijenskom direktoriju

#### `web_app.py`

Glavna datoteka web-verzije. Kreira Flask aplikaciju, sve modele i kontrolere, pokreće pozadinsku simulaciju te definira API rute. Ovo je preporučena ulazna točka za aktualno sučelje.

Pokretanje:

```bash
python web_app.py
```

Aplikacija je dostupna na `http://127.0.0.1:5000/`.

#### `main.py`

Alternativna, starija desktop ulazna točka. Kreira Tkinter prozor, modele i dvije pozadinske niti za kontrolere. Zadržana je radi demonstracije desktop pristupa, ali novo web-sučelje i novi grafikoni nalaze se u `web_app.py`.

Funkcija `ensure_data_file()`:

1. stvara direktorij `data` ako ne postoji;
2. provjerava postoji li `simulation_log.csv`;
3. ako ne postoji, zapisuje zaglavlje CSV datoteke.

#### `requirements.txt`

Sadrži Python biblioteke potrebne za izvođenje projekta, primjerice Flask, pandas, NumPy, scikit-learn, Plotly i biblioteke za testiranje.

#### `README.md`

Kratke upute za instalaciju i osnovni pregled projekta.

#### `DOKUMENTACIJA.md`

Ova datoteka. Predstavlja detaljnu tehničku dokumentaciju sustava.

### 4.2. Direktorij `simulation`

#### `simulation/sensors.py`

Definira klasu `SensorModel`.

- `__init__()` nasumično postavlja početnu temperaturu, vlagu zraka, vlagu tla, pH, NPK i CO₂ u realistične intervale.
- `update()` dodaje malu nasumičnu promjenu svakom senzoru.
- `current_values()` vraća zaokružene vrijednosti u obliku rječnika pogodnog za API i grafove.
- `_clamp(value, minimum, maximum)` sprečava izlazak vrijednosti iz fizički prihvatljivog raspona.

Rasponi modela uključuju 15–45 °C za temperaturu, 10–90 % za vlagu tla, 4,5–8,5 za pH i 200–1200 ppm za CO₂.

#### `simulation/actuators.py`

Definira klasu `ActuatorModel`. Svi aktuatori počinju u isključenom stanju.

- `pump1` – prva pumpa za vodu;
- `pump2` – druga pumpa za vodu;
- `pump3` – pumpa za NPK hranjivo;
- `fan` – ventilator;
- `led` – rasvjeta;
- `greenhouse_open` – stanje otvora plastenika;
- `alarm` – upozorenje.

Svojstvo `state` vraća sva stanja kao jedan rječnik. Dodatni nazivi `water_pump_2` i `npk_pump` omogućuju jasniji prikaz u API-ju.

#### `simulation/weather_station.py`

Definira `WeatherStationModel`.

- `__init__()` postavlja početnu vanjsku temperaturu, vlagu, brzinu vjetra i oborine.
- `update()` mijenja vrijeme malim nasumičnim koracima.
- `current_values()` vraća trenutne vrijednosti.
- `_classify_weather()` dodjeljuje signal `rain`, `wind`, `hot` ili `sunny`.
- `_clamp()` ograničava vrijednosti.

Redoslijed klasifikacije je važan: oborine iznad 2 mm daju signal kiše, zatim se provjerava vjetar iznad 10 km/h, temperatura iznad 30 °C, a u ostalim slučajevima vrijeme je sunčano.

#### `simulation/greenhouse_model.py`

Klasa `GreenhouseModel` predstavlja digitalni model mikroklime.

`simulate_step()` izvodi jedan korak ovim redom:

1. `_apply_actuator_effects()` primjenjuje učinke uključenih uređaja;
2. `_apply_environmental_drift()` dodaje prirodne slučajne promjene;
3. `_apply_weather_influence()` prenosi dio vanjskih uvjeta u plastenik;
4. vraća nove senzorske vrijednosti.

Učinci aktuatora:

- ventilator smanjuje temperaturu, CO₂ i vlagu zraka;
- LED utječe na CO₂ i vlagu zraka;
- svaka vodena pumpa povećava vlagu tla;
- otvoren plastenik približava unutarnje stanje vanjskim uvjetima;
- kiša može povećati vlagu tla ako je plastenik otvoren;
- jak vjetar utječe na koncentraciju CO₂.

Metoda `_apply_environmental_drift()` nužna je kako simulacija ne bi bila potpuno deterministička. Mikroklima se mijenja i kada nijedan aktuator nije aktivan.

#### `simulation/energy_model.py`

Klasa `EnergyModel` računa energetsku bilancu.

Nazivne snage:

| Komponenta | Snaga |
|---|---:|
| ESP32 | 0,5 W |
| Arduino Mega | 0,4 W |
| Senzori | 0,5 W |
| Pumpa za vodu 1 | 12 W |
| Pumpa za vodu 2 | 12 W |
| NPK pumpa | 10 W |
| Ventilator | 8 W |
| LED | 10 W |
| Motor otvora | 15 W |
| Dva solarna panela | 40 W |

Baterija ima modelirani kapacitet `12 V × 20 Ah = 240 Wh`.

- `compute_consumption()` zbraja stalnu potrošnju elektronike i snage uključenih aktuatora.
- `compute_solar_production()` vraća ukupnu proizvodnju dvaju panela.
- `update_battery(consumption)` računa `proizvodnja − potrošnja` i ograničava bateriju na 0–240 Wh.
- `estimate_runtime(consumption)` dijeli preostalu energiju sa snagom potrošnje.
- `current_report()` vraća potrošnju, proizvodnju, bateriju, autonomiju, neto bilancu i solarnu pokrivenost.

#### `simulation/linear_simulation.py`

Funkcija `run_linear_simulation(...)` ispituje unaprijed definiran prijelaz između dva stanja.

Ulazi su početna i završna temperatura, vlaga tla, NPK, CO₂ i broj koraka. Za svaki korak računa se napredak:

`progress = step / (steps − 1)`

Svaka vrijednost dobiva se linearnom interpolacijom:

`vrijednost = početna + (završna − početna) × progress`

Primjer: ako temperatura raste s 20 na 38 °C u 20 koraka, svaki korak dodaje jednak dio ukupne razlike.

Nakon izračuna senzora primjenjuju se pravila:

- pumpa se uključuje kada je vlaga tla ispod 35 %;
- ventilator kada temperatura prijeđe 32 °C;
- plastenik se otvara iznad 35 °C;
- NPK pumpa se uključuje ispod vrijednosti 60;
- alarm se uključuje za NPK ispod 50 ili temperaturu iznad 42 °C.

Za svaki korak nastaje jedan red u pandas DataFrameu. Nakon petlje funkcija pronalazi prvi korak aktivacije svake akcije, računa ukupan broj aktivnih koraka i priprema serije za grafikone. Vraća `(summary, df)`.

Linearna metoda je deterministička: isti ulazi uvijek daju isti rezultat. Koristi se za jasno pokazivanje pragova upravljanja.

#### `simulation/monte_carlo.py`

Monte Carlo metoda ispituje ponašanje sustava u velikom broju nasumičnih scenarija.

`_apply_rules(values)` iz trenutnih senzora i vremena određuje stanja pumpi, ventilatora, LED-a, otvora i alarma.

`_safe_zone(row)` provjerava jesu li temperatura, vlaga tla, CO₂, pH i NPK istodobno u prihvatljivim intervalima.

`run_monte_carlo(simulations=500, steps=12)` radi ovim redom:

1. stvara praznu listu rezultata;
2. za svaki scenarij stvara nove senzore, vrijeme, aktuatore i model plastenika;
3. u svakom vremenskom koraku ažurira vrijeme;
4. spaja senzorske i meteorološke podatke;
5. primjenjuje `_apply_rules()`;
6. postavlja aktuatore;
7. sprema stanje i odluke u listu;
8. poziva `greenhouse.simulate_step()` da akcije utječu na sljedeći korak;
9. nakon svih scenarija pretvara rezultate u DataFrame;
10. grupira podatke po koraku i računa prosječne trendove;
11. računa aktivacije, kritična stanja, sigurnu zonu i vremenske signale.

Ukupan broj analiziranih stanja jednak je:

`broj simulacija × broj koraka`

Tako 10.000 simulacija s 12 koraka daje 120.000 analiziranih stanja. Povećanjem broja scenarija broj aktivacija raste, ali prosjeci se stabiliziraju. To omogućuje procjenu robusnosti upravljačke logike.

### 4.2.1. Analiza neizvjesnosti i intervali pouzdanosti

Statistička analiza neizvjesnosti važan je dio validacije simulacijskog modela. Srednja vrijednost i standardna devijacija opisuju generirane podatke, ali ne pokazuju koliko je precizno procijenjena stvarna srednja vrijednost parametra. Zato se rezultati Monte Carlo simulacije dodatno analiziraju pomoću 95-postotnih intervala pouzdanosti.

U ovom projektu analiza se stvarno izračunava za temperaturu zraka, vlagu tla, pH, NPK i koncentraciju CO₂. Temperatura upravlja ventilacijom i otvaranjem plastenika, vlaga tla pumpama za vodu, pH i NPK opisuju stanje hranjiva, a CO₂ predstavlja važan pokazatelj kvalitete zraka.

#### Procjena intervala pouzdanosti

Za svaki parametar računaju se broj opažanja `n`, sredina `x̄`, standardna devijacija `s`, minimum, maksimum, medijan i standardna greška:

`SE = s / √n`

Monte Carlo eksperimenti stvaraju tisuće opažanja, pa se koristi normalna aproksimacija i margina pogreške:

`M = 1,96 × SE`

Granice 95% intervala su:

`donja granica = x̄ − 1,96 × SE`

`gornja granica = x̄ + 1,96 × SE`

Odnosno: `x̄ − 1,96 × SE ≤ μ ≤ x̄ + 1,96 × SE`.

Kod malog uzorka prikladnija je Studentova t-raspodjela. Međutim, kod velikih Monte Carlo uzoraka t-raspodjela i normalna aproksimacija daju gotovo jednake granice.

Funkcija `confidence_statistics(column)` u `simulation/monte_carlo.py` računa sve pokazatelje. Rezultati se spremaju u `summary["uncertainty"]` za temperaturu, vlagu tla, pH, NPK i CO₂. Web-sučelje iz tih stvarnih rezultata automatski izrađuje tablicu sredina, standardnih devijacija te donjih i gornjih granica 95% intervala.

#### Rezultati analize

Web-aplikacija nakon svakog pokretanja prikazuje donju i gornju granicu te poseban dijagram srednjih vrijednosti s intervalima pouzdanosti. Tablica za završni izvještaj može imati sljedeći oblik:

| Statistički pokazatelj | Temperatura (°C) | Vlaga tla (%) | CO₂ (ppm) |
|---|---:|---:|---:|
| Srednja vrijednost | rezultat simulacije | rezultat simulacije | rezultat simulacije |
| Standardna devijacija | rezultat simulacije | rezultat simulacije | rezultat simulacije |
| Minimalna vrijednost | rezultat simulacije | rezultat simulacije | rezultat simulacije |
| Maksimalna vrijednost | rezultat simulacije | rezultat simulacije | rezultat simulacije |
| Medijan | rezultat simulacije | rezultat simulacije | rezultat simulacije |
| Donja granica 95% CI | rezultat simulacije | rezultat simulacije | rezultat simulacije |
| Gornja granica 95% CI | rezultat simulacije | rezultat simulacije | rezultat simulacije |

Brojevi nisu unaprijed fiksirani jer je model stohastički. U završni rad treba prenijeti rezultate odabranog eksperimenta, primjerice 10.000 simulacija kroz 12 koraka.

#### Diskusija rezultata

Interval pouzdanosti ne znači da se 95% pojedinačnih mjerenja nalazi unutar njega. On opisuje neizvjesnost procjene **srednje vrijednosti**. Pojedinačne vrijednosti mogu biti široko raspršene, a procjena njihove sredine ipak vrlo precizna.

Uzak interval ukazuje na preciznu procjenu, dok širok interval ukazuje na veću varijabilnost ili premalo opažanja. Širina se smanjuje približno s `1/√n`, pa su za dvostruko uži interval potrebna približno četiri puta više opažanja.

Ako se pri povećanju broja simulacija s 500 na 1.000, 5.000 i 10.000 sredine malo mijenjaju, a intervali postaju uži, model pokazuje statističku stabilnost. Ipak, uzak interval ne dokazuje da model savršeno opisuje stvarni plastenik. On potvrđuje preciznost rezultata simulacije; za stvarnu validaciju potrebna je usporedba sa stvarnim mjerenjima.

Izvori neizvjesnosti su nasumične početne vrijednosti, promjene vremena, okolišni drift i promjenjivi učinci aktuatora. Histogram opisuje raspodjelu pojedinačnih vrijednosti, trend njihovu promjenu kroz korake, a interval pouzdanosti preciznost procijenjene sredine. Zajedno daju potpuniju procjenu stabilnosti modela.

#### `simulation/ml_prediction.py`

Klasa `MLPrediction` implementira Random Forest klasifikaciju s dva izlaza.

`__init__()` definira deset ulaznih značajki i odmah trenira model:

- temperatura;
- vlaga zraka;
- vlaga tla;
- pH;
- NPK;
- CO₂;
- vanjska temperatura;
- vanjska vlaga;
- brzina vjetra;
- oborine.

`_generate_dataset(rows=2400)` generira sintetički skup podataka. Vrijednosti nisu potpuno neovisne: unutarnja temperatura ovisi o vanjskoj, vlaga tla o temperaturi i kiši, a CO₂ o temperaturi i vjetru. Ciljevi su `irrigation_needed` i `ventilation_needed`. Mala količina slučajnog šuma sprječava savršeno jednostavna pravila.

`_train_model()`:

1. generira 2.400 redova;
2. dijeli podatke na 80 % za učenje i 20 % za testiranje;
3. stvara `RandomForestClassifier` sa 140 stabala;
4. omata ga u `MultiOutputClassifier` radi dvaju izlaza;
5. trenira model;
6. predviđa testni skup;
7. računa točnost navodnjavanja, ventilacije i zajedničku točnost;
8. računa matrice zabune;
9. računa prosječnu važnost značajki.

`predict(values)` slaže ulaze pravilnim redoslijedom, poziva model i vraća dvije cjelobrojne odluke.

Random Forest je skup stabala odlučivanja. Svako stablo daje odluku, a konačni rezultat nastaje glasovanjem. Prednost je sposobnost modeliranja nelinearnih odnosa i procjena važnosti ulaznih značajki.

#### `simulation/reporting.py`

- `save_monte_carlo_report(summary, df, output_path)` dodaje vremensku oznaku i sprema Monte Carlo DataFrame u CSV.
- `save_prediction_event(values, prediction, recommendation, output_path)` sprema senzore, ML odluke i tekstualnu preporuku. Ako datoteka postoji, novi se red dodaje postojećim podacima.

### 4.3. Direktorij `controllers`

#### `controllers/arduino_mega_controller.py`

`ArduinoMegaController` predstavlja glavni upravljački uređaj.

- `receive_command()` prima naredbu od ESP32 objekta.
- `_process_command()` pretvara naredbe poput `pump1_on`, `fan_off` i `greenhouse_open` u stanja aktuatora.
- `manual_overrides` čuva ručne postavke. Dok ključ postoji, autonomna logika ne smije prepisati korisnikovu odluku.
- `_apply_control_logic()` primjenjuje pragove senzora i vremena na aktuatore koji nisu ručno zaključani.
- `_apply_recommendation_logic()` stvara preporuku navodnjavanja i ventilacije, ali također poštuje ručne postavke.
- `apply_recommendation()` omogućuje izravnu primjenu vanjske ML preporuke.
- `run()` je beskonačna petlja desktop-verzije koja očitava modele svakih 1,5 sekundi.
- `get_status()` vraća status, senzore, aktuatore i posljednju naredbu.
- `_log()` šalje poruku callback funkciji ili konzoli.

Važna sigurnosna logika zatvara plastenik tijekom kiše ili jakog vjetra. Alarm prati pH i NPK. Prva pumpa reagira na opću suhoću, druga na posebno nisku vlagu uz višu temperaturu, a treća dozira NPK.

#### `controllers/esp32_controller.py`

ESP32 je komunikacijski posrednik.

- `send_command()` bilježi naredbu i prosljeđuje je Arduino kontroleru;
- `receive_state()` predstavlja slanje stanja prema dashboardu;
- `run()` svake dvije sekunde provjerava Arduino i dohvaća stanje;
- `_log()` zapisuje komunikacijske događaje.

### 4.4. Direktoriji `templates` i `static`

#### `templates/index.html`

Sadrži strukturu web-sučelja i JavaScript logiku. Funkcije dohvaćaju API podatke, stvaraju kartice senzora, šalju ručne naredbe i crtaju Plotly grafikone.

Posebne funkcije:

- `refresh()` dohvaća trenutno stanje;
- `control()` šalje ručnu naredbu;
- `renderCharts()` crta deset grafikona povijesti;
- `forecast()` prikazuje sljedeća 24 sata;
- `runMonteCarlo()` pokreće i crta Monte Carlo rezultate;
- `runLinear()` pokreće linearnu simulaciju;
- `loadRandomForest()` prikazuje metrike, važnosti i matrice zabune;
- `trainRandomForest()` ponovno trenira model.

#### `static/dashboard.css`

Definira tamno-zeleni vizualni identitet, responzivnu mrežu, kartice, prekidače, kontrole simulacija, opise grafikona i prikaz digitalnog plastenika.

#### `static/plotly.min.js`

Lokalna Plotly biblioteka. Lokalna kopija omogućuje prikaz grafikona bez internetske veze i uklanja ovisnost o CDN-u.

### 4.5. Direktorij `ui`

`ui/dashboard.py` sadrži stariju Tkinter izvedbu. Omogućuje desktop prikaz senzora, simulacija, energije i predikcija. Aktualni razvoj usmjeren je na responzivno web-sučelje, ali ova datoteka pokazuje da se isti modeli mogu koristiti s različitim korisničkim sučeljima.

### 4.6. Direktorij `data`

- `simulation_log.csv` – povijest stanja i događaja;
- `monte_carlo_report.csv` – izvezeni Monte Carlo rezultati;
- `prediction_events.csv` – povijest ML predikcija.

CSV format omogućuje daljnju obradu u Excelu, Pythonu ili statističkim alatima.

### 4.7. Direktorij `tests`

- `test_controller_logic.py` provjerava ručne postavke, preporuke i reakciju na vrijeme;
- `test_ml_prediction.py` provjerava ulazne značajke, format predikcije i meteorološki model;
- `test_reporting.py` provjerava stvaranje CSV izvještaja.

Pokretanje testova:

```bash
python -m pytest -q
```

## 5. Flask API

| Ruta | Metoda | Namjena |
|---|---|---|
| `/` | GET | Glavni dashboard |
| `/api/state` | GET | Senzori, vrijeme, aktuatori, energija i povijest |
| `/api/control` | POST | Ručna naredba aktuatoru |
| `/api/predict` | POST | Random Forest predikcija i preporuka |
| `/api/random_forest` | GET | Točnost, matrice zabune i važnosti značajki |
| `/api/train` | GET | Ponovno treniranje modela |
| `/api/montecarlo` | POST | Monte Carlo simulacija |
| `/api/linear_simulation` | POST | Linearna simulacija |
| `/api/forecast` | GET | Procjena za sljedeća 24 sata |
| `/api/export_state` | GET | Izvoz trenutačnog stanja |
| `/api/export_all` | GET | Izvoz povijesti svih vrijednosti |

## 6. Ručni i autonomni način rada

Sustav je autonoman, ali korisnik zadržava kontrolu. Kada korisnik promijeni prekidač, naredba se sprema u `manual_overrides`. Pozadinska logika zatim provjerava postoji li ručna vrijednost prije automatske odluke. Zbog toga se prekidač ne vraća odmah u prethodno stanje.

Primjer:

1. vlaga tla padne ispod praga i automatika želi uključiti pumpu;
2. korisnik ručno isključi pumpu;
3. `manual_overrides["pump1"] = False`;
4. sljedeći automatski ciklus vidi ručnu postavku i ostavlja pumpu isključenom.

## 7. Grafikoni i interpretacija rezultata

Dashboard prikazuje trendove temperature, vlage zraka, vlage tla i CO₂, histograme raspodjela, energetsku bilancu, stanja aktuatora i odnos pH–NPK.

Monte Carlo grafikoni pokazuju:

- raspodjelu temperature;
- raspodjelu vlage tla;
- broj aktivacija uređaja;
- prosječne trendove kroz korake.

Linearna simulacija pokazuje:

- kontroliranu promjenu temperature i vlage;
- NPK i CO₂;
- trenutak prelaska svakog praga;
- ukupan broj aktivnih koraka.

Random Forest sekcija pokazuje:

- točnost svakog izlaza;
- zajedničku točnost;
- važnost značajki;
- matricu zabune za navodnjavanje;
- matricu zabune za ventilaciju.

U matrici zabune dijagonalna polja predstavljaju točne odluke, a nedijagonalna pogrešne klasifikacije.

## 8. Pokretanje projekta

```bash
pip install -r requirements.txt
python web_app.py
```

Zatim otvoriti:

```text
http://127.0.0.1:5000/
```

Ako preglednik prikazuje staru verziju, potrebno je pritisnuti `Ctrl+F5`.

## 9. Ograničenja modela

Ovo je simulacija, a ne kalibrirani fizički model stvarnog plastenika. Senzorski podaci i ML skup za treniranje sintetički su generirani. Energetski model koristi pojednostavljene konstantne snage, a prognoza za sljedeći dan predstavlja procjenu temeljenu na trenutnom stanju i dnevnom ciklusu, ne stvarnu meteorološku prognozu.

Rezultati zato služe za demonstraciju metoda, usporedbu algoritama i testiranje upravljačke logike. Za primjenu u stvarnom plasteniku potrebno je spojiti stvarne senzore, kalibrirati jednadžbe, koristiti stvarnu vremensku prognozu i trenirati model na izmjerenim podacima.

## 10. Zaključak

Projekt pokazuje kako se modeliranje, deterministička simulacija, stohastička Monte Carlo analiza i strojno učenje mogu objediniti u jedinstven sustav. Linearna simulacija jasno prikazuje pragove, Monte Carlo metoda provjerava ponašanje u velikom broju slučajnih uvjeta, a Random Forest pruža podatkovno zasnovanu predikciju. Autonomni kontroler pretvara rezultate u akcije, dok ručne postavke korisniku omogućuju konačnu kontrolu. Web-sučelje i grafikoni čine rezultate razumljivima, usporedivima i spremnima za izvoz.
