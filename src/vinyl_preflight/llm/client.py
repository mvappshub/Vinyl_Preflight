from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import requests

class LLMClient(ABC):
    @abstractmethod
    def call(self, prompt: str) -> Dict[str, Any]:
        """Send a prompt to an LLM and return a structured response."""
        raise NotImplementedError

class MockLLMClient(LLMClient):
    def call(self, prompt: str) -> Dict[str, Any]:
        return {"text": "MOCK_RESPONSE", "success": True}


class OpenRouterLLMClient(LLMClient):
    def __init__(self, api_url: str, headers: Dict[str, str], model: str, timeout: int = 180):
        self.api_url = api_url
        self.headers = headers
        self.model = model
        self.timeout = timeout

    def call(self, prompt: str) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.0,
        }
        resp = requests.post(self.api_url, headers=self.headers, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

