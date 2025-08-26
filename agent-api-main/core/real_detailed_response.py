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
    Stream agent responses with REAL trace logs and reasoning steps from Agno framework.
    
    This captures the actual agent execution details like in multi-agent-system.py
    """
    try:
        logger.info(f"Starting real detailed streaming for agent {agent_id}")
        
        # Get streaming response with full reasoning and intermediate steps enabled
        if hasattr(agent, 'arun'):
            run_response = await agent.arun(
                message, 
                stream=True,
                user_id=user_id,
                session_id=session_id,
                show_full_reasoning=True,
                stream_intermediate_steps=True
            )
        else:
            # Fallback for synchronous agents
            run_response = agent.run(
                message, 
                stream=True,
                user_id=user_id,
                session_id=session_id,
                show_full_reasoning=True,
                stream_intermediate_steps=True
            )
        
        # Stream each chunk as it comes from the agent
        chunk_count = 0
        if hasattr(run_response, '__aiter__'):
            async for chunk in run_response:
                chunk_count += 1
                
                # Stream the chunk content directly (this includes reasoning, tool calls, etc.)
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content
                elif chunk:
                    yield str(chunk)
                    
                # Small delay to make streaming visible
                await asyncio.sleep(0.01)
                
        else:
            # Handle non-streaming response
            if hasattr(run_response, 'content'):
                yield run_response.content
            else:
                yield str(run_response)
        
        logger.info(f"Completed real detailed streaming for agent {agent_id}, {chunk_count} chunks sent")
        
    except Exception as e:
        logger.error(f"Error in real detailed streaming for agent {agent_id}: {e}")
        yield f"Error: {str(e)}\n\n"


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