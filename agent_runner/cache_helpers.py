"""
Cache invalidation helpers for ensuring database is source of truth.
Provides TTL and DB timestamp checking mechanisms.
"""

import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from agent_runner.db_utils import run_query_with_memory

logger = logging.getLogger(__name__)

class CacheInvalidator:
    """Helper class for cache invalidation based on TTL and DB timestamps."""
    
    @staticmethod
    def is_expired(cache_timestamp: float, ttl_seconds: float) -> bool:
        """
        Check if cache entry is expired based on TTL.
        
        Args:
            cache_timestamp: Unix timestamp when cache was created
            ttl_seconds: Time-to-live in seconds
            
        Returns:
            True if expired, False otherwise
        """
        if cache_timestamp is None:
            return True
        return (time.time() - cache_timestamp) > ttl_seconds
    
    @staticmethod
    async def check_db_timestamp(
        memory_server,
        table: str,
        key_field: str,
        key_value: str,
        timestamp_field: str = "last_updated"
    ) -> Optional[float]:
        """
        Get the last_updated timestamp from DB for a given record.
        
        Args:
            memory_server: MemoryServer instance
            table: Table name
            key_field: Field name to match
            key_value: Value to match
            timestamp_field: Field containing timestamp
            
        Returns:
            Unix timestamp or None if not found
        """
        try:
            query = f"SELECT {timestamp_field} FROM {table} WHERE {key_field} = '{key_value}' LIMIT 1;"
            result = await run_query_with_memory(memory_server, query)
            
            if result and len(result) > 0:
                ts_str = result[0].get(timestamp_field)
                if ts_str:
                    # Parse SurrealDB datetime to Unix timestamp
                    try:
                        from datetime import datetime
                        if isinstance(ts_str, str):
                            # Handle ISO format
                            dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                            return dt.timestamp()
                    except Exception as e:
                        logger.warning(f"Failed to parse timestamp {ts_str}: {e}")
            return None
        except Exception as e:
            logger.warning(f"Failed to check DB timestamp: {e}")
            return None
    
    @staticmethod
    async def should_invalidate_cache(
        memory_server,
        cache_timestamp: float,
        ttl_seconds: float,
        table: str,
        key_field: str,
        key_value: str
    ) -> bool:
        """
        Check if cache should be invalidated based on TTL or DB changes.
        
        Args:
            memory_server: MemoryServer instance
            cache_timestamp: Unix timestamp when cache was created
            ttl_seconds: Time-to-live in seconds
            table: DB table to check
            key_field: Field name to match
            key_value: Value to match
            
        Returns:
            True if cache should be invalidated, False otherwise
        """
        # Check TTL first (fast)
        if CacheInvalidator.is_expired(cache_timestamp, ttl_seconds):
            return True
        
        # Check DB timestamp (slower, but ensures consistency)
        db_timestamp = await CacheInvalidator.check_db_timestamp(
            memory_server, table, key_field, key_value
        )
        
        if db_timestamp and db_timestamp > cache_timestamp:
            logger.debug(f"Cache invalidated: DB updated at {db_timestamp}, cache at {cache_timestamp}")
            return True
        
        return False

