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
    Query saved invoices from DuckDB with line items.

    Args:
        limit: Number of results (1-100)
        offset: Offset for pagination

    Returns:
        InvoiceQueryResponse with invoice data including line items

    Raises:
        HTTPException: 500 if database query fails
        HTTPException: 503 if database not initialized
    """

    await initialize_services()

    if db_tools is None:
        raise HTTPException(status_code=503, detail="Database not initialized")

    try:
        # Query invoices without joining line items first (simpler query)
        result = db_tools.connection.execute(
            """
            SELECT
                i.id,
                i.invoice_no,
                i.date_of_issue,
                i.seller_name,
                i.seller_address,
                i.seller_tax_id,
                i.seller_iban,
                i.client_name,
                i.client_address,
                i.client_tax_id,
                i.vat_percent,
                i.net_worth_total,
                i.vat_total,
                i.gross_worth_total,
                i.confidence_score,
                i.created_at
            FROM invoices i
            LIMIT ? OFFSET ?
            """,
            [limit, offset],
        ).fetchall()

        # Get column names
        description = db_tools.connection.execute(
            """
            SELECT
                i.id,
                i.invoice_no,
                i.date_of_issue,
                i.seller_name,
                i.seller_address,
                i.seller_tax_id,
                i.seller_iban,
                i.client_name,
                i.client_address,
                i.client_tax_id,
                i.vat_percent,
                i.net_worth_total,
                i.vat_total,
                i.gross_worth_total,
                i.confidence_score,
                i.created_at
            FROM invoices i
            LIMIT 1
            """
        ).description

        columns = [desc[0] for desc in description] if description else []

        # Convert rows to dictionaries
        invoices = []
        for row in result:
            inv_dict = dict(zip(columns, row)) if columns else {}

            # Get line items for this invoice
            if inv_dict.get("id"):
                line_items = db_tools.connection.execute(
                    """
                    SELECT
                        item_no,
                        description,
                        qty,
                        unit_measure,
                        net_price,
                        net_worth,
                        vat_percent,
                        gross_worth
                    FROM line_items
                    WHERE invoice_id = ?
                    ORDER BY item_no
                    """,
                    [inv_dict["id"]],
                ).fetchall()

                # Convert line items to list of dicts
                line_items_list = []
                for item in line_items:
                    line_items_list.append({
                        "item_no": item[0],
                        "description": item[1],
                        "qty": item[2],
                        "unit_measure": item[3],
                        "net_price": item[4],
                        "net_worth": item[5],
                        "vat_percent": item[6],
                        "gross_worth": item[7],
                    })

                inv_dict["line_items"] = line_items_list

            invoices.append(inv_dict)

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

    This endpoint:
    1. Receives approval/rejection from Streamlit UI
    2. Resumes the paused workflow
    3. Completes Step 5 (persistence)

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

    if not session.get("is_paused"):
        raise HTTPException(status_code=400, detail="Workflow is not paused")

    # Update approval status
    session_manager.update_session(
        session_id,
        {
            "approval_status": request.approved,
            "review_notes": request.notes,
            "reviewer_id": request.reviewer_id,
            "is_paused": False,
            "state": "processing",  # Resume processing
        },
    )

    # Resume workflow completion (Step 5: Persist)
    asyncio.create_task(resume_workflow_background(session_id, request.approved))

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


async def resume_workflow_background(session_id: str, approved: bool):
    """
    Resume workflow after human review.

    This function:
    1. Gets the paused session
    2. Completes Step 5 (persistence)
    3. Updates session with final state

    Args:
        session_id: Session identifier
        approved: Whether invoice was approved
    """

    try:
        session = session_manager.get_session(session_id)
        if not session:
            print(f"[!] Session {session_id} not found for resume")
            return

        await initialize_services()

        # ========== STEP 5: PERSIST (after approval) ==========
        session_manager.update_session(
            session_id,
            {
                "current_step": 5,
                "current_step_name": "Persist",
            },
        )

        if approved:
            # Save invoice to database
            from models import InvoiceData

            invoice_data = InvoiceData(**session.get("invoice_data", {}))
            invoice_id = save_invoice_to_database(invoice_data, db_tools)

            session_manager.complete_session(session_id, invoice_id)
            print(f"[+] Workflow {session_id} resumed and completed: saved invoice {invoice_id}")
        else:
            # Rejected - don't save
            session_manager.update_session(
                session_id,
                {
                    "state": "rejected",
                    "current_step": 4,
                    "current_step_name": "Review - Rejected",
                },
            )
            print(f"[!] Workflow {session_id} resumed but rejected")

    except Exception as e:
        print(f"[!] Error resuming workflow {session_id}: {str(e)}")
        session_manager.fail_session(session_id, str(e))


def save_invoice_to_database(invoice_data, db_tools):
    """Save invoice to database (imported from main.py)"""
    from main import save_to_database
    return save_to_database(invoice_data, db_tools)


async def run_workflow_background(session_id: str, image_path: str):
    """
    Run invoice processing workflow in background.

    This function:
    1. Creates session state
    2. Calls process_invoice_workflow with skip_human_review=True
    3. Updates session as it progresses
    4. Pauses at Step 4 if human review needed (for Streamlit)
    5. Handles errors gracefully

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
        # Pass skip_human_review=True so it pauses for API instead of CLI
        result_state = await asyncio.to_thread(
            process_invoice_workflow, state, db_tools, skip_human_review=True
        )

        # Check if workflow is paused (waiting for human review)
        if result_state.approval_status is None:
            # Workflow paused at Step 4 - waiting for API review
            session_manager.update_session(
                session_id,
                {
                    "state": "awaiting_human_input",
                    "is_paused": True,
                    "current_step": result_state.current_step,
                    "current_step_name": result_state.current_step_name,
                    "confidence_score": result_state.confidence_score,
                    "invoice_data": result_state.invoice_dict,
                    "paused_reason": f"Confidence {result_state.confidence_score:.1%} below threshold (90%)",
                },
            )
            print(f"[!] Workflow {session_id} paused at Step 4 - waiting for human review")
            return  # Don't continue, wait for API review response

        # Workflow completed
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
