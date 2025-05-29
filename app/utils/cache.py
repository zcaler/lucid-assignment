"""
Caching utility for implementing response caching with TTL support.
Provides in-memory caching for GetPosts endpoint with 5-minute expiration.
"""

from cachetools import TTLCache
from typing import Any, Optional
import threading
from datetime import datetime, timedelta

# Thread-safe cache with 5-minute TTL
# Max size of 1000 entries to prevent memory overflow
posts_cache = TTLCache(maxsize=1000, ttl=300)  # 300 seconds = 5 minutes
cache_lock = threading.RLock()


class CacheService:
    """
    Service class for managing cached data with thread safety.
    Implements TTL-based caching for user posts.
    """
    
    @staticmethod
    def get_user_posts_cache_key(user_id: int) -> str:
        """
        Generate cache key for user posts.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            str: Cache key for the user's posts
        """
        return f"user_posts_{user_id}"
    
    @staticmethod
    def get_cached_posts(user_id: int) -> Optional[Any]:
        """
        Retrieve cached posts for a specific user.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            Any: Cached posts data if exists and not expired, None otherwise
        """
        cache_key = CacheService.get_user_posts_cache_key(user_id)
        
        with cache_lock:
            try:
                cached_data = posts_cache.get(cache_key)
                if cached_data:
                    return cached_data
            except KeyError:
                pass
        
        return None
    
    @staticmethod
    def cache_user_posts(user_id: int, posts_data: Any) -> None:
        """
        Cache posts data for a specific user with TTL.
        
        Args:
            user_id: User's unique identifier
            posts_data: Posts data to cache
        """
        cache_key = CacheService.get_user_posts_cache_key(user_id)
        
        with cache_lock:
            posts_cache[cache_key] = {
                "data": posts_data,
                "cached_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(minutes=5)
            }
    
    @staticmethod
    def invalidate_user_posts_cache(user_id: int) -> None:
        """
        Invalidate cached posts for a specific user.
        Called when user creates or deletes posts.
        
        Args:
            user_id: User's unique identifier
        """
        cache_key = CacheService.get_user_posts_cache_key(user_id)
        
        with cache_lock:
            try:
                del posts_cache[cache_key]
            except KeyError:
                pass  # Cache entry doesn't exist, nothing to invalidate
    
    @staticmethod
    def clear_all_cache() -> None:
        """
        Clear all cached data.
        Useful for testing or memory management.
        """
        with cache_lock:
            posts_cache.clear()
    
    @staticmethod
    def get_cache_info() -> dict:
        """
        Get information about current cache state.
        
        Returns:
            dict: Cache statistics and information
        """
        with cache_lock:
            return {
                "cache_size": len(posts_cache),
                "max_size": posts_cache.maxsize,
                "ttl_seconds": posts_cache.ttl,
                "current_time": datetime.utcnow().isoformat()
            }