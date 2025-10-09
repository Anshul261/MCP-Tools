# Invoice Processing System with Human-in-the-Loop

Complete invoice processing workflow using Agno AI agents and DuckDB for persistence.

## Architecture

```
Invoice Image → Extraction Agent → Analysis Agent → Validation Agent → [Human Review?] → DuckDB
```

## Files

- `models.py` - Pydantic data models for invoices and line items
- `config.py` - Configuration management from .env
- `main.py` - All agents and orchestration logic
- `invoices.db` - DuckDB database (auto-created)

## Features

- OCR text extraction from invoice images using Azure OpenAI vision models
- Intelligent parsing and structuring into database format
- Confidence scoring and validation
- Optional human-in-the-loop review with configurable auto-approval threshold
- DuckDB persistence for invoices and line items
- Handles missing fields gracefully
- Supports multiple invoice formats

## Configuration

Edit `.env` file:

```bash
# Azure OpenAI (Required)
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment

# Database (Optional)
DUCKDB_PATH=./invoices.db

# Human Review (Optional)
HUMAN_REVIEW_ENABLED=True
AUTO_APPROVE_CONFIDENCE=0.90
DEFAULT_CURRENCY=USD
```

## Usage

```bash
python main.py
```

The system will:
1. Find all .jpg and .png files in the current directory
2. Process each invoice through the complete workflow
3. Request human review if confidence < threshold (when enabled)
4. Save approved invoices to DuckDB

## Human Review

When `HUMAN_REVIEW_ENABLED=True`:
- Invoices with confidence >= `AUTO_APPROVE_CONFIDENCE` are auto-approved
- Lower confidence invoices require manual review via CLI prompt
- Review shows extracted data, line items, and financial summary
- Options: approve (yes), reject (no), or edit (not yet implemented)

When `HUMAN_REVIEW_ENABLED=False`:
- All invoices are auto-approved regardless of confidence score

## Database Schema

### invoices table
- Invoice header information (number, date, parties, totals)
- Metadata (confidence score, extraction timestamp)

### line_items table
- Individual line items with FK to invoices
- Item details (description, quantity, price, tax, total)

## Query Examples

```sql
-- View all invoices
SELECT * FROM invoices;

-- View invoice with line items
SELECT
    i.invoice_number,
    i.total_amount,
    l.description,
    l.quantity,
    l.total
FROM invoices i
JOIN line_items l ON i.id = l.invoice_id
WHERE i.invoice_number = '51109338';

-- Invoices requiring review (low confidence)
SELECT invoice_number, confidence_score, total_amount
FROM invoices
WHERE confidence_score < 0.90
ORDER BY confidence_score ASC;
```

## Fixes Applied

1. Made `invoice_number`, `invoice_date`, and `client_name` optional (some invoices don't have them)
2. Fixed database schema to use `AUTOINCREMENT` for primary keys
3. Improved analysis agent to handle missing fields with "UNKNOWN" fallback
4. Enhanced extraction instructions for better OCR accuracy

## Notes

- System handles invoices with missing invoice numbers/dates
- Flexible field extraction for non-standard formats
- All monetary values stored as decimals
- Timestamps track when invoices were processed
