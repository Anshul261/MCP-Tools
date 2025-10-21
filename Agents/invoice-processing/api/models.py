"""
API Request/Response Models
Pydantic schemas for FastAPI endpoints
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class WorkflowStartResponse(BaseModel):
    """Response when starting a new workflow"""
    session_id: str
    status: str
    workflow_name: str
    created_at: Optional[str] = None


class WorkflowProgress(BaseModel):
    """Progress information"""
    steps_completed: int
    total_steps: int = 5
    percentage: int


class WorkflowStatus(BaseModel):
    """Current workflow status"""
    session_id: str
    state: str  # "processing", "completed", "paused", "failed", "rejected"
    current_step: int
    current_step_name: Optional[str] = None
    is_paused: bool
    workflow_run_id: Optional[str] = None
    paused_reason: Optional[str] = None
    progress: Optional[WorkflowProgress] = None
    confidence_score: Optional[float] = None
    invoice_data: Optional[Dict[str, Any]] = None
    validation_errors: Optional[List[str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class WorkflowStateDetail(BaseModel):
    """Complete workflow state for detailed queries"""
    session_id: str
    workflow_state: Dict[str, Any]


class ReviewRequest(BaseModel):
    """Human review request submission"""
    approved: bool
    notes: Optional[str] = None
    reviewer_id: Optional[str] = None


class ReviewResponse(BaseModel):
    """Response to review submission"""
    status: str
    message: str
    session_id: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str


class InvoiceResult(BaseModel):
    """Single invoice result"""
    id: int
    invoice_no: Optional[str] = None
    date_of_issue: Optional[str] = None
    seller_name: Optional[str] = None
    client_name: Optional[str] = None
    total_amount: Optional[float] = None
    confidence_score: Optional[float] = None
    created_at: Optional[str] = None


class InvoiceQueryResponse(BaseModel):
    """Response from invoice query"""
    invoices: List[Dict[str, Any]]
    total: int
    page: int
    limit: int


class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    status_code: int
