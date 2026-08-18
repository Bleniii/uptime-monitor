import requests
import time
import logging

# ----- Logging konfigurieren -----
logging.basicConfig(
    filename="monitor.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# ----- URLs aus Datei lesen (leere Zeilen ignorieren) -----
with open("targets.txt") as f:
    urls = [url.strip() for url in f.read().splitlines() if url.strip() != ""]

# ----- Jede URL prüfen -----
for url in urls:
    start = time.time()  # <-- VOR dem try, damit im except verfügbar

    try:
        response = requests.get(url, timeout=5)
        dauer = time.time() - start

        # Statuscode bewerten
        if response.status_code >= 400:
            logging.warning(f"{url} | Status {response.status_code} (HTTP FEHLER) | {dauer:.3f}s")
        else:
            logging.info(f"{url} | Status {response.status_code} | {dauer:.3f}s")

    except requests.exceptions.Timeout:
        dauer = time.time() - start
        logging.error(f"{url} | TIMEOUT | {dauer:.3f}s")

    except requests.exceptions.ConnectionError:
        dauer = time.time() - start
        logging.error(f"{url} | CONNECTION ERROR | {dauer:.3f}s")

    except Exception as e:
        dauer = time.time() - start
        logging.error(f"{url} | UNKNOWN ERROR: {e} | {dauer:.3f}s")