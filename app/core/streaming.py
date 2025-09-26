import json
import asyncio
import uuid
from typing import AsyncGenerator, Dict, Any, Optional, List, Union
from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..models.requests import StreamEvent, StreamEventType
from ..models.responses import WebStreamingResponse

class StreamingManager:
    """Manages streaming connections and events"""
    
    def __init__(self):
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.stream_history: Dict[str, List[StreamEvent]] = {}
    
    def create_stream(self, user_id: str, session_id: str, stream_type: str = "chat") -> str:
        """Create a new stream and return stream ID"""
        stream_id = f"{stream_type}_{uuid.uuid4().hex[:8]}"
        self.active_streams[stream_id] = {
            "user_id": user_id,
            "session_id": session_id,
            "stream_type": stream_type,
            "created_at": datetime.utcnow(),
            "events_sent": 0,
            "status": "active"
        }
        self.stream_history[stream_id] = []
        return stream_id
    
    def get_stream_info(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get stream information"""
        return self.active_streams.get(stream_id)
    
    def close_stream(self, stream_id: str):
        """Close a stream"""
        if stream_id in self.active_streams:
            self.active_streams[stream_id]["status"] = "closed"
            self.active_streams[stream_id]["closed_at"] = datetime.utcnow()
    
    def add_event(self, stream_id: str, event: StreamEvent):
        """Add an event to stream history"""
        if stream_id in self.stream_history:
            self.stream_history[stream_id].append(event)
            if stream_id in self.active_streams:
                self.active_streams[stream_id]["events_sent"] += 1

class SSEFormatter:
    """Formats events for Server-Sent Events"""
    
    @staticmethod
    def format_event(event_type: str, data: Union[str, Dict[str, Any]], event_id: Optional[str] = None) -> str:
        """Format data as SSE event"""
        lines = []
        
        if event_id:
            lines.append(f"id: {event_id}")
        
        lines.append(f"event: {event_type}")
        
        # Convert data to JSON if it's not a string
        if isinstance(data, dict):
            data_str = json.dumps(data, ensure_ascii=False, default=str)
        else:
            data_str = str(data)
        
        # Split multi-line data
        for line in data_str.split('\n'):
            lines.append(f"data: {line}")
        
        lines.append("")  # Empty line to end event
        return "\n".join(lines)
    
    @staticmethod
    def format_stream_event(event: StreamEvent, stream_id: str) -> str:
        """Format StreamEvent for SSE"""
        web_event = WebStreamingResponse(
            event=event.event_type.value,
            data=event.data,
            timestamp=event.timestamp.isoformat(),
            stream_id=stream_id,
            sequence=event.sequence
        )
        
        return SSEFormatter.format_event(
            event_type=event.event_type.value,
            data=web_event.dict(),
            event_id=f"{stream_id}_{event.sequence or 0}"
        )

class WebStreamingResponseHandler:
    """Handles streaming responses optimized for web interfaces"""
    
    def __init__(self, stream_manager: StreamingManager):
        self.stream_manager = stream_manager
        self.event_sequence = 0
    
    async def create_chat_stream(
        self, 
        user_id: str, 
        session_id: str, 
        message: str,
        agent_system,
        show_reasoning: bool = False,
        stream_intermediate_steps: bool = False
    ) -> AsyncGenerator[str, None]:
        """Create a streaming response for chat"""
        stream_id = self.stream_manager.create_stream(user_id, session_id, "chat")
        
        try:
            # Send initial status event
            yield self._create_sse_event(
                StreamEventType.STATUS,
                {"status": "started", "message": "Initializing chat response"},
                stream_id
            )
            
            # Send message processing event
            yield self._create_sse_event(
                StreamEventType.STATUS,
                {"status": "processing", "message": "Processing your message"},
                stream_id
            )
            
            # Stream the agent response
            async for event in self._stream_agent_response(
                agent_system, message, user_id, session_id, 
                show_reasoning, stream_intermediate_steps, stream_id
            ):
                yield event
            
            # Send completion event
            yield self._create_sse_event(
                StreamEventType.COMPLETE,
                {"status": "completed", "message": "Response completed"},
                stream_id
            )
            
        except Exception as e:
            # Send error event
            yield self._create_sse_event(
                StreamEventType.ERROR,
                {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "message": "An error occurred during processing"
                },
                stream_id
            )
        finally:
            self.stream_manager.close_stream(stream_id)
    
    async def _stream_agent_response(
        self,
        agent_system,
        message: str,
        user_id: str,
        session_id: str,
        show_reasoning: bool,
        stream_intermediate_steps: bool,
        stream_id: str
    ) -> AsyncGenerator[str, None]:
        """Stream agent response with proper event handling"""
        
        # This is a placeholder for the actual agent streaming implementation
        # In the real implementation, we would integrate with the AGNO team streaming
        
        try:
            # For demonstration, we'll simulate streaming events
            # In actual implementation, this would integrate with the agent system
            
            if show_reasoning:
                yield self._create_sse_event(
                    StreamEventType.AGENT_THINKING,
                    {
                        "agent": "team",
                        "step": "analyzing_request",
                        "message": "Analyzing your request and determining best approach"
                    },
                    stream_id
                )
            
            # Simulate tool calls
            if stream_intermediate_steps:
                yield self._create_sse_event(
                    StreamEventType.TOOL_CALL,
                    {
                        "tool": "search",
                        "status": "starting",
                        "message": "Searching for relevant information"
                    },
                    stream_id
                )
            
            # Stream content chunks
            response_chunks = [
                "I understand your question about ",
                message[:50] + "...",
                "\n\nLet me provide you with a comprehensive response.",
                "\n\nBased on the available information, here's what I found:\n\n",
                "• Key point 1: Important information\n",
                "• Key point 2: Additional context\n",
                "• Key point 3: Relevant details\n\n",
                "Would you like me to elaborate on any of these points?"
            ]
            
            for i, chunk in enumerate(response_chunks):
                await asyncio.sleep(0.1)  # Simulate streaming delay
                yield self._create_sse_event(
                    StreamEventType.CONTENT,
                    {"content": chunk, "chunk_index": i},
                    stream_id
                )
            
            if stream_intermediate_steps:
                yield self._create_sse_event(
                    StreamEventType.TOOL_RESULT,
                    {
                        "tool": "search",
                        "status": "completed",
                        "results_count": 5,
                        "message": "Search completed successfully"
                    },
                    stream_id
                )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Agent streaming error: {str(e)}")
    
    def _create_sse_event(
        self, 
        event_type: StreamEventType, 
        data: Dict[str, Any], 
        stream_id: str
    ) -> str:
        """Create a formatted SSE event"""
        self.event_sequence += 1
        
        event = StreamEvent(
            event_type=event_type,
            data=data,
            sequence=self.event_sequence,
            timestamp=datetime.utcnow()
        )
        
        self.stream_manager.add_event(stream_id, event)
        return SSEFormatter.format_stream_event(event, stream_id)

class DocumentProcessingStreamer:
    """Handles streaming for document processing operations"""
    
    def __init__(self, stream_manager: StreamingManager):
        self.stream_manager = stream_manager
        self.event_sequence = 0
    
    async def stream_document_processing(
        self,
        document_id: str,
        user_id: str,
        processing_func,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream document processing events"""
        stream_id = self.stream_manager.create_stream(user_id, document_id, "document_processing")
        
        try:
            # Send start event
            yield self._create_sse_event(
                StreamEventType.STATUS,
                {"status": "started", "document_id": document_id, "stage": "initializing"},
                stream_id
            )
            
            # Stream processing steps
            async for event in self._stream_processing_steps(processing_func, document_id, **kwargs):
                yield event
            
            # Send completion event
            yield self._create_sse_event(
                StreamEventType.COMPLETE,
                {"status": "completed", "document_id": document_id},
                stream_id
            )
            
        except Exception as e:
            yield self._create_sse_event(
                StreamEventType.ERROR,
                {"error": str(e), "document_id": document_id},
                stream_id
            )
        finally:
            self.stream_manager.close_stream(stream_id)
    
    async def _stream_processing_steps(self, processing_func, document_id: str, **kwargs):
        """Stream individual processing steps"""
        # This would be implemented based on the actual document processing pipeline
        stages = [
            {"stage": "uploading", "message": "Uploading document"},
            {"stage": "converting", "message": "Converting document to text"},
            {"stage": "indexing", "message": "Adding to knowledge base"},
            {"stage": "completed", "message": "Document processing completed"}
        ]
        
        for stage in stages:
            await asyncio.sleep(0.5)  # Simulate processing time
            yield self._create_sse_event(
                StreamEventType.STATUS,
                {"document_id": document_id, **stage},
                f"doc_processing_{document_id}"
            )
    
    def _create_sse_event(self, event_type: StreamEventType, data: Dict[str, Any], stream_id: str) -> str:
        """Create SSE event for document processing"""
        self.event_sequence += 1
        
        event = StreamEvent(
            event_type=event_type,
            data=data,
            sequence=self.event_sequence,
            timestamp=datetime.utcnow()
        )
        
        return SSEFormatter.format_stream_event(event, stream_id)

# Create global streaming manager instance
streaming_manager = StreamingManager()

# Utility functions for creating streaming responses
def create_sse_response(generator: AsyncGenerator[str, None]) -> StreamingResponse:
    """Create a StreamingResponse for SSE"""
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

async def create_simple_sse_stream(message: str) -> AsyncGenerator[str, None]:
    """Create a simple SSE stream for testing"""
    formatter = SSEFormatter()
    
    # Send start event
    yield formatter.format_event("start", {"message": "Stream started"})
    
    # Send message
    yield formatter.format_event("message", {"content": message})
    
    # Send end event
    yield formatter.format_event("end", {"message": "Stream completed"})

# Integration with existing agent system placeholder
class AgentStreamingIntegrator:
    """Integrates streaming with the existing AGNO agent system"""
    
    def __init__(self, agent_system):
        self.agent_system = agent_system
        self.streaming_manager = streaming_manager
    
    async def stream_agent_response(
        self,
        message: str,
        user_id: str,
        session_id: str,
        agent_type: str = "team",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response from the AGNO agent system"""
        # This would integrate with the actual AGNO streaming implementation
        # For now, we'll use the WebStreamingResponseHandler
        handler = WebStreamingResponseHandler(self.streaming_manager)
        
        async for event in handler.create_chat_stream(
            user_id, session_id, message, self.agent_system, **kwargs
        ):
            yield event