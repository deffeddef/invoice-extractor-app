import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app # Import the FastAPI app instance
from app.models.invoice import Invoice, ExtractionResult, Vendor, VendorAddress, CustomerAddress, LineItem, SustainabilityMetrics
import io

# Use the client fixture from conftest.py

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Invoice Extractor API. Go to /docs for API documentation."}

@patch('app.services.invoice_parser.parse_invoice')
def test_upload_invoice_success(mock_parse_invoice, client):
    # Mock the parse_invoice function to return a successful result
    mock_parse_invoice.return_value = ExtractionResult(
        status="success",
        invoice_data=Invoice(
            invoice_number="INV-TEST-001",
            invoice_date="2023-01-01",
            vendor=Vendor(name="Test Vendor", address=VendorAddress(street="123 Test St", city="Test City", zip_code="12345", country="Testland"), vat_id="TV123"),
            customer_name="Test Customer",
            customer_address=CustomerAddress(street="456 Test Ave", city="Test Town", zip_code="67890", country="Testland"),
            line_items=[
                LineItem(description="Item A", quantity=1.0, unit_price=10.0, total=10.0, sustainability_score=80.0)
            ],
            subtotal=10.0,
            tax_amount=1.0,
            total_amount=11.0,
            currency="USD",
            sustainability_metrics=SustainabilityMetrics(overall_esg_risk="Low", green_vendor_flag=True, co2_intensive_items_flag=False)
        )
    )

    # Create a dummy file for upload
    file_content = b"This is a dummy invoice content."
    files = {"file": ("test_invoice.pdf", file_content, "application/pdf")}

    response = client.post("/api/upload", files=files)

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["invoice_data"]["invoice_number"] == "INV-TEST-001"
    mock_parse_invoice.assert_called_once()

@patch('app.services.invoice_parser.parse_invoice')
def test_upload_invoice_failure(mock_parse_invoice, client):
    # Mock the parse_invoice function to return an error result
    mock_parse_invoice.return_value = ExtractionResult(
        status="error",
        error_message="Failed to process invoice due to an internal error."
    )

    # Create a dummy file for upload
    file_content = b"This is a dummy invoice content."
    files = {"file": ("test_invoice.txt", file_content, "text/plain")}

    response = client.post("/api/upload", files=files)

    assert response.status_code == 400
    assert response.json()["status"] == "error"
    assert "error_message" in response.json()
    mock_parse_invoice.assert_called_once()

def test_upload_invoice_no_file(client):
    response = client.post("/api/upload")
    assert response.status_code == 422 # Unprocessable Entity due to missing file

def test_upload_invoice_empty_file_name(client):
    file_content = b"dummy content"
    files = {"file": ("", file_content, "application/pdf")}
    response = client.post("/api/upload", files=files)
    assert response.status_code == 400
    assert response.json() == {"detail": "No file name provided."} # This is from the endpoint's explicit check
