"""
Main FastAPI application for IntervueBot.

This module initializes the FastAPI application with all necessary middleware,
routers, and configuration.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from intervuebot.api.v1.router import api_router
from intervuebot.core.config import settings
from intervuebot.core.events import create_start_app_handler, create_stop_app_handler


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        contact={
            "name": "IntervueBot Team",
            "email": "support@intervuebot.com",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        servers=[
            {"url": "http://localhost:8000", "description": "Development server"},
            {"url": "https://api.intervuebot.com", "description": "Production server"},
        ],
    )

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )

    # Add event handlers
    app.add_event_handler("startup", create_start_app_handler(app))
    app.add_event_handler("shutdown", create_stop_app_handler(app))

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """
        Welcome endpoint for IntervueBot API.
        
        Returns:
            JSONResponse: Welcome message and API information
        """
        return JSONResponse(
            content={
                "message": "Welcome to IntervueBot API! 🤖",
                "description": "AI Interview Taker Agent using Agno Framework",
                "version": settings.VERSION,
                "docs": {
                    "swagger_ui": "/docs",
                    "redoc": "/redoc",
                    "openapi_json": f"{settings.API_V1_STR}/openapi.json"
                },
                "endpoints": {
                    "health": f"{settings.API_V1_STR}/health/",
                    "interviews": f"{settings.API_V1_STR}/interviews/"
                },
                "status": "running"
            },
            status_code=200
        )

    # Include routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
    ) 