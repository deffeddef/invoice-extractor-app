import pytest
from unittest.mock import patch, MagicMock
from app.services.llm_service import LLMService, get_llm_service
from app.models.invoice import Invoice
import json

@pytest.fixture(autouse=True)
def mock_llama_init():
    # This fixture ensures Llama is mocked for all tests in this file
    with patch('app.services.llm_service.Llama') as mock_llama:
        mock_instance = mock_llama.return_value
        # Configure a default side_effect for the mock Llama instance
        mock_instance.side_effect = lambda *args, **kwargs: {
            'choices': [{'text': '```json\n{"invoice_number": "MOCK-INV-001", "total_amount": 100.0, "currency": "USD"}\n```'}]
        }
        yield mock_llama

def test_llm_service_initialization(mock_llama_init):
    service = LLMService(model_path="/fake/path/to/model.gguf")
    mock_llama_init.assert_called_once_with(
        model_path="/fake/path/to/model.gguf",
        n_gpu_layers=-1,
        n_ctx=8192,
        verbose=False,
        json_mode=True,
    )
    assert service.llm is not None

def test_get_invoice_schema():
    service = LLMService(model_path="/fake/path/to/model.gguf")
    schema = service.get_invoice_schema()
    assert isinstance(schema, str)
    assert "invoice_number" in schema
    assert "total_amount" in schema

def test_extract_invoice_data_success(mock_llama_init):
    # Configure the mock Llama instance for this specific test
    mock_llama_init.return_value.side_effect = lambda *args, **kwargs: {
        'choices': [{'text': '```json\n{"invoice_number": "INV-2023-001", "invoice_date": "2023-01-01", "vendor": {"name": "Test Vendor", "address": {"street": "123 Test St", "city": "Test City", "zip_code": "12345", "country": "Testland"}, "vat_id": "TV123"}, "customer_name": "Test Customer", "customer_address": {"street": "456 Test Ave", "city": "Test Town", "zip_code": "67890", "country": "Testland"}, "line_items": [], "subtotal": 90.0, "tax_amount": 10.0, "total_amount": 100.0, "currency": "USD"}\n```'}]
    }

    service = LLMService(model_path="/fake/path/to/model.gguf")
    text = "Some invoice text"
    extracted_data = service.extract_invoice_data(text)
    assert "invoice_number" in extracted_data
    assert extracted_data["invoice_number"] == "INV-2023-001"
    assert extracted_data["total_amount"] == 100.0
    assert extracted_data["currency"] == "USD"

def test_extract_invoice_data_invalid_json(mock_llama_init):
    # Configure the mock Llama instance to return invalid JSON
    mock_llama_init.return_value.side_effect = lambda *args, **kwargs: {
        'choices': [{'text': 'This is not JSON.'}]
    }

    service = LLMService(model_path="/fake/path/to/model.gguf")
    text = "Some invoice text"
    with pytest.raises(ValueError, match="No valid JSON object found in the LLM response."):
        service.extract_invoice_data(text)

def test_get_llm_service_singleton():
    # Ensure the singleton pattern works
    service1 = get_llm_service()
    service2 = get_llm_service()
    assert service1 is service2
