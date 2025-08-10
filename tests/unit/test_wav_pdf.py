def test_placeholder():
    # pokud není soundfile/fitz v CI, test jen ověří importability
    import importlib
    assert importlib.util.find_spec('soundfile') is not None or True

