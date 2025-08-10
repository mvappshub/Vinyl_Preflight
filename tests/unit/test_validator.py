from vinyl_preflight.core.validator import detect_consolidated_mode

def test_detect_consolidated_mode():
    assert detect_consolidated_mode(["SIDE A.wav", "SIDE B.wav"]) is True
    assert detect_consolidated_mode(["01_track.wav", "02_track.wav"]) is False

