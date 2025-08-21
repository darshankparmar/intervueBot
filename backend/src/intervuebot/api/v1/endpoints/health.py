"""
Health check endpoints.

This module provides health check and system status endpoints
for monitoring the IntervueBot API.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from intervuebot.core.redis import get_redis_client
from intervuebot.core.config import settings

router = APIRouter()


@router.get("/health",
    summary="Health Check",
    description="""
    Basic health check endpoint to verify the API is running.
    
    Returns a simple status message indicating the service is operational.
    This endpoint is useful for load balancers and monitoring systems.
    """,
    response_description="Health status with basic service information",
    tags=["Health"],
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "service": "IntervueBot API",
                        "version": "1.0.0",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        }
    })
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns:
        Dict[str, Any]: Health status information
        
    Example Response:
        {
            "status": "healthy",
            "service": "IntervueBot API",
            "version": "1.0.0",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    """
    return {
        "status": "healthy",
        "service": "IntervueBot API",
        "version": "1.0.0",
        "timestamp": "2024-01-15T10:30:00Z"
    }


@router.get("/status",
    summary="Detailed System Status",
    description="""
    Comprehensive system status endpoint that provides detailed information
    about the IntervueBot API, including Redis connectivity, agent status,
    and system configuration.
    
    This endpoint is useful for debugging and monitoring system health.
    """,
    response_description="Detailed system status and configuration information",
    tags=["Health"],
    responses={
        200: {
            "description": "System status information",
            "content": {
                "application/json": {
                    "example": {
                        "status": "operational",
                        "service": "IntervueBot API",
                        "version": "1.0.0",
                        "environment": "development",
                        "redis": {
                            "status": "connected",
                            "url": "redis://localhost:6379"
                        },
                        "agents": {
                            "adaptive_interview_agent": "initialized",
                            "resume_analyzer": "initialized"
                        },
                        "features": [
                            "Resume Analysis",
                            "Adaptive Questioning",
                            "Performance-Based Difficulty",
                            "Comprehensive Evaluation"
                        ],
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        503: {
            "description": "Service is unhealthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "error": "Redis connection failed",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        }
    })
async def system_status() -> Dict[str, Any]:
    """
    Detailed system status endpoint.
    
    Returns:
        Dict[str, Any]: Comprehensive system status information
        
    Raises:
        HTTPException: If system is unhealthy
        
    Example Response:
        {
            "status": "operational",
            "service": "IntervueBot API",
            "version": "1.0.0",
            "environment": "development",
            "redis": {
                "status": "connected",
                "url": "redis://localhost:6379"
            },
            "agents": {
                "adaptive_interview_agent": "initialized",
                "resume_analyzer": "initialized"
            },
            "features": [
                "Resume Analysis",
                "Adaptive Questioning",
                "Performance-Based Difficulty",
                "Comprehensive Evaluation"
            ],
            "timestamp": "2024-01-15T10:30:00Z"
        }
    """
    try:
        # Check Redis connection
        redis_client = get_redis_client()
        if redis_client:
            redis_status = "connected"
            redis_url = settings.REDIS_URL
        else:
            redis_status = "disconnected"
            redis_url = settings.REDIS_URL
        
        status_info = {
            "status": "operational",
            "service": "IntervueBot API",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "redis": {
                "status": redis_status,
                "url": redis_url
            },
            "agents": {
                "adaptive_interview_agent": "initialized",
                "resume_analyzer": "initialized"
            },
            "features": [
                "Resume Analysis",
                "Adaptive Questioning",
                "Performance-Based Difficulty",
                "Comprehensive Evaluation",
                "Smart Follow-ups"
            ],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        return status_info
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2024-01-15T10:30:00Z"
            }
        )


@router.get("/redis",
    summary="Redis Health Check",
    description="""
    Specific Redis health check endpoint to verify Redis connectivity
    and get detailed Redis statistics.
    
    This endpoint tests the Redis connection and returns connection
    status and basic Redis information.
    """,
    response_description="Redis connection status and statistics",
    tags=["Health"],
    responses={
        200: {
            "description": "Redis is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "connected",
                        "url": "redis://localhost:6379",
                        "info": {
                            "redis_version": "7.0.0",
                            "connected_clients": 5,
                            "used_memory_human": "1.2M",
                            "uptime_in_seconds": 3600
                        },
                        "ping": "PONG",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        503: {
            "description": "Redis is unhealthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "disconnected",
                        "error": "Connection refused",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        }
    })
async def redis_health() -> Dict[str, Any]:
    """
    Redis health check endpoint.
    
    Returns:
        Dict[str, Any]: Redis connection status and statistics
        
    Raises:
        HTTPException: If Redis is not accessible
        
    Example Response:
        {
            "status": "connected",
            "url": "redis://localhost:6379",
            "info": {
                "redis_version": "7.0.0",
                "connected_clients": 5,
                "used_memory_human": "1.2M",
                "uptime_in_seconds": 3600
            },
            "ping": "PONG",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    """
    try:
        redis_client = get_redis_client()
        if not redis_client:
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "disconnected",
                    "error": "Redis client not available",
                    "timestamp": "2024-01-15T10:30:00Z"
                }
            )
        
        # Test Redis connection
        ping_result = await redis_client.ping()
        info = await redis_client.info()
        
        redis_health = {
            "status": "connected",
            "url": settings.REDIS_URL,
            "info": {
                "redis_version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0)
            },
            "ping": ping_result,
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        return redis_health
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "disconnected",
                "error": str(e),
                "timestamp": "2024-01-15T10:30:00Z"
            }
        ) 