from vinyl_preflight.llm.service import LLMExtractionService
from vinyl_preflight.llm.client import MockLLMClient

def test_llm_service_extraction():
    mock_client = MockLLMClient()
    service = LLMExtractionService(mock_client)
    
    documents = [{"identifier": "test.pdf", "content": "Track 1: Song A"}]
    result = service.extract_tracks_from_documents(documents)
    
    # Mock client vrací prázdné results, ale service by měl fungovat
    assert result is not None

def test_llm_service_empty_documents():
    mock_client = MockLLMClient()
    service = LLMExtractionService(mock_client)
    
    result = service.extract_tracks_from_documents([])
    assert result is None
