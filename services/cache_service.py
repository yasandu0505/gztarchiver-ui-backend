import time
from typing import Dict, Any, Optional, Tuple
from config.settings import settings


class CacheService:
    """Service for managing cache with TTL"""
    
    def __init__(self, ttl: Optional[int] = None):
        """
        Initialize cache service.
        
        Args:
            ttl: Time to live in seconds. If not provided, uses settings.
        """
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.ttl = ttl or settings.cache_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if key not in self.cache:
            return None
        
        cached_data, cache_time = self.cache[key]
        current_time = time.time()
        
        if current_time - cache_time < self.ttl:
            return cached_data
        
        # Cache expired, remove it
        del self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache with current timestamp.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        current_time = time.time()
        self.cache[key] = (value, current_time)
    
    def clear(self, key: Optional[str] = None) -> None:
        """
        Clear cache entry or all cache.
        
        Args:
            key: Cache key to clear. If None, clears all cache.
        """
        if key is None:
            self.cache.clear()
        elif key in self.cache:
            del self.cache[key]
    
    def exists(self, key: str) -> bool:
        """
        Check if cache key exists and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and not expired, False otherwise
        """
        return self.get(key) is not None

