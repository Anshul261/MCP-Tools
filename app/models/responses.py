from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from .requests import BaseResponse, StreamEvent, DocumentProcessingStatus, AgentType

# Chat Response Models
class ChatSession(BaseModel):
    """Chat session information"""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User ID for the session")
    title: Optional[str] = Field(None, description="Session title")
    created_at: datetime = Field(..., description="Session creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    message_count: int = Field(0, description="Number of messages in session")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Session metadata")

class ChatResponse(BaseResponse):
    """Response model for chat message"""
    response: str = Field(..., description="Agent response content")
    session_id: str = Field(..., description="Session ID for the conversation")
    agent_used: AgentType = Field(..., description="Agent that generated the response")
    tokens_used: Optional[int] = Field(None, description="Tokens consumed in generation")
    response_time: Optional[float] = Field(None, description="Response time in seconds")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="Sources used in response")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Tools called during generation")
    reasoning_steps: Optional[List[str]] = Field(None, description="Intermediate reasoning steps")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional response metadata")

class StreamingChatResponse(BaseModel):
    """Streaming chat response wrapper"""
    stream_id: str = Field(..., description="Unique stream identifier")
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    events: List[StreamEvent] = Field(default_factory=list, description="Stream events")
    status: str = Field("active", description="Stream status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Stream metadata")

class SessionListResponse(BaseResponse):
    """Response model for session listing"""
    sessions: List[ChatSession] = Field(..., description="List of user sessions")
    total_count: int = Field(..., description="Total number of sessions")
    page_info: Dict[str, Any] = Field(..., description="Pagination information")

class SessionResponse(BaseResponse):
    """Response model for single session operations"""
    session: ChatSession = Field(..., description="Session information")

class SessionCreateResponse(BaseResponse):
    """Response model for creating a new session"""
    session: ChatSession = Field(..., description="Created session information")

class SessionDeleteResponse(BaseResponse):
    """Response model for deleting a session"""
    session_id: str = Field(..., description="ID of deleted session")
    message: str = Field("Session deleted successfully", description="Confirmation message")

# Document Management Response Models
class DocumentInfo(BaseModel):
    """Document information model"""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    content_type: Optional[str] = Field(None, description="MIME type")
    size_bytes: int = Field(..., description="File size in bytes")
    status: DocumentProcessingStatus = Field(..., description="Processing status")
    created_at: datetime = Field(..., description="Upload timestamp")
    processed_at: Optional[datetime] = Field(None, description="Processing completion timestamp")
    description: Optional[str] = Field(None, description="Document description")
    tags: Optional[List[str]] = Field(None, description="Document tags")
    pages: Optional[int] = Field(None, description="Number of pages (for documents)")
    word_count: Optional[int] = Field(None, description="Word count")
    processing_error: Optional[str] = Field(None, description="Processing error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional document metadata")

class DocumentUploadResponse(BaseResponse):
    """Response model for document upload"""
    document: DocumentInfo = Field(..., description="Uploaded document information")
    processing_started: bool = Field(..., description="Whether processing was initiated")
    estimated_processing_time: Optional[float] = Field(None, description="Estimated processing time in seconds")

class DocumentListResponse(BaseResponse):
    """Response model for document listing"""
    documents: List[DocumentInfo] = Field(..., description="List of documents")
    total_count: int = Field(..., description="Total number of documents")
    page_info: Dict[str, Any] = Field(..., description="Pagination information")
    filter_info: Optional[Dict[str, Any]] = Field(None, description="Applied filters")

class DocumentResponse(BaseResponse):
    """Response model for single document operations"""
    document: DocumentInfo = Field(..., description="Document information")

class DocumentDeleteResponse(BaseResponse):
    """Response model for deleting a document"""
    document_id: str = Field(..., description="ID of deleted document")
    removed_from_knowledge_base: bool = Field(..., description="Whether document was removed from KB")
    message: str = Field("Document deleted successfully", description="Confirmation message")

class ReindexResponse(BaseResponse):
    """Response model for knowledge base reindexing"""
    documents_reindexed: int = Field(..., description="Number of documents reindexed")
    processing_time: float = Field(..., description="Processing time in seconds")
    knowledge_base_size: int = Field(..., description="Total knowledge base size")
    index_updated: bool = Field(..., description="Whether index was successfully updated")
    errors: Optional[List[str]] = Field(None, description="Any errors encountered during reindexing")

# System Response Models
class ComponentStatus(BaseModel):
    """Individual component status"""
    name: str = Field(..., description="Component name")
    status: str = Field(..., description="Component status (healthy, degraded, unhealthy)")
    details: Optional[str] = Field(None, description="Status details")
    last_check: datetime = Field(..., description="Last health check timestamp")
    response_time: Optional[float] = Field(None, description="Response time in seconds")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional component metadata")

class MemoryStats(BaseModel):
    """Memory database statistics"""
    total_memories: int = Field(..., description="Total number of memories")
    user_memories: int = Field(..., description="Number of user-specific memories")
    session_summaries: int = Field(..., description="Number of session summaries")
    database_size_mb: float = Field(..., description="Database size in MB")
    active_sessions: int = Field(..., description="Number of active sessions")
    unique_users: int = Field(..., description="Number of unique users")
    last_memory_created: Optional[datetime] = Field(None, description="Timestamp of last memory creation")

class AgentStatus(BaseModel):
    """Individual agent status"""
    agent_name: str = Field(..., description="Agent name")
    agent_type: AgentType = Field(..., description="Agent type")
    status: str = Field(..., description="Agent status")
    model_info: Dict[str, Any] = Field(..., description="Model configuration")
    capabilities: List[str] = Field(..., description="Agent capabilities")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    total_requests: int = Field(0, description="Total requests processed")
    error_rate: float = Field(0.0, description="Error rate (0.0 to 1.0)")

class HealthResponse(BaseResponse):
    """Response model for health check"""
    overall_status: str = Field(..., description="Overall system status")
    components: List[ComponentStatus] = Field(..., description="Individual component statuses")
    system_info: Dict[str, Any] = Field(..., description="System information")
    uptime_seconds: float = Field(..., description="System uptime in seconds")

class MemoryStatusResponse(BaseResponse):
    """Response model for memory status"""
    memory_stats: MemoryStats = Field(..., description="Memory database statistics")
    storage_info: Dict[str, Any] = Field(..., description="Storage database information")
    recent_activity: List[Dict[str, Any]] = Field(..., description="Recent memory activity")

class AgentStatusResponse(BaseResponse):
    """Response model for agent status"""
    agents: List[AgentStatus] = Field(..., description="Agent status information")
    system_info: Dict[str, Any] = Field(..., description="System-level agent information")
    knowledge_base_info: Optional[Dict[str, Any]] = Field(None, description="Knowledge base status")

# Streaming and WebSocket Response Models
class WebStreamingResponse(BaseModel):
    """Web-optimized streaming response"""
    event: str = Field(..., description="Event type for web client")
    data: Union[str, Dict[str, Any]] = Field(..., description="Event data")
    timestamp: str = Field(..., description="ISO timestamp")
    stream_id: Optional[str] = Field(None, description="Stream identifier")
    sequence: Optional[int] = Field(None, description="Event sequence number")

class StreamStatus(BaseModel):
    """Stream status information"""
    stream_id: str = Field(..., description="Stream identifier")
    status: str = Field(..., description="Stream status")
    events_sent: int = Field(..., description="Number of events sent")
    start_time: datetime = Field(..., description="Stream start time")
    duration: Optional[float] = Field(None, description="Stream duration in seconds")
    error: Optional[str] = Field(None, description="Error message if stream failed")

# Error Response Models
class ValidationErrorResponse(BaseResponse):
    """Response model for validation errors"""
    success: bool = Field(False)
    error_type: str = Field("validation_error")
    validation_errors: List[Dict[str, Any]] = Field(..., description="Detailed validation errors")

class NotFoundErrorResponse(BaseResponse):
    """Response model for 404 errors"""
    success: bool = Field(False)
    error_type: str = Field("not_found")
    resource_type: str = Field(..., description="Type of resource not found")
    resource_id: Optional[str] = Field(None, description="ID of resource not found")

class RateLimitErrorResponse(BaseResponse):
    """Response model for rate limiting errors"""
    success: bool = Field(False)
    error_type: str = Field("rate_limit_exceeded")
    retry_after: int = Field(..., description="Seconds to wait before retrying")
    limit_info: Dict[str, Any] = Field(..., description="Rate limit information")

# Utility Response Models
class PaginationInfo(BaseModel):
    """Pagination information"""
    current_page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")

class BatchOperationResponse(BaseResponse):
    """Response model for batch operations"""
    total_items: int = Field(..., description="Total items processed")
    successful_items: int = Field(..., description="Successfully processed items")
    failed_items: int = Field(..., description="Failed items")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="Detailed error information")
    processing_time: float = Field(..., description="Total processing time")

# API Metadata Models  
class APIInfo(BaseModel):
    """API information model"""
    name: str = Field("AGNO Multi-Agent API", description="API name")
    version: str = Field("1.0.0", description="API version")
    description: str = Field("REST API for AGNO multi-agent system", description="API description")
    endpoints: Dict[str, Any] = Field(..., description="Available endpoints")
    capabilities: List[str] = Field(..., description="API capabilities")
    rate_limits: Dict[str, Any] = Field(..., description="Rate limiting information")