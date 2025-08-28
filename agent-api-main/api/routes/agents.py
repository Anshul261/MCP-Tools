# api/routes/agents.py
from typing import List, Optional, AsyncGenerator, Dict, Any
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid
from datetime import datetime
import logging
import json
import time

from agents.selector import (
    get_available_agents,
    get_agent,
    validate_agent_id,
    get_agent_info,
    list_all_agents_info
)
from core.real_detailed_response import stream_real_detailed_agent_response, stream_simple_agent_response_real

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["Agents"])


class ChatRequest(BaseModel):
    """Request model for agent chat"""
    message: str
    user_id: Optional[str] = "default_user"
    session_id: Optional[str] = None
    stream: bool = True
    stream_format: str = "web"  # "web" or "console"
    include_reasoning: bool = False  # For web, reasoning is optional
    debug_mode: bool = False
    detailed_breakdown: bool = True  # Kept for backwards compatibility


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


class WebStreamingResponse:
    """Handles structured streaming responses for web interfaces"""
    
    def __init__(self, agent_id: str, user_id: str, session_id: str):
        self.agent_id = agent_id
        self.user_id = user_id
        self.session_id = session_id
        self.start_time = time.time()
        self.message_id = f"{session_id}_{int(time.time())}"
        logger.info(f"WebStreamingResponse initialized for agent {agent_id}, session {session_id}")
    
    def create_event(self, event_type: str, data: Any, metadata: Optional[Dict] = None) -> str:
        """Create a structured JSON event for streaming"""
        event = {
            "id": self.message_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "data": data
        }
        
        if metadata:
            event["metadata"] = metadata
            
        logger.debug(f"Created {event_type} event for agent {self.agent_id}")
        return f"data: {json.dumps(event)}\n\n"
    
    def status_event(self, status: str, message: str) -> str:
        """Create a status update event"""
        logger.info(f"Agent {self.agent_id} status: {status} - {message}")
        return self.create_event("status", {
            "status": status,
            "message": message
        })
    
    def content_event(self, content: str, is_partial: bool = True) -> str:
        """Create a content chunk event"""
        logger.debug(f"Agent {self.agent_id} content chunk: {len(content)} chars")
        return self.create_event("content", {
            "content": content,
            "is_partial": is_partial
        })
    
    def tool_call_event(self, tool_name: str, args: Dict, status: str = "started") -> str:
        """Create a tool call event"""
        logger.info(f"Agent {self.agent_id} tool call: {tool_name} - {status}")
        return self.create_event("tool_call", {
            "tool_name": tool_name,
            "arguments": args,
            "status": status
        })
    
    def agent_response_event(self, agent_name: str, content: str) -> str:
        """Create an agent response event for teams"""
        logger.info(f"Team member response from {agent_name}: {len(content)} chars")
        return self.create_event("agent_response", {
            "agent_name": agent_name,
            "content": content
        })
    
    def reasoning_event(self, reasoning_step: str) -> str:
        """Create a reasoning step event"""
        logger.debug(f"Agent {self.agent_id} reasoning step: {len(reasoning_step)} chars")
        return self.create_event("reasoning", {
            "step": reasoning_step
        })
    
    def complete_event(self, final_response: str) -> str:
        """Create a completion event"""
        elapsed = time.time() - self.start_time
        logger.info(f"Agent {self.agent_id} completed response in {elapsed:.2f}s")
        return self.create_event("complete", {
            "final_response": final_response,
            "elapsed_time": elapsed
        })
    
    def error_event(self, error_message: str) -> str:
        """Create an error event"""
        logger.error(f"Agent {self.agent_id} error: {error_message}")
        return self.create_event("error", {
            "error": error_message
        })


async def stream_web_agent_response(
    agent, 
    message: str, 
    agent_id: str, 
    user_id: str = "default_user",
    session_id: str = None,
    include_reasoning: bool = False
) -> AsyncGenerator[str, None]:
    """
    Stream agent responses in web-friendly structured JSON format with proper token buffering
    """
    try:
        streamer = WebStreamingResponse(agent_id, user_id, session_id)
        logger.info(f"Starting web streaming for agent {agent_id} with message: '{message[:50]}...'")
        
        # Send initial status
        yield streamer.status_event("processing", f"Processing your request with {agent_id}")
        
        # Get streaming response from agent
        logger.debug(f"Getting streaming response from agent {agent_id}")
        run_response = await agent.arun(message, stream=True)
        
        # Token buffering for better streaming experience
        token_buffer = ""
        buffer_size = 5  # Send content every 5 tokens
        token_count = 0
        accumulated_content = ""
        previous_chunk = ""
        
        tool_calls_seen = []
        agent_responses = []
        
        logger.debug(f"Starting to process chunks from agent {agent_id}")
        chunk_count = 0
        
        async for chunk in run_response:
            chunk_count += 1
            try:
                logger.debug(f"Processing chunk {chunk_count} from agent {agent_id}")
                
                # Handle different chunk types from AGNO
                if hasattr(chunk, 'content') and chunk.content:
                    content = chunk.content.strip()
                    if content:
                        # Apply the AGGRESSIVE spacing fix from the original console version
                        if previous_chunk:
                            if (not content.startswith(('.', ',', '!', '?', ';', ':', ')', ']', '}', '"', "'")) and
                                not previous_chunk.endswith((' ', '\n', '\t', '-', '(', '[', '{'))):
                                token_buffer += ' '
                                accumulated_content += ' '
                        
                        token_buffer += content
                        accumulated_content += content
                        previous_chunk = content
                        token_count += 1
                        
                        # Send buffered content when buffer reaches size or on punctuation
                        should_flush = (
                            token_count >= buffer_size or 
                            content.endswith(('.', '!', '?', '\n')) or
                            chunk_count % 10 == 0  # Periodic flush every 10 chunks
                        )
                        
                        if should_flush and token_buffer.strip():
                            logger.debug(f"Flushing buffer: '{token_buffer[:50]}...'")
                            yield streamer.content_event(token_buffer, is_partial=True)
                            token_buffer = ""
                            token_count = 0
                
                # Handle tool calls
                if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                    # Flush any remaining buffer before tool call
                    if token_buffer.strip():
                        yield streamer.content_event(token_buffer, is_partial=True)
                        token_buffer = ""
                        token_count = 0
                    
                    for tool_call in chunk.tool_calls:
                        tool_name = getattr(tool_call, 'name', 'unknown_tool')
                        args = getattr(tool_call, 'arguments', {})
                        tool_calls_seen.append((tool_name, args))
                        logger.info(f"Tool call detected: {tool_name} with args: {args}")
                        yield streamer.tool_call_event(tool_name, args, "executing")
                
                # Handle tool call results
                if hasattr(chunk, 'tool_results') and chunk.tool_results:
                    for result in chunk.tool_results:
                        tool_name = getattr(result, 'tool_name', 'unknown_tool')
                        logger.info(f"Tool call completed: {tool_name}")
                        yield streamer.tool_call_event(tool_name, {}, "completed")
                
                # Handle team member responses
                if hasattr(chunk, 'member_response') and chunk.member_response:
                    # Flush buffer before member response
                    if token_buffer.strip():
                        yield streamer.content_event(token_buffer, is_partial=True)
                        token_buffer = ""
                        token_count = 0
                    
                    member_name = getattr(chunk.member_response, 'agent_name', 'Team Member')
                    member_content = getattr(chunk.member_response, 'content', str(chunk.member_response))
                    agent_responses.append((member_name, member_content))
                    logger.info(f"Team member {member_name} responded with {len(member_content)} chars")
                    yield streamer.agent_response_event(member_name, member_content)
                
                # Handle reasoning steps (if requested and available)
                if include_reasoning and hasattr(chunk, 'reasoning') and chunk.reasoning:
                    logger.debug(f"Reasoning step: {chunk.reasoning[:50]}...")
                    yield streamer.reasoning_event(chunk.reasoning)
                
            except Exception as chunk_error:
                logger.error(f"Error processing chunk {chunk_count}: {chunk_error}")
                continue
        
        # Flush any remaining buffer
        if token_buffer.strip():
            logger.debug(f"Final buffer flush: '{token_buffer[:50]}...'")
            yield streamer.content_event(token_buffer, is_partial=True)
        
        logger.info(f"Processed {chunk_count} chunks from agent {agent_id}")
        logger.info(f"Tool calls seen: {len(tool_calls_seen)}, Agent responses: {len(agent_responses)}")
        logger.info(f"Final accumulated content length: {len(accumulated_content)} chars")
        
        # Send completion event with properly spaced content
        yield streamer.complete_event(accumulated_content)
        logger.info(f"Completed web streaming for agent {agent_id}")
        
    except Exception as e:
        logger.error(f"Error in web streaming for agent {agent_id}: {e}", exc_info=True)
        try:
            streamer = WebStreamingResponse(agent_id, user_id, session_id)
            yield streamer.error_event(str(e))
        except Exception as error_event_error:
            logger.error(f"Failed to create error event: {error_event_error}")
            # Fallback error response
            yield f"data: {json.dumps({'event_type': 'error', 'data': {'error': str(e)}})}\n\n"


async def stream_agent_response(
    agent, 
    message: str, 
    agent_id: str, 
    stream_format: str = "web",
    include_reasoning: bool = False,
    detailed_breakdown: bool = True,
    user_id: str = "default_user",
    session_id: str = None
) -> AsyncGenerator[str, None]:
    """
    Stream agent responses with optional detailed breakdown.
    """
    try:
        logger.info(f"Starting streaming response for agent {agent_id}, format={stream_format}")
        
        if stream_format == "web":
            # Use structured JSON streaming for web interfaces
            logger.info(f"Using web streaming format for agent {agent_id}")
            async for chunk in stream_web_agent_response(
                agent, message, agent_id, user_id, session_id, include_reasoning
            ):
                yield chunk
        elif detailed_breakdown:
            # Use detailed breakdown streaming with REAL agent traces
            logger.info(f"Using detailed breakdown streaming for agent {agent_id}")
            async for chunk in stream_real_detailed_agent_response(agent, message, agent_id, user_id, session_id):
                yield f"data: {chunk}\n\n"
        else:
            # Use simple streaming (original behavior)
            logger.info(f"Using simple streaming for agent {agent_id}")
            async for chunk in stream_simple_agent_response_real(agent, message, agent_id):
                yield f"data: {chunk}\n\n"
        
        logger.info(f"Completed streaming response for agent {agent_id}")
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        logger.error(f"Error in streaming response for agent {agent_id}: {e}", exc_info=True)
        if stream_format == "web":
            try:
                streamer = WebStreamingResponse(agent_id, user_id, session_id)
                yield streamer.error_event(str(e))
            except Exception as error_event_error:
                logger.error(f"Failed to create error event: {error_event_error}")
                yield f"data: {json.dumps({'event_type': 'error', 'data': {'error': str(e)}})}\n\n"
        else:
            yield f"data: Error: {str(e)}\n\n"
        yield "data: [DONE]\n\n"


@router.get("", response_model=List[str])
async def list_agents():
    """
    Returns a list of all available agent and team IDs.
    
    Returns:
        List[str]: List of agent/team identifiers
    """
    agents = get_available_agents()
    logger.info(f"Listed {len(agents)} available agents: {agents}")
    return agents


@router.get("/info", response_model=List[AgentInfo])
async def list_agents_info():
    """
    Returns detailed information about all available agents and teams.
    
    Returns:
        List[AgentInfo]: List of agent/team information
    """
    agents_info = list_all_agents_info()
    logger.info(f"Retrieved info for {len(agents_info)} agents/teams")
    return agents_info


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
        logger.warning(f"Agent or team '{agent_id}' not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent or team '{agent_id}' not found"
        )
    logger.info(f"Retrieved info for agent {agent_id}: {info['name']}")
    return info


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
        logger.warning(f"Invalid agent ID requested: {agent_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent or team '{agent_id}' not found"
        )
    
    # Generate session ID if not provided
    session_id = request.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    logger.info(f"Chat request for agent {agent_id}")
    logger.info(f"  User: {request.user_id}")
    logger.info(f"  Session: {session_id}")
    logger.info(f"  Stream format: {request.stream_format}")
    logger.info(f"  Include reasoning: {request.include_reasoning}")
    logger.info(f"  Message: '{request.message[:100]}...'")
    
    try:
        # Create agent instance
        logger.debug(f"Creating agent instance for {agent_id}")
        agent = get_agent(
            agent_id=agent_id,
            user_id=request.user_id,
            session_id=session_id,
            debug_mode=request.debug_mode
        )
        logger.info(f"Successfully created agent {agent_id}")
        
        if request.stream:
            # Return streaming response
            logger.info(f"Starting streaming response for agent {agent_id}")
            return StreamingResponse(
                stream_agent_response(
                    agent, 
                    request.message, 
                    agent_id,
                    request.stream_format,
                    request.include_reasoning,
                    request.detailed_breakdown,
                    request.user_id,
                    session_id
                ),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                }
            )
        else:
            # Return complete response
            logger.info(f"Getting complete response from agent {agent_id}")
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
            
            logger.info(f"Agent {agent_id} completed non-streaming response: {len(content)} chars")
            
            return ChatResponse(
                response=content,
                session_id=session_id,
                user_id=request.user_id,
                agent_id=agent_id
            )
    
    except Exception as e:
        logger.error(f"Error in chat with agent {agent_id}: {e}", exc_info=True)
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
    logger.info(f"Validating agent {agent_id}")
    
    if not validate_agent_id(agent_id):
        logger.warning(f"Agent validation failed: {agent_id} not found")
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
        
        validation_result = {
            "valid": True,
            "agent_id": agent_id,
            "type": "team" if hasattr(agent, 'members') else "agent",
            "name": getattr(agent, 'name', 'Unknown')
        }
        
        logger.info(f"Agent {agent_id} validation successful: {validation_result}")
        return validation_result
        
    except Exception as e:
        logger.error(f"Agent validation failed for {agent_id}: {e}")
        return {
            "valid": False,
            "agent_id": agent_id,
            "error": str(e)
        }