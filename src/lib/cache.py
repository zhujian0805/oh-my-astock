"""Multi-layer caching system for stock data with TTL support.

Provides both in-memory and persistent file-based caching with configurable
TTL (Time To Live) for different data types. Inspired by best practices from
the /home/jzhu/stock repository.
"""

import hashlib
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import pandas as pd


class CacheKey:
    """Generate consistent cache keys for operations and parameters."""

    @staticmethod
    def generate(method: str, **params) -> str:
        """Generate an MD5-based cache key from method name and parameters.

        Args:
            method: The method/operation name
            **params: Parameters to include in the cache key

        Returns:
            MD5 hash of the method and sorted parameters
        """
        param_str = json.dumps(params, sort_keys=True, default=str)
        combined = f"{method}:{param_str}"
        return hashlib.md5(combined.encode()).hexdigest()


class InMemoryCache:
    """In-memory cache with TTL support for frequently accessed data."""

    def __init__(self):
        """Initialize empty in-memory cache."""
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str, ttl_seconds: int) -> Optional[Any]:
        """Retrieve value from cache if not expired.

        Args:
            key: Cache key
            ttl_seconds: Time-to-live in seconds

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if key not in self._cache:
            self._misses += 1
            return None

        value, timestamp = self._cache[key]
        if time.time() - timestamp > ttl_seconds:
            del self._cache[key]
            self._misses += 1
            return None

        self._hits += 1
        return value

    def set(self, key: str, value: Any) -> None:
        """Store value in cache with current timestamp.

        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cached items."""
        self._cache.clear()

    def stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        total = self._hits + self._misses
        return {
            'hits': self._hits,
            'misses': self._misses,
            'total': total,
            'size': len(self._cache),
        }


class PersistentFileCache:
    """File-based persistent cache with TTL support."""

    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize file-based cache.

        Args:
            cache_dir: Cache directory path. Defaults to ~/.cache/oh-my-astock/
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser('~/.cache/oh-my-astock')

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str, ttl_seconds: int) -> Optional[Any]:
        """Retrieve value from file cache if not expired.

        Args:
            key: Cache key
            ttl_seconds: Time-to-live in seconds

        Returns:
            Cached value if file exists and not expired, None otherwise
        """
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        try:
            # Check file age
            file_age = time.time() - cache_file.stat().st_mtime
            if file_age > ttl_seconds:
                cache_file.unlink()  # Delete expired cache
                return None

            # Read and return cached data
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return data.get('value')
        except Exception:
            # Silently ignore cache read errors
            return None

    def set(self, key: str, value: Any) -> None:
        """Store value in file cache.

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
        """
        cache_file = self.cache_dir / f"{key}.json"

        try:
            data = {
                'value': value,
                'timestamp': datetime.now().isoformat(),
            }
            with open(cache_file, 'w') as f:
                json.dump(data, f, default=str)
        except Exception:
            # Silently ignore cache write errors
            pass

    def clear(self) -> None:
        """Clear all cached files."""
        try:
            for cache_file in self.cache_dir.glob('*.json'):
                cache_file.unlink()
        except Exception:
            pass


class DataFrameCache:
    """Specialized cache for pandas DataFrames with serialization support."""

    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize DataFrame cache.

        Args:
            cache_dir: Cache directory path. Defaults to ~/.cache/oh-my-astock/
        """
        self.cache_dir = Path(cache_dir or os.path.expanduser('~/.cache/oh-my-astock'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str, ttl_seconds: int) -> Optional[pd.DataFrame]:
        """Retrieve DataFrame from cache if not expired.

        Args:
            key: Cache key
            ttl_seconds: Time-to-live in seconds

        Returns:
            Cached DataFrame if exists and not expired, None otherwise
        """
        cache_file = self.cache_dir / f"{key}.parquet"

        if not cache_file.exists():
            return None

        try:
            # Check file age
            file_age = time.time() - cache_file.stat().st_mtime
            if file_age > ttl_seconds:
                cache_file.unlink()  # Delete expired cache
                return None

            # Read and return cached DataFrame
            return pd.read_parquet(cache_file)
        except Exception:
            # Silently ignore cache read errors
            return None

    def set(self, key: str, value: pd.DataFrame) -> None:
        """Store DataFrame in cache using Parquet format.

        Args:
            key: Cache key
            value: DataFrame to cache
        """
        cache_file = self.cache_dir / f"{key}.parquet"

        try:
            value.to_parquet(cache_file)
        except Exception:
            # Silently ignore cache write errors
            pass


class MultiLayerCache:
    """Multi-layer caching system combining in-memory and persistent cache.

    Provides efficient caching with automatic TTL expiration and fallback
    between memory and disk storage.
    """

    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize multi-layer cache.

        Args:
            cache_dir: Cache directory path. Defaults to ~/.cache/oh-my-astock/
        """
        self.memory_cache = InMemoryCache()
        self.file_cache = PersistentFileCache(cache_dir)
        self.df_cache = DataFrameCache(cache_dir)

    def get_historical_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
    ) -> Optional[pd.DataFrame]:
        """Get historical data from cache with memory→disk fallback.

        Args:
            stock_code: Stock code (e.g., '600938')
            start_date: Start date as string (YYYY-MM-DD)
            end_date: End date as string (YYYY-MM-DD)

        Returns:
            Cached DataFrame if available, None otherwise
        """
        # Default TTL: 7 days for historical data
        ttl = 7 * 24 * 60 * 60

        key = CacheKey.generate(
            'historical_data',
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
        )

        # Try memory cache first (faster)
        result = self.memory_cache.get(key, ttl)
        if result is not None:
            return result

        # Try persistent cache (slower but survives process restart)
        result = self.df_cache.get(key, ttl)
        if result is not None:
            # Restore to memory cache for next access
            self.memory_cache.set(key, result)
            return result

        return None

    def set_historical_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        data: pd.DataFrame,
    ) -> None:
        """Store historical data in both caches.

        Args:
            stock_code: Stock code
            start_date: Start date as string
            end_date: End date as string
            data: DataFrame to cache
        """
        key = CacheKey.generate(
            'historical_data',
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
        )

        # Store in both layers
        self.memory_cache.set(key, data)
        self.df_cache.set(key, data)

    def get_realtime_data(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """Get real-time data from cache with TTL.

        Args:
            stock_code: Stock code

        Returns:
            Cached real-time data if available, None otherwise
        """
        # Default TTL: 2 minutes for real-time data
        ttl = 2 * 60

        key = CacheKey.generate('realtime_data', stock_code=stock_code)

        # Try memory cache first
        result = self.memory_cache.get(key, ttl)
        if result is not None:
            return result

        # Try persistent cache
        result = self.file_cache.get(key, ttl)
        if result is not None:
            # Restore to memory cache
            self.memory_cache.set(key, result)
            return result

        return None

    def set_realtime_data(self, stock_code: str, data: Dict[str, Any]) -> None:
        """Store real-time data in both caches.

        Args:
            stock_code: Stock code
            data: Real-time data dictionary
        """
        key = CacheKey.generate('realtime_data', stock_code=stock_code)
        self.memory_cache.set(key, data)
        self.file_cache.set(key, data)

    def clear(self) -> None:
        """Clear all caches."""
        self.memory_cache.clear()
        self.file_cache.clear()
        self.df_cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache hit/miss stats
        """
        return {
            'memory': self.memory_cache.stats(),
        }


# Global cache instance
_global_cache: Optional[MultiLayerCache] = None


def get_cache() -> MultiLayerCache:
    """Get or create the global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = MultiLayerCache()
    return _global_cache
