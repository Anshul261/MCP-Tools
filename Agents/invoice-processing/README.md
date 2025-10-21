# Invoice Processing System

A complete invoice processing workflow using Agno AI agents, FastAPI backend, and Streamlit UI. Extracts invoice data from images, validates it, and stores in DuckDB with human-in-the-loop approval.

## Quick Start (3 Commands)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env  # Edit with your Azure OpenAI credentials

# 3. Run everything (3 terminals)
# Terminal 1:
python server.py

# Terminal 2:
streamlit run streamlit_app.py

# Terminal 3 (Optional - CLI only):
python main.py
```

Open browser: `http://localhost:8501` for Streamlit UI
API Docs: `http://localhost:8000/docs` for interactive API documentation

---

## System Overview

### Architecture

```
Invoice Image
    |
[Step 1] Extract (OCR via Azure Vision)
    |
[Step 2] Analyze (Structure into JSON)
    |
[Step 3] Validate (Quality check & confidence score)
    |
[Step 4] Review (Human approval if confidence < 90%)
    |
[Step 5] Persist (Save to DuckDB)
```

### Components

| Component | Purpose | Port |
|-----------|---------|------|
| **FastAPI Server** (`server.py`) | REST API for workflow management | 8000 |
| **Streamlit UI** (`streamlit_app.py`) | Web interface for testing | 8501 |
| **CLI** (`main.py`) | Legacy batch processing | - |
| **DuckDB** (`invoices.db`) | Data persistence | - |

---

## Features

- OCR Extraction - Azure OpenAI vision models extract text from invoice images
- Intelligent Parsing - Structures raw text into JSON with invoice & line items
- Validation - Validates data quality and calculates confidence scores
- Human-in-the-Loop - Pauses workflow if confidence < 90% for manual review
- REST API - Full API for programmatic access
- Real-time UI - Streamlit interface with live progress tracking
- Database - DuckDB with invoices and line_items tables
- Backward Compatible - Original CLI still works unchanged

---

## Configuration

### Environment Variables (.env)

```bash
# Azure OpenAI (Required)
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-06-01

# Database (Optional)
DUCKDB_PATH=./invoices.db

# Human Review (Optional)
HUMAN_REVIEW_ENABLED=True
AUTO_APPROVE_CONFIDENCE=0.90
DEFAULT_CURRENCY=USD
```

---

## Usage

### Option 1: Web UI (Recommended)

1. Upload Invoice - Go to "Upload Invoice" tab, select an image
2. Monitor Progress - Watch "Monitor Workflow" for real-time updates
3. Review if Needed - If confidence is low, approve or reject in the UI
4. View Results - Check "View Results" to see all processed invoices

### Option 2: REST API

```bash
# Upload invoice and start processing
SESSION_ID=$(curl -s -X POST -F "file=@invoice.jpg" \
  http://localhost:8000/api/v1/workflow/start | jq -r '.session_id')

echo "Session: $SESSION_ID"

# Check status
curl http://localhost:8000/api/v1/workflow/$SESSION_ID | jq

# Approve invoice
curl -X POST -H "Content-Type: application/json" \
  -d '{"approved": true, "notes": "OK", "reviewer_id": "user@company.com"}' \
  http://localhost:8000/api/v1/workflow/$SESSION_ID/review-response

# View results
curl http://localhost:8000/api/v1/invoices | jq
```

### Option 3: CLI (Legacy)

```bash
# Process all batch1-*.jpg files in current directory
python main.py
```

---

## API Endpoints

### Workflow Management

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/workflow/start` | Upload invoice and start processing |
| GET | `/api/v1/workflow/{session_id}` | Get workflow status |
| GET | `/api/v1/workflow/{session_id}/state` | Get detailed workflow state |
| POST | `/api/v1/workflow/{session_id}/review-response` | Submit human approval/rejection |

### Data Access

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/invoices` | Query saved invoices with line items |
| GET | `/api/v1/stats` | Get session statistics |
| GET | `/api/v1/health` | API health check |

Full API docs: http://localhost:8000/docs

---

## Database Schema

### invoices table

```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY,
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
```

### line_items table

```sql
CREATE TABLE line_items (
    id INTEGER PRIMARY KEY,
    invoice_id INTEGER,
    item_no INTEGER,
    description VARCHAR,
    qty DECIMAL(10,2),
    unit_measure VARCHAR,
    net_price DECIMAL(10,2),
    net_worth DECIMAL(12,2),
    vat_percent DECIMAL(5,2),
    gross_worth DECIMAL(12,2),
    FOREIGN KEY(invoice_id) REFERENCES invoices(id)
);
```

---

## Query Examples

```bash
# View all invoices with line item counts
uv run python -c "import duckdb; conn = duckdb.connect('invoices.db'); \
  result = conn.execute('SELECT i.invoice_no, COUNT(l.id) as items FROM invoices i \
  LEFT JOIN line_items l ON i.id = l.invoice_id GROUP BY i.id, i.invoice_no').fetchall(); \
  print(result)"

# View specific invoice with all line items
uv run python -c "import duckdb; conn = duckdb.connect('invoices.db'); \
  result = conn.execute('SELECT * FROM line_items WHERE invoice_id = 1 ORDER BY item_no').fetchall(); \
  print(result)"

# Get low-confidence invoices
uv run python -c "import duckdb; conn = duckdb.connect('invoices.db'); \
  result = conn.execute('SELECT invoice_no, confidence_score, gross_worth_total FROM invoices \
  WHERE confidence_score < 0.90 ORDER BY confidence_score').fetchall(); \
  print(result)"
```

---

## Workflow States

| State | Meaning |
|-------|---------|
| initializing | Session created, waiting to start |
| processing | Workflow in progress (Steps 1-5) |
| awaiting_human_input | Paused at Step 4 waiting for approval |
| completed | Successfully processed and saved |
| rejected | Rejected during human review |
| failed | Error during processing |

---

## Troubleshooting

### API Server is not running
```bash
python server.py
```
Check port 8000: `lsof -i :8000`

### Module not found
```bash
pip install -r requirements.txt
```

### File upload fails
- Ensure `uploads/` directory exists
- Verify file is JPG/PNG and < 10MB
- Check disk space available

### Azure OpenAI errors
- Verify `.env` file has correct credentials
- Check API key and endpoint URL
- Confirm API version matches your deployment

### Database errors
```bash
# Clear old database
rm invoices.db

# Verify line items exist
uv run python -c "import duckdb; conn = duckdb.connect('invoices.db'); \
  print(conn.execute('SELECT COUNT(*) FROM line_items').fetchone())"
```

---

## File Structure

```
invoice-processing/
├── server.py                 # FastAPI app entry point
├── streamlit_app.py         # Streamlit UI
├── main.py                  # CLI batch processing
├── workflow.py              # Agno workflow with 5 steps
├── models.py                # Pydantic data models
├── config.py                # Configuration from .env
├── api/
│   ├── routes.py            # API endpoint definitions
│   ├── models.py            # API request/response schemas
│   └── session_manager.py   # Session state management
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── invoices.db             # DuckDB database (auto-created)
├── uploads/                # Uploaded invoice images
└── README.md               # This file
```

---

## Development

### Running Tests

```bash
# Test API endpoint
curl http://localhost:8000/api/v1/health

# Test workflow
curl -X POST -F "file=@sample.jpg" http://localhost:8000/api/v1/workflow/start
```

### Checking Logs

- API server logs (if running in terminal)
- Streamlit logs (automatic in browser)
- Check uploads/ for saved images
- Check invoices.db for data

### Adding New Features

1. New API Endpoint - Add to `api/routes.py`
2. New Workflow Step - Add executor in `workflow.py`
3. New UI Page - Add to `streamlit_app.py` with new sidebar option
4. Database Schema Change - Update `models.py` and re-initialize

---

## Performance Notes

- Average processing time per invoice: 5-15 seconds
- Database queries optimized with proper indexing
- API handles ~10 concurrent uploads
- Streamlit UI refreshes every 2 seconds during processing
- Line items displayed in consolidated table format

---

## Support & Documentation

- API Interactive Docs: http://localhost:8000/docs
- Streamlit Settings Tab: Check API status and configuration
- Database Inspector: Use DuckDB command line or Python client
