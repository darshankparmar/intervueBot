"""
Application event handlers for startup and shutdown.

This module contains event handlers for initializing and cleaning up
application resources.
"""

import logging
from typing import Callable

from fastapi import FastAPI

from intervuebot.core.config import settings
from intervuebot.core.redis import close_redis_client, get_redis_client
from intervuebot.agents.adaptive_interview_agent import adaptive_interview_agent
from intervuebot.services.resume_analyzer import resume_analyzer

logger = logging.getLogger(__name__)


def create_start_app_handler(app: FastAPI) -> Callable:
    """
    Create startup event handler.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Callable: Startup event handler
    """

    async def start_app() -> None:
        """Initialize application resources on startup."""
        logger.info("Starting IntervueBot application...")
        
        # Initialize database connection
        # TODO: Add database initialization
        
        # Initialize Redis connection
        try:
            await get_redis_client()
            logger.info("Redis connection initialized")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            logger.info("Continuing without Redis - some features may be limited")
        
        # Initialize AI agents
        try:
            # Test adaptive interview agent initialization
            from intervuebot.schemas.interview import CandidateProfile, DifficultyLevel, ExperienceLevel, InterviewType
            from intervuebot.schemas.interview import ResumeAnalysis
            
            # Create test candidate profile
            test_candidate = CandidateProfile(
                name="Test Candidate",
                email="test@example.com",
                position="Software Engineer",
                experience_level=ExperienceLevel.MID_LEVEL,
                interview_type=InterviewType.TECHNICAL,
                files=[]  # Empty files list for testing
            )
            
            # Test adaptive agent
            test_question = await adaptive_interview_agent.generate_next_question(
                candidate_profile=test_candidate,
                previous_responses=[],
                resume_analysis=None,
                position="Software Engineer",
                current_difficulty=DifficultyLevel.MEDIUM,
                interview_progress=0.0,
                question_count=0
            )
            logger.info("Adaptive interview agent initialized successfully")
            
            # Test resume analyzer
            test_resume_analysis = await resume_analyzer.analyze_resume(
                resume_files=[],
                position="Software Engineer"
            )
            logger.info("Resume analyzer initialized successfully")
            
        except Exception as e:
            logger.warning(f"Agent initialization failed: {e}")
        
        logger.info("IntervueBot application started successfully!")

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    """
    Create shutdown event handler.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Callable: Shutdown event handler
    """

    async def stop_app() -> None:
        """Clean up application resources on shutdown."""
        logger.info("Shutting down IntervueBot application...")
        
        # Close database connections
        # TODO: Add database cleanup
        
        # Close Redis connections
        await close_redis_client()
        
        # Clean up AI agents
        # TODO: Add agent cleanup
        
        logger.info("IntervueBot application shutdown complete!")

    return stop_app 