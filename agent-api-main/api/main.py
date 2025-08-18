# api/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.settings import (
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    CORS_ORIGINS,
    DEBUG_MODE,
    DOCS_ENABLED
)
from api.routes.v1_router import v1_router
from core.database import db_manager
from core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO if not DEBUG_MODE else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting Custom Agent API...")
    
    # Validate configuration
    missing_settings = settings.validate_required_settings()
    if missing_settings:
        logger.warning(f"Missing configuration: {missing_settings}")
    else:
        logger.info("All required settings are configured")
    
    # Initialize knowledge base if documents exist
    try:
        await db_manager.initialize_knowledge_base(recreate=False)
        logger.info("Knowledge base initialization completed")
    except Exception as e:
        logger.warning(f"Knowledge base initialization failed: {e}")
    
    # Health check
    try:
        health = db_manager.health_check()
        logger.info(f"Database health check: {health}")
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    logger.info("Custom Agent API startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Custom Agent API...")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application
    
    Returns:
        FastAPI: Configured FastAPI application
    """
    
    # Create FastAPI app with lifespan
    app = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=API_VERSION,
        debug=DEBUG_MODE,
        docs_url="/docs" if DOCS_ENABLED else None,
        redoc_url="/redoc" if DOCS_ENABLED else None,
        openapi_url="/openapi.json" if DOCS_ENABLED else None,
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(v1_router)
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Custom Agent API",
            "version": API_VERSION,
            "docs": "/docs" if DOCS_ENABLED else None,
            "health": "/v1/health"
        }
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Global exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc) if DEBUG_MODE else "An unexpected error occurred"
            }
        )
    
    return app


# Create the app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=DEBUG_MODE,
        log_level="info" if not DEBUG_MODE else "debug"
    )