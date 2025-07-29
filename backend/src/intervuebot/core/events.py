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
from intervuebot.agents.interview_agent import interview_agent
from intervuebot.agents.evaluation_agent import evaluation_agent
from intervuebot.agents.question_generator_agent import question_generator_agent

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
            # Test interview agent initialization
            test_question = interview_agent.generate_question(
                position="Software Engineer",
                category="technical",
                difficulty="medium"
            )
            logger.info("Interview agent initialized successfully")
            
            # Test evaluation agent initialization
            test_evaluation = evaluation_agent.score_response(
                question="What is Python?",
                response="Python is a programming language",
                position="Software Engineer",
                category="technical"
            )
            logger.info("Evaluation agent initialized successfully")
            
            # Test question generator agent initialization
            test_questions = question_generator_agent.generate_question_sequence(
                position="Software Engineer",
                interview_type="technical",
                experience_level="mid-level",
                required_skills=["Python", "JavaScript"]
            )
            logger.info("Question generator agent initialized successfully")
            
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