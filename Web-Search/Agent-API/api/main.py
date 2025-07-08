"""
FastAPI main application for Agent API
"""
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from db import get_db, init_db, close_db
from agents import create_enhanced_agent, EnhancedSearchAgent
from agents.search_tools import SEARCH_TOOLS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class ChatRequest(BaseModel):
    message: str
    user_id: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    user_id: str
    timestamp: str
    metrics: Optional[Dict[str, Any]] = None

class SessionRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    created_at: str
    is_active: bool
    config: Dict[str, Any]

class SearchRequest(BaseModel):
    query: str
    tool: str = "web_search"
    parameters: Dict[str, Any] = {}

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    tool: str
    metadata: Dict[str, Any]

class MetricsResponse(BaseModel):
    user_id: str
    session_id: str
    metrics: Dict[str, Any]
    timestamp: str

# In-memory agent storage (for production, consider Redis or similar)
agent_instances: Dict[str, EnhancedSearchAgent] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting Agent API server...")
    await init_db()
    logger.info("✅ Database initialized")
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down Agent API server...")
    
    # Cleanup agent instances
    for agent_key, agent in agent_instances.items():
        try:
            await agent.cleanup()
        except Exception as e:
            logger.warning(f"Error cleaning up agent {agent_key}: {e}")
    
    agent_instances.clear()
    await close_db()
    logger.info("✅ Server shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Agent API",
    description="Production-ready Agent API with search capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to get or create agent
async def get_agent(
    user_id: str,
    session_id: Optional[str],
    db: AsyncSession
) -> EnhancedSearchAgent:
    """Get or create an agent instance"""
    
    agent_key = f"{user_id}:{session_id}" if session_id else f"{user_id}:new"
    
    if agent_key not in agent_instances:
        logger.info(f"Creating new agent for {agent_key}")
        agent = await create_enhanced_agent(db, user_id, session_id)
        agent_instances[agent_key] = agent
    else:
        logger.info(f"Using existing agent for {agent_key}")
    
    return agent_instances[agent_key]

# API Routes

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agent API v1.0.0",
        "status": "running",
        "available_tools": list(SEARCH_TOOLS.keys()),
        "endpoints": {
            "chat": "/chat",
            "search": "/search",
            "sessions": "/sessions",
            "metrics": "/metrics",
            "health": "/health",
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2025-01-08T00:00:00Z"}

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """
    Chat with the agent
    """
    try:
        # Get or create agent
        agent = await get_agent(request.user_id, request.session_id, db)
        
        # Process the query
        result = await agent.process_query(request.message)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return ChatResponse(
            response=result["response"],
            session_id=result["session_id"],
            user_id=result["user_id"],
            timestamp=result["timestamp"],
            metrics=result.get("metrics")
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Direct search endpoint using available tools
    """
    try:
        if request.tool not in SEARCH_TOOLS:
            raise HTTPException(
                status_code=400,
                detail=f"Tool {request.tool} not available. Available tools: {list(SEARCH_TOOLS.keys())}"
            )
        
        # Execute search
        search_function = SEARCH_TOOLS[request.tool]
        
        if request.tool == "web_search":
            results = await search_function(request.query, **request.parameters)
        elif request.tool == "news_search":
            results = await search_function(request.query, **request.parameters)
        elif request.tool == "smart_search":
            results = await search_function(request.query, **request.parameters)
        elif request.tool == "research_search":
            results = await search_function(request.query, **request.parameters)
        else:
            results = await search_function(request.query)
        
        # Format response
        if isinstance(results, dict) and "results" in results:
            # For smart_search and research_search
            return SearchResponse(
                results=results["results"],
                query=request.query,
                tool=request.tool,
                metadata=results.get("search_metadata", {})
            )
        else:
            # For web_search and news_search
            return SearchResponse(
                results=results,
                query=request.query,
                tool=request.tool,
                metadata={"result_count": len(results)}
            )
            
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: SessionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create or load a session
    """
    try:
        # Create agent (this will handle session creation)
        agent = await get_agent(request.user_id, request.session_id, db)
        
        # Get session info from database
        from db.models import AgentSession
        from sqlalchemy import select
        
        result = await db.execute(
            select(AgentSession).where(
                AgentSession.session_id == agent.session_id,
                AgentSession.user_id == request.user_id
            )
        )
        session = result.scalar_one()
        
        return SessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            created_at=session.created_at.isoformat(),
            is_active=session.is_active,
            config=session.config or {}
        )
        
    except Exception as e:
        logger.error(f"Session creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{user_id}")
async def get_user_sessions(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all sessions for a user
    """
    try:
        from db.models import AgentSession
        from sqlalchemy import select, desc
        
        result = await db.execute(
            select(AgentSession)
            .where(AgentSession.user_id == user_id)
            .order_by(desc(AgentSession.created_at))
        )
        sessions = result.scalars().all()
        
        return [
            {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "agent_name": session.agent_name,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "is_active": session.is_active,
                "config": session.config or {}
            }
            for session in sessions
        ]
        
    except Exception as e:
        logger.error(f"Get sessions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{user_id}/{session_id}/history")
async def get_session_history(
    user_id: str,
    session_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    Get conversation history for a session
    """
    try:
        # Get agent
        agent = await get_agent(user_id, session_id, db)
        
        # Get history
        history = await agent.get_session_history(limit)
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "messages": history,
            "total_messages": len(history)
        }
        
    except Exception as e:
        logger.error(f"Get history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/{user_id}")
async def get_user_metrics(
    user_id: str,
    session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get metrics for a user/session
    """
    try:
        # Get agent
        agent = await get_agent(user_id, session_id, db)
        
        # Get metrics
        metrics = await agent.get_agent_metrics()
        
        return MetricsResponse(
            user_id=user_id,
            session_id=session_id or agent.session_id,
            metrics=metrics,
            timestamp="2025-01-08T00:00:00Z"
        )
        
    except Exception as e:
        logger.error(f"Get metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
async def get_available_tools():
    """
    Get available search tools
    """
    return {
        "tools": list(SEARCH_TOOLS.keys()),
        "descriptions": {
            "web_search": "General web search using Brave Search API",
            "news_search": "Recent news articles and developments",
            "smart_search": "Multi-strategy intelligent search with persistence",
            "research_search": "Comprehensive academic and authoritative research"
        }
    }

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )