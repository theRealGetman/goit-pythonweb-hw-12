"""
Redis cache service.

This module provides Redis-based caching functionality.
"""

import json
from typing import Optional, Any

import redis.asyncio as redis

from src.config.config import settings


class RedisService:
    """
    Service for Redis caching operations.

    Provides methods to set, get, and delete cached data.
    """

    def __init__(self):
        """Initialize Redis connection pool."""
        self.redis_pool = redis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            decode_responses=True,
        )
        self.redis = redis.Redis(connection_pool=self.redis_pool)

    async def set(self, key: str, value: Any, expire: int = None) -> None:
        """
        Set a value in Redis cache with optional expiration.

        Args:
            key: Cache key
            value: Value to store (will be JSON serialized)
            expire: Optional expiration time in seconds
        """
        serialized_value = json.dumps(value)
        await self.redis.set(key, serialized_value, ex=expire)

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from Redis cache.

        Args:
            key: Cache key

        Returns:
            Any: Deserialized cached value if found, None otherwise
        """
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None

    async def delete(self, key: str) -> None:
        """
        Delete a value from Redis cache.

        Args:
            key: Cache key to delete
        """
        await self.redis.delete(key)

    async def flush(self) -> None:
        """
        Clear the entire Redis cache.

        Use with caution as this affects all cached data.
        """
        await self.redis.flushdb()


# Singleton instance of RedisService
_redis_service = None


def get_redis_service() -> RedisService:
    """
    Get Redis service dependency.

    Returns a singleton instance of the Redis service.

    Returns:
        RedisService: Redis caching service
    """
    global _redis_service
    if _redis_service is None:
        _redis_service = RedisService()
    return _redis_service
