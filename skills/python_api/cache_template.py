# ═══════════════════════════════════════════════════════════════
# CACHE TEMPLATE
# Response caching patterns for Flask APIs
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Choose caching backend (memory, file, or Redis)
# 3. Apply @cached decorator to endpoints
#
# ═══════════════════════════════════════════════════════════════

import json
import hashlib
import logging
import threading
import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# CACHE BACKENDS
# ═══════════════════════════════════════════════════════════════


class CacheBackend:
    """Base class for cache backends."""

    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl: int = None):
        raise NotImplementedError

    def delete(self, key: str):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def exists(self, key: str) -> bool:
        return self.get(key) is not None


class MemoryCache(CacheBackend):
    """In-memory cache with TTL support."""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: Dict[str, Dict] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]

            # Check expiration
            if entry['expires_at'] and datetime.utcnow() > entry['expires_at']:
                del self._cache[key]
                return None

            return entry['value']

    def set(self, key: str, value: Any, ttl: int = None):
        with self._lock:
            # Evict oldest if at capacity
            if len(self._cache) >= self.max_size:
                oldest = min(self._cache, key=lambda k: self._cache[k]['created_at'])
                del self._cache[oldest]

            expires_at = None
            if ttl:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl)

            self._cache[key] = {
                'value': value,
                'created_at': datetime.utcnow(),
                'expires_at': expires_at,
            }

    def delete(self, key: str):
        with self._lock:
            self._cache.pop(key, None)

    def clear(self):
        with self._lock:
            self._cache.clear()

    def cleanup_expired(self):
        """Remove expired entries."""
        with self._lock:
            now = datetime.utcnow()
            expired = [
                k for k, v in self._cache.items()
                if v['expires_at'] and now > v['expires_at']
            ]
            for key in expired:
                del self._cache[key]
            return len(expired)

    def stats(self) -> Dict:
        """Get cache statistics."""
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
            }


class FileCache(CacheBackend):
    """File-based cache for persistence across restarts."""

    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _get_path(self, key: str) -> Path:
        """Get file path for cache key."""
        # Hash key to create safe filename
        hashed = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hashed}.cache"

    def get(self, key: str) -> Optional[Any]:
        path = self._get_path(key)

        if not path.exists():
            return None

        try:
            with open(path, 'rb') as f:
                entry = pickle.load(f)

            # Check expiration
            if entry['expires_at'] and datetime.utcnow() > entry['expires_at']:
                path.unlink()
                return None

            return entry['value']
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = None):
        path = self._get_path(key)

        expires_at = None
        if ttl:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)

        entry = {
            'key': key,
            'value': value,
            'created_at': datetime.utcnow(),
            'expires_at': expires_at,
        }

        with self._lock:
            with open(path, 'wb') as f:
                pickle.dump(entry, f)

    def delete(self, key: str):
        path = self._get_path(key)
        if path.exists():
            path.unlink()

    def clear(self):
        with self._lock:
            for path in self.cache_dir.glob("*.cache"):
                path.unlink()


class SQLiteCache(CacheBackend):
    """SQLite-based cache for thread-safe persistence."""

    def __init__(self, db_path: str = "cache/cache.db"):
        import sqlite3

        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._local = threading.local()

        # Initialize table
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value BLOB,
                created_at TEXT,
                expires_at TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_expires ON cache(expires_at)")
        conn.commit()

    def _get_conn(self):
        if not hasattr(self._local, 'conn'):
            import sqlite3
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self._local.conn

    def get(self, key: str) -> Optional[Any]:
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT value, expires_at FROM cache WHERE key = ?",
            (key,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        value_blob, expires_at = row

        # Check expiration
        if expires_at:
            expires = datetime.fromisoformat(expires_at)
            if datetime.utcnow() > expires:
                self.delete(key)
                return None

        return pickle.loads(value_blob)

    def set(self, key: str, value: Any, ttl: int = None):
        conn = self._get_conn()

        expires_at = None
        if ttl:
            expires_at = (datetime.utcnow() + timedelta(seconds=ttl)).isoformat()

        value_blob = pickle.dumps(value)

        conn.execute("""
            INSERT OR REPLACE INTO cache (key, value, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        """, (key, value_blob, datetime.utcnow().isoformat(), expires_at))
        conn.commit()

    def delete(self, key: str):
        conn = self._get_conn()
        conn.execute("DELETE FROM cache WHERE key = ?", (key,))
        conn.commit()

    def clear(self):
        conn = self._get_conn()
        conn.execute("DELETE FROM cache")
        conn.commit()

    def cleanup_expired(self) -> int:
        """Remove expired entries."""
        conn = self._get_conn()
        cursor = conn.execute(
            "DELETE FROM cache WHERE expires_at IS NOT NULL AND expires_at < ?",
            (datetime.utcnow().isoformat(),)
        )
        conn.commit()
        return cursor.rowcount


# ═══════════════════════════════════════════════════════════════
# CACHE MANAGER
# ═══════════════════════════════════════════════════════════════


class CacheManager:
    """
    Centralized cache management.

    Features:
    - Multiple cache backends
    - Cache namespacing
    - Automatic cleanup
    """

    def __init__(self, backend: CacheBackend = None, default_ttl: int = 300):
        self.backend = backend or MemoryCache()
        self.default_ttl = default_ttl
        self._stats = {'hits': 0, 'misses': 0}

    def get(self, key: str, namespace: str = None) -> Optional[Any]:
        """Get value from cache."""
        full_key = f"{namespace}:{key}" if namespace else key
        value = self.backend.get(full_key)

        if value is not None:
            self._stats['hits'] += 1
        else:
            self._stats['misses'] += 1

        return value

    def set(self, key: str, value: Any, ttl: int = None, namespace: str = None):
        """Set value in cache."""
        full_key = f"{namespace}:{key}" if namespace else key
        self.backend.set(full_key, value, ttl or self.default_ttl)

    def delete(self, key: str, namespace: str = None):
        """Delete from cache."""
        full_key = f"{namespace}:{key}" if namespace else key
        self.backend.delete(full_key)

    def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: int = None,
        namespace: str = None
    ) -> Any:
        """Get from cache or compute and store."""
        value = self.get(key, namespace)
        if value is None:
            value = factory()
            self.set(key, value, ttl, namespace)
        return value

    def invalidate_namespace(self, namespace: str):
        """Invalidate all keys in a namespace."""
        # This is a simplified version - full implementation
        # would need to track keys per namespace
        logger.warning(f"Namespace invalidation not fully implemented: {namespace}")

    def stats(self) -> Dict:
        """Get cache statistics."""
        total = self._stats['hits'] + self._stats['misses']
        hit_rate = self._stats['hits'] / total if total > 0 else 0

        return {
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'hit_rate': f"{hit_rate:.2%}",
            'backend': type(self.backend).__name__,
        }


# ═══════════════════════════════════════════════════════════════
# FLASK DECORATORS
# ═══════════════════════════════════════════════════════════════


# Global cache instance (initialize in your app)
_cache: Optional[CacheManager] = None


def init_cache(app, backend: CacheBackend = None, default_ttl: int = 300):
    """Initialize cache for Flask app."""
    global _cache
    _cache = CacheManager(backend, default_ttl)
    app.extensions['cache'] = _cache
    return _cache


def cached(ttl: int = None, key_func: Callable = None, namespace: str = None):
    """
    Decorator to cache endpoint responses.

    Args:
        ttl: Time-to-live in seconds
        key_func: Custom function to generate cache key
        namespace: Cache namespace

    Example:
        @app.route('/api/data')
        @cached(ttl=60)
        def get_data():
            return expensive_operation()
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            if _cache is None:
                return f(*args, **kwargs)

            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                from flask import request
                cache_key = f"{request.path}:{request.query_string.decode()}"

            # Try cache
            cached_value = _cache.get(cache_key, namespace)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value

            # Execute and cache
            result = f(*args, **kwargs)
            _cache.set(cache_key, result, ttl, namespace)
            logger.debug(f"Cache miss, stored: {cache_key}")

            return result
        return decorated
    return decorator


def invalidate_cache(key: str = None, namespace: str = None):
    """Invalidate cache entry or namespace."""
    if _cache:
        if key:
            _cache.delete(key, namespace)
        elif namespace:
            _cache.invalidate_namespace(namespace)


# ═══════════════════════════════════════════════════════════════
# MEMOIZATION DECORATOR
# ═══════════════════════════════════════════════════════════════


def memoize(ttl: int = 300, max_size: int = 100):
    """
    Memoize function results.

    Args:
        ttl: Time-to-live in seconds
        max_size: Maximum cached results

    Example:
        @memoize(ttl=60)
        def expensive_calculation(x, y):
            return x ** y
    """
    cache = {}
    order = []
    lock = threading.Lock()

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            # Create cache key from arguments
            key = (args, tuple(sorted(kwargs.items())))
            key_hash = hash(key)

            with lock:
                # Check cache
                if key_hash in cache:
                    entry = cache[key_hash]
                    if time.time() < entry['expires']:
                        return entry['value']
                    else:
                        del cache[key_hash]
                        order.remove(key_hash)

            # Execute
            result = f(*args, **kwargs)

            with lock:
                # Store result
                cache[key_hash] = {
                    'value': result,
                    'expires': time.time() + ttl,
                }
                order.append(key_hash)

                # Evict oldest if over capacity
                while len(cache) > max_size:
                    oldest = order.pop(0)
                    del cache[oldest]

            return result

        # Add cache control methods
        decorated.cache_clear = lambda: cache.clear() or order.clear()
        decorated.cache_info = lambda: {'size': len(cache), 'max_size': max_size}

        return decorated
    return decorator


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("=" * 60)
    print("CACHE TEMPLATE DEMO")
    print("=" * 60)

    # Test MemoryCache
    print("\n--- Memory Cache ---")
    mem_cache = MemoryCache()
    mem_cache.set("key1", {"data": "value1"}, ttl=5)
    print(f"Set key1, get: {mem_cache.get('key1')}")
    print(f"Stats: {mem_cache.stats()}")

    # Test SQLiteCache
    print("\n--- SQLite Cache ---")
    sql_cache = SQLiteCache("test_cache.db")
    sql_cache.set("key2", [1, 2, 3], ttl=10)
    print(f"Set key2, get: {sql_cache.get('key2')}")

    # Test CacheManager
    print("\n--- Cache Manager ---")
    manager = CacheManager(MemoryCache(), default_ttl=60)

    # get_or_set pattern
    def expensive_operation():
        print("  Computing...")
        time.sleep(0.1)
        return {"computed": True}

    result1 = manager.get_or_set("computed_key", expensive_operation)
    print(f"First call: {result1}")

    result2 = manager.get_or_set("computed_key", expensive_operation)
    print(f"Second call (cached): {result2}")

    print(f"Stats: {manager.stats()}")

    # Test memoization
    print("\n--- Memoization ---")

    @memoize(ttl=5)
    def slow_function(n):
        print(f"  Computing fib({n})...")
        if n < 2:
            return n
        return slow_function(n-1) + slow_function(n-2)

    start = time.time()
    result = slow_function(10)
    print(f"fib(10) = {result}, time: {time.time()-start:.3f}s")

    start = time.time()
    result = slow_function(10)
    print(f"fib(10) cached = {result}, time: {time.time()-start:.6f}s")

    print(f"Cache info: {slow_function.cache_info()}")

    # Cleanup
    import os
    if os.path.exists("test_cache.db"):
        os.remove("test_cache.db")

    print("\nDone!")
