"""
API router for version 1 endpoints.

This module centralizes all API routing for version 1 of the API.
"""

from fastapi import APIRouter

from intervuebot.api.v1.endpoints import health, interviews, uploads

# Create the main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["Interviews"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["Uploads"]) 