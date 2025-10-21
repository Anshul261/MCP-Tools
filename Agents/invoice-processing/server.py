"""
FastAPI Server
Entry point for REST API server
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from api.routes import router, initialize_services

# ============================================================================
# Lifespan Context Manager
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.

    Startup:
    - Initialize database and services
    - Create upload directory

    Shutdown:
    - Cleanup (can be extended for graceful shutdown)
    """

    # Startup
    print("[+] Starting Invoice Processing API...")
    await initialize_services()
    print("[+] Services initialized")

    yield

    # Shutdown
    print("[+] Shutting down Invoice Processing API...")


# ============================================================================
# Create FastAPI App
# ============================================================================

app = FastAPI(
    title="Invoice Processing API",
    description="Process invoices with human-in-the-loop review using Agno workflows",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ============================================================================
# Middleware
# ============================================================================

# Add CORS middleware to allow requests from different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


# ============================================================================
# Routes
# ============================================================================

# Include all API routes
app.include_router(router)


# ============================================================================
# Root Endpoint
# ============================================================================


@app.get("/")
async def root():
    """API root endpoint with documentation links"""
    return {
        "name": "Invoice Processing API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health",
        "status": "running",
    }


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 70)
    print("Invoice Processing API")
    print("=" * 70)
    print("\nAPI Documentation: http://localhost:8000/docs")
    print("Alternative Docs: http://localhost:8000/redoc")
    print("\nEndpoints:")
    print("  POST   /api/v1/workflow/start           - Upload and start processing")
    print("  GET    /api/v1/workflow/{session_id}    - Get workflow status")
    print("  GET    /api/v1/workflow/{session_id}/state - Get detailed state")
    print("  POST   /api/v1/workflow/{session_id}/review-response - Submit review")
    print("  GET    /api/v1/invoices                 - Query saved invoices")
    print("  GET    /api/v1/health                   - Health check")
    print("  GET    /api/v1/stats                    - Session statistics")
    print("\n" + "=" * 70 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False,
    )
