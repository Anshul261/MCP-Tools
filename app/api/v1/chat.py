from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
import uuid
from datetime import datetime

from ...core.streaming import (
    WebStreamingResponseHandler, 
    streaming_manager, 
    create_sse_response,
    AgentStreamingIntegrator
)
from ...models.requests import (
    ChatRequest,
    CreateSessionRequest,
    WebStreamingRequest,
    AgentType
)
from ...models.responses import (
    ChatResponse,
    SessionListResponse,
    SessionCreateResponse,
    SessionDeleteResponse,
    ChatSession
)
from ...core.agents import get_agent_system
from ...core.database import get_session_storage, get_memory_system

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# Dependency to get agent system
async def get_agents():
    return get_agent_system()

# Dependency to get storage
async def get_storage():
    return get_session_storage()

# Dependency to get memory
async def get_memory():
    return get_memory_system()

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    agents = Depends(get_agents),
    storage = Depends(get_storage),
    memory = Depends(get_memory)
):
    """
    Send a message to the AI agent team
    
    Supports both streaming and non-streaming responses based on the request parameters.
    """
    try:
        # Generate session ID if not provided
        if not request.session_id:
            request.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        if request.stream:
            # Return streaming response
            async def stream_generator():
                agent_generator = agents.get_agent_response(
                    message=request.message,
                    user_id=request.user_id,
                    session_id=request.session_id,
                    agent_type=request.agent_type or AgentType.TEAM,
                    stream=True,
                    show_reasoning=request.show_reasoning,
                    stream_intermediate_steps=request.stream_intermediate_steps
                )
                
                async for chunk in agent_generator:
                    # Convert agent response to SSE format
                    import json
                    yield f"data: {json.dumps(chunk)}\n\n"
            
            return create_sse_response(stream_generator())
        
        else:
            # Non-streaming response (for backwards compatibility)
            response_generator = agents.get_agent_response(
                message=request.message,
                user_id=request.user_id,
                session_id=request.session_id,
                agent_type=request.agent_type or AgentType.TEAM,
                stream=False
            )
            
            # Get the response from the async generator
            response_content = ""
            async for response_chunk in response_generator:
                if response_chunk.get("type") == "response":
                    response_content = response_chunk.get("content", "")
                elif response_chunk.get("type") == "content":
                    response_content += response_chunk.get("data", {}).get("content", "")
            
            response = type('Response', (), {'content': response_content})()
            
            return ChatResponse(
                success=True,
                response=response.content if hasattr(response, 'content') else str(response),
                session_id=request.session_id,
                agent_used=request.agent_type or "team",
                timestamp=datetime.utcnow()
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.post("/message/stream")
async def send_message_stream(
    request: WebStreamingRequest,
    agents = Depends(get_agents)
):
    """
    Send a message with optimized streaming for web interfaces
    
    Returns Server-Sent Events (SSE) stream with real-time response chunks.
    """
    try:
        # Generate session ID if not provided
        if not request.session_id:
            request.session_id = f"web_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Create streaming handler
        handler = WebStreamingResponseHandler(streaming_manager)
        
        # Create the streaming response
        generator = handler.create_chat_stream(
            user_id=request.user_id,
            session_id=request.session_id,
            message=request.message,
            agent_system=agents,
            show_reasoning=request.include_reasoning,
            stream_intermediate_steps=request.include_tool_calls
        )
        
        return create_sse_response(generator)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating stream: {str(e)}")

@router.get("/sessions/{user_id}", response_model=SessionListResponse)
async def list_sessions(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    storage = Depends(get_storage)
):
    """
    List chat sessions for a specific user
    
    Returns paginated list of sessions with metadata.
    """
    try:
        # Get sessions from storage (this needs to be implemented based on AGNO storage API)
        sessions_data = await storage.get_sessions(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        sessions = []
        for session_data in sessions_data.get('sessions', []):
            sessions.append(ChatSession(
                session_id=session_data.get('session_id'),
                user_id=user_id,
                title=session_data.get('title'),
                created_at=session_data.get('created_at', datetime.utcnow()),
                updated_at=session_data.get('updated_at', datetime.utcnow()),
                message_count=session_data.get('message_count', 0),
                metadata=session_data.get('metadata', {})
            ))
        
        return SessionListResponse(
            success=True,
            sessions=sessions,
            total_count=sessions_data.get('total_count', len(sessions)),
            page_info={
                "current_page": offset // limit + 1,
                "per_page": limit,
                "has_next": sessions_data.get('has_more', False),
                "total_count": sessions_data.get('total_count', len(sessions))
            },
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sessions: {str(e)}")

@router.post("/sessions", response_model=SessionCreateResponse)
async def create_session(
    request: CreateSessionRequest,
    storage = Depends(get_storage),
    memory = Depends(get_memory)
):
    """
    Create a new chat session for a user
    
    Initializes session storage and memory context.
    """
    try:
        # Generate session ID
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Create session in storage
        session_data = {
            'session_id': session_id,
            'user_id': request.user_id,
            'title': request.title or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'message_count': 0,
            'metadata': request.metadata or {}
        }
        
        # Store session
        await storage.create_session(session_data)
        
        # Initialize memory context if needed
        if memory:
            await memory.initialize_session(session_id, request.user_id)
        
        session = ChatSession(**session_data)
        
        return SessionCreateResponse(
            success=True,
            session=session,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@router.delete("/sessions/{session_id}", response_model=SessionDeleteResponse)
async def delete_session(
    session_id: str,
    storage = Depends(get_storage),
    memory = Depends(get_memory)
):
    """
    Delete a chat session and all associated data
    
    Removes session from storage and clears memory context.
    """
    try:
        # Check if session exists
        session_exists = await storage.session_exists(session_id)
        if not session_exists:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Delete from storage
        await storage.delete_session(session_id)
        
        # Clear memory context
        if memory:
            await memory.clear_session(session_id)
        
        return SessionDeleteResponse(
            success=True,
            session_id=session_id,
            message="Session deleted successfully",
            timestamp=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    storage = Depends(get_storage)
):
    """
    Get messages from a specific session
    
    Returns paginated message history for the session.
    """
    try:
        # Get messages from storage
        messages = await storage.get_session_messages(
            session_id=session_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "messages": messages,
            "timestamp": datetime.utcnow()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")

@router.get("/stream/{stream_id}/status")
async def get_stream_status(stream_id: str):
    """
    Get the status of an active stream
    
    Returns stream information and event count.
    """
    try:
        stream_info = streaming_manager.get_stream_info(stream_id)
        
        if not stream_info:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        return {
            "success": True,
            "stream_info": stream_info,
            "timestamp": datetime.utcnow()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stream status: {str(e)}")