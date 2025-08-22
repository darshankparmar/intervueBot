"""
API router for version 1 endpoints.

This module centralizes all API routing for version 1 of the API.
"""

from fastapi import APIRouter

from .endpoints import health, interviews, files

# Create the main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["Interviews"])
api_router.include_router(files.router, prefix="/files", tags=["Files"]) 