# Enhanced Invoice Processing Architecture

## Overview

This document describes the refactored architecture using **Agno Workflows + AgentOS + Human-in-the-Loop + Streamlit**.

### Core Innovation

Instead of a linear pipeline, we now use:
1. **Agno Workflow** - Named steps for orchestration
2. **AgentOS** - FastAPI integration with agent lifecycle management
3. **HITL at Agent Level** - `requires_user_input` tools for pausing execution
4. **Custom FastAPI Routes** - RESTful API for workflow control
5. **Streamlit UI** - Real-time monitoring and human review interface

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────┐    ┌──────────────────────────┐               │
│  │   Streamlit UI           │    │   Web Browser (REST)     │               │
│  │  - Upload invoice        │    │  - API testing           │               │
│  │  - Monitor workflow      │    │  - Direct endpoints      │               │
│  │  - Human review UI       │    │  - WebSocket streaming   │               │
│  │  - View results          │    │                          │               │
│  └──────────────┬───────────┘    └──────────────┬───────────┘               │
│                 │                               │                           │
│                 └───────────────┬───────────────┘                           │
│                                 │                                           │
└─────────────────────────────────┼───────────────────────────────────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │   HTTP/WebSocket Layer     │
                    └─────────────┬──────────────┘
                                  │
┌─────────────────────────────────┼───────────────────────────────────────────┐
│                           API LAYER (FastAPI)                               │
├─────────────────────────────────┼───────────────────────────────────────────┤
│                                 │                                            │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                    AgentOS Application                             │     │
│  │  ┌──────────────────────────────────────────────────────────────┐ │     │
│  │  │  Custom FastAPI Routes (base_app)                           │ │     │
│  │  │  ├─ POST   /api/v1/workflow/start                           │ │     │
│  │  │  ├─ GET    /api/v1/workflow/{session_id}                    │ │     │
│  │  │  ├─ POST   /api/v1/workflow/{session_id}/review-response    │ │     │
│  │  │  ├─ GET    /api/v1/workflow/{session_id}/state              │ │     │
│  │  │  ├─ WS     /ws/workflow/{session_id}                         │ │     │
│  │  │  ├─ GET    /api/v1/invoices (query results)                 │ │     │
│  │  │  └─ GET    /health                                          │ │     │
│  │  └──────────────────────────────────────────────────────────────┘ │     │
│  │                                                                     │     │
│  │  ┌──────────────────────────────────────────────────────────────┐ │     │
│  │  │  Workflow Orchestration Layer                               │ │     │
│  │  │  ┌────────────────────────────────────────────────────────┐ │ │     │
│  │  │  │ Workflow: InvoiceProcessingWorkflow                   │ │ │     │
│  │  │  │                                                        │ │ │     │
│  │  │  │ Steps:                                                 │ │ │     │
│  │  │  │ 1. Extract Step → Agent(OCR)                          │ │ │     │
│  │  │  │ 2. Analyze Step → Agent(JSON Parser)                  │ │ │     │
│  │  │  │ 3. Validate Step → Agent(Validator)                   │ │ │     │
│  │  │  │ 4. Review Step → Agent(Reviewer with HITL)            │ │ │     │
│  │  │  │ 5. Persist Step → Custom Function(Save to DB)         │ │ │     │
│  │  │  └────────────────────────────────────────────────────────┘ │ │     │
│  │  └──────────────────────────────────────────────────────────────┘ │     │
│  │                                                                     │     │
│  │  ┌──────────────────────────────────────────────────────────────┐ │     │
│  │  │  Session Manager                                            │ │     │
│  │  │  - Track active workflows                                   │ │     │
│  │  │  - Store paused states                                      │ │     │
│  │  │  - Manage run IDs and continuations                         │ │     │
│  │  └──────────────────────────────────────────────────────────────┘ │     │
│  │                                                                     │     │
│  │  ┌──────────────────────────────────────────────────────────────┐ │     │
│  │  │  Model Layer (Azure OpenAI)                                 │ │     │
│  │  └──────────────────────────────────────────────────────────────┘ │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                                │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  AgentOS Routes (auto-generated)                                   │     │
│  │  - /agents - List agents                                           │     │
│  │  - /agents/{agent_id}/runs - Agent runs                            │     │
│  │  - /docs - OpenAPI documentation                                   │     │
│  │  - /admin - AgentOS dashboard                                      │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────┼───────────────────────────────────────────┐
│                        PERSISTENCE LAYER                                    │
├─────────────────────────────────┼───────────────────────────────────────────┤
│                                 │                                            │
│  ┌──────────────────────┐   ┌───▼─────────────────┐   ┌────────────────┐   │
│  │  DuckDB              │   │  SQLiteDb           │   │   File Storage │   │
│  │ (Invoice Data)       │   │ (Session State)      │   │ (Uploaded      │   │
│  │                      │   │                      │   │  Images)       │   │
│  │ - invoices table     │   │ - workflow_sessions │   │                │   │
│  │ - line_items table   │   │ - paused_states     │   │                │   │
│  │ - audit_log table    │   │ - run_history       │   │                │   │
│  └──────────────────────┘   └────────────────────┘   └────────────────┘   │
│                                                                             │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Concepts

### 1. Human-in-the-Loop at Agent Level

Instead of external CLI prompts, we use Agno's built-in HITL:

```python
# Define a tool that requires user input (approval)
@tool(requires_user_input=True)
def approve_invoice(
    invoice_id: str,
    confidence_score: float,
    notes: str = ""
) -> str:
    """Request user approval for invoice processing.

    Args:
        invoice_id: The invoice ID to review
        confidence_score: Extraction confidence (0-1)
        notes: Review notes
    """
    # This tool causes the agent to PAUSE execution
    # API receives the pause event
    # Streamlit displays the UI
    # User provides input
    # API continues the run
    return f"Invoice {invoice_id} approved"
```

**Flow:**
1. Agent executing Step 4 (Review) encounters `approve_invoice` tool
2. Agent execution **pauses** (run marked as `is_paused=True`)
3. API detects pause and stores state
4. Streamlit polls API, gets pause event, displays review UI
5. User clicks "Approve/Reject"
6. Streamlit sends response to API via `/review-response`
7. API calls `agent.continue_run()` with user input
8. Workflow resumes and completes

---

### 2. Session Management

Each workflow execution has a **session_id**:

```
Session ID: "invoice_2024_001"
├─ workflow_run_id: "run_uuid_123"  (Agno RunOutput.run_id)
├─ current_step: 4 (Review)
├─ state: "paused_at_review"
├─ image_path: "uploads/invoice.jpg"
├─ extracted_data: {...}
├─ paused_tools: [approve_invoice]
├─ ui_state: "waiting_for_user_input"
└─ created_at: 2024-10-21T10:30:00Z
```

**Persistence:** Store in SQLiteDb with `workflow_sessions` table

---

### 3. Workflow Steps vs Agent Agents

| Entity | Purpose | Responsibility |
|---|---|---|
| **Workflow Step** | Orchestrate sequence | Call agent, capture output, pass to next step |
| **Agent with HITL** | Execute tasks | Extract/analyze data, pause for human input, continue |
| **Custom Function Step** | Non-agent logic | Save to DB, format response, side effects |

---

## Data Flow: Complete Example

### Scenario: Process invoice with low confidence requiring human review

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. UPLOAD PHASE                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ User (Streamlit) → POST /api/v1/workflow/start                         │
│                    {image_file: <binary>}                              │
│                    ↓                                                   │
│ API Route Handler                                                       │
│  - Save image to disk                                                  │
│  - Create session_id: "invoice_20241021_001"                           │
│  - Start workflow in background task                                   │
│  - Return {session_id, status: "processing"}                           │
│                    ↓                                                   │
│ Response → Streamlit (polling begins)                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 2. EXTRACTION PHASE (Step 1)                                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ Workflow Step: "Extract"                                               │
│ ├─ Agent: ExtractionAgent                                              │
│ └─ Tool: Azure Vision API (via agent)                                  │
│     ├─ Input: {image_path, instructions}                               │
│     ├─ Process: OCR text extraction                                    │
│     └─ Output: Raw text from invoice                                   │
│                                                                         │
│ Session State Update:                                                  │
│ └─ current_step: 1                                                     │
│    extracted_text: "Invoice 51109338..."                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 3. ANALYSIS PHASE (Step 2)                                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ Workflow Step: "Analyze"                                               │
│ ├─ Agent: AnalysisAgent                                                │
│ └─ Process:                                                            │
│     ├─ Input: {extracted_text}                                         │
│     ├─ LLM parses to JSON                                              │
│     └─ Output: Structured invoice data                                 │
│                                                                         │
│ Session State Update:                                                  │
│ └─ current_step: 2                                                     │
│    invoice_data: {invoice_no, seller_name, line_items: [...]}          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 4. VALIDATION PHASE (Step 3)                                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ Workflow Step: "Validate"                                              │
│ ├─ Agent: ValidationAgent                                              │
│ └─ Process:                                                            │
│     ├─ Input: {invoice_data}                                           │
│     ├─ Validate structure, math, required fields                       │
│     └─ Output: {is_valid, confidence_score, errors}                    │
│                                                                         │
│ Session State Update:                                                  │
│ └─ current_step: 3                                                     │
│    confidence_score: 0.75 (LOW - requires review)                      │
│    validation_result: {...}                                            │
│                                                                         │
│ ** DECISION POINT **                                                   │
│ IF confidence_score < AUTO_APPROVE_THRESHOLD (0.90)                    │
│    THEN proceed to Step 4 (Human Review)                               │
│    ELSE skip to Step 5 (Persist)                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 5. REVIEW PHASE (Step 4) - HUMAN-IN-THE-LOOP                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ Workflow Step: "Review"                                                │
│ ├─ Agent: ReviewAgent (with HITL tools)                                │
│ └─ Process:                                                            │
│     ├─ Agent runs with tool: approve_invoice()                         │
│     ├─ Tool marked with @tool(requires_user_input=True)                │
│     ├─ Agent prepares arguments for the tool:                          │
│     │   {invoice_id, data, confidence_score, notes}                    │
│     │                                                                  │
│     ├─ Agent execution PAUSES                                          │
│     │   RunOutput.is_paused = True                                     │
│     │   RunOutput.tools_requiring_user_input = [approve_invoice]       │
│     │                                                                  │
│     └─ Agent awaits human decision                                     │
│                                                                         │
│ Session State Update:                                                  │
│ ├─ current_step: 4                                                     │
│ ├─ state: "paused_at_review"                                           │
│ ├─ paused_run_id: "run_uuid_456"                                       │
│ ├─ ui_state: "waiting_for_approval"                                    │
│ └─ awaiting_tools: [approve_invoice]                                   │
│                                                                         │
│ ** API DETECTS PAUSE **                                                │
│ API Handler                                                            │
│  - Receives is_paused=True from workflow                               │
│  - Stores session state                                                │
│  - Marks session.state = "awaiting_human_input"                        │
│                                                                         │
│ ** STREAMLIT SHOWS REVIEW UI **                                        │
│ Streamlit                                                              │
│  - Polls GET /api/v1/workflow/{session_id}                             │
│  - Receives is_paused=True, state="awaiting_human_input"               │
│  - Renders approval card with:                                         │
│    ├─ Invoice details (seller, client, amount)                         │
│    ├─ Line items preview                                               │
│    ├─ Confidence score: 75%                                            │
│    ├─ Validation warnings/errors                                       │
│    ├─ Approve button                                                   │
│    ├─ Reject button                                                    │
│    └─ Notes textarea                                                   │
│                                                                         │
│ User Interaction                                                        │
│  - User reviews data                                                   │
│  - User clicks "Approve" with optional notes                           │
│                                                                         │
│ ** STREAMLIT SENDS APPROVAL RESPONSE **                                │
│ Streamlit → POST /api/v1/workflow/{session_id}/review-response         │
│            {approval: true, notes: "Looks good"}                       │
│                                                                         │
│ ** API RESUMES WORKFLOW **                                             │
│ API Handler                                                            │
│  - Receives approval response                                          │
│  - Updates session.approval = true                                     │
│  - Calls agent.continue_run(                                           │
│      run_id=paused_run_id,                                             │
│      updated_tools=[approve_invoice_with_result]                       │
│    )                                                                   │
│  - Agent continues execution with the user input                       │
│                                                                         │
│ ** AGENT RESUMES **                                                    │
│ Agent ResumesAgent                                                     │
│  - Sees approve_invoice tool now has user_input_value=True             │
│  - Continues past the paused point                                     │
│  - Completes Step 4                                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 6. PERSISTENCE PHASE (Step 5)                                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ Workflow Step: "Persist"                                               │
│ ├─ Executor: Custom function (not an agent)                            │
│ └─ Process:                                                            │
│     ├─ Input: {invoice_data, approval_status}                          │
│     ├─ Save to DuckDB invoices table                                   │
│     ├─ Save line_items to DuckDB                                       │
│     ├─ Record in audit log                                             │
│     └─ Output: {invoice_id, timestamp}                                 │
│                                                                         │
│ Session State Update:                                                  │
│ ├─ current_step: 5                                                     │
│ ├─ state: "completed"                                                  │
│ ├─ invoice_id: 42                                                      │
│ └─ completed_at: 2024-10-21T10:35:00Z                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 7. COMPLETION PHASE                                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ Streamlit polls GET /api/v1/workflow/{session_id}                       │
│  - Receives state="completed", invoice_id=42                           │
│  - Displays success message                                            │
│  - Shows "View Invoice" link                                           │
│                                                                         │
│ User can:                                                              │
│  - View the saved invoice in the database                              │
│  - Download extracted data as JSON/CSV                                 │
│  - Process another invoice                                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

### Base URL
```
http://localhost:8000
```

### Custom Routes (base_app)

#### 1. Start Workflow
```http
POST /api/v1/workflow/start
Content-Type: multipart/form-data

file: <invoice image>

Response (202 Accepted):
{
  "session_id": "invoice_20241021_001",
  "status": "processing",
  "created_at": "2024-10-21T10:30:00Z",
  "workflow_name": "InvoiceProcessingWorkflow"
}
```

#### 2. Get Workflow Status
```http
GET /api/v1/workflow/{session_id}

Response (200 OK):
{
  "session_id": "invoice_20241021_001",
  "state": "awaiting_human_input",  // or "processing", "completed", "failed"
  "current_step": 4,
  "current_step_name": "Review",
  "is_paused": true,
  "workflow_run_id": "run_uuid_456",
  "paused_reason": "Awaiting user approval",
  "progress": {
    "steps_completed": 3,
    "total_steps": 5,
    "percentage": 60
  },
  "invoice_data": {
    "invoice_no": "51109338",
    "seller_name": "Andrews, Kirby and Valdez",
    "line_items": [...],
    "confidence_score": 0.75
  },
  "validation_errors": ["Low confidence score"],
  "created_at": "2024-10-21T10:30:00Z",
  "updated_at": "2024-10-21T10:32:00Z"
}
```

#### 3. Submit Review Response (HITL)
```http
POST /api/v1/workflow/{session_id}/review-response
Content-Type: application/json

{
  "approved": true,
  "notes": "Data looks correct, minor discrepancy noted",
  "reviewer_id": "user_123"
}

Response (200 OK):
{
  "status": "acknowledged",
  "message": "Review response recorded, workflow resuming",
  "session_id": "invoice_20241021_001"
}
```

#### 4. Get Workflow State
```http
GET /api/v1/workflow/{session_id}/state

Response (200 OK):
{
  "session_id": "invoice_20241021_001",
  "workflow_state": {
    "extracted_text": "Invoice 51109338...",
    "invoice_data": {...},
    "validation_result": {...},
    "approval_status": "approved",
    "invoice_id": 42
  }
}
```

#### 5. WebSocket Stream
```
WS ws://localhost:8000/ws/workflow/{session_id}

Stream Events (Server → Client):
{
  "event": "step_started",
  "step": 1,
  "step_name": "Extract",
  "timestamp": "2024-10-21T10:30:05Z"
}

{
  "event": "step_completed",
  "step": 1,
  "step_name": "Extract",
  "duration_ms": 2500,
  "timestamp": "2024-10-21T10:30:07Z"
}

{
  "event": "awaiting_input",
  "step": 4,
  "step_name": "Review",
  "ui_data": {
    "invoice_id": "51109338",
    "confidence_score": 0.75,
    "invoice_data": {...}
  },
  "timestamp": "2024-10-21T10:32:00Z"
}

{
  "event": "workflow_completed",
  "final_state": {
    "invoice_id": 42,
    "status": "saved"
  },
  "timestamp": "2024-10-21T10:35:00Z"
}
```

#### 6. Query Results
```http
GET /api/v1/invoices?limit=10&offset=0

Response (200 OK):
{
  "invoices": [
    {
      "id": 42,
      "invoice_no": "51109338",
      "seller_name": "Andrews, Kirby and Valdez",
      "total_amount": 6204.19,
      "confidence_score": 0.75,
      "created_at": "2024-10-21T10:35:00Z",
      "line_items": [...]
    }
  ],
  "total": 42,
  "page": 0,
  "limit": 10
}
```

#### 7. Health Check
```http
GET /health

Response (200 OK):
{
  "status": "healthy",
  "timestamp": "2024-10-21T10:40:00Z",
  "version": "1.0.0"
}
```

### AgentOS Auto-Generated Routes

```
GET  /agents                     # List all agents
GET  /agents/{agent_id}/runs     # Agent run history
GET  /docs                       # OpenAPI documentation
GET  /admin                      # AgentOS admin dashboard
```

---

## Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| **Framework** | FastAPI | REST API + WebSocket support |
| **Agent Framework** | Agno | Workflow orchestration, agents, HITL |
| **AI Model** | Azure OpenAI (GPT-4V) | Vision + text processing |
| **UI** | Streamlit | Real-time dashboard |
| **Persistence** | DuckDB + SQLiteDb | Data + session state |
| **Async** | AsyncIO + Uvicorn | Non-blocking execution |

---

## File Structure

```
invoice-processing/
├─ config.py                    # Configuration management
├─ models.py                    # Pydantic data models
├─ agents/
│  ├─ __init__.py
│  ├─ extraction.py             # ExtractionAgent definition
│  ├─ analysis.py               # AnalysisAgent definition
│  ├─ validation.py             # ValidationAgent definition
│  └─ reviewer.py               # ReviewAgent with HITL tools
├─ workflow.py                  # InvoiceProcessingWorkflow
├─ database.py                  # DuckDB + SQLiteDb setup
├─ session_manager.py           # Session state management
├─ api/
│  ├─ __init__.py
│  ├─ routes.py                 # Custom FastAPI routes
│  ├─ websocket.py              # WebSocket handlers
│  └─ responses.py              # Response models
├─ main.py                      # FastAPI app + AgentOS
├─ streamlit_app.py             # Streamlit UI
└─ requirements.txt             # Python dependencies
```

---

## Key Design Decisions

### 1. Why AgentOS + Custom FastAPI?
- **AgentOS** provides agent lifecycle, runs, and admin UI
- **Custom FastAPI** provides domain-specific endpoints
- Combined: Full control + framework benefits

### 2. Why HITL at Agent Level (not Workflow)?
- Agents support `requires_user_input` tools natively
- Workflow HITL is coming but not ready yet
- Agent-level pause/resume is production-ready

### 3. Why Workflow instead of Team?
- Workflow provides named steps for logging
- Better for linear processes (our invoice pipeline)
- Integrates with AgentOS session tracking

### 4. Why Both DuckDB + SQLiteDb?
- **DuckDB** = business data (invoices, line items)
- **SQLiteDb** = agent state/sessions (Agno requirement)
- Separate concerns, easy to query

### 5. Why WebSocket?
- Real-time step progress to Streamlit
- Live UI updates during long-running operations
- Better UX than polling

---

## Implementation Priority

1. **Phase 1**: Refactor main.py → workflow.py
   - Convert steps to Agno Workflow
   - Keep same agents logic

2. **Phase 2**: Create custom FastAPI routes
   - Add endpoints for workflow control
   - Session management layer

3. **Phase 3**: Implement HITL integration
   - Create ReviewAgent with HITL tools
   - Hook pause/resume to API

4. **Phase 4**: Build Streamlit UI
   - Connect to API endpoints
   - Real-time monitoring

5. **Phase 5**: Add WebSocket support
   - Stream step progress
   - Live workflow visualization

---

## Next Steps

Ready to implement? Start with Phase 1:
- Refactor to Agno Workflow structure
- Maintain current functionality
- Set up AgentOS integration
