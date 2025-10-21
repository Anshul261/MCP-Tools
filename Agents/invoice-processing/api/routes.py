"""
FastAPI Routes
All workflow-related API endpoints
"""

import uuid
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse

from workflow import process_invoice_workflow, WorkflowSessionState, get_workflow_progress
from main import initialize_database
from config import Config
from api.models import (
    WorkflowStartResponse,
    WorkflowStatus,
    WorkflowStateDetail,
    ReviewRequest,
    ReviewResponse,
    HealthCheckResponse,
    InvoiceQueryResponse,
)
from api.session_manager import SessionManager

# ============================================================================
# Router Setup
# ============================================================================

router = APIRouter(prefix="/api/v1", tags=["invoice-workflow"])

# Global session manager and database
session_manager = SessionManager()
db_tools = None
upload_dir = Path("uploads")


async def initialize_services():
    """Initialize services on startup"""
    global db_tools, upload_dir

    # Create uploads directory
    upload_dir.mkdir(exist_ok=True)

    # Initialize database
    if db_tools is None:
        db_tools = initialize_database()


# ============================================================================
# ENDPOINT 1: Start Workflow
# ============================================================================


@router.post("/workflow/start", response_model=WorkflowStartResponse, status_code=202)
async def start_workflow(file: UploadFile = File(...)):
    """
    Upload invoice image and start processing workflow.

    Returns session_id for polling status.

    Args:
        file: Invoice image file (jpg/png)

    Returns:
        WorkflowStartResponse with session_id and status

    Raises:
        HTTPException: 400 if file upload fails
    """

    # Initialize services if needed
    await initialize_services()

    # Generate unique session ID
    session_id = f"inv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

    # Save uploaded file
    try:
        content = await file.read()
        file_path = upload_dir / f"{session_id}.jpg"

        with open(file_path, "wb") as f:
            f.write(content)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")

    # Create session in manager
    session_manager.create_session(session_id, str(file_path))

    # Start workflow in background
    asyncio.create_task(run_workflow_background(session_id, str(file_path)))

    return WorkflowStartResponse(
        session_id=session_id,
        status="processing",
        workflow_name="InvoiceProcessingWorkflow",
        created_at=datetime.now().isoformat(),
    )


# ============================================================================
# ENDPOINT 2: Get Workflow Status
# ============================================================================


@router.get("/workflow/{session_id}", response_model=WorkflowStatus)
async def get_workflow_status(session_id: str):
    """
    Get current workflow status and progress.

    Args:
        session_id: Session identifier from start_workflow

    Returns:
        WorkflowStatus with current state and progress

    Raises:
        HTTPException: 404 if session not found
    """

    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Calculate progress
    progress = {
        "steps_completed": session["current_step"],
        "total_steps": 5,
        "percentage": int((session["current_step"] / 5) * 100),
    }

    return WorkflowStatus(
        session_id=session_id,
        state=session["state"],
        current_step=session["current_step"],
        current_step_name=session["current_step_name"],
        is_paused=session["is_paused"],
        workflow_run_id=session.get("workflow_run_id"),
        paused_reason=session.get("paused_reason"),
        progress=progress,
        confidence_score=session.get("confidence_score"),
        invoice_data=session.get("invoice_data"),
        validation_errors=session.get("validation_errors", []),
        created_at=session.get("created_at"),
        updated_at=session.get("updated_at"),
    )


# ============================================================================
# ENDPOINT 3: Get Workflow State (Detailed)
# ============================================================================


@router.get("/workflow/{session_id}/state", response_model=WorkflowStateDetail)
async def get_workflow_state(session_id: str):
    """
    Get complete workflow state for detailed inspection.

    Args:
        session_id: Session identifier

    Returns:
        WorkflowStateDetail with full state

    Raises:
        HTTPException: 404 if session not found
    """

    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return WorkflowStateDetail(session_id=session_id, workflow_state=session)


# ============================================================================
# ENDPOINT 4: Query Invoices from Database
# ============================================================================


@router.get("/invoices", response_model=InvoiceQueryResponse)
async def query_invoices(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0)):
    """
    Query saved invoices from DuckDB.

    Args:
        limit: Number of results (1-100)
        offset: Offset for pagination

    Returns:
        InvoiceQueryResponse with invoice data

    Raises:
        HTTPException: 500 if database query fails
        HTTPException: 503 if database not initialized
    """

    await initialize_services()

    if db_tools is None:
        raise HTTPException(status_code=503, detail="Database not initialized")

    try:
        # Query invoices
        result = db_tools.connection.execute(
            "SELECT * FROM invoices LIMIT ? OFFSET ?", [limit, offset]
        ).fetchall()

        # Get column names for better response
        description = db_tools.connection.execute(
            "PRAGMA table_info(invoices)"
        ).fetchall()
        columns = [col[1] for col in description]

        # Convert rows to dictionaries
        invoices = [dict(zip(columns, row)) for row in result]

        # Get total count
        total_result = db_tools.connection.execute(
            "SELECT COUNT(*) FROM invoices"
        ).fetchone()
        total = total_result[0]

        return InvoiceQueryResponse(
            invoices=invoices,
            total=total,
            page=offset // limit,
            limit=limit,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database query failed: {str(e)}"
        )


# ============================================================================
# ENDPOINT 5: Health Check
# ============================================================================


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint.

    Returns:
        HealthCheckResponse with status
    """

    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
    )


# ============================================================================
# ENDPOINT 6: Submit Review Response (HITL)
# ============================================================================


@router.post("/workflow/{session_id}/review-response", response_model=ReviewResponse)
async def submit_review_response(session_id: str, request: ReviewRequest):
    """
    Submit human review response (approval/rejection).

    This is for Phase 3 HITL integration.
    Currently stores the approval but doesn't resume workflow.

    Args:
        session_id: Session identifier
        request: ReviewRequest with approved status and notes

    Returns:
        ReviewResponse acknowledging the submission

    Raises:
        HTTPException: 404 if session not found
        HTTPException: 400 if workflow not paused
    """

    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Store approval response
    session_manager.update_session(
        session_id,
        {
            "approval_status": request.approved,
            "review_notes": request.notes,
            "reviewer_id": request.reviewer_id,
            "is_paused": False,
        },
    )

    message = (
        "Invoice approved" if request.approved else "Invoice rejected"
    )
    message += " and will be saved" if request.approved else " - not saving"

    return ReviewResponse(
        status="acknowledged",
        message=message,
        session_id=session_id,
    )


# ============================================================================
# ENDPOINT 7: Get Session Statistics
# ============================================================================


@router.get("/stats")
async def get_statistics():
    """
    Get workflow statistics.

    Returns:
        Dictionary with session statistics
    """

    stats = session_manager.get_statistics()

    return {
        "timestamp": datetime.now().isoformat(),
        "statistics": stats,
    }


# ============================================================================
# BACKGROUND TASK: Run Workflow
# ============================================================================


async def run_workflow_background(session_id: str, image_path: str):
    """
    Run invoice processing workflow in background.

    This function:
    1. Creates session state
    2. Calls process_invoice_workflow (wrapper around main.process_invoice)
    3. Updates session as it progresses
    4. Handles errors gracefully

    Args:
        session_id: Session identifier
        image_path: Path to invoice image
    """

    try:
        # Initialize services
        await initialize_services()

        session = session_manager.get_session(session_id)
        session_manager.update_session(session_id, {"state": "processing"})

        # Create workflow session state
        state = WorkflowSessionState(session_id, image_path)

        # Run workflow in thread pool (blocking operation)
        result_state = await asyncio.to_thread(
            process_invoice_workflow, state, db_tools
        )

        # Update session with results
        if result_state.invoice_id:
            session_manager.complete_session(session_id, result_state.invoice_id)
            print(f"[+] Workflow {session_id} completed successfully")
        else:
            session_manager.update_session(
                session_id,
                {
                    "state": "rejected",
                    "current_step": 4,
                    "current_step_name": "Review - Rejected",
                },
            )
            print(f"[!] Workflow {session_id} rejected during review")

    except Exception as e:
        print(f"[!] Error in workflow {session_id}: {str(e)}")
        session_manager.fail_session(session_id, str(e))
