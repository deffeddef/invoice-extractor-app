import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.services.llm_service import LLMService
from app.services.sustainability_service import SustainabilityService

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def mock_llm_service():
    with patch('app.services.llm_service.Llama') as mock_llama:
        mock_instance = mock_llama.return_value
        mock_instance.side_effect = lambda *args, **kwargs: {'choices': [{'text': '```json\n{"invoice_number": "TEST-123", "total_amount": 100.0, "currency": "USD"}\n```'}]}
        yield

@pytest.fixture
def mock_sustainability_service():
    with patch('app.services.sustainability_service.SustainabilityService') as mock_service:
        mock_instance = mock_service.return_value
        mock_instance.analyze_invoice_sustainability.side_effect = lambda invoice: invoice # Return invoice unchanged for now
        yield

