# Implementation Guide: Agno Workflow + AgentOS + HITL

## Phase 1: Refactor to Agno Workflow

### Step 1.1: Create workflow.py

```python
# workflow.py
from typing import Optional
from agno.agent import Agent
from agno.workflow import Workflow, Step
from agno.db.sqlite import SqliteDb
from agno.models.azure import AzureOpenAI
from agno.media import Image
import json
from datetime import datetime

from config import Config
from models import InvoiceData, InvoiceLineItem
from agents.extraction import create_extraction_agent
from agents.analysis import create_analysis_agent
from agents.validation import create_validation_agent
from agents.reviewer import create_reviewer_agent
from database import initialize_databases, save_invoice_to_database

# ============================================================================
# Session State Models
# ============================================================================

class WorkflowSessionState:
    """Stores workflow session state across steps"""
    def __init__(self, session_id: str, image_path: str):
        self.session_id = session_id
        self.image_path = image_path
        self.extracted_text: Optional[str] = None
        self.invoice_dict: Optional[dict] = None
        self.validation_result: Optional[dict] = None
        self.confidence_score: float = 0.0
        self.approval_status: Optional[bool] = None
        self.invoice_id: Optional[int] = None
        self.workflow_run_id: Optional[str] = None
        self.created_at = datetime.now()

# ============================================================================
# Step Executors
# ============================================================================

def extract_step_executor(session_state: WorkflowSessionState,
                         db_tools: SqliteDb) -> WorkflowSessionState:
    """Step 1: Extract text from invoice image"""
    print(f"\n[1/5] Extracting text from invoice image...")

    agent = create_extraction_agent()
    result = agent.run(
        "Extract all text from this invoice image with perfect accuracy.",
        images=[Image(filepath=session_state.image_path)],
    )

    session_state.extracted_text = result.content
    print(f"[+] Extracted {len(session_state.extracted_text)} characters")
    return session_state


def analysis_step_executor(session_state: WorkflowSessionState,
                          db_tools: SqliteDb) -> WorkflowSessionState:
    """Step 2: Analyze and structure extracted text"""
    print(f"\n[2/5] Analyzing and structuring invoice data...")

    agent = create_analysis_agent()
    result = agent.run(
        f"Parse this invoice text into the exact JSON structure:\n\n{session_state.extracted_text}"
    )

    try:
        response_text = result.content.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]

        session_state.invoice_dict = json.loads(response_text.strip())
        print(f"[+] Successfully structured invoice data")
        print(f"[+] Found {len(session_state.invoice_dict.get('line_items', []))} line items")
    except json.JSONDecodeError as e:
        print(f"[!] Error parsing JSON: {e}")
        session_state.invoice_dict = {}

    return session_state


def validation_step_executor(session_state: WorkflowSessionState,
                            db_tools: SqliteDb) -> WorkflowSessionState:
    """Step 3: Validate data quality"""
    print(f"\n[3/5] Validating invoice data...")

    agent = create_validation_agent()
    result = agent.run(
        f"Validate this invoice data:\n\n{json.dumps(session_state.invoice_dict, indent=2)}"
    )

    try:
        validation_response = result.content.strip()
        if validation_response.startswith("```"):
            validation_response = validation_response.split("```")[1]
            if validation_response.startswith("json"):
                validation_response = validation_response[4:]

        session_state.validation_result = json.loads(validation_response.strip())
        session_state.confidence_score = session_state.validation_result.get("confidence_score", 0.5)
        session_state.invoice_dict["confidence_score"] = session_state.confidence_score

        print(f"[+] Validation complete - Confidence: {session_state.confidence_score:.2%}")
    except json.JSONDecodeError:
        print("[!] Could not parse validation response")
        session_state.confidence_score = 0.5
        session_state.invoice_dict["confidence_score"] = 0.5

    return session_state


def review_step_executor(session_state: WorkflowSessionState,
                        db_tools: SqliteDb) -> WorkflowSessionState:
    """Step 4: Request human review if needed"""
    print(f"\n[4/5] Review process...")

    # If high confidence, auto-approve
    if session_state.confidence_score >= Config.AUTO_APPROVE_CONFIDENCE:
        print(f"[+] Auto-approved (confidence {session_state.confidence_score:.2%} >= {Config.AUTO_APPROVE_CONFIDENCE:.2%})")
        session_state.approval_status = True
        return session_state

    # If human review disabled, auto-approve
    if not Config.HUMAN_REVIEW_ENABLED:
        print("[+] Human review disabled - auto-approving")
        session_state.approval_status = True
        return session_state

    # Use ReviewAgent with HITL tools
    print(f"[!] Manual review required (confidence {session_state.confidence_score:.2%} < {Config.AUTO_APPROVE_CONFIDENCE:.2%})")

    agent = create_reviewer_agent()
    result = agent.run(
        f"Review this invoice data and decide whether to approve:\n\n{json.dumps(session_state.invoice_dict, indent=2)}",
    )

    # Agent will pause here waiting for human input via HITL
    # The API layer will handle resume

    # For now, set approval_status from agent's decision
    if "approved" in result.content.lower():
        session_state.approval_status = True
    else:
        session_state.approval_status = False

    return session_state


def persist_step_executor(session_state: WorkflowSessionState,
                         db_tools: SqliteDb) -> WorkflowSessionState:
    """Step 5: Save to database"""
    print(f"\n[5/5] Saving to database...")

    if not session_state.approval_status:
        print("[!] Invoice not approved - skipping save")
        return session_state

    try:
        invoice_data = InvoiceData(**session_state.invoice_dict)
        invoice_id = save_invoice_to_database(invoice_data, db_tools)
        session_state.invoice_id = invoice_id
        print(f"[+] Invoice saved with ID: {invoice_id}")
    except Exception as e:
        print(f"[!] Error saving invoice: {e}")

    return session_state

# ============================================================================
# Workflow Definition
# ============================================================================

def create_invoice_processing_workflow() -> Workflow:
    """Create the invoice processing workflow"""

    # Initialize databases
    db_tools = initialize_databases()

    # Define workflow steps
    workflow = Workflow(
        name="InvoiceProcessingWorkflow",
        description="Process invoices through extraction, analysis, validation, review, and persistence",
        steps=[
            Step(
                name="Extract",
                description="OCR text extraction from invoice image",
                # Note: For Phase 1, using custom executors
                # In Phase 3, we'll replace with agents that support HITL
            ),
            Step(
                name="Analyze",
                description="Structure extracted text into JSON format",
            ),
            Step(
                name="Validate",
                description="Validate data quality and calculate confidence score",
            ),
            Step(
                name="Review",
                description="Request human review if confidence is low",
            ),
            Step(
                name="Persist",
                description="Save approved invoice to database",
            ),
        ],
        db=db_tools,
    )

    return workflow, db_tools
```

### Step 1.2: Create Agent Files

```python
# agents/extraction.py
from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from config import Config

def create_extraction_agent() -> Agent:
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

Extract ALL text from this invoice image with perfect accuracy...""",
        markdown=True,
    )
```

Similar files for `agents/analysis.py`, `agents/validation.py`, and `agents/reviewer.py`

---

## Phase 2: Create Custom FastAPI Routes

### Step 2.1: Create routes.py

```python
# api/routes.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uuid
from pathlib import Path
import asyncio
from datetime import datetime

from workflow import create_invoice_processing_workflow, WorkflowSessionState
from session_manager import SessionManager
from models import ReviewResponse

app = FastAPI()
session_manager = SessionManager()

# ============================================================================
# API Routes
# ============================================================================

@app.post("/api/v1/workflow/start")
async def start_workflow(file: UploadFile = File(...)):
    """Start a new invoice processing workflow"""

    # Generate session ID
    session_id = f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    # Save uploaded file
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / f"{session_id}.jpg"

    try:
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File upload failed: {e}")

    # Create session state
    session_state = WorkflowSessionState(session_id=session_id, image_path=str(file_path))
    session_manager.create_session(session_id, session_state)

    # Start workflow in background
    workflow, db_tools = create_invoice_processing_workflow()
    asyncio.create_task(run_workflow_background(session_id, session_state, workflow, db_tools))

    return {
        "session_id": session_id,
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "workflow_name": "InvoiceProcessingWorkflow"
    }


@app.get("/api/v1/workflow/{session_id}")
async def get_workflow_status(session_id: str):
    """Get current workflow status"""

    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "state": session.get("state", "processing"),
        "current_step": session.get("current_step", 0),
        "current_step_name": session.get("current_step_name", "Unknown"),
        "is_paused": session.get("is_paused", False),
        "workflow_run_id": session.get("workflow_run_id"),
        "paused_reason": session.get("paused_reason"),
        "progress": {
            "steps_completed": session.get("current_step", 0),
            "total_steps": 5,
            "percentage": int((session.get("current_step", 0) / 5) * 100)
        },
        "invoice_data": session.get("invoice_data"),
        "confidence_score": session.get("confidence_score"),
        "validation_errors": session.get("validation_errors", []),
        "created_at": session.get("created_at"),
        "updated_at": session.get("updated_at")
    }


@app.post("/api/v1/workflow/{session_id}/review-response")
async def submit_review_response(session_id: str, response: ReviewResponse):
    """Submit human review response (approval/rejection)"""

    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.get("is_paused"):
        raise HTTPException(status_code=400, detail="Workflow is not paused")

    # Update session with approval
    session["approval_status"] = response.approved
    session["review_notes"] = response.notes
    session["reviewer_id"] = response.reviewer_id

    # Resume workflow
    workflow_run_id = session.get("workflow_run_id")
    # TODO: Integrate with Agno's continue_run()

    session_manager.update_session(session_id, session)

    return {
        "status": "acknowledged",
        "message": "Review response recorded, workflow resuming",
        "session_id": session_id
    }


@app.get("/api/v1/workflow/{session_id}/state")
async def get_workflow_state(session_id: str):
    """Get detailed workflow state"""

    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "workflow_state": {
            "extracted_text": session.get("extracted_text", ""),
            "invoice_data": session.get("invoice_data"),
            "validation_result": session.get("validation_result"),
            "approval_status": session.get("approval_status"),
            "invoice_id": session.get("invoice_id")
        }
    }


@app.get("/api/v1/invoices")
async def query_invoices(limit: int = 10, offset: int = 0):
    """Query saved invoices from database"""
    # TODO: Implement DuckDB query
    return {
        "invoices": [],
        "total": 0,
        "page": offset // limit,
        "limit": limit
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# ============================================================================
# Background Task
# ============================================================================

async def run_workflow_background(session_id: str, state: WorkflowSessionState,
                                 workflow, db_tools):
    """Run workflow in background"""
    try:
        session = session_manager.get_session(session_id)
        session["state"] = "processing"

        # Step 1: Extract
        session["current_step"] = 1
        session["current_step_name"] = "Extract"
        state = await asyncio.to_thread(extract_step_executor, state, db_tools)

        # Step 2: Analyze
        session["current_step"] = 2
        session["current_step_name"] = "Analyze"
        state = await asyncio.to_thread(analysis_step_executor, state, db_tools)

        # Step 3: Validate
        session["current_step"] = 3
        session["current_step_name"] = "Validate"
        state = await asyncio.to_thread(validation_step_executor, state, db_tools)

        # Step 4: Review (may pause here)
        session["current_step"] = 4
        session["current_step_name"] = "Review"

        # Check if review is needed
        if state.confidence_score < Config.AUTO_APPROVE_CONFIDENCE and Config.HUMAN_REVIEW_ENABLED:
            session["is_paused"] = True
            session["state"] = "awaiting_human_input"
            session["paused_reason"] = f"Low confidence score: {state.confidence_score:.2%}"

            # Wait for approval response (polling or event)
            # TODO: Implement proper wait mechanism

        else:
            state.approval_status = True

        # Step 5: Persist (only if approved)
        if state.approval_status:
            session["current_step"] = 5
            session["current_step_name"] = "Persist"
            state = await asyncio.to_thread(persist_step_executor, state, db_tools)
            session["state"] = "completed"
            session["invoice_id"] = state.invoice_id
        else:
            session["state"] = "rejected"

        session_manager.update_session(session_id, session)

    except Exception as e:
        session = session_manager.get_session(session_id)
        session["state"] = "failed"
        session["error"] = str(e)
        session_manager.update_session(session_id, session)
```

### Step 2.2: Create session_manager.py

```python
# session_manager.py
from typing import Dict, Optional
import json

class SessionManager:
    """Manage workflow sessions"""

    def __init__(self):
        self.sessions: Dict[str, dict] = {}

    def create_session(self, session_id: str, state):
        """Create new session"""
        self.sessions[session_id] = {
            "session_id": session_id,
            "state": "initializing",
            "created_at": state.created_at.isoformat(),
            "current_step": 0,
            "is_paused": False
        }

    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session"""
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, data: dict):
        """Update session"""
        if session_id in self.sessions:
            self.sessions[session_id].update(data)

    def delete_session(self, session_id: str):
        """Delete session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
```

---

## Phase 3: Implement HITL Integration

### Step 3.1: Create ReviewAgent with HITL

```python
# agents/reviewer.py
from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.tools import tool
from agno.tools.function import UserInputField
from config import Config
from typing import List

# Define HITL tool
@tool(requires_user_input=True)
def approve_invoice(
    invoice_id: str,
    confidence_score: float,
    seller_name: str,
    total_amount: str,
    notes: str = ""
) -> str:
    """Request user approval for invoice processing.

    Args:
        invoice_id: The invoice ID to review
        confidence_score: Extraction confidence (0-1)
        seller_name: Seller company name
        total_amount: Total invoice amount
        notes: Optional review notes
    """
    # This tool triggers HITL pause
    # The API layer will intercept the pause and wait for user input
    return f"Invoice {invoice_id} requires user approval with notes: {notes}"


def create_reviewer_agent() -> Agent:
    """Agent for reviewing invoices with human-in-the-loop"""
    return Agent(
        name="ReviewerAgent",
        model=AzureOpenAI(
            id=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            azure_deployment=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
        ),
        tools=[approve_invoice],
        instructions="""You are an invoice review specialist.

Review the provided invoice data and if confidence is low or there are concerns:
- Call the approve_invoice tool with details
- This will pause execution pending human approval

The human reviewer will use the Streamlit UI to approve or reject.""",
        markdown=True,
    )
```

### Step 3.2: Update API to Handle HITL

```python
# api/routes.py - Add HITL handler

from agno.agent import Agent

# Track paused agents
paused_agents: Dict[str, Dict] = {}

async def run_workflow_with_hitl(session_id: str, state: WorkflowSessionState, agent: Agent):
    """Run agent with HITL support"""

    run_response = agent.run(
        f"Review this invoice:\n{json.dumps(state.invoice_dict, indent=2)}"
    )

    # Check if agent paused for user input
    if run_response.is_paused:
        session = session_manager.get_session(session_id)
        session["is_paused"] = True
        session["state"] = "awaiting_human_input"
        session["workflow_run_id"] = run_response.run_id
        session["tools_requiring_input"] = [
            {
                "tool_name": tool.tool_name,
                "tool_args": tool.tool_args,
                "user_input_schema": [
                    {
                        "name": field.name,
                        "type": str(field.field_type),
                        "description": field.description
                    }
                    for field in tool.user_input_schema
                ]
            }
            for tool in run_response.tools_requiring_user_input
        ]

        # Store paused agent for later resumption
        paused_agents[session_id] = {
            "agent": agent,
            "run_response": run_response,
            "paused_at": datetime.now()
        }

        session_manager.update_session(session_id, session)
        return False  # Indicate workflow paused

    # Agent completed without pause
    return True  # Indicate workflow should continue


@app.post("/api/v1/workflow/{session_id}/review-response")
async def submit_review_response(session_id: str, response: ReviewResponse):
    """Handle human review response and resume agent"""

    if session_id not in paused_agents:
        raise HTTPException(status_code=400, detail="No paused workflow for this session")

    paused = paused_agents[session_id]
    agent = paused["agent"]
    run_response = paused["run_response"]

    # Update tool with user input
    for tool in run_response.tools_requiring_user_input:
        for field in tool.user_input_schema:
            if field.name == "notes":
                field.value = response.notes
            # ... set other fields based on response

        tool.confirmed = response.approved

    # Resume agent execution
    continued_response = agent.continue_run(run_response=run_response)

    # Update session
    session = session_manager.get_session(session_id)
    session["approval_status"] = response.approved
    session["is_paused"] = False

    # Clean up
    del paused_agents[session_id]
    session_manager.update_session(session_id, session)

    return {
        "status": "resumed",
        "message": "Workflow resumed after human input",
        "session_id": session_id
    }
```

---

## Phase 4: Build Streamlit UI

```python
# streamlit_app.py
import streamlit as st
import requests
import time
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Invoice Processing System", layout="wide")

# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.title("Invoice Processor")
    page = st.radio("Navigate", ["Upload", "Monitor", "Results"])

# ============================================================================
# Page: Upload
# ============================================================================

if page == "Upload":
    st.title("Upload Invoice")

    uploaded_file = st.file_uploader("Choose invoice image", type=["jpg", "jpeg", "png"])

    if uploaded_file and st.button("Process Invoice"):
        # Upload to API
        files = {"file": uploaded_file}
        response = requests.post(f"{API_BASE}/api/v1/workflow/start", files=files)

        if response.status_code == 202:
            data = response.json()
            st.session_state.session_id = data["session_id"]
            st.success(f"Workflow started: {data['session_id']}")
            st.switch_page("pages/1_Monitor.py")  # Switch to monitor page
        else:
            st.error(f"Error: {response.text}")

# ============================================================================
# Page: Monitor (Polling)
# ============================================================================

elif page == "Monitor":
    st.title("Workflow Monitor")

    if "session_id" not in st.session_state:
        st.info("No active workflow. Upload an invoice first.")
    else:
        session_id = st.session_state.session_id

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"Session: {session_id}")
        with col2:
            if st.button("Refresh"):
                st.rerun()

        # Poll for status
        response = requests.get(f"{API_BASE}/api/v1/workflow/{session_id}")
        status_data = response.json()

        # Progress bar
        progress = status_data["progress"]["percentage"] / 100
        st.progress(progress, text=f"Step {status_data['current_step']}/5")

        # Steps display
        st.subheader("Workflow Steps")
        steps = ["Extract", "Analyze", "Validate", "Review", "Persist"]
        current = status_data["current_step"]

        cols = st.columns(5)
        for i, step_name in enumerate(steps):
            with cols[i]:
                if i < current:
                    st.success(f"✓ {step_name}")
                elif i == current:
                    st.info(f"⏳ {step_name}")
                else:
                    st.write(f"◯ {step_name}")

        # Current step info
        st.write("---")
        st.write(f"**Current Step:** {status_data['current_step_name']}")

        # Human-in-the-loop UI
        if status_data["is_paused"]:
            st.warning(f"⏸️ **Workflow Paused:** {status_data['paused_reason']}")

            # Display invoice data for review
            if status_data["invoice_data"]:
                st.subheader("Invoice Data for Review")
                invoice = status_data["invoice_data"]

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Invoice No:** {invoice.get('invoice_no')}")
                    st.write(f"**Seller:** {invoice.get('seller_name')}")
                    st.write(f"**Client:** {invoice.get('client_name')}")
                with col2:
                    st.write(f"**Total:** ${invoice.get('gross_worth_total')}")
                    st.write(f"**Confidence:** {status_data['confidence_score']:.1%}")

                # Line items preview
                if invoice.get('line_items'):
                    st.write("**Line Items:**")
                    for item in invoice['line_items'][:3]:
                        st.write(f"- {item['description']}: {item['qty']} @ ${item['net_price']}")
                    if len(invoice['line_items']) > 3:
                        st.write(f"... and {len(invoice['line_items']) - 3} more items")

            # Review form
            st.subheader("Review & Approve")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Approve"):
                    review_response = {
                        "approved": True,
                        "notes": st.text_area("Notes (optional)", key="approve_notes", height=100),
                        "reviewer_id": "user_123"  # TODO: Get from auth
                    }

                    resp = requests.post(
                        f"{API_BASE}/api/v1/workflow/{session_id}/review-response",
                        json=review_response
                    )

                    if resp.status_code == 200:
                        st.success("Approval recorded! Workflow resuming...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Error: {resp.text}")

            with col2:
                if st.button("❌ Reject"):
                    review_response = {
                        "approved": False,
                        "notes": st.text_area("Reason for rejection", key="reject_notes", height=100),
                        "reviewer_id": "user_123"
                    }

                    resp = requests.post(
                        f"{API_BASE}/api/v1/workflow/{session_id}/review-response",
                        json=review_response
                    )

                    if resp.status_code == 200:
                        st.success("Rejection recorded!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Error: {resp.text}")

        # Auto-refresh if processing
        if status_data["state"] not in ["completed", "failed", "rejected"]:
            time.sleep(2)
            st.rerun()

        # Completion message
        if status_data["state"] == "completed":
            st.success(f"✅ **Completed!** Invoice saved with ID: {status_data.get('invoice_id')}")

# ============================================================================
# Page: Results
# ============================================================================

elif page == "Results":
    st.title("Processing Results")

    response = requests.get(f"{API_BASE}/api/v1/invoices?limit=10")
    invoices = response.json()["invoices"]

    if invoices:
        st.dataframe(
            [
                {
                    "ID": inv["id"],
                    "Invoice #": inv["invoice_no"],
                    "Seller": inv["seller_name"],
                    "Amount": f"${inv['total_amount']}",
                    "Confidence": f"{inv['confidence_score']:.1%}",
                    "Created": inv["created_at"]
                }
                for inv in invoices
            ]
        )
    else:
        st.info("No invoices processed yet.")
```

---

## Phase 5: Add WebSocket Support

```python
# api/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio

@app.websocket("/ws/workflow/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket stream for real-time workflow updates"""

    await websocket.accept()

    try:
        session_manager.add_websocket(session_id, websocket)

        # Initial state
        session = session_manager.get_session(session_id)
        await websocket.send_json({
            "event": "workflow_started",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })

        # Stream updates
        while True:
            await asyncio.sleep(1)

            session = session_manager.get_session(session_id)

            if session and session.get("last_event_sent") != session.get("updated_at"):
                await websocket.send_json({
                    "event": "status_update",
                    "state": session.get("state"),
                    "current_step": session.get("current_step"),
                    "is_paused": session.get("is_paused"),
                    "timestamp": datetime.now().isoformat()
                })

                session["last_event_sent"] = session.get("updated_at")

    except WebSocketDisconnect:
        session_manager.remove_websocket(session_id)
```

---

## Summary: Implementation Roadmap

| Phase | Files | Key Tasks | Estimated Time |
|-------|-------|-----------|---|
| 1 | workflow.py, agents/*.py | Refactor to Agno Workflow structure | 4-6 hours |
| 2 | api/routes.py, session_manager.py | FastAPI + AgentOS integration | 6-8 hours |
| 3 | agents/reviewer.py, HITL handlers | Human-in-the-loop integration | 4-5 hours |
| 4 | streamlit_app.py | UI dashboard | 5-6 hours |
| 5 | api/websocket.py | Real-time streaming | 2-3 hours |
| **Total** | | | **21-28 hours** |

---

## Testing Strategy

1. **Phase 1 Tests**: Verify workflow steps execute in sequence
2. **Phase 2 Tests**: Test API endpoints with mock sessions
3. **Phase 3 Tests**: Simulate HITL pause/resume
4. **Phase 4 Tests**: End-to-end with Streamlit + API
5. **Phase 5 Tests**: WebSocket streaming with multiple clients

---

## Deployment

1. **Development**: `python main.py` (FastAPI dev server)
2. **Production**: `uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4`
3. **Streamlit**: `streamlit run streamlit_app.py`

---

## Next: Ready to Start?

Proceed to **Phase 1** implementation or ask clarifying questions!
