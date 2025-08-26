# core/real_detailed_response.py
from typing import AsyncGenerator
import asyncio
import logging

logger = logging.getLogger(__name__)


async def stream_real_detailed_agent_response(
    agent, 
    message: str, 
    agent_id: str, 
    user_id: str = "default_user",
    session_id: str = None
) -> AsyncGenerator[str, None]:
    """
    Stream agent responses following official Agno agent-api standards.
    
    Simple implementation that yields chunk.content directly as per official standards.
    """
    try:
        logger.info(f"Starting streaming for agent {agent_id}")
        
        # Get streaming response - use standard Agno arun with stream=True
        run_response = await agent.arun(message, stream=True)
        
        # Stream each chunk as it comes from the agent (following official standard)
        async for chunk in run_response:
            # chunk.content only contains the text response from the Agent.
            # For advanced use cases, we should yield the entire chunk
            # that contains the tool calls and intermediate steps.
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content
        
        logger.info(f"Completed streaming for agent {agent_id}")
        
    except Exception as e:
        logger.error(f"Error in streaming for agent {agent_id}: {e}")
        yield f"Error: {str(e)}"


async def stream_simple_agent_response_real(agent, message: str, agent_id: str) -> AsyncGenerator[str, None]:
    """
    Stream simple agent responses (original behavior) with word boundary fixes.
    """
    try:
        logger.info(f"Starting simple streaming response for agent {agent_id}")
        
        # Get response from agent
        if hasattr(agent, 'arun'):
            run_response = await agent.arun(message, stream=True)
        else:
            # Fallback for synchronous agents
            run_response = agent.run(message, stream=True)
        
        # Stream the response
        chunk_count = 0
        if hasattr(run_response, '__aiter__'):
            async for chunk in run_response:
                if hasattr(chunk, 'content') and chunk.content:
                    chunk_count += 1
                    yield chunk.content
                
        else:
            # Handle non-streaming response
            if hasattr(run_response, 'content'):
                yield run_response.content
            else:
                yield str(run_response)
        
        logger.info(f"Completed simple streaming response for agent {agent_id}, {chunk_count} chunks sent")
        
    except Exception as e:
        logger.error(f"Error in simple streaming response for agent {agent_id}: {e}")
        yield f"Error: {str(e)}"