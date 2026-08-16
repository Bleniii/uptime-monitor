import requests
import time
import logging

# ----- Logging konfigurieren (einmal am Anfang) -----
logging.basicConfig(
    filename="monitor.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# Konfiguration einlesen. Leerzeilen am Ende oder in der Mitte ignorieren,
# da requests.get("") sonst eine InvalidURL-Exception wirft.
with open("targets.txt") as f:
    urls = [url.strip() for url in f.read().splitlines() if url.strip() != ""]

# ----- Jede URL prüfen -----
for url in urls:
    try:
        start = time.time()
        response = requests.get(url, timeout=5)
        end = time.time()
        dauer = end - start
        
       # Erfolg ins Log schreiben
        logging.info(f"{url} | Status {response.status_code} | {dauer:.3f}s")

    except requests.exceptions.Timeout:
        logging.error(f"{url} | TIMEOUT")
    except requests.exceptions.ConnectionError:
        logging.error(f"{url} | CONNECTION ERROR")
    except Exception as e:
        logging.error(f"{url} | UNKNOWN ERROR: {e}")