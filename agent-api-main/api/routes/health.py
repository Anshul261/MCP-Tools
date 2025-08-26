# api/routes/health.py
from fastapi import APIRouter
from typing import Dict, Any

from core.database import db_manager
from core.config import settings
from core.document_processor import doc_processor

router = APIRouter(tags=["Health"])


@router.get("/health")
async def get_health() -> Dict[str, Any]:
    """
    Comprehensive health check for the API
    
    Returns:
        Dict containing health status of various components
    """
    
    # Basic API health
    health_status = {
        "status": "healthy",
        "api": {
            "name": settings.api.title,
            "version": settings.api.version,
            "debug": settings.api.debug
        }
    }
    
    # Database health check
    try:
        db_health = db_manager.health_check()
        health_status["database"] = db_health
    except Exception as e:
        health_status["database"] = {"status": "error", "error": str(e)}
    
    # Document processor health
    try:
        doc_stats = doc_processor.get_document_stats()
        health_status["documents"] = {
            "status": "healthy",
            "total_documents": doc_stats["total_documents"],
            "converted_documents": doc_stats["converted_documents"],
            "knowledge_base_loaded": doc_stats["knowledge_base_loaded"]
        }
    except Exception as e:
        health_status["documents"] = {"status": "error", "error": str(e)}
    
    # Configuration health
    missing_settings = settings.validate_required_settings()
    if missing_settings:
        health_status["configuration"] = {
            "status": "warning",
            "missing": missing_settings
        }
    else:
        health_status["configuration"] = {"status": "healthy"}
    
    # Determine overall status
    component_statuses = []
    for component, data in health_status.items():
        if component != "status" and component != "api":
            if isinstance(data, dict) and "status" in data:
                component_statuses.append(data["status"])
    
    if "error" in component_statuses:
        health_status["status"] = "unhealthy"
    elif "warning" in component_statuses:
        health_status["status"] = "degraded"
    else:
        health_status["status"] = "healthy"
    
    return health_status


@router.get("/health/quick")
async def get_quick_health() -> Dict[str, str]:
    """
    Quick health check that only returns basic status
    
    Returns:
        Simple status response
    """
    return {"status": "healthy"}


@router.get("/health/database")
async def get_database_health() -> Dict[str, Any]:
    """
    Database-specific health check
    
    Returns:
        Database health status
    """
    try:
        return db_manager.health_check()
    except Exception as e:
        return {"status": "error", "error": str(e)}