"""
AGNO Multi-Agent API Server

FastAPI application providing REST API endpoints for the AGNO multi-agent system
with comprehensive streaming support for chat, document processing, and system monitoring.
"""

import os
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import API routers
from .api.v1.chat import router as chat_router
from .api.v1.documents import router as documents_router
from .api.v1.system import router as system_router

# Import core components
from .core.agents import agent_system
from .core.database import db_manager
from .core.streaming import streaming_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Application startup/shutdown lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting AGNO Multi-Agent API Server...")
    
    try:
        # Initialize core systems
        logger.info("Initializing core systems...")
        
        # Agent system should already be initialized
        if hasattr(agent_system, 'initialized') and agent_system.initialized:
            logger.info(" Agent system initialized successfully")
        else:
            logger.warning("  Agent system not fully initialized")
        
        # Database manager should be initialized
        logger.info(" Database systems initialized")
        
        # Streaming manager is ready
        logger.info(" Streaming system initialized")
        
        # Log system status
        logger.info(f"=€ AGNO Multi-Agent API Server started successfully")
        logger.info(f"=á Streaming support: Enabled (SSE)")
        logger.info(f"> Agent system: {'Initialized' if agent_system.initialized else 'Mock mode'}")
        
        app.state.startup_time = time.time()
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    # Shutdown
    logger.info("Shutting down AGNO Multi-Agent API Server...")
    
    # Close any active streams
    try:
        active_streams = len(streaming_manager.active_streams)
        if active_streams > 0:
            logger.info(f"Closing {active_streams} active streams...")
            for stream_id in list(streaming_manager.active_streams.keys()):
                streaming_manager.close_stream(stream_id)
    except Exception as e:
        logger.warning(f"Error closing streams: {e}")
    
    logger.info(" Server shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="AGNO Multi-Agent API",
    description="""
    REST API for AGNO multi-agent system with comprehensive streaming support.
    
    ## Features
    
    * **Multi-Agent Chat**: Coordinate between document and web search agents
    * **Streaming Responses**: Real-time Server-Sent Events (SSE) streaming
    * **Document Processing**: Upload, process, and index documents
    * **Knowledge Base**: Search through processed documents
    * **Session Management**: Persistent conversation sessions with memory
    * **System Monitoring**: Health checks, metrics, and status endpoints
    
    ## Streaming Support
    
    All chat endpoints support Server-Sent Events (SSE) for real-time streaming:
    * Content streaming for immediate response display
    * Status updates during processing
    * Tool call notifications
    * Error handling with graceful fallbacks
    
    ## Authentication
    
    Currently operates without authentication. User identification is handled
    via `user_id` parameters in requests.
    
    ## Rate Limiting
    
    No rate limiting currently implemented. Consider implementing rate limiting
    for production deployments.
    """,
    version="1.0.0",
    contact={
        "name": "AGNO Multi-Agent System",
        "url": "https://github.com/your-org/agno-multi-agent-api",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing information"""
    start_time = time.time()
    
    # Log request
    logger.info(f"=è {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"=ä {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"L {request.method} {request.url.path} - ERROR ({process_time:.3f}s): {str(e)}")
        raise

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception in {request.method} {request.url.path}: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again.",
            "timestamp": time.time(),
            "request_id": getattr(request.state, 'request_id', None)
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": time.time() - getattr(app.state, 'startup_time', time.time()),
        "version": "1.0.0"
    }

# Root endpoint with API information
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "AGNO Multi-Agent API",
        "version": "1.0.0",
        "description": "REST API for AGNO multi-agent system with streaming support",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "api": {
                "chat": "/api/v1/chat",
                "documents": "/api/v1/documents", 
                "system": "/api/v1/system"
            }
        },
        "features": [
            "streaming_responses",
            "multi_agent_coordination",
            "document_processing",
            "knowledge_base_search",
            "session_management",
            "memory_persistence"
        ],
        "timestamp": time.time()
    }

# Include API routers
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(system_router)

# Development server configuration
if __name__ == "__main__":
    # Configuration for development
    config = {
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", 8000)),
        "reload": os.getenv("ENVIRONMENT", "development") == "development",
        "log_level": os.getenv("LOG_LEVEL", "info").lower(),
        "workers": 1,  # Use 1 worker for development
    }
    
    print(f"""
=€ Starting AGNO Multi-Agent API Server
=á Server: http://{config['host']}:{config['port']}
=Ö Docs: http://{config['host']}:{config['port']}/docs
=' Environment: {os.getenv("ENVIRONMENT", "development")}
""")
    
    uvicorn.run("app.main:app", **config)