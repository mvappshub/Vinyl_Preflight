from vinyl_preflight.models import Track, Project
from pathlib import Path

def test_models_basic():
    t = Track(title='Song A', side='A', track_number=1, duration_seconds=180.0)
    assert t.title == 'Song A'
    p = Project(name='TestProj', pdfs=[Path('a.pdf')], wavs=[Path('a.wav')])
    assert p.name == 'TestProj'

