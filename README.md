# Uptime Monitor
[![Tests](https://github.com/Bleniii/uptime-monitor/actions/workflows/tests.yml/badge.svg)](https://github.com/Bleniii/uptime-monitor/actions/workflows/tests.yml)

Ein kleines Werkzeug, das
prüft, ob Websites erreichbar sind, und die Ergebnisse protokolliert.

## Status

- [x] URL-Abfrage mit Statuscode und Antwortzeit
- [x] Konfiguration über Datei, Logging
- [x] Fehlerbehandlung: Timeout, Verbindungsfehler, HTTP-Fehler
- [x] Unit-Tests mit pytest und Mocking
- [x] Betrieb als systemd-Service
- [x] Docker-Container
- [x] GitHub-Actions-Pipeline
- [x] `/metrics`-Endpoint für Prometheus
- [x] Dokumentation nachführen für Prometheus
- [ ] Versionierung und Dokumentation: Einführung und Dokumentation: Code
- [ ] Docker-Image-Build in der Pipeline
- [x] DNS-Fehler von Verbindungsfehlern trennen
- [ ] Wissenstest zum Projekt & Dokumentation abschliessen

## Funktion

- Prüft die in `targets.txt` konfigurierten URLs, alle 60 Sekunden
- Erfasst HTTP-Statuscode und Antwortzeit
- Unterscheidet Erfolg (INFO), HTTP-Fehler ab Status 400 (WARNING) und
  ausbleibende Antwort durch Timeout oder Verbindungsfehler (ERROR)
- Schreibt nach stdout, damit systemd oder Docker das Logging übernehmen
- Stellt drei Metriken unter `http://localhost:8000/metrics` bereit

## Technik

Python 3.11, requests, prometheus-client, pytest mit unittest.mock,
systemd, Docker, GitHub Actions

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

Das Programm läuft dauerhaft und prüft alle 60 Sekunden. Metriken unter
`http://localhost:8000/metrics`, Beenden mit `Strg+C`.

## Metriken

| Metrik | Bedeutung |
|---|---|
| `uptime_erreichbar{url}` | 1 = Antwort erhalten, 0 = keine |
| `uptime_status{url}` | HTTP-Statuscode, fehlt wenn keine Antwort kam |
| `uptime_versuchsdauer_sekunden{url}` | Dauer des Versuchs, auch im Fehlerfall |

## Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

Die Tests für `pruefe_url` ersetzen `requests.get` durch einen Mock und laufen
ohne Netzwerkzugriff.

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

```bash
docker build -t uptime-monitor .
docker run --rm -p 8000:8000 uptime-monitor
```

Der Container läuft unter einem unprivilegierten Benutzer. `-p 8000:8000`
verbindet den Container-Port mit dem Host — ohne diese Angabe ist `/metrics`
von aussen nicht erreichbar.

## Hintergrund

Dieses Projekt ist als Lernprojekt entstanden. Ziel war, Linux und typische
DevOps-Werkzeuge an einer echten Anwendung kennenzulernen: Systemdienste mit
systemd, Containerisierung mit Docker, automatisierte Tests und eine
CI/CD-Pipeline. Der Uptime-Monitor selbst ist bewusst klein gehalten, damit
der Fokus auf dem Drumherum liegt.