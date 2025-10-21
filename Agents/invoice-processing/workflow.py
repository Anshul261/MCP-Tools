"""
Agno Workflow for Invoice Processing
Uses proper Agno Workflow and Step classes for orchestration
Phases 1-3: Extract → Analyze → Validate → Review → Persist
"""

from typing import Optional
from datetime import datetime
from agno.db.sqlite import SqliteDb
from agno.workflow import Workflow, Step

# ============================================================================
# Session State Class
# ============================================================================


class WorkflowSessionState:
    """
    Lightweight session state tracker for API coordination.
    Tracks workflow progress without modifying existing agent/pipeline logic.
    """

    def __init__(self, session_id: str, image_path: str):
        """
        Initialize workflow session state

        Args:
            session_id: Unique session identifier
            image_path: Path to invoice image
        """
        self.session_id = session_id
        self.image_path = image_path
        self.current_step = 0
        self.current_step_name = None
        self.is_paused = False
        self.approval_status = None
        self.invoice_id = None
        self.extracted_text = None
        self.invoice_dict = None
        self.confidence_score = None
        self.validation_result = None
        self.created_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert state to dictionary"""
        return {
            "session_id": self.session_id,
            "image_path": self.image_path,
            "current_step": self.current_step,
            "current_step_name": self.current_step_name,
            "is_paused": self.is_paused,
            "approval_status": self.approval_status,
            "invoice_id": self.invoice_id,
            "extracted_text": self.extracted_text[:100] if self.extracted_text else None,
            "invoice_dict": self.invoice_dict,
            "confidence_score": self.confidence_score,
            "validation_result": self.validation_result,
            "created_at": self.created_at.isoformat(),
        }


# ============================================================================
# Step Executor Functions for Agno Workflow Steps
# ============================================================================


def step_extract_executor(session_state: WorkflowSessionState) -> WorkflowSessionState:
    """
    Step 1 Executor: Extract text from invoice image using Azure Vision
    Called by Agno Workflow Step: "Extract"
    """
    from main import create_extraction_agent
    from agno.media import Image

    print(f"\n[Step 1/5] Extract - OCR text extraction")
    session_state.current_step = 1
    session_state.current_step_name = "Extract"

    extraction_agent = create_extraction_agent()
    extraction_result = extraction_agent.run(
        "Extract all text from this invoice image with perfect accuracy.",
        images=[Image(filepath=session_state.image_path)],
    )
    session_state.extracted_text = extraction_result.content
    print(f"[✓] Extracted {len(session_state.extracted_text)} characters")
    return session_state


def step_analyze_executor(session_state: WorkflowSessionState) -> WorkflowSessionState:
    """
    Step 2 Executor: Analyze and structure extracted text into JSON
    Called by Agno Workflow Step: "Analyze"
    """
    from main import create_analysis_agent
    import json

    print(f"\n[Step 2/5] Analyze - Structure invoice data")
    session_state.current_step = 2
    session_state.current_step_name = "Analyze"

    analysis_agent = create_analysis_agent()
    analysis_result = analysis_agent.run(
        f"Parse this invoice text into the exact JSON structure specified:\n\n{session_state.extracted_text}"
    )

    try:
        response_text = analysis_result.content.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        session_state.invoice_dict = json.loads(response_text.strip())
        print(f"[✓] Found {len(session_state.invoice_dict.get('line_items', []))} line items")
    except json.JSONDecodeError as e:
        print(f"[!] Error parsing JSON: {e}")
        raise

    return session_state


def step_validate_executor(session_state: WorkflowSessionState) -> WorkflowSessionState:
    """
    Step 3 Executor: Validate data quality and calculate confidence score
    Called by Agno Workflow Step: "Validate"
    """
    from main import create_validation_agent
    import json

    print(f"\n[Step 3/5] Validate - Data quality check")
    session_state.current_step = 3
    session_state.current_step_name = "Validate"

    validation_agent = create_validation_agent()
    validation_result = validation_agent.run(
        f"Validate this invoice data:\n\n{json.dumps(session_state.invoice_dict, indent=2)}"
    )

    try:
        validation_response = validation_result.content.strip()
        if validation_response.startswith("```"):
            validation_response = validation_response.split("```")[1]
            if validation_response.startswith("json"):
                validation_response = validation_response[4:]

        session_state.validation_result = json.loads(validation_response.strip())
        session_state.confidence_score = session_state.validation_result.get("confidence_score", 0.5)
        session_state.invoice_dict["confidence_score"] = session_state.confidence_score
        print(f"[✓] Confidence score: {session_state.confidence_score:.2%}")
    except json.JSONDecodeError:
        print("[!] Could not parse validation response")
        session_state.confidence_score = 0.5

    return session_state


def step_review_executor(session_state: WorkflowSessionState) -> WorkflowSessionState:
    """
    Step 4 Executor: Review - Check if human approval needed
    Called by Agno Workflow Step: "Review"
    """
    from config import Config

    print(f"\n[Step 4/5] Review - Human approval check")
    session_state.current_step = 4
    session_state.current_step_name = "Review"

    needs_review = (
        session_state.confidence_score < Config.AUTO_APPROVE_CONFIDENCE
        and Config.HUMAN_REVIEW_ENABLED
    )

    if needs_review:
        # Pause for API review (don't ask CLI)
        print(f"[!] Low confidence {session_state.confidence_score:.2%} - Pausing for user review")
        session_state.is_paused = True
        session_state.approval_status = None  # Waiting for user
        return session_state
    else:
        # Auto approve
        print(f"[✓] Auto-approved (confidence {session_state.confidence_score:.2%} >= {Config.AUTO_APPROVE_CONFIDENCE:.2%})")
        session_state.approval_status = True
        return session_state


def step_persist_executor(session_state: WorkflowSessionState, db_tools: SqliteDb = None) -> WorkflowSessionState:
    """
    Step 5 Executor: Persist - Save to database
    Called by Agno Workflow Step: "Persist"
    """
    from main import save_to_database, initialize_database
    from models import InvoiceData

    print(f"\n[Step 5/5] Persist - Save to database")
    session_state.current_step = 5
    session_state.current_step_name = "Persist"

    if session_state.approval_status is None:
        # Still waiting for approval, don't save yet
        print("[!] Waiting for approval, not saving yet")
        return session_state

    if not session_state.approval_status:
        # Rejected
        print("[!] Invoice rejected - not saving")
        return session_state

    # Save invoice
    try:
        if db_tools is None:
            db_tools = initialize_database()

        invoice_data = InvoiceData(**session_state.invoice_dict)
        invoice_id = save_to_database(invoice_data, db_tools)
        session_state.invoice_id = invoice_id
        print(f"[✓] Saved invoice ID: {invoice_id}")
    except Exception as e:
        print(f"[!] Error saving: {e}")
        raise

    return session_state


# ============================================================================
# Create Agno Workflow with Named Steps
# ============================================================================


def create_invoice_processing_workflow(db_tools: SqliteDb = None) -> Workflow:
    """
    Create Agno Workflow with named steps for invoice processing.

    This uses Agno's Workflow + Step classes for:
    - Better logging on AgentOS
    - Named step identification
    - Sequential execution with state passing
    - Future support for Agno platform

    Each Step has an executor= parameter pointing to the function that runs it.

    Returns:
        Agno Workflow instance with 5 named steps
    """

    workflow = Workflow(
        name="InvoiceProcessingWorkflow",
        description="Process invoices through extraction, analysis, validation, review, and persistence",
        steps=[
            Step(
                name="Extract",
                description="OCR text extraction from invoice image using Azure Vision",
                executor=step_extract_executor,
            ),
            Step(
                name="Analyze",
                description="Structure extracted text into JSON format",
                executor=step_analyze_executor,
            ),
            Step(
                name="Validate",
                description="Validate data quality and calculate confidence score",
                executor=step_validate_executor,
            ),
            Step(
                name="Review",
                description="Request human review if confidence is low",
                executor=step_review_executor,
            ),
            Step(
                name="Persist",
                description="Save approved invoice to database",
                executor=lambda state: step_persist_executor(state, db_tools),
            ),
        ],
    )

    return workflow


# ============================================================================
# Main Workflow Executor - Runs All Steps
# ============================================================================


def process_invoice_workflow(
    session_state: WorkflowSessionState,
    db_tools: SqliteDb,
    skip_human_review: bool = False
) -> WorkflowSessionState:
    """
    Execute invoice processing workflow with all 5 steps.

    This function:
    1. Runs Step 1: Extract (OCR)
    2. Runs Step 2: Analyze (JSON parsing)
    3. Runs Step 3: Validate (Quality check)
    4. Runs Step 4: Review (Human approval check)
    5. Runs Step 5: Persist (Save to DB)

    Each step updates the session_state which is returned to the API
    for Streamlit UI to display progress.

    Args:
        session_state: Workflow state tracker
        db_tools: DuckDB tools instance
        skip_human_review: If True, pause for API review instead of CLI

    Returns:
        Updated session_state with results
    """

    try:
        # Create workflow instance (for logging/tracking)
        workflow = create_invoice_processing_workflow(db_tools)
        print(f"\n{'='*70}")
        print(f"Starting Workflow: {workflow.name}")
        print(f"{'='*70}")

        # ============ Step 1: Extract ============
        print(f"\nExecuting Step 1: Extract")
        session_state = step_extract_executor(session_state)

        # ============ Step 2: Analyze ============
        print(f"\nExecuting Step 2: Analyze")
        session_state = step_analyze_executor(session_state)

        # ============ Step 3: Validate ============
        print(f"\nExecuting Step 3: Validate")
        session_state = step_validate_executor(session_state)

        # ============ Step 4: Review ============
        print(f"\nExecuting Step 4: Review")
        session_state = step_review_executor(session_state)

        # If paused (waiting for user), don't continue to Step 5
        if session_state.is_paused:
            print(f"\n[!] Workflow paused at Step 4 - waiting for user review")
            return session_state

        # ============ Step 5: Persist ============
        print(f"\nExecuting Step 5: Persist")
        session_state = step_persist_executor(session_state, db_tools)

        print(f"\n{'='*70}")
        print(f"Workflow Complete: {workflow.name}")
        print(f"{'='*70}\n")

        return session_state

    except Exception as e:
        print(f"\n[!] Error in workflow: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


# ============================================================================
# Helper Functions
# ============================================================================


def get_workflow_progress(session_state: WorkflowSessionState) -> dict:
    """
    Calculate workflow progress

    Args:
        session_state: Current session state

    Returns:
        Progress information
    """
    total_steps = 5
    completed_steps = session_state.current_step

    return {
        "steps_completed": completed_steps,
        "total_steps": total_steps,
        "percentage": int((completed_steps / total_steps) * 100),
        "current_step": session_state.current_step_name,
    }
