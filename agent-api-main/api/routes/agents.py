# api/routes/agents.py
from typing import List, Optional, AsyncGenerator, Dict, Any
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid
from datetime import datetime
import logging

from agents.selector import (
    get_available_agents,
    get_agent,
    validate_agent_id,
    get_agent_info,
    list_all_agents_info
)
from core.detailed_response import stream_detailed_agent_response, stream_simple_agent_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["Agents"])


class ChatRequest(BaseModel):
    """Request model for agent chat"""
    message: str
    user_id: Optional[str] = "default_user"
    session_id: Optional[str] = None
    stream: bool = True
    debug_mode: bool = False
    detailed_breakdown: bool = True  # Enable detailed breakdown by default


class ChatResponse(BaseModel):
    """Response model for non-streaming chat"""
    response: str
    session_id: str
    user_id: str
    agent_id: str


class AgentInfo(BaseModel):
    """Agent information model"""
    id: str
    name: str
    description: str
    type: str  # "agent" or "team"


@router.get("", response_model=List[str])
async def list_agents():
    """
    Returns a list of all available agent and team IDs.
    
    Returns:
        List[str]: List of agent/team identifiers
    """
    return get_available_agents()


@router.get("/info", response_model=List[AgentInfo])
async def list_agents_info():
    """
    Returns detailed information about all available agents and teams.
    
    Returns:
        List[AgentInfo]: List of agent/team information
    """
    return list_all_agents_info()


@router.get("/{agent_id}/info", response_model=AgentInfo)
async def get_agent_details(agent_id: str):
    """
    Get detailed information about a specific agent or team.
    
    Args:
        agent_id: The ID of the agent or team
        
    Returns:
        AgentInfo: Detailed agent/team information
    """
    info = get_agent_info(agent_id)
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent or team '{agent_id}' not found"
        )
    return info


async def stream_agent_response(
    agent, 
    message: str, 
    agent_id: str, 
    detailed_breakdown: bool = True,
    user_id: str = "default_user",
    session_id: str = None
) -> AsyncGenerator[str, None]:
    """
    Stream agent responses with optional detailed breakdown.
    
    Args:
        agent: The agent or team instance
        message: User message to process
        agent_id: Agent identifier for logging
        detailed_breakdown: Whether to include detailed breakdown
        user_id: User identifier
        session_id: Session identifier
        
    Yields:
        Text chunks from the agent response in SSE format
    """
    try:
        logger.info(f"Starting streaming response for agent {agent_id}, detailed={detailed_breakdown}")
        
        if detailed_breakdown:
            # Use detailed breakdown streaming
            async for chunk in stream_detailed_agent_response(agent, message, agent_id, user_id, session_id):
                yield f"data: {chunk}\n\n"
        else:
            # Use simple streaming (original behavior)
            async for chunk in stream_simple_agent_response(agent, message, agent_id):
                yield f"data: {chunk}\n\n"
        
        logger.info(f"Completed streaming response for agent {agent_id}")
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        logger.error(f"Error in streaming response for agent {agent_id}: {e}")
        yield f"data: Error: {str(e)}\n\n"
        yield "data: [DONE]\n\n"


@router.post("/{agent_id}/chat")
async def chat_with_agent(agent_id: str, request: ChatRequest):
    """
    Send a message to a specific agent or team and get a response.
    
    Args:
        agent_id: The ID of the agent or team to interact with
        request: Chat request parameters
        
    Returns:
        Either a streaming response or the complete agent response
    """
    # Validate agent ID
    if not validate_agent_id(agent_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent or team '{agent_id}' not found"
        )
    
    # Generate session ID if not provided
    session_id = request.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    logger.info(f"Chat request for agent {agent_id}, user {request.user_id}, session {session_id}")
    
    try:
        # Create agent instance
        agent = get_agent(
            agent_id=agent_id,
            user_id=request.user_id,
            session_id=session_id,
            debug_mode=request.debug_mode
        )
        
        if request.stream:
            # Return streaming response
            return StreamingResponse(
                stream_agent_response(
                    agent, 
                    request.message, 
                    agent_id,
                    request.detailed_breakdown,
                    request.user_id,
                    session_id
                ),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        else:
            # Return complete response
            if hasattr(agent, 'arun'):
                response = await agent.arun(request.message, stream=False)
            else:
                # Fallback for synchronous agents
                response = agent.run(request.message, stream=False)
            
            # Extract content from response
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            return ChatResponse(
                response=content,
                session_id=session_id,
                user_id=request.user_id,
                agent_id=agent_id
            )
    
    except Exception as e:
        logger.error(f"Error in chat with agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/{agent_id}/validate")
async def validate_agent(agent_id: str) -> Dict[str, Any]:
    """
    Validate that an agent or team exists and can be created.
    
    Args:
        agent_id: The ID of the agent or team to validate
        
    Returns:
        Validation result
    """
    if not validate_agent_id(agent_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent or team '{agent_id}' not found"
        )
    
    try:
        # Try to create the agent to validate it works
        agent = get_agent(
            agent_id=agent_id,
            user_id="validation_user",
            session_id="validation_session",
            debug_mode=False
        )
        
        return {
            "valid": True,
            "agent_id": agent_id,
            "type": "team" if hasattr(agent, 'members') else "agent",
            "name": getattr(agent, 'name', 'Unknown')
        }
        
    except Exception as e:
        logger.error(f"Agent validation failed for {agent_id}: {e}")
        return {
            "valid": False,
            "agent_id": agent_id,
            "error": str(e)
        }