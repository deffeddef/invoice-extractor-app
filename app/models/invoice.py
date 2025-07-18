from pydantic import BaseModel, Field
from typing import List, Optional, Union

class VendorAddress(BaseModel):
    street: Optional[str] = Field(None, description="Street and house number.")
    city: Optional[str] = Field(None, description="City.")
    zip_code: Optional[str] = Field(None, description="Postal code.")
    country: Optional[str] = Field(None, description="Country.")

class Vendor(BaseModel):
    name: Optional[str] = Field(None, description="The name of the vendor.")
    address: Optional[VendorAddress] = Field(None, description="The address of the vendor.")
    vat_id: Optional[str] = Field(None, description="The VAT ID of the vendor.")

class SustainabilityMetrics(BaseModel):
    overall_esg_risk: Optional[str] = Field(None, description="Overall ESG risk assessment (e.g., 'Low', 'Medium', 'High').")
    green_vendor_flag: Optional[bool] = Field(None, description="True if the vendor is identified as a green vendor.")
    co2_intensive_items_flag: Optional[bool] = Field(None, description="True if any line item is identified as CO2 intensive.")

class LineItem(BaseModel):
    description: str = Field(description="Description of the item or service.")
    quantity: float = Field(description="Quantity of the item or service.")
    unit_price: float = Field(description="Unit price of the item or service.")
    total: float = Field(description="Total price for the line item.")
    sustainability_score: Optional[float] = Field(None, description="A calculated sustainability score for the item (0-100).")

class CustomerAddress(BaseModel):
    street: Optional[str] = Field(None, description="Street and house number.")
    city: Optional[str] = Field(None, description="City.")
    zip_code: Optional[str] = Field(None, description="Postal code.")
    country: Optional[str] = Field(None, description="Country.")

class Invoice(BaseModel):
    invoice_number: Optional[str] = Field(None, description="The invoice number.")
    invoice_date: Optional[str] = Field(None, description="The date of the invoice.")
    vendor: Optional[Vendor] = Field(None, description="Details of the vendor.")
    customer_name: Optional[str] = Field(None, description="The name of the customer.")
    customer_address: Optional[CustomerAddress] = Field(None, description="The address of the customer.")
    line_items: List[LineItem] = Field([], description="List of line items in the invoice.")
    subtotal: Optional[float] = Field(None, description="The subtotal amount before taxes and discounts.")
    tax_amount: Optional[float] = Field(None, description="The total tax amount.")
    total_amount: float = Field(description="The total amount due.")
    currency: Optional[str] = Field(None, description="The currency of the amounts (e.g., USD, EUR).")
    sustainability_metrics: Optional[SustainabilityMetrics] = Field(None, description="Sustainability metrics for the invoice.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "invoice_number": "INV-2023-001",
                    "invoice_date": "2023-01-15",
                    "vendor": {
                        "name": "Example Corp",
                        "address": {
                            "street": "123 Main St",
                            "city": "Anytown",
                            "zip_code": "12345",
                            "country": "USA"
                        },
                        "vat_id": "US123456789"
                    },
                    "customer_name": "Customer Name",
                    "customer_address": {
                        "street": "456 Oak Ave",
                        "city": "Otherville",
                        "zip_code": "67890",
                        "country": "USA"
                    },
                    "line_items": [
                        {
                            "description": "Product A",
                            "quantity": 2.0,
                            "unit_price": 10.0,
                            "total": 20.0,
                            "sustainability_score": 85.0
                        },
                        {
                            "description": "Service B",
                            "quantity": 1.0,
                            "unit_price": 50.0,
                            "total": 50.0,
                            "sustainability_score": 70.0
                        }
                    ],
                    "subtotal": 70.0,
                    "tax_amount": 7.0,
                    "total_amount": 77.0,
                    "currency": "USD",
                    "sustainability_metrics": {
                        "overall_esg_risk": "Low",
                        "green_vendor_flag": True,
                        "co2_intensive_items_flag": False
                    }
                }
            ]
        }
    }

class ExtractionResult(BaseModel):
    status: str
    invoice_data: Optional[Invoice] = None
    error_message: Optional[str] = None