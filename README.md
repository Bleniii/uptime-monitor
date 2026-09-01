# Uptime Monitor
[![Tests](https://github.com/Bleniii/uptime-monitor/actions/workflows/tests.yml/badge.svg)](https://github.com/Bleniii/uptime-monitor/actions/workflows/tests.yml)

Ein kleines Werkzeug, das
prüft, ob Websites erreichbar sind, und die Ergebnisse protokolliert.

## Status

- [x] URL-Abfrage mit Statuscode und Antwortzeit
- [x] Konfiguration über Datei, Logging
- [x] Fehlerbehandlung: Timeout, Verbindungsfehler, HTTP-Fehler
- [x] Unit-Tests mit pytest und Mocking
- [x] Betrieb als systemd-Service mit Timer
- [x] Neuen User erstellen und konfigurieren für Docker
- [x] Docker-Container
- [x] GitHub-Actions-Pipeline
- [ ] `/metrics`-Endpoint für Prometheus

## Funktion

- Prüft die in `targets.txt` konfigurierten URLs
- Erfasst HTTP-Statuscode und Antwortzeit
- Unterscheidet Erfolg (INFO), HTTP-Fehler ab Status 400 (WARNING) und
  ausbleibende Antwort durch Timeout oder Verbindungsfehler (ERROR)
- Schreibt nach stdout, damit systemd oder Docker das Logging übernehmen

## Technik

Python 3.11, `requests`, `pytest` mit `unittest.mock`, systemd, Docker

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
python3 monitor.py
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

Die Tests für `pruefe_url` ersetzen `requests.get` durch einen Mock und laufen
ohne Netzwerkzugriff.

## Betrieb als Dienst

Die systemd-Units liegen unter `systemd/`. Der Service ist vom Typ `oneshot`,
ein Timer startet ihn alle 10 Minuten.
Bevor man die Units verwenden kann muss man in der service-konfiguration anpassen; `systemd/uptime-monitor.service`
User=*anpassen*
WorkingDirectory=*anpassen* (Pfad-zum-projektordner)
ExecStart=*anpassen* (Pfad-zum-projektordner/.venv/bin/python monitor.py)

## Hintergrund
Dieses Projekt ist als Lernprojekt entstanden. Ziel war, Linux und typische DevOps-Werkzeuge 
an einer echten Anwendung kennenzulernen. Systemdienste mit systemd, Containerisierung mit Docker, 
automatisierte Tests und eine CI/CD-Pipeline. 
Der Uptime-Monitor dient als cooles Feature. Der Fokus liegt auf die Umgebung.
