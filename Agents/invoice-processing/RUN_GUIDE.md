# How to Run the Invoice Processing System

## Prerequisites

1. **Python 3.9+** installed
2. **Environment variables** configured in `.env`:
   ```
   AZURE_OPENAI_API_KEY=your_key
   AZURE_OPENAI_ENDPOINT=your_endpoint
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
   AZURE_OPENAI_API_VERSION=2024-06-01
   DUCKDB_PATH=./invoices.db
   HUMAN_REVIEW_ENABLED=True
   AUTO_APPROVE_CONFIDENCE=0.90
   DEFAULT_CURRENCY=USD
   ```

## Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start API Server (Terminal 1)

```bash
python server.py
```

You should see:
```
===================================================================
Invoice Processing API
===================================================================

API Documentation: http://localhost:8000/docs
...
```

### Step 3: Start Streamlit UI (Terminal 2)

```bash
streamlit run streamlit_app.py
```

Streamlit will open automatically at `http://localhost:8501`

---

## Using the System

### 1. Upload Invoice (Streamlit UI)
- Go to **"🚀 Upload Invoice"** tab
- Select an invoice image (JPG/PNG)
- Click upload

### 2. Monitor Progress (Streamlit UI)
- Go to **"📊 Monitor Workflow"** tab
- Watch the workflow progress through 5 steps
- If confidence is low, you'll see a human review form

### 3. Approve/Reject (Streamlit UI)
- Review the invoice data
- Add notes if needed
- Click **"✅ Approve"** or **"❌ Reject"**

### 4. View Results (Streamlit UI)
- Go to **"📈 View Results"** tab
- Browse all processed invoices
- See statistics on success rate

---

## Alternative: CLI Only

If you only want to use the original CLI (no API/UI):

```bash
python main.py
```

This processes all `batch1-*.jpg` files in the current directory, just like before.

---

## Alternative: API Only (curl/Postman)

Use the API directly without Streamlit:

### 1. Upload Invoice
```bash
curl -X POST -F "file=@invoice.jpg" \
  http://localhost:8000/api/v1/workflow/start
```

Response:
```json
{
  "session_id": "inv_20241021_143022_a2b3c4",
  "status": "processing"
}
```

### 2. Check Status
```bash
curl http://localhost:8000/api/v1/workflow/inv_20241021_143022_a2b3c4
```

### 3. Approve Invoice
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "notes": "OK",
    "reviewer_id": "user@company.com"
  }' \
  http://localhost:8000/api/v1/workflow/inv_20241021_143022_a2b3c4/review-response
```

### 4. View Results
```bash
curl http://localhost:8000/api/v1/invoices
```

See `API_USAGE.md` for complete endpoint documentation.

---

## Running Everything Together

**Terminal 1: API Server**
```bash
python server.py
```

**Terminal 2: Streamlit UI**
```bash
streamlit run streamlit_app.py
```

**Terminal 3: CLI (Optional)**
```bash
python main.py
```

All three work simultaneously on the same database!

---

## Folder Structure

After running, you'll have:

```
invoice-processing/
├─ api/                    # API modules
├─ uploads/                # Uploaded invoice images
├─ invoices.db            # DuckDB database
├─ server.py              # FastAPI app (run this)
├─ streamlit_app.py       # Streamlit UI (run this)
├─ main.py                # CLI (or run this)
├─ requirements.txt       # Dependencies
└─ ...
```

---

## Troubleshooting

### "API Server is not running"
- Make sure `python server.py` is running in Terminal 1
- Check that port 8000 is available
- Try: `lsof -i :8000`

### "Module not found" error
- Install dependencies: `pip install -r requirements.txt`
- Make sure you're in the right directory

### File upload fails
- Check `uploads/` directory exists
- Verify file is JPG/PNG and < 10MB
- Make sure disk space is available

### Azure OpenAI errors
- Verify `.env` file has correct credentials
- Check AZURE_OPENAI_API_KEY is set
- Verify API version in .env matches your deployment

### Database errors
- Try deleting old `.db` files: `rm *.db`
- Ensure you have write permissions
- Check disk space

---

## Architecture Overview

```
User (Streamlit UI)
    ↓
FastAPI Server (port 8000)
    ↓
Session Manager (tracks state)
    ↓
Workflow Wrapper (calls existing code)
    ↓
Invoice Processing Pipeline
    ↓
DuckDB (stores results)
```

---

## What Each Component Does

### `server.py` (FastAPI)
- REST API on port 8000
- Handles file uploads
- Manages sessions
- Returns JSON responses
- Runs workflows in background

### `streamlit_app.py` (Streamlit UI)
- Web interface on port 8501
- Uploads files to API
- Polls workflow status
- Shows human review form
- Displays results

### `workflow.py` (Wrapper)
- Wraps existing main.py logic
- Doesn't modify existing code
- Tracks session state

### `main.py` (CLI)
- Original entry point
- Processes batch1-*.jpg files
- Shows terminal output
- Unchanged functionality

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/workflow/start` | POST | Upload and start |
| `/api/v1/workflow/{id}` | GET | Get status |
| `/api/v1/workflow/{id}/state` | GET | Full state |
| `/api/v1/workflow/{id}/review-response` | POST | Approve/reject |
| `/api/v1/invoices` | GET | Query results |
| `/api/v1/health` | GET | Health check |
| `/api/v1/stats` | GET | Statistics |

See `API_USAGE.md` for detailed examples.

---

## Next Steps

### Immediate
✅ Run API + Streamlit
✅ Test with sample invoices
✅ Verify workflow works

### Soon
- Deploy to server
- Add authentication
- Configure CORS for production

### Future
- WebSocket streaming
- Advanced dashboard
- Workflow templates

---

## Documentation

- **API Usage:** `API_USAGE.md`
- **Architecture:** `ARCHITECTURE.md`
- **Implementation:** `IMPLEMENTATION_GUIDE.md`
- **Summary:** `IMPLEMENTATION_SUMMARY.md`

---

## Support

For issues:
1. Check the documentation files above
2. Verify API is running: `curl http://localhost:8000/health`
3. Check logs in terminal windows
4. Verify `.env` configuration

---

## Summary

```bash
# Terminal 1
python server.py

# Terminal 2
streamlit run streamlit_app.py

# Open browser: http://localhost:8501
```

Done! 🎉
