from vinyl_preflight.app import run

def test_pipeline_e2e():
    r = run({'source': 'test-src'})
    assert r['status'] == 'done'
    assert 'report' in r

