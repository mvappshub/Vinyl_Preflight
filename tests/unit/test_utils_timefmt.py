from vinyl_preflight.utils.timefmt import seconds_to_mmss, safe_round

def test_seconds_to_mmss():
    assert seconds_to_mmss(0) == "+00:00"
    assert seconds_to_mmss(65) == "+01:05"
    assert seconds_to_mmss(-65) == "-01:05"
    assert seconds_to_mmss(None) == "N/A"
    assert seconds_to_mmss("x") == "Chyba"

def test_safe_round():
    assert safe_round(3.14159) == 3.14
    assert safe_round(None) is None
    assert safe_round(3.14159, 3) == 3.142

