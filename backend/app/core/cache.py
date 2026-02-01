"""Redis cache client wrapper for content caching."""

import redis
import json
import hashlib
import logging
from typing import Optional, Any, Dict
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheClient:
    """Redis cache client with graceful degradation."""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = settings.CACHE_ENABLED

        if self.enabled:
            try:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache connected successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Caching disabled.")
                self.enabled = False
                self.redis_client = None

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled or not self.redis_client:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        if not self.enabled or not self.redis_client:
            return False

        try:
            serialized = json.dumps(value)
            if ttl_seconds:
                self.redis_client.setex(key, ttl_seconds, serialized)
            else:
                self.redis_client.set(key, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.enabled or not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.enabled or not self.redis_client:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache clear pattern error for {pattern}: {e}")
            return 0

    @staticmethod
    def make_cache_key(prefix: str, **kwargs) -> str:
        """Generate cache key from prefix and parameters."""
        # Sort kwargs for consistent key generation
        sorted_params = sorted(kwargs.items())
        param_str = json.dumps(sorted_params, sort_keys=True)
        param_hash = hashlib.sha256(param_str.encode()).hexdigest()[:16]
        return f"{prefix}:{param_hash}"

    @staticmethod
    def make_content_hash(content: str) -> str:
        """Generate hash for content validation caching."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def get_vocab_cache_key(self, language: str, level: str, exclusions: list) -> str:
        """Generate cache key for vocabulary."""
        return self.make_cache_key(
            f"vocab:{language}:{level}",
            exclusions=sorted(exclusions) if exclusions else []
        )

    def get_grammar_cache_key(self, language: str, level: str) -> str:
        """Generate cache key for grammar."""
        return f"grammar:{language}:{level}"

    def get_validation_cache_key(self, content_hash: str) -> str:
        """Generate cache key for validation results."""
        return f"validation:{content_hash}"

    def get_recent_words_cache_key(self, user_id: int, language: str, module: str) -> str:
        """Generate cache key for recent words query."""
        return f"recent_words:{user_id}:{language}:{module}"


# Global cache instance
cache = CacheClient()
