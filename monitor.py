import requests
import time
import logging


def lade_targets(pfad):
    """
    Liest die Datei mit den URLs ein.
    Gibt eine Liste mit bereinigten, nicht-leeren URLs zurück.
    """
    with open(pfad) as f:
        urls = [url.strip() for url in f.read().splitlines() if url.strip() != ""]
    return urls


def pruefe_url(url):
    """
    Prüft eine einzelne URL.
    Gibt ein Dictionary zurück:
        - Bei Erfolg: {"url": url, "status": response.status_code, "dauer": dauer, "fehler": None}
        - Bei Fehler: {"url": url, "status": None, "dauer": dauer, "fehler": "TIMEOUT"} etc.
    """
    start = time.time()

    try:
        response = requests.get(url, timeout=5)
        dauer = time.time() - start
        return {"url": url, "status": response.status_code, "dauer": dauer, "fehler": None}

    except requests.exceptions.Timeout:
        dauer = time.time() - start
        return {"url": url, "status": None, "dauer": dauer, "fehler": "TIMEOUT"}

    except requests.exceptions.ConnectionError:
        dauer = time.time() - start
        return {"url": url, "status": None, "dauer": dauer, "fehler": "CONNECTION ERROR"}

    except Exception as e:
        dauer = time.time() - start
        return {"url": url, "status": None, "dauer": dauer, "fehler": f"UNKNOWN ERROR: {e}"}


# ----- Hauptprogramm (nur wenn Skript direkt ausgeführt wird) -----
if __name__ == "__main__":
    # Logging konfigurieren
    logging.basicConfig(
        filename="monitor.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )

    urls = lade_targets("targets.txt")

    for url in urls:
        ergebnis = pruefe_url(url)

        if ergebnis["fehler"] is None:
            # Erfolgreiche Antwort
            if ergebnis["status"] >= 400:
                logging.warning(f"{ergebnis['url']} | Status {ergebnis['status']} (HTTP FEHLER) | {ergebnis['dauer']:.3f}s")
            else:
                logging.info(f"{ergebnis['url']} | Status {ergebnis['status']} | {ergebnis['dauer']:.3f}s")
        else:
            # Fehlerfall
            logging.error(f"{ergebnis['url']} | {ergebnis['fehler']} | {ergebnis['dauer']:.3f}s")