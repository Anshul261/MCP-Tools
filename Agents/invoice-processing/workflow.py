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
    session_state: WorkflowSessionState,
    db_tools: SqliteDb,
    skip_human_review: bool = False  # Skip CLI review, use API instead
) -> WorkflowSessionState:
    """
    Main workflow wrapper with API-aware human review.

    This is a thin wrapper that:
    1. Calls existing process_invoice() from main.py
    2. Handles human review via API (not CLI)
    3. Tracks state in session_state for API consumption
    4. Returns the updated session state

    The existing pipeline logic remains completely untouched.
    We just wrap it to track progress and enable API-based pause/resume.

    Args:
        session_state: Workflow state tracker
        db_tools: DuckDB tools instance
        skip_human_review: If True, skip CLI review and pause for API

    Returns:
        Updated session_state with results
    """

    # Import here to avoid circular imports
    from main import (
        initialize_database,
        create_extraction_agent,
        create_analysis_agent,
        create_validation_agent,
        save_to_database,
    )
    from agno.media import Image
    import json

    try:
        # ============ STEP 1: EXTRACT ============
        session_state.current_step = 1
        session_state.current_step_name = "Extract"

        extraction_agent = create_extraction_agent()
        extraction_result = extraction_agent.run(
            "Extract all text from this invoice image with perfect accuracy.",
            images=[Image(filepath=session_state.image_path)],
        )
        session_state.extracted_text = extraction_result.content
        print(f"[+] Step 1 Complete: Extracted {len(session_state.extracted_text)} characters")

        # ============ STEP 2: ANALYZE ============
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
            print(f"[+] Step 2 Complete: Found {len(session_state.invoice_dict.get('line_items', []))} line items")
        except json.JSONDecodeError as e:
            print(f"[!] Error parsing JSON: {e}")
            session_state.invoice_dict = {}
            raise

        # ============ STEP 3: VALIDATE ============
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
            print(f"[+] Step 3 Complete: Confidence {session_state.confidence_score:.2%}")
        except json.JSONDecodeError:
            print("[!] Could not parse validation response")
            session_state.confidence_score = 0.5
            session_state.invoice_dict["confidence_score"] = 0.5

        # ============ STEP 4: REVIEW (API-AWARE) ============
        session_state.current_step = 4
        session_state.current_step_name = "Review"

        from config import Config
        from models import InvoiceData

        # Check if we need human review
        needs_review = (
            session_state.confidence_score < Config.AUTO_APPROVE_CONFIDENCE
            and Config.HUMAN_REVIEW_ENABLED
        )

        if needs_review and skip_human_review:
            # *** PAUSE FOR API REVIEW ***
            print(f"[!] Low confidence {session_state.confidence_score:.2%} - Pausing for API review")
            session_state.current_step_name = "Review (Awaiting User)"
            return session_state  # Return with approval_status = None (workflow paused)

        elif needs_review and not skip_human_review:
            # *** USE CLI REVIEW (backward compat) ***
            print(f"[!] Low confidence {session_state.confidence_score:.2%} - Using CLI review")
            from main import human_review as cli_human_review
            invoice_data = InvoiceData(**session_state.invoice_dict)
            approved, _ = cli_human_review(invoice_data, session_state.extracted_text)
            session_state.approval_status = approved
        else:
            # *** AUTO APPROVE ***
            print(f"[+] Auto-approved (confidence {session_state.confidence_score:.2%} >= {Config.AUTO_APPROVE_CONFIDENCE:.2%})")
            session_state.approval_status = True

        print(f"[+] Step 4 Complete: Approval = {session_state.approval_status}")

        # ============ STEP 5: PERSIST (Only if approved) ============
        if session_state.approval_status is None:
            # Still waiting for API review, don't continue
            print(f"[!] Workflow paused at Step 4 - waiting for human review")
            return session_state

        session_state.current_step = 5
        session_state.current_step_name = "Persist"

        if session_state.approval_status:
            invoice_data = InvoiceData(**session_state.invoice_dict)
            invoice_id = save_to_database(invoice_data, db_tools)
            session_state.invoice_id = invoice_id
            print(f"[+] Step 5 Complete: Saved invoice ID {invoice_id}")
        else:
            print(f"[!] Invoice rejected - not saving")

        return session_state

    except Exception as e:
        print(f"[!] Error in workflow: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


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
