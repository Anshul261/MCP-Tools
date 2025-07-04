#!/usr/bin/env python3
"""
Simple example of integrating Brave Search MCP Server with Agno AI Agent (Azure OpenAI)

This is a minimal working example that demonstrates the core integration.
"""

import asyncio
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.azure.openai_chat import AzureOpenAI
from agno.tools.mcp import MCPTools

load_dotenv()

async def main():
    """Main function to run the Brave Search Agent"""
    
    print("🚀 Starting Brave Search Agent with Azure OpenAI...")
    
    azure_model = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    )

    mcp_command = f"python {os.path.abspath('server.py')}"
    
    async with MCPTools(command=mcp_command) as mcp_tools:
        
        agent = Agent(
            model=azure_model,
            tools=[mcp_tools],
            instructions="""
            You are a helpful research assistant with access to Brave Search.
            
            Available tools:
            - web_search: General web search
            - news_search: Search for news articles  
            - smart_search: Intelligent search with multiple strategies
            - research_search: Comprehensive research
            
            Choose the appropriate tool based on the user's query and provide helpful, well-organized responses.
            """,
            markdown=True,
            show_tool_calls=True
        )
        
        query = "What are the latest breakthroughs in quantum computing?"
        
        print(f"🔍 Query: {query}")
        print("=" * 60)
        
        await agent.aprint_response(query, stream=True)

if __name__ == "__main__":
    asyncio.run(main())