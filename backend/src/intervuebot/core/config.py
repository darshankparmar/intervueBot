"""
Configuration settings for IntervueBot.

This module contains all configuration settings using Pydantic Settings
for type safety and environment variable support.
"""

import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, HttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Project information
    PROJECT_NAME: str = "IntervueBot"
    PROJECT_DESCRIPTION: str = "AI Interview Taker Agent using Agno Framework"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Assemble CORS origins."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "intervuebot"
    POSTGRES_PASSWORD: str = "intervuebot"
    POSTGRES_DB: str = "intervuebot"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Assemble database connection string."""
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None

    # Default LLM provider (set to Google for development)
    DEFAULT_LLM_PROVIDER: str = "google"
    DEFAULT_LLM_MODEL: str = "gemini-pro"

    # Interview settings
    MAX_INTERVIEW_DURATION_MINUTES: int = 60
    MAX_QUESTIONS_PER_INTERVIEW: int = 20
    QUESTION_TIMEOUT_SECONDS: int = 300  # 5 minutes

    # Interview sequence settings
    MIN_INTERVIEW_DURATION_MINUTES: int = 30
    DEFAULT_INTERVIEW_DURATION_MINUTES: int = 60

    # Phase-specific settings
    INTRODUCTION_PHASE_DURATION: int = 5
    WARM_UP_PHASE_DURATION: int = 8
    TECHNICAL_BASIC_PHASE_DURATION: int = 15
    TECHNICAL_ADVANCED_PHASE_DURATION: int = 20
    BEHAVIORAL_PHASE_DURATION: int = 15
    PROBLEM_SOLVING_PHASE_DURATION: int = 12
    SITUATIONAL_PHASE_DURATION: int = 10
    CULTURAL_FIT_PHASE_DURATION: int = 8
    CLOSING_PHASE_DURATION: int = 5

    # Logging settings
    LOG_LEVEL: str = "INFO"

    # Development settings
    ENABLE_AGENT_INITIALIZATION_TESTS: bool = True
    ENABLE_REDIS_HEALTH_CHECK: bool = True
    ENABLE_DETAILED_LOGGING: bool = True

    # Deployment settings
    ENVIRONMENT: str = "development"

    # Monitoring settings
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    # Cache settings
    ENABLE_LLM_CACHE: bool = True
    LLM_CACHE_TTL_HOURS: int = 24
    ENABLE_SESSION_CACHE: bool = True
    SESSION_CACHE_TTL_HOURS: int = 1

    # Rate limiting
    ENABLE_RATE_LIMITING: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 1000

    # Allowed hosts for security
    ALLOWED_HOSTS: List[str] = ["*"]

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings() 