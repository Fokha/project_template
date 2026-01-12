# ═══════════════════════════════════════════════════════════════
# DEDUPLICATION TEMPLATE
# Duplicate prevention patterns for APIs
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Choose dedup backend (memory, SQLite, Redis)
# 3. Apply @deduplicate decorator to endpoints
#
# ═══════════════════════════════════════════════════════════════

import hashlib
import json
import logging
import threading
import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DEDUP BACKENDS
# ═══════════════════════════════════════════════════════════════


class DedupBackend:
    """Base class for deduplication backends."""

    def check_and_set(self, key: str, ttl: int) -> bool:
        """
        Check if key exists, set if not.

        Returns:
            True if this is the first occurrence (not a duplicate)
            False if this is a duplicate
        """
        raise NotImplementedError

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        raise NotImplementedError

    def delete(self, key: str):
        """Delete a key."""
        raise NotImplementedError

    def clear(self):
        """Clear all keys."""
        raise NotImplementedError

    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns count removed."""
        raise NotImplementedError


class MemoryDedupBackend(DedupBackend):
    """In-memory deduplication with TTL."""

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._cache: Dict[str, float] = {}  # key -> expires_at
        self._lock = threading.Lock()

    def check_and_set(self, key: str, ttl: int) -> bool:
        now = time.time()
        expires_at = now + ttl

        with self._lock:
            # Check if exists and not expired
            if key in self._cache:
                if self._cache[key] > now:
                    return False  # Duplicate
                # Expired, remove it
                del self._cache[key]

            # Evict oldest if at capacity
            if len(self._cache) >= self.max_size:
                oldest = min(self._cache, key=self._cache.get)
                del self._cache[oldest]

            # Set new entry
            self._cache[key] = expires_at
            return True  # Not a duplicate

    def exists(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            if key in self._cache:
                if self._cache[key] > now:
                    return True
                del self._cache[key]
            return False

    def delete(self, key: str):
        with self._lock:
            self._cache.pop(key, None)

    def clear(self):
        with self._lock:
            self._cache.clear()

    def cleanup_expired(self) -> int:
        now = time.time()
        with self._lock:
            expired = [k for k, exp in self._cache.items() if exp <= now]
            for key in expired:
                del self._cache[key]
            return len(expired)

    def stats(self) -> Dict:
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
            }


class SQLiteDedupBackend(DedupBackend):
    """SQLite-based deduplication for persistence."""

    def __init__(self, db_path: str = "data/dedup_cache.db"):
        import sqlite3

        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._local = threading.local()

        # Initialize table
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dedup_cache (
                key TEXT PRIMARY KEY,
                expires_at REAL NOT NULL,
                created_at REAL NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_expires ON dedup_cache(expires_at)")
        conn.commit()

    def _get_conn(self):
        import sqlite3
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self._local.conn

    def check_and_set(self, key: str, ttl: int) -> bool:
        now = time.time()
        expires_at = now + ttl
        conn = self._get_conn()

        # Check if exists
        cursor = conn.execute(
            "SELECT expires_at FROM dedup_cache WHERE key = ?",
            (key,)
        )
        row = cursor.fetchone()

        if row:
            if row[0] > now:
                return False  # Duplicate
            # Expired, update it
            conn.execute(
                "UPDATE dedup_cache SET expires_at = ?, created_at = ? WHERE key = ?",
                (expires_at, now, key)
            )
        else:
            # Insert new
            conn.execute(
                "INSERT INTO dedup_cache (key, expires_at, created_at) VALUES (?, ?, ?)",
                (key, expires_at, now)
            )

        conn.commit()
        return True  # Not a duplicate

    def exists(self, key: str) -> bool:
        now = time.time()
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT 1 FROM dedup_cache WHERE key = ? AND expires_at > ?",
            (key, now)
        )
        return cursor.fetchone() is not None

    def delete(self, key: str):
        conn = self._get_conn()
        conn.execute("DELETE FROM dedup_cache WHERE key = ?", (key,))
        conn.commit()

    def clear(self):
        conn = self._get_conn()
        conn.execute("DELETE FROM dedup_cache")
        conn.commit()

    def cleanup_expired(self) -> int:
        now = time.time()
        conn = self._get_conn()
        cursor = conn.execute(
            "DELETE FROM dedup_cache WHERE expires_at <= ?",
            (now,)
        )
        conn.commit()
        return cursor.rowcount


# ═══════════════════════════════════════════════════════════════
# DEDUPLICATION MANAGER
# ═══════════════════════════════════════════════════════════════


class DedupManager:
    """
    Centralized deduplication management.

    Features:
    - Multiple backends (memory, SQLite, Redis)
    - Configurable TTL per category
    - Automatic cleanup
    """

    def __init__(
        self,
        backend: DedupBackend = None,
        default_ttl: int = 60,
        cleanup_interval: int = 300
    ):
        self.backend = backend or MemoryDedupBackend()
        self.default_ttl = default_ttl
        self._cleanup_interval = cleanup_interval
        self._last_cleanup = time.time()

    def is_duplicate(
        self,
        key: str,
        ttl: int = None,
        namespace: str = None
    ) -> bool:
        """
        Check if this is a duplicate.

        Args:
            key: Unique identifier
            ttl: Time-to-live in seconds
            namespace: Optional namespace prefix

        Returns:
            True if duplicate, False if first occurrence
        """
        # Periodic cleanup
        if time.time() - self._last_cleanup > self._cleanup_interval:
            self._cleanup()

        full_key = f"{namespace}:{key}" if namespace else key
        is_first = self.backend.check_and_set(full_key, ttl or self.default_ttl)
        return not is_first

    def generate_key(self, *args, **kwargs) -> str:
        """Generate a dedup key from arguments."""
        data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(data.encode()).hexdigest()

    def clear(self, namespace: str = None):
        """Clear dedup cache (or specific namespace)."""
        if namespace:
            # SQLite backend would need pattern-based deletion
            logger.warning("Namespace-based clearing not fully implemented")
        else:
            self.backend.clear()

    def _cleanup(self):
        """Run cleanup of expired entries."""
        removed = self.backend.cleanup_expired()
        self._last_cleanup = time.time()
        if removed > 0:
            logger.debug(f"Dedup cleanup: removed {removed} expired entries")


# ═══════════════════════════════════════════════════════════════
# FLASK DECORATOR
# ═══════════════════════════════════════════════════════════════


# Global dedup manager (initialize in your app)
_dedup: Optional[DedupManager] = None


def init_dedup(
    app=None,
    backend: DedupBackend = None,
    default_ttl: int = 60
) -> DedupManager:
    """Initialize deduplication for Flask app."""
    global _dedup
    _dedup = DedupManager(backend, default_ttl)
    if app:
        app.extensions['dedup'] = _dedup
    return _dedup


def deduplicate(
    ttl: int = None,
    key_func: Callable = None,
    namespace: str = None,
    on_duplicate: str = "reject"  # reject, ignore, log
):
    """
    Decorator to prevent duplicate requests.

    Args:
        ttl: Time window in seconds
        key_func: Custom function to generate dedup key
        namespace: Dedup namespace
        on_duplicate: Action on duplicate (reject, ignore, log)

    Example:
        @app.route('/api/submit', methods=['POST'])
        @deduplicate(ttl=60, namespace='submit')
        def submit():
            ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            if _dedup is None:
                return f(*args, **kwargs)

            from flask import request, jsonify

            # Generate dedup key
            if key_func:
                key = key_func(request)
            else:
                # Default: hash of method + path + body
                body = request.get_data(as_text=True)
                key = _dedup.generate_key(
                    request.method,
                    request.path,
                    body,
                    request.headers.get('X-Idempotency-Key', '')
                )

            # Check for duplicate
            if _dedup.is_duplicate(key, ttl, namespace):
                logger.warning(f"Duplicate request detected: {key[:16]}...")

                if on_duplicate == "reject":
                    return jsonify({
                        "success": False,
                        "error": "DUPLICATE_REQUEST",
                        "message": "This request has already been processed",
                    }), 409

                elif on_duplicate == "ignore":
                    return jsonify({
                        "success": True,
                        "message": "Request already processed (cached)",
                    }), 200

                # on_duplicate == "log": just log and continue

            return f(*args, **kwargs)
        return decorated
    return decorator


# ═══════════════════════════════════════════════════════════════
# IDEMPOTENCY KEY HANDLER
# ═══════════════════════════════════════════════════════════════


class IdempotencyHandler:
    """
    Handle idempotency keys for safe retries.

    Stores the response for a given idempotency key
    so retried requests return the same response.
    """

    def __init__(self, backend: DedupBackend = None, ttl: int = 3600):
        self.backend = backend or MemoryDedupBackend()
        self.ttl = ttl
        self._responses: Dict[str, Dict] = {}
        self._lock = threading.Lock()

    def check_key(self, idempotency_key: str) -> Optional[Dict]:
        """
        Check if we have a stored response for this key.

        Returns:
            Stored response if exists, None otherwise
        """
        if not idempotency_key:
            return None

        with self._lock:
            if idempotency_key in self._responses:
                entry = self._responses[idempotency_key]
                if entry['expires_at'] > time.time():
                    return entry['response']
                del self._responses[idempotency_key]

        return None

    def store_response(
        self,
        idempotency_key: str,
        response: Dict,
        status_code: int
    ):
        """Store response for future retrieval."""
        if not idempotency_key:
            return

        with self._lock:
            self._responses[idempotency_key] = {
                'response': response,
                'status_code': status_code,
                'expires_at': time.time() + self.ttl,
            }


def idempotent(handler: IdempotencyHandler):
    """
    Decorator for idempotent endpoints.

    Requires X-Idempotency-Key header.

    Example:
        @app.route('/api/payments', methods=['POST'])
        @idempotent(idempotency_handler)
        def create_payment():
            ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            from flask import request, jsonify

            idempotency_key = request.headers.get('X-Idempotency-Key')

            # Check for stored response
            stored = handler.check_key(idempotency_key)
            if stored:
                logger.info(f"Returning cached response for idempotency key: {idempotency_key[:16]}...")
                return jsonify(stored), 200

            # Execute request
            result = f(*args, **kwargs)

            # Store response
            if idempotency_key:
                if isinstance(result, tuple):
                    response_data = result[0].get_json()
                    status_code = result[1] if len(result) > 1 else 200
                else:
                    response_data = result.get_json()
                    status_code = 200

                handler.store_response(idempotency_key, response_data, status_code)

            return result
        return decorated
    return decorator


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("=" * 60)
    print("DEDUPLICATION TEMPLATE DEMO")
    print("=" * 60)

    # Test MemoryDedupBackend
    print("\n--- Memory Backend ---")
    backend = MemoryDedupBackend()

    # First request - not duplicate
    result1 = backend.check_and_set("request_1", ttl=5)
    print(f"First request: is_first={result1}")

    # Second request - duplicate
    result2 = backend.check_and_set("request_1", ttl=5)
    print(f"Second request: is_first={result2}")

    # Different key - not duplicate
    result3 = backend.check_and_set("request_2", ttl=5)
    print(f"Different key: is_first={result3}")

    print(f"Stats: {backend.stats()}")

    # Test DedupManager
    print("\n--- Dedup Manager ---")
    manager = DedupManager(default_ttl=10)

    key = manager.generate_key("POST", "/api/submit", {"amount": 100})
    print(f"Generated key: {key}")

    is_dup1 = manager.is_duplicate(key, namespace="payments")
    print(f"First check: is_duplicate={is_dup1}")

    is_dup2 = manager.is_duplicate(key, namespace="payments")
    print(f"Second check: is_duplicate={is_dup2}")

    # Test SQLite backend
    print("\n--- SQLite Backend ---")
    sql_backend = SQLiteDedupBackend("test_dedup.db")

    sql_backend.check_and_set("sql_key_1", ttl=60)
    print(f"Key exists: {sql_backend.exists('sql_key_1')}")

    # Cleanup
    import os
    if os.path.exists("test_dedup.db"):
        os.remove("test_dedup.db")

    # Flask example
    print("\n--- Flask Integration Example ---")
    print("""
    from flask import Flask
    app = Flask(__name__)

    # Initialize dedup
    init_dedup(app, default_ttl=60)

    @app.route('/api/submit', methods=['POST'])
    @deduplicate(ttl=60, namespace='submit')
    def submit():
        # Process submission
        return jsonify({"success": True})
    """)

    print("\nDone!")
