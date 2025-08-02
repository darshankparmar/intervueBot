"""
Main API router for v1 endpoints.

This module combines all API routers into a single router instance.
"""

from fastapi import APIRouter

from intervuebot.api.v1.endpoints import health, interviews

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["Interviews"]) 