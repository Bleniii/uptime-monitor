from unittest.mock import patch, Mock
import requests  # ← Wichtig: requests selbst importieren für die Exception
from monitor import lade_targets, pruefe_url


# ----- TEST 1: Datei-Einlesen (kein Mock) -----
def test_lade_targets_filtert_leerzeilen(tmp_path):
    datei = tmp_path / "targets.txt"
    datei.write_text("https://a.ch\n\nhttps://b.ch\n")
    
    ergebnis = lade_targets(str(datei))
    
    assert ergebnis == ["https://a.ch", "https://b.ch"]


# ----- TEST 2: Erfolgreiche Anfrage (Mock) -----
@patch("monitor.requests.get")
def test_pruefe_url_erfolg(mock_get):
    fake_response = Mock()
    fake_response.status_code = 200
    mock_get.return_value = fake_response

    ergebnis = pruefe_url("https://egal.ch")

    assert ergebnis["status"] == 200
    assert ergebnis["fehler"] is None
    assert ergebnis["url"] == "https://egal.ch"
    assert isinstance(ergebnis["dauer"], float)  # optional: Prüft, dass eine Zeit gemessen wurde


# ----- TEST 3: ConnectionError (Mock) -----
@patch("monitor.requests.get")
def test_pruefe_url_connection_error(mock_get):
    # Simuliere einen ConnectionError
    mock_get.side_effect = requests.exceptions.ConnectionError

    ergebnis = pruefe_url("https://egal.ch")

    assert ergebnis["status"] is None
    assert ergebnis["fehler"] == "CONNECTION ERROR"
    assert ergebnis["url"] == "https://egal.ch"
    assert isinstance(ergebnis["dauer"], float)
    
    # ----- TEST 4: Timeout (Mock) -----
@patch("monitor.requests.get")
def test_pruefe_url_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout

    ergebnis = pruefe_url("https://egal.ch")

    assert ergebnis["status"] is None
    assert ergebnis["fehler"] == "TIMEOUT"
    assert ergebnis["url"] == "https://egal.ch"
    assert isinstance(ergebnis["dauer"], float)