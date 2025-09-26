from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class StreamingFormat(str, Enum):
    """Supported streaming formats for responses"""
    JSON = "json"
    TEXT = "text"
    SSE = "sse"

class ChatMessageRole(str, Enum):
    """Chat message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class AgentType(str, Enum):
    """Available agent types"""
    DOC_AGENT = "doc_agent"
    WEB_AGENT = "web_agent"
    TEAM = "team"

class DocumentProcessingStatus(str, Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Chat Request Models
class ChatMessage(BaseModel):
    """Individual chat message"""
    role: ChatMessageRole
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    """Request model for chat message endpoint"""
    message: str = Field(..., description="User message to send to agents")
    user_id: str = Field(..., description="Unique user identifier")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    agent_type: Optional[AgentType] = Field(AgentType.TEAM, description="Specific agent to use")
    stream: bool = Field(True, description="Enable streaming response")
    streaming_format: StreamingFormat = Field(StreamingFormat.SSE, description="Streaming format")
    show_reasoning: bool = Field(False, description="Show intermediate reasoning steps")
    stream_intermediate_steps: bool = Field(False, description="Stream intermediate processing steps")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens in response")
    temperature: Optional[float] = Field(None, description="Model temperature override")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional request metadata")

class CreateSessionRequest(BaseModel):
    """Request model for creating new chat session"""
    user_id: str = Field(..., description="User ID for the session")
    title: Optional[str] = Field(None, description="Optional session title")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Session metadata")

# Document Management Request Models
class DocumentUploadRequest(BaseModel):
    """Request model for document upload (metadata, file handled separately)"""
    filename: str = Field(..., description="Original filename")
    content_type: Optional[str] = Field(None, description="MIME type of the file")
    description: Optional[str] = Field(None, description="Document description")
    tags: Optional[List[str]] = Field(None, description="Document tags for organization")
    auto_process: bool = Field(True, description="Automatically process and index document")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional document metadata")

class DocumentQuery(BaseModel):
    """Query parameters for document listing"""
    limit: int = Field(20, ge=1, le=100, description="Number of documents to return")
    offset: int = Field(0, ge=0, description="Offset for pagination")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    search: Optional[str] = Field(None, description="Search in document content/metadata")
    status: Optional[DocumentProcessingStatus] = Field(None, description="Filter by processing status")
    sort_by: Optional[str] = Field("created_at", description="Field to sort by")
    sort_desc: bool = Field(True, description="Sort in descending order")

class ReindexRequest(BaseModel):
    """Request model for knowledge base reindexing"""
    force: bool = Field(False, description="Force complete rebuild of knowledge base")
    document_ids: Optional[List[str]] = Field(None, description="Specific documents to reindex")
    clear_existing: bool = Field(False, description="Clear existing index before rebuilding")

# System and Utility Request Models
class MemoryQuery(BaseModel):
    """Query parameters for memory retrieval"""
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    session_id: Optional[str] = Field(None, description="Filter by session ID")
    limit: int = Field(10, ge=1, le=100, description="Number of memories to return")
    include_summaries: bool = Field(True, description="Include session summaries")
    include_user_memories: bool = Field(True, description="Include user-specific memories")

class HealthCheckRequest(BaseModel):
    """Request model for health check (optional parameters)"""
    detailed: bool = Field(False, description="Include detailed component status")
    check_db: bool = Field(True, description="Check database connectivity")
    check_agents: bool = Field(True, description="Check agent availability")
    check_knowledge_base: bool = Field(True, description="Check knowledge base status")

# Base Response Models (used as base classes)
class BaseResponse(BaseModel):
    """Base response model with common fields"""
    success: bool = Field(..., description="Whether the request was successful")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Unique request identifier")

class ErrorResponse(BaseResponse):
    """Standard error response model"""
    success: bool = Field(False, description="Always false for error responses")
    error_code: str = Field(..., description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    trace_id: Optional[str] = Field(None, description="Error trace identifier")

# Streaming Event Models
class StreamEventType(str, Enum):
    """Types of streaming events"""
    STATUS = "status"
    CONTENT = "content"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    AGENT_THINKING = "agent_thinking"
    ERROR = "error"
    COMPLETE = "complete"
    METADATA = "metadata"

class StreamEvent(BaseModel):
    """Individual streaming event"""
    event_type: StreamEventType = Field(..., description="Type of streaming event")
    data: Union[str, Dict[str, Any]] = Field(..., description="Event data payload")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    sequence: Optional[int] = Field(None, description="Event sequence number")
    agent_name: Optional[str] = Field(None, description="Name of the agent generating this event")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional event metadata")

class WebStreamingRequest(BaseModel):
    """Specialized request for web interface streaming"""
    message: str = Field(..., description="User message")
    user_id: str = Field(..., description="User ID")
    session_id: Optional[str] = Field(None, description="Session ID")
    stream_format: StreamingFormat = Field(StreamingFormat.SSE, description="Streaming format")
    include_reasoning: bool = Field(False, description="Include reasoning in stream")
    include_tool_calls: bool = Field(True, description="Include tool calls in stream")
    response_format: str = Field("web", description="Response format optimized for web")