import pytest
from app.services.sustainability_service import SustainabilityService
from app.models.invoice import Invoice, LineItem, Vendor, SustainabilityMetrics

def test_calculate_item_sustainability_score():
    service = SustainabilityService()
    
    # Test a normal item
    item1 = LineItem(description="Office Supplies", quantity=10.0, unit_price=1.0, total=10.0)
    score1 = service.calculate_item_sustainability_score(item1)
    assert 45 <= score1 <= 55 # Base score is 50, CO2 is low for generic items

    # Test an eco-labeled item
    item2 = LineItem(description="Recycled paper", quantity=1.0, unit_price=5.0, total=5.0)
    score2 = service.calculate_item_sustainability_score(item2)
    assert score2 > 70 # Should get a boost for eco-label

    # Test a CO2 intensive item
    item3 = LineItem(description="Electronics component", quantity=1.0, unit_price=100.0, total=100.0)
    score3 = service.calculate_item_sustainability_score(item3)
    assert score3 < 40 # Should get a penalty for high CO2

def test_analyze_invoice_sustainability():
    service = SustainabilityService()

    # Create a sample invoice
    vendor = Vendor(name="GreenCorp", address=None, vat_id=None)
    line_item1 = LineItem(description="Organic Vegetables", quantity=5.0, unit_price=2.0, total=10.0)
    line_item2 = LineItem(description="Electronics", quantity=1.0, unit_price=50.0, total=50.0)

    invoice = Invoice(
        invoice_number="INV-001",
        invoice_date="2023-01-01",
        vendor=vendor,
        customer_name="Test Customer",
        customer_address=None,
        line_items=[line_item1, line_item2],
        subtotal=60.0,
        tax_amount=5.0,
        total_amount=65.0,
        currency="USD"
    )

    # Analyze sustainability
    analyzed_invoice = service.analyze_invoice_sustainability(invoice)

    # Assertions for line item scores
    assert analyzed_invoice.line_items[0].sustainability_score is not None
    assert analyzed_invoice.line_items[1].sustainability_score is not None
    assert analyzed_invoice.line_items[0].sustainability_score > analyzed_invoice.line_items[1].sustainability_score # Organic should be better than electronics

    # Assertions for overall sustainability metrics
    assert analyzed_invoice.sustainability_metrics is not None
    assert analyzed_invoice.sustainability_metrics.green_vendor_flag is True # GreenCorp should be flagged as green
    assert analyzed_invoice.sustainability_metrics.co2_intensive_items_flag is True # Electronics should trigger this
    assert analyzed_invoice.sustainability_metrics.overall_esg_risk == "Low" # GreenCorp + some good items

    # Test with a non-green vendor
    vendor2 = Vendor(name="RegularCo", address=None, vat_id=None)
    invoice2 = Invoice(
        invoice_number="INV-002",
        vendor=vendor2,
        line_items=[line_item1],
        total_amount=10.0
    )
    analyzed_invoice2 = service.analyze_invoice_sustainability(invoice2)
    assert analyzed_invoice2.sustainability_metrics.green_vendor_flag is False
    assert analyzed_invoice2.sustainability_metrics.overall_esg_risk == "Medium"
