from abc import ABC, abstractmethod
from typing import Any, Dict

class LLMClient(ABC):
    @abstractmethod
    def call(self, prompt: str) -> Dict[str, Any]:
        """Send a prompt to an LLM and return a structured response."""
        raise NotImplementedError

class MockLLMClient(LLMClient):
    def call(self, prompt: str) -> Dict[str, Any]:
        return {"text": "MOCK_RESPONSE", "success": True}

