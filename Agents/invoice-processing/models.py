"""
Pydantic models for invoice data structure
Optimized for batch1 invoice format (Invoice 51109338)
"""

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class InvoiceLineItem(BaseModel):
    """Individual line item in an invoice"""

    item_no: int = Field(..., description="Line item number")
    description: str = Field(..., description="Item description")
    qty: Decimal = Field(..., description="Quantity of items")
    unit_measure: str = Field(..., description="Unit of measure (e.g., each)")
    net_price: Decimal = Field(..., description="Price per unit before VAT")
    net_worth: Decimal = Field(..., description="Total net value (qty * net_price)")
    vat_percent: Decimal = Field(..., description="VAT percentage (e.g., 10)")
    gross_worth: Decimal = Field(..., description="Total with VAT included")


class InvoiceData(BaseModel):
    """Structured invoice data model for batch1 format"""

    # Invoice identifiers
    invoice_no: str = Field(..., description="Invoice number")
    date_of_issue: str = Field(..., description="Date of issue")

    # Seller information
    seller_name: str = Field(..., description="Seller company name")
    seller_address: str = Field(..., description="Seller full address")
    seller_tax_id: str = Field(..., description="Seller tax ID")
    seller_iban: str = Field(..., description="Seller IBAN")

    # Client information
    client_name: str = Field(..., description="Client company name")
    client_address: str = Field(..., description="Client full address")
    client_tax_id: str = Field(..., description="Client tax ID")

    # Line items
    line_items: List[InvoiceLineItem] = Field(
        ..., description="List of invoice line items"
    )

    # Summary totals
    vat_percent: Decimal = Field(..., description="VAT percentage applied")
    net_worth_total: Decimal = Field(..., description="Total net worth (before VAT)")
    vat_total: Decimal = Field(..., description="Total VAT amount")
    gross_worth_total: Decimal = Field(..., description="Total gross worth (with VAT)")

    # Metadata
    confidence_score: float = Field(
        default=0.0, description="Extraction confidence score (0-1)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "invoice_no": "51109338",
                "date_of_issue": "04/13/2013",
                "seller_name": "Andrews, Kirby and Valdez",
                "seller_address": "58861 Gonzalez Prairie, Lake Daniellefurt, IN 57228",
                "seller_tax_id": "945-82-2137",
                "seller_iban": "GB75MCRL06841367619257",
                "client_name": "Becker Ltd",
                "client_address": "8012 Stewart Summit Apt. 455, North Douglas, AZ 95355",
                "client_tax_id": "942-80-0517",
                "line_items": [
                    {
                        "item_no": 1,
                        "description": "CLEARANCE! Fast Dell Desktop Computer PC DUAL CORE WINDOWS 10 4/8/16GB RAM",
                        "qty": "3.00",
                        "unit_measure": "each",
                        "net_price": "209.00",
                        "net_worth": "627.00",
                        "vat_percent": "10",
                        "gross_worth": "689.70",
                    }
                ],
                "vat_percent": "10",
                "net_worth_total": "5640.17",
                "vat_total": "564.02",
                "gross_worth_total": "6204.19",
                "confidence_score": 0.95,
            }
        }


class ReviewRequest(BaseModel):
    """Model for human review request"""

    invoice_data: InvoiceData
    extracted_text: str
    image_path: str
    requires_review: bool = True
    review_reason: Optional[str] = None


class ReviewResponse(BaseModel):
    """Model for human review response"""

    approved: bool
    modified_data: Optional[InvoiceData] = None
    feedback: Optional[str] = None
