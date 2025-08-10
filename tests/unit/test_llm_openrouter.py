from vinyl_preflight.llm.client import OpenRouterLLMClient
import pytest

class DummyResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code
    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("HTTP error")
    def json(self):
        return self._json


def test_openrouter_client_call(monkeypatch):
    called = {}
    def fake_post(url, headers=None, json=None, timeout=None):
        called['ok'] = True
        return DummyResponse({"choices": [{"message": {"content": '{"results": []}'}}]})
    monkeypatch.setattr("requests.post", fake_post)

    client = OpenRouterLLMClient(api_url="http://x", headers={}, model="m")
    r = client.call("hello")
    assert 'choices' in r
    assert called.get('ok') is True

