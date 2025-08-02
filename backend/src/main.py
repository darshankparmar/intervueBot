"""
Main FastAPI application for IntervueBot.

This module initializes the FastAPI application with all necessary middleware,
routers, and configuration.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

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
        title="IntervueBot API",
        description="""
# IntervueBot - AI Interview Taker Agent 🤖

## Overview
IntervueBot is an intelligent AI-powered interview system that conducts adaptive interviews using the Agno Framework. 
The system analyzes candidate resumes, generates context-aware questions, and provides comprehensive evaluations.

## Key Features
- **Resume Analysis**: AI-powered extraction of skills, experience, and project details
- **Adaptive Questioning**: Dynamic question generation based on responses and background
- **Performance-Based Difficulty**: Automatic adjustment of question difficulty
- **Comprehensive Evaluation**: Multi-dimensional response scoring and feedback
- **Smart Follow-ups**: Context-aware next questions based on previous answers

## Interview Flow
1. **Start Interview**: Upload resume files and provide candidate details
2. **Get Questions**: Receive adaptive questions based on resume analysis
3. **Submit Responses**: Provide answers and receive real-time evaluation
4. **Finalize Interview**: Complete interview and generate comprehensive report
5. **Get Report**: Access detailed evaluation and hiring recommendations

## Experience Levels
- **junior**: 0-2 years experience
- **mid-level**: 2-5 years experience  
- **senior**: 5+ years experience
- **lead**: 7+ years with leadership experience

## Interview Types
- **technical**: Focus on technical skills and problem-solving
- **behavioral**: Focus on past experiences and soft skills
- **mixed**: Combination of technical and behavioral questions
- **leadership**: Focus on leadership and management skills

## File Types
- **resume**: Main resume/CV file
- **cv**: Alternative CV format
- **cover_letter**: Cover letter or motivation letter

## Authentication
Currently, the API does not require authentication for development purposes.

## Rate Limiting
API requests are rate-limited to ensure fair usage.

For more information, visit our [GitHub repository](https://github.com/yourusername/intervuebot).
        """,
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        contact={
            "name": "IntervueBot Team",
            "email": "support@intervuebot.com",
            "url": "https://github.com/yourusername/intervuebot",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        servers=[
            {"url": "http://localhost:8000", "description": "Development server"},
            {"url": "https://api.intervuebot.com", "description": "Production server"},
        ],
        tags_metadata=[
            {
                "name": "Root",
                "description": "Welcome and API information endpoints",
            },
            {
                "name": "Health",
                "description": "Health check and system status endpoints",
            },
            {
                "name": "Interviews",
                "description": "Adaptive interview management endpoints",
            },
        ],
    )

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
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
                "version": "1.0.0",
                "docs": {
                    "swagger_ui": "/docs",
                    "redoc": "/redoc",
                    "openapi_json": f"{settings.API_V1_STR}/openapi.json"
                },
                "endpoints": {
                    "health": f"{settings.API_V1_STR}/health/",
                    "interviews": f"{settings.API_V1_STR}/interviews/"
                },
                "status": "running",
                "features": [
                    "Resume Analysis",
                    "Adaptive Questioning", 
                    "Performance-Based Difficulty",
                    "Comprehensive Evaluation",
                    "Smart Follow-ups"
                ]
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
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 