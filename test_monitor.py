from unittest.mock import patch, Mock, MagicMock
import requests
from urllib3.exceptions import NameResolutionError
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
    assert isinstance(ergebnis["dauer"], float)


# ----- TEST 3: ConnectionError ohne DNS-Grund (Mock) -----
@patch("monitor.requests.get")
def test_pruefe_url_connection_error(mock_get):
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


# ----- TEST 5: ConnectionError mit DNS-Grund (Mock) -----
@patch("monitor.requests.get")
def test_pruefe_url_dns_error(mock_get):
    """Eine ConnectionError, deren args[0].reason eine NameResolutionError ist, muss 'DNS ERROR' liefern."""
    fake_maxretry = MagicMock()
    fake_maxretry.reason = NameResolutionError("egal.ch", None, None)

    dns_exception = requests.exceptions.ConnectionError(fake_maxretry)
    mock_get.side_effect = dns_exception

    ergebnis = pruefe_url("http://nicht-existent-testdomain.invalid")

    assert ergebnis["status"] is None
    assert ergebnis["fehler"] == "DNS ERROR"
    assert ergebnis["url"] == "http://nicht-existent-testdomain.invalid"
    assert isinstance(ergebnis["dauer"], float)
