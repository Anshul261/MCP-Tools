# core/web_streaming.py
from typing import AsyncGenerator, Dict, Any, Optional
import json
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class WebStreamingResponse:
    """Handles structured streaming responses for web interfaces"""
    
    def __init__(self, agent_id: str, user_id: str, session_id: str):
        self.agent_id = agent_id
        self.user_id = user_id
        self.session_id = session_id
        self.start_time = time.time()
        self.message_id = f"{session_id}_{int(time.time())}"
    
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
            
        return f"data: {json.dumps(event)}\n\n"
    
    def status_event(self, status: str, message: str) -> str:
        """Create a status update event"""
        return self.create_event("status", {
            "status": status,
            "message": message
        })
    
    def content_event(self, content: str, is_partial: bool = True) -> str:
        """Create a content chunk event"""
        return self.create_event("content", {
            "content": content,
            "is_partial": is_partial
        })
    
    def tool_call_event(self, tool_name: str, args: Dict, status: str = "started") -> str:
        """Create a tool call event"""
        return self.create_event("tool_call", {
            "tool_name": tool_name,
            "arguments": args,
            "status": status
        })
    
    def agent_response_event(self, agent_name: str, content: str) -> str:
        """Create an agent response event for teams"""
        return self.create_event("agent_response", {
            "agent_name": agent_name,
            "content": content
        })
    
    def complete_event(self, final_response: str) -> str:
        """Create a completion event"""
        elapsed = time.time() - self.start_time
        return self.create_event("complete", {
            "final_response": final_response,
            "elapsed_time": elapsed
        })
    
    def error_event(self, error_message: str) -> str:
        """Create an error event"""
        return self.create_event("error", {
            "error": error_message
        })


async def stream_web_agent_response(
    agent, 
    message: str, 
    agent_id: str, 
    user_id: str = "default_user",
    session_id: str = None,
    include_reasoning: bool = True
) -> AsyncGenerator[str, None]:
    """
    Stream agent responses in web-friendly structured JSON format
    """
    try:
        streamer = WebStreamingResponse(agent_id, user_id, session_id)
        logger.info(f"Starting web streaming for agent {agent_id}")
        
        # Send initial status
        yield streamer.status_event("processing", f"Processing your request with {agent_id}")
        
        # Get streaming response from agent
        run_response = await agent.arun(message, stream=True)
        
        # Track state for better parsing
        accumulated_content = ""
        current_tool_calls = {}
        
        async for chunk in run_response:
            try:
                # Handle different chunk types from AGNO
                if hasattr(chunk, 'content') and chunk.content:
                    content = chunk.content.strip()
                    if content:
                        accumulated_content += content
                        yield streamer.content_event(content, is_partial=True)
                
                # Handle tool calls
                if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                    for tool_call in chunk.tool_calls:
                        tool_name = getattr(tool_call, 'name', 'unknown_tool')
                        args = getattr(tool_call, 'arguments', {})
                        yield streamer.tool_call_event(tool_name, args, "executing")
                
                # Handle team member responses
                if hasattr(chunk, 'member_response') and chunk.member_response:
                    member_name = getattr(chunk.member_response, 'agent_name', 'Team Member')
                    member_content = getattr(chunk.member_response, 'content', str(chunk.member_response))
                    yield streamer.agent_response_event(member_name, member_content)
                
                # Handle reasoning steps (if requested and available)
                if include_reasoning and hasattr(chunk, 'reasoning'):
                    yield streamer.create_event("reasoning", {
                        "step": chunk.reasoning
                    })
                
            except Exception as chunk_error:
                logger.error(f"Error processing chunk: {chunk_error}")
                continue
        
        # Send completion event
        yield streamer.complete_event(accumulated_content)
        logger.info(f"Completed web streaming for agent {agent_id}")
        
    except Exception as e:
        logger.error(f"Error in web streaming for agent {agent_id}: {e}")
        streamer = WebStreamingResponse(agent_id, user_id, session_id)
        yield streamer.error_event(str(e))