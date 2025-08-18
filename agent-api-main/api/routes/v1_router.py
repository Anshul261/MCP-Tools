# api/routes/v1_router.py
from fastapi import APIRouter

from api.routes.health import router as health_router
from api.routes.agents import router as agents_router
from api.routes.documents import router as documents_router

# Create v1 router
v1_router = APIRouter(prefix="/v1")

# Include all route modules
v1_router.include_router(health_router)
v1_router.include_router(agents_router)
v1_router.include_router(documents_router)