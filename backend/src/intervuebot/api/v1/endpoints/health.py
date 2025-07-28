"""
Health check endpoints.

This module provides health check and status endpoints for monitoring
the application's health and status.
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter

from intervuebot.core.config import settings
from intervuebot.core.redis import get_interview_stats, get_redis_client

router = APIRouter()


@router.get("/", 
    summary="Basic Health Check",
    description="Simple health check endpoint to verify the API is running",
    response_description="Health status with timestamp",
    tags=["Health"])
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint.
    
    This endpoint provides a simple way to verify that the IntervueBot API
    is running and responding to requests.
    
    Returns:
        Dict[str, str]: Health status with timestamp
        
    Example Response:
        {
            "status": "healthy",
            "timestamp": "2024-01-01T12:00:00.000000"
        }
    """
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@router.get("/status",
    summary="Detailed Application Status",
    description="Get detailed information about the application status, version, and configuration",
    response_description="Detailed application status information",
    tags=["Health"])
async def status() -> Dict[str, Any]:
    """
    Detailed application status.
    
    This endpoint provides comprehensive information about the IntervueBot
    application including version, project name, and debug status.
    
    Returns:
        Dict[str, Any]: Application status information
        
    Example Response:
        {
            "status": "healthy",
            "timestamp": "2024-01-01T12:00:00.000000",
            "version": "0.1.0",
            "project_name": "IntervueBot",
            "debug": false
        }
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "project_name": settings.PROJECT_NAME,
        "debug": settings.DEBUG,
    }


@router.get("/redis",
    summary="Redis Health Check",
    description="Check Redis connection status and get interview statistics",
    response_description="Redis connection status and statistics",
    tags=["Health"])
async def redis_health() -> Dict[str, Any]:
    """
    Redis health check endpoint.
    
    This endpoint tests the Redis connection and returns statistics
    about interview sessions and cached data.
    
    Returns:
        Dict[str, Any]: Redis status and statistics
        
    Example Response:
        {
            "status": "healthy",
            "redis_connected": true,
            "timestamp": "2024-01-01T12:00:00.000000",
            "statistics": {
                "total_sessions": 10,
                "active_sessions": 2
            }
        }
    """
    try:
        # Test Redis connection
        client = await get_redis_client()
        await client.ping()
        
        # Get interview statistics
        stats = await get_interview_stats()
        
        return {
            "status": "healthy",
            "redis_connected": True,
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": stats,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "redis_connected": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        } 