"""
Invoice Processing System with Human-in-the-Loop
Specialized for batch1 invoice format (Invoice 51109338)
Workflow: Image → Extract → Analyze → Validate → [Review] → Persist to DuckDB
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from agno.agent import Agent
from agno.media import Image
from agno.models.azure import AzureOpenAI
from agno.tools.duckdb import DuckDbTools
from config import Config
from models import InvoiceData, InvoiceLineItem

# ============================================================================
# Database Setup
# ============================================================================


def initialize_database():
    """Initialize DuckDB database with invoice schema for batch1 format"""
    db_tools = DuckDbTools(db_path=Config.DUCKDB_PATH)

    # Create invoices table
    invoices_schema = """
    CREATE SEQUENCE IF NOT EXISTS invoices_seq START 1;
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY DEFAULT nextval('invoices_seq'),
        invoice_no VARCHAR,
        date_of_issue VARCHAR,
        seller_name VARCHAR,
        seller_address VARCHAR,
        seller_tax_id VARCHAR,
        seller_iban VARCHAR,
        client_name VARCHAR,
        client_address VARCHAR,
        client_tax_id VARCHAR,
        vat_percent DECIMAL(5,2),
        net_worth_total DECIMAL(12,2),
        vat_total DECIMAL(12,2),
        gross_worth_total DECIMAL(12,2),
        confidence_score DECIMAL(3,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    # Create line_items table
    line_items_schema = """
    CREATE SEQUENCE IF NOT EXISTS line_items_seq START 1;
    CREATE TABLE IF NOT EXISTS line_items (
        id INTEGER PRIMARY KEY DEFAULT nextval('line_items_seq'),
        invoice_id INTEGER,
        item_no INTEGER,
        description TEXT,
        qty DECIMAL(10,2),
        unit_measure VARCHAR,
        net_price DECIMAL(10,2),
        net_worth DECIMAL(12,2),
        vat_percent DECIMAL(5,2),
        gross_worth DECIMAL(12,2),
        FOREIGN KEY (invoice_id) REFERENCES invoices(id)
    );
    """

    # Execute schema creation
    db_tools.connection.execute(invoices_schema)
    db_tools.connection.execute(line_items_schema)

    print("[+] Database initialized successfully")
    return db_tools


# ============================================================================
# Agents
# ============================================================================


def create_extraction_agent():
    """Agent for OCR and text extraction from invoice images"""
    return Agent(
        name="ExtractionAgent",
        model=AzureOpenAI(
            id=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            azure_deployment=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
        ),
        instructions="""You are an expert OCR agent specializing in invoice text extraction.

Extract ALL text from this invoice image with perfect accuracy. The invoice has this structure:

1. Header: Invoice no and Date of issue
2. Seller section: Company name, address, Tax Id, IBAN
3. Client section: Company name, address, Tax Id
4. ITEMS table with columns: No., Description, Qty, UM, Net price, Net worth, VAT [%], Gross worth
5. SUMMARY section with: VAT [%], Net worth, VAT, Gross worth
6. Total row with final amounts

Extract every single piece of information exactly as it appears. Preserve all numbers, percentages, and text precisely.""",
        markdown=True,
    )


def create_analysis_agent():
    """Agent for analyzing and structuring extracted text into JSON format"""
    return Agent(
        name="AnalysisAgent",
        model=AzureOpenAI(
            id=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            azure_deployment=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
        ),
        instructions="""You are an expert data analyst specializing in invoice processing.

Parse the extracted invoice text into this EXACT JSON structure:

{{
    "invoice_no": "string",
    "date_of_issue": "string (MM/DD/YYYY format)",
    "seller_name": "string",
    "seller_address": "string (full address on one line)",
    "seller_tax_id": "string",
    "seller_iban": "string",
    "client_name": "string",
    "client_address": "string (full address on one line)",
    "client_tax_id": "string",
    "line_items": [
        {{
            "item_no": integer,
            "description": "string",
            "qty": "decimal string (e.g., '3.00')",
            "unit_measure": "string (e.g., 'each')",
            "net_price": "decimal string (e.g., '209.00')",
            "net_worth": "decimal string (e.g., '627.00')",
            "vat_percent": "decimal string (e.g., '10')",
            "gross_worth": "decimal string (e.g., '689.70')"
        }}
    ],
    "vat_percent": "decimal string",
    "net_worth_total": "decimal string",
    "vat_total": "decimal string",
    "gross_worth_total": "decimal string"
}}

CRITICAL RULES:
1. Extract ALL line items from the ITEMS table (there are 7 items)
2. For item 7 which has unusual formatting, parse it carefully
3. Use decimal format with 2 places: "209.00" not "209"
4. Remove any commas from numbers: "1 394,67" becomes "1394.67"
5. Get summary totals from the SUMMARY section at bottom
6. Return ONLY the JSON object, no markdown, no explanation""",
        markdown=False,
    )


def create_validation_agent():
    """Agent for validating data quality and calculating confidence scores"""
    return Agent(
        name="ValidationAgent",
        model=AzureOpenAI(
            id=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            azure_deployment=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
        ),
        instructions="""You are a data quality expert specializing in invoice validation.

Validate this invoice data for batch1 format:

VALIDATION CHECKS:
1. All required fields present (invoice_no, date_of_issue, seller info, client info)
2. Exactly 7 line items extracted
3. Mathematical accuracy:
   - Each line item: net_worth = qty * net_price
   - Each line item: gross_worth = net_worth * (1 + vat_percent/100)
   - Summary: net_worth_total = sum of all line item net_worth values
   - Summary: vat_total = net_worth_total * (vat_percent/100)
   - Summary: gross_worth_total = net_worth_total + vat_total
4. All decimal values properly formatted

Calculate confidence score (0.0 to 1.0):
- All fields present: +0.30
- Correct number of line items (7): +0.20
- Mathematical accuracy within 1% tolerance: +0.30
- Proper formatting: +0.20

Return JSON:
{{
    "is_valid": true/false,
    "confidence_score": 0.0-1.0,
    "validation_errors": ["list of errors"],
    "warnings": ["list of warnings"],
    "line_items_count": integer
}}""",
        markdown=False,
    )


# ============================================================================
# Human-in-the-Loop Review
# ============================================================================


def human_review(
    invoice_data: InvoiceData, extracted_text: str
) -> tuple[bool, Optional[InvoiceData]]:
    """
    Present invoice data to human for review and approval
    Returns: (approved: bool, modified_data: Optional[InvoiceData])
    """
    print("\n" + "=" * 80)
    print("HUMAN REVIEW REQUIRED")
    print("=" * 80)

    print(f"\nInvoice No: {invoice_data.invoice_no}")
    print(f"Date: {invoice_data.date_of_issue}")
    print(f"Confidence Score: {invoice_data.confidence_score:.2%}")

    print(f"\nSeller: {invoice_data.seller_name}")
    print(f"  Address: {invoice_data.seller_address}")
    print(f"  Tax ID: {invoice_data.seller_tax_id}")
    print(f"  IBAN: {invoice_data.seller_iban}")

    print(f"\nClient: {invoice_data.client_name}")
    print(f"  Address: {invoice_data.client_address}")
    print(f"  Tax ID: {invoice_data.client_tax_id}")

    print(f"\nLine Items ({len(invoice_data.line_items)}):")
    for item in invoice_data.line_items:
        print(f"\n  {item.item_no}. {item.description}")
        print(f"     Qty: {item.qty} {item.unit_measure}")
        print(f"     Net Price: {item.net_price} | Net Worth: {item.net_worth}")
        print(f"     VAT: {item.vat_percent}% | Gross Worth: {item.gross_worth}")

    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print(f"VAT Rate: {invoice_data.vat_percent}%")
    print(f"Net Worth Total: $ {invoice_data.net_worth_total}")
    print(f"VAT Total: $ {invoice_data.vat_total}")
    print(f"Gross Worth Total: $ {invoice_data.gross_worth_total}")
    print(f"{'=' * 80}")

    while True:
        response = input("\nApprove this invoice? (yes/no): ").strip().lower()

        if response in ["yes", "y"]:
            return True, invoice_data
        elif response in ["no", "n"]:
            feedback = input("Reason for rejection: ").strip()
            print(f"[!] Invoice rejected: {feedback}")
            return False, None
        else:
            print("Invalid response. Please enter 'yes' or 'no'.")


# ============================================================================
# Database Persistence
# ============================================================================


def save_to_database(invoice_data: InvoiceData, db_tools: DuckDbTools) -> int:
    """Save approved invoice to DuckDB and return invoice ID"""

    # Insert invoice record using parameterized query
    invoice_insert = """
    INSERT INTO invoices (
        invoice_no, date_of_issue, seller_name, seller_address, seller_tax_id,
        seller_iban, client_name, client_address, client_tax_id,
        vat_percent, net_worth_total, vat_total, gross_worth_total, confidence_score
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    db_tools.connection.execute(
        invoice_insert,
        [
            invoice_data.invoice_no,
            invoice_data.date_of_issue,
            invoice_data.seller_name,
            invoice_data.seller_address,
            invoice_data.seller_tax_id,
            invoice_data.seller_iban,
            invoice_data.client_name,
            invoice_data.client_address,
            invoice_data.client_tax_id,
            float(invoice_data.vat_percent),
            float(invoice_data.net_worth_total),
            float(invoice_data.vat_total),
            float(invoice_data.gross_worth_total),
            invoice_data.confidence_score,
        ],
    )

    # Get the inserted invoice ID
    result = db_tools.connection.execute("SELECT MAX(id) FROM invoices;").fetchone()
    invoice_id = result[0]

    # Insert line items using parameterized query
    line_item_insert = """
    INSERT INTO line_items (
        invoice_id, item_no, description, qty, unit_measure,
        net_price, net_worth, vat_percent, gross_worth
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    for item in invoice_data.line_items:
        db_tools.connection.execute(
            line_item_insert,
            [
                invoice_id,
                item.item_no,
                item.description,
                float(item.qty),
                item.unit_measure,
                float(item.net_price),
                float(item.net_worth),
                float(item.vat_percent),
                float(item.gross_worth),
            ],
        )

    print(f"\n[+] Invoice saved to database with ID: {invoice_id}")
    return invoice_id


# ============================================================================
# Main Workflow
# ============================================================================


def process_invoice(image_path: str, db_tools: DuckDbTools) -> Optional[int]:
    """
    Process a single invoice through the complete workflow
    Returns: invoice_id if successful, None if rejected or failed
    """
    print("\n" + "=" * 80)
    print(f"PROCESSING INVOICE: {Path(image_path).name}")
    print("=" * 80)

    # Verify image exists
    if not Path(image_path).exists():
        print(f"[!] Error: Image not found at {image_path}")
        return None

    # Step 1: Extract text from image
    print("\n[1/5] Extracting text from invoice image...")
    extraction_agent = create_extraction_agent()

    extraction_result = extraction_agent.run(
        "Extract all text from this invoice image with perfect accuracy.",
        images=[Image(filepath=image_path)],
    )
    extracted_text = extraction_result.content
    print(f"[+] Extracted {len(extracted_text)} characters")

    # Step 2: Analyze and structure data
    print("\n[2/5] Analyzing and structuring invoice data...")
    analysis_agent = create_analysis_agent()

    analysis_result = analysis_agent.run(
        f"Parse this invoice text into the exact JSON structure specified:\n\n{extracted_text}"
    )

    # Parse JSON response
    try:
        response_text = analysis_result.content.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]

        invoice_dict = json.loads(response_text.strip())
        print("[+] Successfully structured invoice data")
        print(f"[+] Found {len(invoice_dict.get('line_items', []))} line items")
    except json.JSONDecodeError as e:
        print(f"[!] Error parsing JSON response: {e}")
        print(f"Response was: {analysis_result.content[:1000]}")
        return None

    # Step 3: Validate data
    print("\n[3/5] Validating invoice data...")
    validation_agent = create_validation_agent()

    validation_result = validation_agent.run(
        f"Validate this invoice data:\n\n{json.dumps(invoice_dict, indent=2)}"
    )

    try:
        validation_response = validation_result.content.strip()
        if validation_response.startswith("```"):
            validation_response = validation_response.split("```")[1]
            if validation_response.startswith("json"):
                validation_response = validation_response[4:]

        validation_data = json.loads(validation_response.strip())
        confidence_score = validation_data.get("confidence_score", 0.5)

        invoice_dict["confidence_score"] = confidence_score

        print(f"[+] Validation complete - Confidence: {confidence_score:.2%}")
        print(
            f"[+] Line items count: {validation_data.get('line_items_count', 'unknown')}"
        )

        if validation_data.get("validation_errors"):
            print(f"[!] Validation errors:")
            for error in validation_data["validation_errors"]:
                print(f"    - {error}")
        if validation_data.get("warnings"):
            print(f"[!] Warnings:")
            for warning in validation_data["warnings"]:
                print(f"    - {warning}")

    except json.JSONDecodeError:
        print("[!] Could not parse validation response, using default confidence 0.5")
        invoice_dict["confidence_score"] = 0.5
        confidence_score = 0.5

    # Create InvoiceData object
    try:
        invoice_data = InvoiceData(**invoice_dict)
    except Exception as e:
        print(f"[!] Error creating InvoiceData object: {e}")
        print(f"Data: {json.dumps(invoice_dict, indent=2)}")
        return None

    # Step 4: Human review (if enabled)
    print("\n[4/5] Review process...")

    if Config.HUMAN_REVIEW_ENABLED:
        if confidence_score >= Config.AUTO_APPROVE_CONFIDENCE:
            print(
                f"[+] Auto-approved (confidence {confidence_score:.2%} >= {Config.AUTO_APPROVE_CONFIDENCE:.2%})"
            )
            approved = True
            final_data = invoice_data
        else:
            print(
                f"[!] Manual review required (confidence {confidence_score:.2%} < {Config.AUTO_APPROVE_CONFIDENCE:.2%})"
            )
            approved, final_data = human_review(invoice_data, extracted_text)
    else:
        print("[+] Human review disabled - auto-approving")
        approved = True
        final_data = invoice_data

    if not approved or final_data is None:
        print("\n[!] Invoice processing cancelled - not approved")
        return None

    # Step 5: Save to database
    print("\n[5/5] Saving to database...")
    invoice_id = save_to_database(final_data, db_tools)

    print("\n" + "=" * 80)
    print(f"[+] INVOICE PROCESSING COMPLETE - ID: {invoice_id}")
    print("=" * 80)

    return invoice_id


# ============================================================================
# Main Entry Point
# ============================================================================


def main():
    """Main entry point"""
    print("\nInvoice Processing System - Batch1 Format")
    print("=" * 80)

    # Display configuration
    Config.display()

    # Initialize database
    db_tools = initialize_database()

    # Find all batch1 invoices
    invoice_dir = Path(".")
    batch1_invoices = sorted(invoice_dir.glob("batch1-*.jpg"))

    if not batch1_invoices:
        print("[!] No batch1 invoice images found (batch1-*.jpg)")
        return

    print(f"\n[+] Found {len(batch1_invoices)} batch1 invoice(s)")
    for idx, inv in enumerate(batch1_invoices, 1):
        print(f"    {idx}. {inv.name}")

    # Process each invoice
    results = []
    for invoice_path in batch1_invoices:
        try:
            invoice_id = process_invoice(str(invoice_path), db_tools)
            results.append((invoice_path.name, invoice_id))
        except Exception as e:
            print(f"\n[!] Error processing {invoice_path.name}: {e}")
            import traceback

            traceback.print_exc()
            results.append((invoice_path.name, None))

    # Summary
    print("\n" + "=" * 80)
    print("PROCESSING SUMMARY")
    print("=" * 80)
    successful = sum(1 for _, id in results if id is not None)
    print(f"[+] Successful: {successful}/{len(results)}")
    print(f"[!] Failed: {len(results) - successful}/{len(results)}")

    if successful > 0:
        print("\n[+] Successfully processed invoices:")
        for name, inv_id in results:
            if inv_id:
                print(f"    - {name}: ID {inv_id}")

        print("\n[+] Query the database:")
        print(f"   SELECT * FROM invoices;")
        print(f"   SELECT * FROM line_items;")
        print(f"   SELECT i.invoice_no, i.gross_worth_total, COUNT(l.id) as items")
        print(f"   FROM invoices i LEFT JOIN line_items l ON i.id = l.invoice_id")
        print(f"   GROUP BY i.id, i.invoice_no, i.gross_worth_total;")


if __name__ == "__main__":
    main()
