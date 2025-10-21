# API Usage Guide

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the API Server

```bash
# Method 1: Direct Python
python server.py

# Method 2: Uvicorn CLI
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Method 3: Production with workers
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

**Output:**
```
===================================================================
Invoice Processing API
===================================================================

API Documentation: http://localhost:8000/docs
Alternative Docs: http://localhost:8000/redoc

Endpoints:
  POST   /api/v1/workflow/start           - Upload and start processing
  GET    /api/v1/workflow/{session_id}    - Get workflow status
  GET    /api/v1/workflow/{session_id}/state - Get detailed state
  POST   /api/v1/workflow/{session_id}/review-response - Submit review
  GET    /api/v1/invoices                 - Query saved invoices
  GET    /api/v1/health                   - Health check
  GET    /api/v1/stats                    - Session statistics

===================================================================
```

---

## API Endpoints

### 1. Start Workflow (Upload Invoice)

**Request:**
```bash
curl -X POST \
  -F "file=@invoice.jpg" \
  http://localhost:8000/api/v1/workflow/start
```

**Response (202 Accepted):**
```json
{
  "session_id": "inv_20241021_143022_a2b3c4",
  "status": "processing",
  "workflow_name": "InvoiceProcessingWorkflow",
  "created_at": "2024-10-21T14:30:22.123456"
}
```

**Notes:**
- File is saved to `uploads/` directory
- Returns immediately with session_id
- Processing happens in background
- Use session_id to poll for status

---

### 2. Get Workflow Status

**Request:**
```bash
curl http://localhost:8000/api/v1/workflow/{session_id}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/workflow/inv_20241021_143022_a2b3c4
```

**Response (200 OK - Processing):**
```json
{
  "session_id": "inv_20241021_143022_a2b3c4",
  "state": "processing",
  "current_step": 2,
  "current_step_name": "Analyze",
  "is_paused": false,
  "workflow_run_id": null,
  "paused_reason": null,
  "progress": {
    "steps_completed": 2,
    "total_steps": 5,
    "percentage": 40
  },
  "confidence_score": null,
  "invoice_data": null,
  "validation_errors": [],
  "created_at": "2024-10-21T14:30:22.123456",
  "updated_at": "2024-10-21T14:30:25.654321"
}
```

**Response (200 OK - Completed):**
```json
{
  "session_id": "inv_20241021_143022_a2b3c4",
  "state": "completed",
  "current_step": 5,
  "current_step_name": "Completed",
  "is_paused": false,
  "workflow_run_id": null,
  "paused_reason": null,
  "progress": {
    "steps_completed": 5,
    "total_steps": 5,
    "percentage": 100
  },
  "confidence_score": 0.95,
  "invoice_data": {
    "invoice_no": "51109338",
    "seller_name": "Andrews, Kirby and Valdez",
    "client_name": "Becker Ltd",
    "gross_worth_total": "6204.19",
    "line_items": [...]
  },
  "validation_errors": [],
  "created_at": "2024-10-21T14:30:22.123456",
  "updated_at": "2024-10-21T14:30:45.987654"
}
```

**States:**
- `initializing` - Session created, waiting to start
- `processing` - Workflow in progress
- `awaiting_human_input` - Paused for human review
- `completed` - Successfully processed and saved
- `rejected` - Rejected during human review
- `failed` - Error during processing

---

### 3. Get Detailed Workflow State

**Request:**
```bash
curl http://localhost:8000/api/v1/workflow/{session_id}/state
```

**Response (200 OK):**
```json
{
  "session_id": "inv_20241021_143022_a2b3c4",
  "workflow_state": {
    "session_id": "inv_20241021_143022_a2b3c4",
    "image_path": "uploads/inv_20241021_143022_a2b3c4.jpg",
    "state": "completed",
    "current_step": 5,
    "current_step_name": "Completed",
    "is_paused": false,
    "paused_reason": null,
    "paused_at_step": null,
    "workflow_run_id": null,
    "awaiting_approval": false,
    "approval_status": true,
    "review_notes": null,
    "reviewer_id": null,
    "extracted_text": "Invoice 51109338...",
    "invoice_data": {...},
    "confidence_score": 0.95,
    "validation_result": {...},
    "validation_errors": [],
    "invoice_id": 42,
    "error": null,
    "created_at": "2024-10-21T14:30:22.123456",
    "updated_at": "2024-10-21T14:30:45.987654"
  }
}
```

---

### 4. Submit Review Response (Human Approval)

**Request (Approve):**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "notes": "Invoice looks correct, approved for payment",
    "reviewer_id": "john.doe@company.com"
  }' \
  http://localhost:8000/api/v1/workflow/{session_id}/review-response
```

**Request (Reject):**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "approved": false,
    "notes": "Amount mismatch with PO, needs correction",
    "reviewer_id": "john.doe@company.com"
  }' \
  http://localhost:8000/api/v1/workflow/{session_id}/review-response
```

**Response (200 OK):**
```json
{
  "status": "acknowledged",
  "message": "Invoice approved and will be saved",
  "session_id": "inv_20241021_143022_a2b3c4"
}
```

**Or (Reject):**
```json
{
  "status": "acknowledged",
  "message": "Invoice rejected - not saving",
  "session_id": "inv_20241021_143022_a2b3c4"
}
```

---

### 5. Query Saved Invoices

**Request (All invoices):**
```bash
curl "http://localhost:8000/api/v1/invoices"
```

**Request (Pagination):**
```bash
curl "http://localhost:8000/api/v1/invoices?limit=20&offset=0"
```

**Response (200 OK):**
```json
{
  "invoices": [
    {
      "id": 42,
      "invoice_no": "51109338",
      "date_of_issue": "04/13/2013",
      "seller_name": "Andrews, Kirby and Valdez",
      "seller_address": "58861 Gonzalez Prairie, Lake Daniellefurt, IN 57228",
      "client_name": "Becker Ltd",
      "vat_percent": 10,
      "net_worth_total": 5640.17,
      "vat_total": 564.02,
      "gross_worth_total": 6204.19,
      "confidence_score": 0.95,
      "created_at": "2024-10-21T14:30:45.987654"
    }
  ],
  "total": 42,
  "page": 0,
  "limit": 20
}
```

---

### 6. Health Check

**Request:**
```bash
curl http://localhost:8000/api/v1/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-10-21T14:35:00.123456",
  "version": "1.0.0"
}
```

---

### 7. Get Statistics

**Request:**
```bash
curl http://localhost:8000/api/v1/stats
```

**Response (200 OK):**
```json
{
  "timestamp": "2024-10-21T14:35:00.123456",
  "statistics": {
    "total_sessions": 42,
    "completed": 38,
    "failed": 2,
    "paused": 2,
    "processing": 0,
    "success_rate": 90.48
  }
}
```

---

## Complete Workflow Example

### Step 1: Upload Invoice
```bash
SESSION_ID=$(curl -s -X POST -F "file=@invoice.jpg" \
  http://localhost:8000/api/v1/workflow/start | jq -r '.session_id')

echo "Session ID: $SESSION_ID"
```

### Step 2: Poll for Status (Every 2 seconds)
```bash
while true; do
  curl -s http://localhost:8000/api/v1/workflow/$SESSION_ID | jq '.'
  sleep 2
done
```

### Step 3: When Ready, Approve
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "notes": "Approved for processing",
    "reviewer_id": "user123"
  }' \
  http://localhost:8000/api/v1/workflow/$SESSION_ID/review-response
```

### Step 4: Query Results
```bash
curl "http://localhost:8000/api/v1/invoices?limit=10" | jq '.'
```

---

## Python Client Example

```python
import requests
import time
import json

BASE_URL = "http://localhost:8000/api/v1"

def process_invoice(image_path: str):
    """End-to-end invoice processing"""

    # 1. Upload invoice
    print(f"Uploading {image_path}...")
    with open(image_path, 'rb') as f:
        response = requests.post(
            f"{BASE_URL}/workflow/start",
            files={'file': f}
        )

    data = response.json()
    session_id = data['session_id']
    print(f"Session ID: {session_id}")

    # 2. Poll for completion
    print("Processing...")
    while True:
        response = requests.get(f"{BASE_URL}/workflow/{session_id}")
        status = response.json()

        print(f"Step {status['current_step']}/5: {status['current_step_name']}")

        if status['state'] == 'completed':
            print(f"✓ Completed! Invoice ID: {status.get('invoice_id')}")
            break
        elif status['state'] == 'failed':
            print(f"✗ Failed: {status.get('error')}")
            break
        elif status['state'] == 'awaiting_human_input':
            print(f"⏸ Waiting for human approval (confidence: {status['confidence_score']:.1%})")

            # Submit approval
            response = requests.post(
                f"{BASE_URL}/workflow/{session_id}/review-response",
                json={
                    "approved": True,
                    "notes": "Approved for processing",
                    "reviewer_id": "user123"
                }
            )
            print("Approval submitted")

        time.sleep(2)

    # 3. Get detailed state
    response = requests.get(f"{BASE_URL}/workflow/{session_id}/state")
    state = response.json()
    print(json.dumps(state['workflow_state'], indent=2))

if __name__ == "__main__":
    process_invoice("batch1-0.jpg")
```

---

## CLI Backward Compatibility

The CLI still works exactly as before:

```bash
# Process invoices from CLI (unchanged)
python main.py

# Output:
# Invoice Processing System - Batch1 Format
# [+] Found 2 batch1 invoice(s)
#     1. batch1-0.jpg
#     2. batch1-1.jpg
#
# Processing invoice: batch1-0.jpg
# ...
```

Both CLI and API can run simultaneously using the same database.

---

## Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "server.py"]
```

Build and run:
```bash
docker build -t invoice-api .
docker run -p 8000:8000 -v $(pwd)/uploads:/app/uploads invoice-api
```

---

## Troubleshooting

### API won't start
- Check Python version: `python --version` (requires 3.9+)
- Install dependencies: `pip install -r requirements.txt`
- Check port 8000 is available: `lsof -i :8000`

### File upload fails
- Check `uploads/` directory exists
- Verify file size < 10MB
- Use supported formats: jpg, jpeg, png

### Database errors
- Delete existing `.db` files: `rm *.db`
- Check disk space
- Verify DuckDB is installed: `pip install duckdb`

### Workflow stuck processing
- Check server logs for errors
- Verify Azure OpenAI credentials in `.env`
- Check API rate limits

---

## Next Steps

1. ✅ **Phase 1-3 Complete:** REST API with basic workflow management
2. ⏳ **Phase 4 (Future):** Streamlit UI for real-time monitoring
3. ⏳ **Phase 5 (Future):** WebSocket streaming for live updates
4. ⏳ **Phase 3 Full (Future):** Agno Agent-level HITL with continue_run()

For now, use this REST API with your client of choice (Postman, curl, Python requests, etc.).
