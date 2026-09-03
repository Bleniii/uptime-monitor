# Uptime Monitor

[![Tests](https://github.com/Bleniii/uptime-monitor/actions/workflows/tests.yml/badge.svg)](https://github.com/Bleniii/uptime-monitor/actions/workflows/tests.yml)

Ein kleines Werkzeug, das prüft, ob Websites erreichbar sind, die Ergebnisse
protokolliert und als Metriken für Prometheus bereitstellt.

## Status

- [x] URL-Abfrage mit Statuscode und Antwortzeit
- [x] Konfiguration über Datei, Logging
- [x] Fehlerbehandlung: Timeout, Verbindungsfehler, HTTP-Fehler
- [x] DNS-Fehler von Verbindungsfehlern trennen
- [x] Unit-Tests mit pytest und Mocking
- [x] Betrieb als systemd-Service
- [x] Docker-Container
- [x] GitHub-Actions-Pipeline mit Tests und Image-Build
- [x] `/metrics`-Endpoint für Prometheus
- [x] Prometheus und Grafana über docker-compose
- [x] Dashboard: Verfügbarkeit, Antwortzeit, Statuscode
- [ ] Dashboard als Code ins Repository
- [ ] Alarmregel für `uptime_erreichbar == 0`
- [ ] Versionierung und Dokumentation: Einführung und Code-Dokumentation
- [ ] Wissenstest zum Projekt und Dokumentation abschliessen

## Funktion

- Prüft die in `targets.txt` konfigurierten URLs, alle 60 Sekunden
- Erfasst HTTP-Statuscode und Antwortzeit
- Unterscheidet Erfolg (INFO), HTTP-Fehler ab Status 400 (WARNING) und
  ausbleibende Antwort durch Timeout oder Verbindungsfehler (ERROR)
- Schreibt nach stdout, damit systemd oder Docker das Logging übernehmen
- Stellt drei Metriken unter `http://localhost:8000/metrics` bereit

## Technik

Python 3.11, requests, prometheus-client, pytest mit unittest.mock,
systemd, Docker, docker compose, Prometheus, Grafana, GitHub Actions

## Installation

```bash
git clone https://github.com/Bleniii/uptime-monitor.git
cd uptime-monitor
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Verwendung

URLs in `targets.txt` eintragen, eine pro Zeile. Dann:

```bash
python monitor.py
```

Das Programm läuft dauerhaft und prüft alle 60 Sekunden. Metriken unter
`http://localhost:8000/metrics`, Beenden mit `Strg+C`.

## Metriken

| Metrik | Bedeutung |
|---|---|
| `uptime_erreichbar{url}` | 1 = Antwort erhalten, 0 = keine |
| `uptime_status{url}` | HTTP-Statuscode. Die Zeitreihe verschwindet, sobald keine Antwort mehr kommt — ein stehengebliebener alter Wert wäre irreführend |
| `uptime_versuchsdauer_sekunden{url}` | Dauer des Versuchs, auch im Fehlerfall |

`uptime_erreichbar` und `uptime_status` beantworten verschiedene Fragen: Ein
Statuscode 404 bedeutet, dass der Server geantwortet hat — erreichbar ist er
also. Für die Alarmierung ergibt das zwei getrennte Regeln, eine für die
Infrastruktur und eine für die Anwendung.

## Monitoring-Stack

Prometheus holt die Metriken ab, Grafana stellt sie dar. Alle drei Dienste
laufen über eine `docker-compose.yml`:

```bash
docker compose up -d --build
docker compose ps
```

| Dienst | Adresse | Zweck |
|---|---|---|
| Monitor | http://localhost:8000/metrics | Liefert die Messwerte |
| Prometheus | http://localhost:9090 | Sammelt und speichert sie |
| Grafana | http://localhost:3000 | Zeigt sie als Dashboard |

Grafana meldet sich mit `admin` / `admin`. Die Prometheus-Datenquelle wird
beim Start aus `grafana/provisioning/` eingelesen, sie muss nicht von Hand
angelegt werden.

Prometheus erreicht den Monitor über den Servicenamen `monitor:8000` im
internen Compose-Netzwerk — nicht über `localhost`, das im Container auf den
Container selbst zeigt.

Die gesammelten Daten liegen in zwei Named Volumes (`prometheus-data`,
`grafana-data`). `docker compose down` lässt sie bestehen, `docker compose
down -v` löscht sie.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

Die Tests für `pruefe_url` ersetzen `requests.get` durch einen Mock und laufen
ohne Netzwerkzugriff.

Bei jedem Push und Pull Request führt GitHub Actions dieselben Tests aus und
baut das Docker-Image. Konfiguration unter `.github/workflows/tests.yml`.

## Betrieb als Dienst

Die systemd-Unit liegt unter `systemd/`. Der Service ist vom Typ `simple` und
läuft dauerhaft; `Restart=always` startet ihn nach einem Absturz neu.

Vor der Verwendung anzupassen in `systemd/uptime-monitor.service`:

```ini
User=<benutzername>
WorkingDirectory=<pfad-zum-projektordner>
ExecStart=<pfad-zum-projektordner>/.venv/bin/python monitor.py
```

Dann:

```bash
sudo cp systemd/uptime-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now uptime-monitor.service
journalctl -u uptime-monitor.service -f
```

## Docker

Der normale Weg ist `docker compose up` (siehe Monitoring-Stack). Nur das
Image allein bauen und starten:

```bash
docker build -t uptime-monitor .
docker run --rm -p 8000:8000 uptime-monitor
```

Der Container läuft unter einem unprivilegierten Benutzer. `-p 8000:8000`
verbindet den Container-Port mit dem Host — ohne diese Angabe ist `/metrics`
von aussen nicht erreichbar.

**Port 8000 ist nur einmal vergeben.** systemd-Dienst, Compose-Stack und
Einzelcontainer schliessen sich gegenseitig aus. Läuft eines davon bereits,
scheitert das nächste mit `address already in use`.

## Hintergrund

Dieses Projekt ist als Lernprojekt entstanden. Ziel war, Linux und typische
DevOps-Werkzeuge an einer echten Anwendung kennenzulernen: Systemdienste mit
systemd, Containerisierung mit Docker, automatisierte Tests, eine
CI/CD-Pipeline und Observability mit Prometheus und Grafana. Der
Uptime-Monitor selbst ist bewusst klein gehalten, damit der Fokus auf dem
Drumherum liegt.

## Lizenz

MIT — siehe [LICENSE](LICENSE).