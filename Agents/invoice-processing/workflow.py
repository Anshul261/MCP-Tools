"""
Workflow Wrapper
Wraps existing invoice processing logic for API consumption
Minimal refactoring - calls existing main.py functions
"""

from typing import Optional
from datetime import datetime
from agno.db.sqlite import SqliteDb

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
# Workflow Wrapper - Calls Existing Functions
# ============================================================================


def process_invoice_workflow(
    session_state: WorkflowSessionState, db_tools: SqliteDb
) -> WorkflowSessionState:
    """
    Main workflow wrapper.

    This is a thin wrapper that:
    1. Calls existing process_invoice() from main.py
    2. Tracks state in session_state for API consumption
    3. Returns the updated session state

    The existing pipeline logic remains completely untouched.
    We just wrap it to track progress and enable pause/resume.

    Args:
        session_state: Workflow state tracker
        db_tools: DuckDB tools instance

    Returns:
        Updated session_state with results
    """

    # Import here to avoid circular imports
    from main import process_invoice

    # Call the existing process_invoice function
    # It handles: extraction, analysis, validation, human review, persistence
    # It returns: invoice_id if successful, None if rejected or failed
    invoice_id = process_invoice(session_state.image_path, db_tools)

    # Update session state based on result
    session_state.current_step = 5
    session_state.current_step_name = "Completed"

    if invoice_id:
        session_state.approval_status = True
        session_state.invoice_id = invoice_id
    else:
        session_state.approval_status = False

    return session_state


# ============================================================================
# Alternative: For Future Phase 3 - Agent-Level HITL
# ============================================================================
# These functions are stubs for when we integrate Agno Workflow + HITL
# Currently, they're just for planning purposes


def initialize_workflow_database(db_path: str = None) -> SqliteDb:
    """
    Initialize workflow session database.

    Currently uses existing DuckDB setup.
    In Phase 3, can be extended to use separate SQLiteDb for workflow state.

    Args:
        db_path: Optional custom path

    Returns:
        Initialized database tools
    """
    from main import initialize_database

    return initialize_database()


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


# ============================================================================
# Stub Functions - For Future Implementation
# ============================================================================
# These are placeholders for Agno Workflow integration in Phase 2
# Currently not used, but documented for reference


def create_agno_workflow():
    """
    [FUTURE] Create Agno Workflow with named steps.

    This will use Agno's Workflow + Step classes:
    - Step 1: Extract (ExtractionAgent)
    - Step 2: Analyze (AnalysisAgent)
    - Step 3: Validate (ValidationAgent)
    - Step 4: Review (ReviewAgent with HITL)
    - Step 5: Persist (Save to DB)

    For now, we're just wrapping existing main.py logic.
    """
    pass


def create_reviewer_agent_with_hitl():
    """
    [FUTURE] Create ReviewAgent with human-in-the-loop tools.

    This will use Agno's @tool(requires_user_input=True) decorator
    to pause agent execution and wait for human approval.

    For now, we're using existing human_review() CLI in main.py.
    """
    pass
