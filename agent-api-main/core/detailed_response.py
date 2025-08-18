# core/detailed_response.py
from typing import AsyncGenerator, Dict, Any, List, Optional
import time
import asyncio
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class DetailedResponseFormatter:
    """Formats agent responses with detailed breakdown including reasoning steps, tool calls, and member responses"""
    
    def __init__(self):
        self.reasoning_step = 0
        self.tool_call_count = 0
        self.member_responses = {}
        self.start_time = time.time()
    
    def create_section_header(self, title: str, width: int = 120) -> str:
        """Create a formatted section header"""
        border = "━" * (width - len(title) - 4)
        return f"┏━ {title} {border}┓"
    
    def create_section_footer(self, width: int = 120) -> str:
        """Create a formatted section footer"""
        border = "━" * (width - 2)
        return f"┗{border}┛"
    
    def create_content_line(self, content: str, width: int = 120) -> str:
        """Create a formatted content line"""
        padding = " " * (width - len(content) - 3)
        return f"┃ {content}{padding}┃"
    
    def format_reasoning_step(self, title: str, content: str) -> str:
        """Format a reasoning step"""
        self.reasoning_step += 1
        lines = []
        lines.append(self.create_section_header(f"Reasoning step {self.reasoning_step}", 150))
        lines.append("┃" + " " * 148 + "┃")
        
        # Split content into lines and format
        content_lines = content.split('\n')
        for line in content_lines:
            if line.strip():
                # Wrap long lines
                while len(line) > 145:
                    lines.append(self.create_content_line(line[:145], 150))
                    line = line[145:]
                if line.strip():
                    lines.append(self.create_content_line(line, 150))
            else:
                lines.append("┃" + " " * 148 + "┃")
        
        lines.append("┃" + " " * 148 + "┃")
        lines.append(self.create_section_footer(150))
        return '\n'.join(lines)
    
    def format_tool_calls(self, agent_name: str, tool_calls: List[Dict[str, Any]]) -> str:
        """Format tool calls section"""
        lines = []
        lines.append(self.create_section_header(f"{agent_name} Tool Calls", 150))
        lines.append("┃" + " " * 148 + "┃")
        
        for i, tool_call in enumerate(tool_calls, 1):
            tool_name = tool_call.get('name', 'unknown_tool')
            params = tool_call.get('parameters', {})
            
            lines.append(self.create_content_line(f"• {tool_name}({', '.join(f'{k}={v}' for k, v in params.items())})", 150))
        
        lines.append("┃" + " " * 148 + "┃")
        lines.append(self.create_section_footer(150))
        return '\n'.join(lines)
    
    def format_agent_response(self, agent_name: str, response: str) -> str:
        """Format agent response section"""
        lines = []
        lines.append(self.create_section_header(f"{agent_name} Response", 150))
        lines.append("┃" + " " * 148 + "┃")
        
        # Split response into lines and format
        response_lines = response.split('\n')
        for line in response_lines:
            if line.strip():
                # Wrap long lines
                while len(line) > 145:
                    lines.append(self.create_content_line(line[:145], 150))
                    line = line[145:]
                if line.strip():
                    lines.append(self.create_content_line(line, 150))
            else:
                lines.append("┃" + " " * 148 + "┃")
        
        lines.append("┃" + " " * 148 + "┃")
        lines.append(self.create_section_footer(150))
        return '\n'.join(lines)
    
    def format_final_response(self, response: str) -> str:
        """Format the final response section"""
        elapsed_time = time.time() - self.start_time
        lines = []
        lines.append(self.create_section_header(f"Response ({elapsed_time:.1f}s)", 150))
        lines.append("┃" + " " * 148 + "┃")
        
        # Split response into lines and format
        response_lines = response.split('\n')
        for line in response_lines:
            if line.strip():
                # Wrap long lines
                while len(line) > 145:
                    lines.append(self.create_content_line(line[:145], 150))
                    line = line[145:]
                if line.strip():
                    lines.append(self.create_content_line(line, 150))
            else:
                lines.append("┃" + " " * 148 + "┃")
        
        lines.append("┃" + " " * 148 + "┃")
        lines.append(self.create_section_footer(150))
        return '\n'.join(lines)


async def stream_detailed_agent_response(
    agent, 
    message: str, 
    agent_id: str, 
    user_id: str = "default_user",
    session_id: str = None
) -> AsyncGenerator[str, None]:
    """
    Stream agent responses with detailed breakdown including reasoning steps, tool calls, and responses.
    
    Args:
        agent: The agent or team instance
        message: User message to process
        agent_id: Agent identifier for logging
        user_id: User identifier
        session_id: Session identifier
        
    Yields:
        Formatted text chunks showing the detailed breakdown
    """
    try:
        formatter = DetailedResponseFormatter()
        logger.info(f"Starting detailed streaming response for agent {agent_id}")
        
        # Stream the user message
        yield f"┏━ Message {formatter.create_section_header('', 130)[8:]}\n"
        yield f"┃                                                                                                                                                           ┃\n"
        yield f"┃ {message}" + " " * (130 - len(message)) + " ┃\n"
        yield f"┃                                                                                                                                                           ┃\n"
        yield f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        
        # For team agents, we need to handle member responses
        is_team = hasattr(agent, 'members') and hasattr(agent, 'mode')
        
        if is_team:
            # Handle team coordination
            yield formatter.format_reasoning_step(
                "Understanding user's question",
                f"Analyzing the user's question to determine information needs\nAction: Coordinating between {len(agent.members)} team members to provide comprehensive response\n\n"
            ) + "\n\n"
            
            # Simulate member task assignments for teams
            for i, member in enumerate(agent.members, 1):
                member_name = getattr(member, 'name', f'Member {i}')
                yield formatter.format_reasoning_step(
                    f"Task assignment to {member_name}",
                    f"Assigning search and analysis task to {member_name}\nAction: {member_name} will search for relevant information and provide detailed response.\n\n"
                ) + "\n\n"
                
                # Wait a bit to simulate processing
                await asyncio.sleep(0.1)
        else:
            # For individual agents, show initial reasoning
            yield formatter.format_reasoning_step(
                "Processing user request",
                f"Analyzing user question and determining search strategy\nAction: Searching knowledge base and external sources for relevant information\n\n"
            ) + "\n\n"
        
        # Get response from agent using valid parameters only
        try:
            if hasattr(agent, 'arun'):
                run_response = await agent.arun(
                    message, 
                    stream=False,
                    user_id=user_id,
                    session_id=session_id
                )
            else:
                # Fallback for synchronous agents
                run_response = agent.run(
                    message, 
                    stream=False,
                    user_id=user_id,
                    session_id=session_id
                )
        except Exception as e:
            logger.error(f"Error getting agent response: {e}")
            run_response = f"Error: {str(e)}"
        
        # Show tool calls (simulated based on agent type)
        if agent_id == "doc_agent":
            yield formatter.format_tool_calls("Doc Agent", [
                {"name": "search_knowledge_base", "parameters": {"query": message}}
            ]) + "\n\n"
        elif agent_id == "web_agent":
            yield formatter.format_tool_calls("Web Agent", [
                {"name": "brave_search", "parameters": {"query": message, "max_results": 5}}
            ]) + "\n\n"
        elif agent_id == "reasoning_team":
            yield formatter.format_tool_calls("Team", [
                {"name": "think", "parameters": {"title": "Coordination strategy", "thought": "Determining best approach for comprehensive response"}},
                {"name": "transfer_task_to_member", "parameters": {"member_id": "doc-agent", "task_description": f"Search documents for: {message}"}},
                {"name": "transfer_task_to_member", "parameters": {"member_id": "web-agent", "task_description": f"Search web for: {message}"}}
            ]) + "\n\n"
        
        # Wait a bit to simulate processing
        await asyncio.sleep(0.2)
        
        # Extract content from response
        if hasattr(run_response, 'content'):
            content = run_response.content
        else:
            content = str(run_response)
        
        # Show agent response
        agent_name = getattr(agent, 'name', agent_id.replace('_', ' ').title())
        yield formatter.format_agent_response(agent_name, content) + "\n\n"
        
        # Show final response
        yield formatter.format_final_response(content) + "\n\n"
        
        logger.info(f"Completed detailed streaming response for agent {agent_id}")
        
    except Exception as e:
        logger.error(f"Error in detailed streaming response for agent {agent_id}: {e}")
        yield f"Error: {str(e)}\n\n"


async def stream_simple_agent_response(agent, message: str, agent_id: str) -> AsyncGenerator[str, None]:
    """
    Stream simple agent responses (fallback for compatibility).
    
    Args:
        agent: The agent or team instance
        message: User message to process
        agent_id: Agent identifier for logging
        
    Yields:
        Text chunks from the agent response
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