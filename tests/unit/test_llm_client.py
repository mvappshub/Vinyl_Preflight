from vinyl_preflight.llm.client import MockLLMClient

def test_mock_llm():
    c = MockLLMClient()
    r = c.call('hello')
    assert r['success'] is True

