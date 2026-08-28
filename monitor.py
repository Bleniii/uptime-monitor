"""Einfacher URL-Monitor mit Retry und exponentiellem Backoff.

HTTP-Statuscodes, grob nach erster Ziffer:
    2xx  Erfolg            z. B. 200 OK
    3xx  Weiterleitung     z. B. 301 dauerhaft, 302 temporär
    4xx  Fehler beim Client 400 ungültig, 401 nicht angemeldet,
                            403 verboten, 404 nicht gefunden
    5xx  Fehler beim Server 500 intern, 502 Gateway, 503 überlastet,
                            504 Gateway-Timeout

Für das Retry ist nur die Grenze bei 500 entscheidend: 4xx sind endgültige
Antworten (ein zweiter Versuch ändert nichts), 5xx sind oft vorübergehend.

Benötigt Python 3.10+ (wegen `int | None`) und das Paket `requests`.
"""

import logging
import time
from typing import NamedTuple

import requests


class Ergebnis(NamedTuple):
    """Das Resultat einer Prüfung. Zugriff per ergebnis.status statt ["status"]."""

    url: str
    status: int | None
    dauer: float
    fehler: str | None
    versuche: int


def lade_targets(pfad: str) -> list[str]:
    """Liest die URL-Datei. Leere Zeilen und #-Kommentare werden übersprungen."""
    with open(pfad, encoding="utf-8") as f:
        return [
            url for line in f
            if (url := line.strip()) and not url.startswith("#")
        ]


def _fehlername(exc: Exception) -> str:
    """Übersetzt eine requests-Exception in ein kurzes Label.

    Timeout wird zuerst geprüft: ConnectTimeout erbt von Timeout UND von
    ConnectionError, bei umgekehrter Reihenfolge wäre die Zuordnung falsch.
    """
    if isinstance(exc, requests.exceptions.Timeout):
        return "TIMEOUT"
    if isinstance(exc, requests.exceptions.ConnectionError):
        return "CONNECTION ERROR"
    return f"{type(exc).__name__}: {exc}"


def pruefe_url(
    url: str,
    session: requests.Session | None = None,
    timeout: float = 5.0,
    versuche: int = 3,
    pause: float = 0.5,
) -> Ergebnis:
    """Prüft eine URL und wiederholt bei vorübergehenden Fehlern.

    Wiederholt wird bei Netzwerkfehlern und HTTP 5xx. Statuscodes unter 500
    (auch 404 oder 403) gelten als endgültige Antwort und werden sofort
    zurückgegeben. Die Wartezeit verdoppelt sich pro Versuch.
    """
    get = session.get if session is not None else requests.get
    status: int | None = None
    fehler: str | None = None
    dauer = 0.0

    for versuch in range(1, versuche + 1):
        start = time.perf_counter()
        try:
            response = get(url, timeout=timeout)
            dauer = time.perf_counter() - start
            if response.status_code < 500:
                return Ergebnis(url, response.status_code, dauer, None, versuch)
            status = response.status_code
            fehler = f"HTTP {status}"
        except requests.exceptions.RequestException as exc:
            dauer = time.perf_counter() - start
            status = None
            fehler = _fehlername(exc)

        # Nach dem letzten Versuch nicht mehr schlafen.
        if versuch < versuche:
            time.sleep(pause * 2 ** (versuch - 1))

    return Ergebnis(url, status, dauer, fehler, versuche)


# ----- Hauptprogramm (nur wenn Skript direkt ausgeführt wird) -----
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
    )

    # Session hält die TCP-Verbindung offen (Keep-Alive) und spart pro
    # weiterer URL auf derselben Domain einen TLS-Handshake.
    with requests.Session() as session:
        for url in lade_targets("targets.txt"):
            e = pruefe_url(url, session=session)

            if e.fehler:
                level, text = logging.ERROR, e.fehler
            elif e.status >= 400:
                level, text = logging.WARNING, f"Status {e.status} (HTTP FEHLER)"
            else:
                level, text = logging.INFO, f"Status {e.status}"

            hinweis = f" | {e.versuche} Versuche" if e.versuche > 1 else ""
            logging.log(level, "%s | %s | %.3fs%s", e.url, text, e.dauer, hinweis)
