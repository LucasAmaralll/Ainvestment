"""
SQLite-based caching system to reduce API calls and improve performance.
"""

import sqlite3
import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional
from pathlib import Path

from src.utils.config import settings
from src.utils.logger import logger


class CacheManager:
    """
    Simple SQLite cache with TTL support.
    
    Usage:
        cache = CacheManager()
        
        # Try to get from cache
        data = cache.get("stock_aapl_1y")
        if data is None:
            # Fetch from API
            data = expensive_api_call()
            # Store in cache
            cache.set("stock_aapl_1y", data, ttl_hours=24)
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize cache manager.
        
        Args:
            db_path: Path to SQLite database. Defaults to config setting.
        """
        self.db_path = db_path or settings.cache_db_path
        self.enabled = settings.cache_enabled
        
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()
    
    def _init_db(self) -> None:
        """Create cache table if it doesn't exist."""
        if not self.enabled:
            return
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    created_at TIMESTAMP,
                    expires_at TIMESTAMP
                )
            """)
            
            # Create index on expiration
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at 
                ON cache(expires_at)
            """)
            
            conn.commit()
    
    def _generate_key(self, key: str) -> str:
        """Generate a hash-based cache key."""
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if not self.enabled:
            return None
        
        try:
            hashed_key = self._generate_key(key)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT value, expires_at FROM cache WHERE key = ?",
                    (hashed_key,)
                )
                row = cursor.fetchone()
                
                if row is None:
                    logger.debug("cache_miss", key=key)
                    return None
                
                value_blob, expires_at = row
                expires_at = datetime.fromisoformat(expires_at)
                
                # Check if expired
                if datetime.now() >= expires_at:
                    logger.debug("cache_expired", key=key)
                    self.delete(key)
                    return None
                
                # Deserialize
                value = pickle.loads(value_blob)
                logger.debug("cache_hit", key=key)
                return value
                
        except Exception as e:
            logger.warning("cache_get_error", key=key, error=str(e))
            return None
    
    def set(self, key: str, value: Any, ttl_hours: Optional[int] = None) -> bool:
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (must be picklable)
            ttl_hours: Time to live in hours. Defaults to config setting.
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            hashed_key = self._generate_key(key)
            ttl = ttl_hours or settings.cache_ttl_hours
            
            created_at = datetime.now()
            expires_at = created_at + timedelta(hours=ttl)
            
            # Serialize value
            value_blob = pickle.dumps(value)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO cache 
                    (key, value, created_at, expires_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (hashed_key, value_blob, created_at, expires_at)
                )
                conn.commit()
            
            logger.debug("cache_set", key=key, ttl_hours=ttl)
            return True
            
        except Exception as e:
            logger.warning("cache_set_error", key=key, error=str(e))
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a cache entry."""
        if not self.enabled:
            return False
        
        try:
            hashed_key = self._generate_key(key)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cache WHERE key = ?", (hashed_key,))
                conn.commit()
            
            logger.debug("cache_delete", key=key)
            return True
            
        except Exception as e:
            logger.warning("cache_delete_error", key=key, error=str(e))
            return False
    
    def clear_expired(self) -> int:
        """
        Remove all expired cache entries.
        
        Returns:
            Number of entries removed
        """
        if not self.enabled:
            return 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM cache WHERE expires_at < ?",
                    (datetime.now(),)
                )
                count = cursor.rowcount
                conn.commit()
            
            logger.info("cache_cleared_expired", count=count)
            return count
            
        except Exception as e:
            logger.warning("cache_clear_expired_error", error=str(e))
            return 0
    
    def clear_all(self) -> bool:
        """Clear entire cache."""
        if not self.enabled:
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cache")
                conn.commit()
            
            logger.info("cache_cleared_all")
            return True
            
        except Exception as e:
            logger.warning("cache_clear_all_error", error=str(e))
            return False
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM cache")
                total = cursor.fetchone()[0]
                
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM cache WHERE expires_at < ?",
                    (datetime.now(),)
                )
                expired = cursor.fetchone()[0]
            
            return {
                "enabled": True,
                "total_entries": total,
                "expired_entries": expired,
                "valid_entries": total - expired,
            }
            
        except Exception as e:
            logger.warning("cache_stats_error", error=str(e))
            return {"enabled": True, "error": str(e)}


# Global cache instance
cache = CacheManager()
