from monitor import lade_targets

def test_lade_targets_filtert_leerzeilen(tmp_path):
    datei = tmp_path / "targets.txt"
    datei.write_text("https://a.ch\n\nhttps://b.ch\n")
    
    ergebnis = lade_targets(str(datei))
    
    assert ergebnis == ["https://a.ch", "https://b.ch"]    