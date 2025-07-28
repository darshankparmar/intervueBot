"""
Redis connection and utility functions.

This module provides Redis connection management and common utility
functions for caching, session management, and real-time features.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

import redis.asyncio as redis
from redis.exceptions import RedisError

from intervuebot.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis connection
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """
    Get Redis client instance.
    
    Returns:
        redis.Redis: Redis client instance
    """
    global _redis_client
    
    if _redis_client is None:
        try:
            logger.info(f"Attempting to connect to Redis at {settings.REDIS_URL}")
            client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=30,
                socket_timeout=30,
                retry_on_timeout=True,
                retry_on_error=[TimeoutError, ConnectionError],
            )
            logger.info(f"Redis client created: {type(client)}")
            # Test connection
            ping_result = await client.ping()
            logger.info(f"Redis ping result: {ping_result} (type: {type(ping_result)})")
            if not ping_result:
                raise RedisError("Redis ping failed")
            _redis_client = client
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            logger.error(f"Exception type: {type(e)}")
            raise
    
    return _redis_client


async def close_redis_client():
    """Close Redis connection."""
    global _redis_client
    
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")


# Session Management
async def store_interview_session(session_id: str, session_data: Dict[str, Any], ttl: int = 3600):
    """
    Store interview session data in Redis.
    
    Args:
        session_id: Unique session identifier
        session_data: Session data to store
        ttl: Time to live in seconds (default: 1 hour)
    """
    client = await get_redis_client()
    key = f"interview_session:{session_id}"
    await client.setex(key, ttl, json.dumps(session_data))


async def get_interview_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve interview session data from Redis.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Optional[Dict[str, Any]]: Session data or None if not found
    """
    client = await get_redis_client()
    key = f"interview_session:{session_id}"
    data = await client.get(key)
    return json.loads(data) if data else None


async def delete_interview_session(session_id: str):
    """
    Delete interview session data from Redis.
    
    Args:
        session_id: Unique session identifier
    """
    client = await get_redis_client()
    key = f"interview_session:{session_id}"
    await client.delete(key)


# Caching
async def cache_llm_response(prompt_hash: str, response: str, ttl: int = 86400):
    """
    Cache LLM response to avoid repeated expensive API calls.
    
    Args:
        prompt_hash: Hash of the prompt for cache key
        response: LLM response to cache
        ttl: Time to live in seconds (default: 24 hours)
    """
    client = await get_redis_client()
    key = f"llm_cache:{prompt_hash}"
    await client.setex(key, ttl, response)


async def get_cached_llm_response(prompt_hash: str) -> Optional[str]:
    """
    Get cached LLM response.
    
    Args:
        prompt_hash: Hash of the prompt for cache key
        
    Returns:
        Optional[str]: Cached response or None if not found
    """
    client = await get_redis_client()
    key = f"llm_cache:{prompt_hash}"
    return await client.get(key)


# Rate Limiting
async def check_rate_limit(user_id: str, endpoint: str, limit: int = 100, window: int = 60) -> bool:
    """
    Check if user has exceeded rate limit for an endpoint.
    
    Args:
        user_id: User identifier
        endpoint: API endpoint
        limit: Maximum requests per window
        window: Time window in seconds
        
    Returns:
        bool: True if within limit, False if exceeded
    """
    client = await get_redis_client()
    key = f"rate_limit:{user_id}:{endpoint}"
    
    # Increment counter
    current = await client.incr(key)
    
    # Set expiry on first request
    if current == 1:
        await client.expire(key, window)
    
    return current <= limit


# Analytics
async def increment_interview_metric(metric: str, value: int = 1):
    """
    Increment interview analytics metric.
    
    Args:
        metric: Metric name
        value: Value to increment by
    """
    client = await get_redis_client()
    await client.incr(f"metric:{metric}", value)


async def get_interview_stats() -> Dict[str, Any]:
    """
    Get real-time interview statistics.
    
    Returns:
        Dict[str, Any]: Interview statistics
    """
    client = await get_redis_client()
    
    # Get active sessions count
    active_sessions = len(await client.keys("interview_session:*"))
    
    # Get total interviews
    total_interviews = await client.get("metric:total_interviews") or "0"
    
    return {
        "active_sessions": active_sessions,
        "total_interviews": int(total_interviews),
        "timestamp": "2024-01-01T00:00:00Z"  # TODO: Add proper timestamp
    }


# Queue Management
async def add_to_evaluation_queue(task_data: Dict[str, Any]):
    """
    Add evaluation task to queue.
    
    Args:
        task_data: Task data to queue
    """
    client = await get_redis_client()
    await client.lpush("evaluation_queue", json.dumps(task_data))


async def get_evaluation_task() -> Optional[Dict[str, Any]]:
    """
    Get next evaluation task from queue.
    
    Returns:
        Optional[Dict[str, Any]]: Task data or None if queue is empty
    """
    client = await get_redis_client()
    task = await client.brpop("evaluation_queue", timeout=1)
    
    if task:
        return json.loads(task[1])
    return None 