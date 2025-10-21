"""
Session Manager
Manages workflow session state and persistence
"""

from typing import Dict, Optional, List
from datetime import datetime
import json


class SessionManager:
    """
    In-memory session storage for workflow execution state.
    Can be extended with file persistence or Redis.
    """

    def __init__(self):
        """Initialize session storage"""
        self.sessions: Dict[str, dict] = {}

    def create_session(self, session_id: str, image_path: str) -> dict:
        """
        Create a new workflow session

        Args:
            session_id: Unique session identifier
            image_path: Path to uploaded invoice image

        Returns:
            Created session data
        """
        now = datetime.now().isoformat()

        session = {
            "session_id": session_id,
            "image_path": image_path,
            "state": "initializing",  # initializing, processing, awaiting_human_input, completed, failed, rejected
            "current_step": 0,
            "current_step_name": None,
            "is_paused": False,
            "paused_reason": None,
            "paused_at_step": None,
            "workflow_run_id": None,
            "awaiting_approval": False,
            "approval_status": None,
            "review_notes": None,
            "reviewer_id": None,
            "created_at": now,
            "updated_at": now,
            "extracted_text": None,
            "invoice_data": None,
            "confidence_score": None,
            "validation_result": None,
            "validation_errors": [],
            "invoice_id": None,
            "error": None,
        }

        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[dict]:
        """
        Get session by ID

        Args:
            session_id: Session identifier

        Returns:
            Session data or None if not found
        """
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, updates: dict) -> Optional[dict]:
        """
        Update session with new data

        Args:
            session_id: Session identifier
            updates: Dictionary of fields to update

        Returns:
            Updated session data or None if session not found
        """
        if session_id not in self.sessions:
            return None

        self.sessions[session_id].update(updates)
        self.sessions[session_id]["updated_at"] = datetime.now().isoformat()
        return self.sessions[session_id]

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def list_sessions(self, state: Optional[str] = None) -> List[dict]:
        """
        List all sessions, optionally filtered by state

        Args:
            state: Optional state filter (e.g., "completed", "processing")

        Returns:
            List of sessions
        """
        if state:
            return [s for s in self.sessions.values() if s["state"] == state]
        return list(self.sessions.values())

    def get_session_count(self) -> int:
        """Get total number of sessions"""
        return len(self.sessions)

    def get_active_sessions(self) -> List[dict]:
        """Get all active (non-completed) sessions"""
        active_states = ["initializing", "processing", "awaiting_human_input"]
        return [s for s in self.sessions.values() if s["state"] in active_states]

    def get_paused_sessions(self) -> List[dict]:
        """Get all paused sessions awaiting human input"""
        return [s for s in self.sessions.values() if s["is_paused"]]

    def set_step_progress(self, session_id: str, step: int, step_name: str) -> Optional[dict]:
        """
        Update step progress

        Args:
            session_id: Session identifier
            step: Current step number
            step_name: Step name

        Returns:
            Updated session
        """
        return self.update_session(
            session_id,
            {
                "current_step": step,
                "current_step_name": step_name,
                "state": "processing",
            },
        )

    def pause_at_step(
        self, session_id: str, step: int, reason: str, run_id: str
    ) -> Optional[dict]:
        """
        Pause workflow at a step (for HITL)

        Args:
            session_id: Session identifier
            step: Step where paused
            reason: Reason for pause
            run_id: Agno run_id for resumption

        Returns:
            Updated session
        """
        return self.update_session(
            session_id,
            {
                "is_paused": True,
                "paused_at_step": step,
                "paused_reason": reason,
                "workflow_run_id": run_id,
                "awaiting_approval": True,
                "state": "awaiting_human_input",
            },
        )

    def resume_from_pause(self, session_id: str) -> Optional[dict]:
        """
        Resume workflow after human approval

        Args:
            session_id: Session identifier

        Returns:
            Updated session
        """
        return self.update_session(
            session_id,
            {
                "is_paused": False,
                "awaiting_approval": False,
                "state": "processing",
            },
        )

    def complete_session(self, session_id: str, invoice_id: int) -> Optional[dict]:
        """
        Mark session as completed with resulting invoice ID

        Args:
            session_id: Session identifier
            invoice_id: ID of saved invoice

        Returns:
            Updated session
        """
        return self.update_session(
            session_id,
            {
                "state": "completed",
                "invoice_id": invoice_id,
                "current_step": 5,
                "current_step_name": "Completed",
            },
        )

    def fail_session(self, session_id: str, error: str) -> Optional[dict]:
        """
        Mark session as failed

        Args:
            session_id: Session identifier
            error: Error message

        Returns:
            Updated session
        """
        return self.update_session(
            session_id,
            {
                "state": "failed",
                "error": error,
            },
        )

    def reject_session(self, session_id: str, reason: str) -> Optional[dict]:
        """
        Mark session as rejected by human reviewer

        Args:
            session_id: Session identifier
            reason: Rejection reason

        Returns:
            Updated session
        """
        return self.update_session(
            session_id,
            {
                "state": "rejected",
                "approval_status": False,
                "review_notes": reason,
                "is_paused": False,
            },
        )

    def export_session(self, session_id: str) -> Optional[str]:
        """
        Export session as JSON string

        Args:
            session_id: Session identifier

        Returns:
            JSON string or None if session not found
        """
        session = self.get_session(session_id)
        if session:
            return json.dumps(session, indent=2, default=str)
        return None

    def get_statistics(self) -> dict:
        """
        Get session statistics

        Returns:
            Dictionary with statistics
        """
        total = len(self.sessions)
        completed = sum(1 for s in self.sessions.values() if s["state"] == "completed")
        failed = sum(1 for s in self.sessions.values() if s["state"] == "failed")
        paused = sum(1 for s in self.sessions.values() if s["is_paused"])
        processing = sum(
            1 for s in self.sessions.values() if s["state"] == "processing"
        )

        return {
            "total_sessions": total,
            "completed": completed,
            "failed": failed,
            "paused": paused,
            "processing": processing,
            "success_rate": (completed / total * 100) if total > 0 else 0,
        }
