# ═══════════════════════════════════════════════════════════════
# DEDUPLICATION CACHE TEMPLATE
# Prevent duplicate messages across distributed systems
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Initialize with SQLite or Redis backend
# 3. Use is_duplicate() before processing messages
#
# ═══════════════════════════════════════════════════════════════

import sqlite3
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
from contextlib import contextmanager
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# TTL CONFIGURATION
# ═══════════════════════════════════════════════════════════════


class DedupTTL:
    """TTL settings for different message types."""
    SIGNAL = 300        # 5 minutes - trading signals
    NOTIFICATION = 60   # 1 minute - Telegram/Discord messages
    WEBHOOK = 30        # 30 seconds - webhook triggers
    TRADE = 600         # 10 minutes - trade events
    DEFAULT = 120       # 2 minutes - fallback


# ═══════════════════════════════════════════════════════════════
# SQLITE DEDUP CACHE
# ═══════════════════════════════════════════════════════════════


class SQLiteDedupCache:
    """
    SQLite-based deduplication cache.

    Works across multiple processes (gunicorn workers).
    Self-cleaning with TTL expiration.
    """

    def __init__(self, db_path: str = "data/dedup_cache.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dedup_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_type TEXT NOT NULL,
                    key_hash TEXT NOT NULL,
                    key_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    metadata TEXT,
                    UNIQUE(cache_type, key_hash)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_dedup_expires
                ON dedup_cache(expires_at)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_dedup_type_hash
                ON dedup_cache(cache_type, key_hash)
            """)
            conn.commit()
            logger.info(f"Dedup cache initialized: {self.db_path}")

    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager."""
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=30.0,
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def is_duplicate(
        self,
        key: str,
        cache_type: str = "default",
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        Check if message is duplicate.

        If not duplicate, registers it and returns False.
        If duplicate, returns True.

        Args:
            key: Unique message identifier
            cache_type: Type of message (signal, notification, etc.)
            ttl_seconds: Custom TTL (uses default if not specified)

        Returns:
            True if duplicate, False if new
        """
        key_hash = self._hash_key(key)
        ttl = ttl_seconds or self._get_ttl(cache_type)
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)

        with self._lock:
            with self._get_connection() as conn:
                # Check for existing non-expired entry
                existing = conn.execute("""
                    SELECT id FROM dedup_cache
                    WHERE cache_type = ? AND key_hash = ? AND expires_at > ?
                """, (cache_type, key_hash, datetime.utcnow())).fetchone()

                if existing:
                    logger.debug(f"Duplicate found: {cache_type}/{key[:50]}")
                    return True

                # Insert new entry (or update if exists but expired)
                conn.execute("""
                    INSERT OR REPLACE INTO dedup_cache
                    (cache_type, key_hash, key_value, expires_at)
                    VALUES (?, ?, ?, ?)
                """, (cache_type, key_hash, key[:200], expires_at))
                conn.commit()

                logger.debug(f"Registered: {cache_type}/{key[:50]} (TTL: {ttl}s)")
                return False

    def check_only(self, key: str, cache_type: str = "default") -> bool:
        """
        Check if duplicate WITHOUT registering.

        Use this for read-only checks.
        """
        key_hash = self._hash_key(key)

        with self._get_connection() as conn:
            existing = conn.execute("""
                SELECT id FROM dedup_cache
                WHERE cache_type = ? AND key_hash = ? AND expires_at > ?
            """, (cache_type, key_hash, datetime.utcnow())).fetchone()

            return existing is not None

    def register(
        self,
        key: str,
        cache_type: str = "default",
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Explicitly register a key without checking.

        Use after successfully processing a message.
        """
        key_hash = self._hash_key(key)
        ttl = ttl_seconds or self._get_ttl(cache_type)
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        meta_json = json.dumps(metadata) if metadata else None

        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO dedup_cache
                (cache_type, key_hash, key_value, expires_at, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (cache_type, key_hash, key[:200], expires_at, meta_json))
            conn.commit()

    def clear(self, cache_type: Optional[str] = None):
        """Clear cache entries."""
        with self._get_connection() as conn:
            if cache_type:
                conn.execute(
                    "DELETE FROM dedup_cache WHERE cache_type = ?",
                    (cache_type,)
                )
            else:
                conn.execute("DELETE FROM dedup_cache")
            conn.commit()
            logger.info(f"Cache cleared: {cache_type or 'all'}")

    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns count removed."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM dedup_cache WHERE expires_at < ?",
                (datetime.utcnow(),)
            )
            conn.commit()
            count = cursor.rowcount
            if count > 0:
                logger.info(f"Cleaned up {count} expired entries")
            return count

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._get_connection() as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM dedup_cache WHERE expires_at > ?",
                (datetime.utcnow(),)
            ).fetchone()[0]

            by_type = conn.execute("""
                SELECT cache_type, COUNT(*) as count
                FROM dedup_cache
                WHERE expires_at > ?
                GROUP BY cache_type
            """, (datetime.utcnow(),)).fetchall()

            return {
                "total_entries": total,
                "by_type": {row["cache_type"]: row["count"] for row in by_type},
                "database_path": str(self.db_path),
            }

    def _hash_key(self, key: str) -> str:
        """Generate hash for key."""
        return hashlib.sha256(key.encode()).hexdigest()

    def _get_ttl(self, cache_type: str) -> int:
        """Get TTL for cache type."""
        return getattr(DedupTTL, cache_type.upper(), DedupTTL.DEFAULT)


# ═══════════════════════════════════════════════════════════════
# SIGNAL DEDUPLICATION HELPER
# ═══════════════════════════════════════════════════════════════


class SignalDeduplicator:
    """
    Specialized deduplicator for trading signals.

    Creates keys from: symbol + direction + timestamp_window
    """

    def __init__(self, cache: SQLiteDedupCache, window_minutes: int = 5):
        self.cache = cache
        self.window_minutes = window_minutes

    def is_duplicate_signal(
        self,
        symbol: str,
        direction: str,
        confidence: Optional[float] = None
    ) -> bool:
        """
        Check if trading signal is duplicate.

        Signals within the same time window for same symbol/direction
        are considered duplicates.
        """
        # Create time window key
        now = datetime.utcnow()
        window = now.replace(
            minute=(now.minute // self.window_minutes) * self.window_minutes,
            second=0,
            microsecond=0
        )

        key = f"{symbol}_{direction}_{window.isoformat()}"

        return self.cache.is_duplicate(
            key=key,
            cache_type="signal",
            ttl_seconds=DedupTTL.SIGNAL
        )

    def is_duplicate_notification(
        self,
        message: str,
        channel: str = "default"
    ) -> bool:
        """Check if notification is duplicate."""
        key = f"{channel}_{message}"

        return self.cache.is_duplicate(
            key=key,
            cache_type="notification",
            ttl_seconds=DedupTTL.NOTIFICATION
        )


# ═══════════════════════════════════════════════════════════════
# FLASK INTEGRATION
# ═══════════════════════════════════════════════════════════════


def create_dedup_routes(app, cache: SQLiteDedupCache):
    """Add dedup cache endpoints to Flask app."""
    from flask import jsonify

    @app.route('/dedup/status', methods=['GET'])
    def dedup_status():
        return jsonify({
            'success': True,
            'stats': cache.get_stats(),
        })

    @app.route('/dedup/clear', methods=['POST'])
    def dedup_clear():
        cache.clear()
        return jsonify({
            'success': True,
            'message': 'Cache cleared',
        })

    @app.route('/dedup/cleanup', methods=['POST'])
    def dedup_cleanup():
        count = cache.cleanup_expired()
        return jsonify({
            'success': True,
            'removed': count,
        })


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    # Initialize cache
    cache = SQLiteDedupCache("data/dedup_cache.db")

    # Create signal deduplicator
    dedup = SignalDeduplicator(cache)

    # Test signal deduplication
    print("\n=== Signal Deduplication Test ===")

    # First signal - should NOT be duplicate
    result1 = dedup.is_duplicate_signal("XAUUSD", "BUY", 0.85)
    print(f"First XAUUSD BUY: is_duplicate = {result1}")  # False

    # Same signal again - should BE duplicate
    result2 = dedup.is_duplicate_signal("XAUUSD", "BUY", 0.90)
    print(f"Second XAUUSD BUY: is_duplicate = {result2}")  # True

    # Different direction - should NOT be duplicate
    result3 = dedup.is_duplicate_signal("XAUUSD", "SELL", 0.75)
    print(f"XAUUSD SELL: is_duplicate = {result3}")  # False

    # Different symbol - should NOT be duplicate
    result4 = dedup.is_duplicate_signal("US30", "BUY", 0.80)
    print(f"US30 BUY: is_duplicate = {result4}")  # False

    # Print stats
    print("\n=== Cache Stats ===")
    stats = cache.get_stats()
    print(f"Total entries: {stats['total_entries']}")
    print(f"By type: {stats['by_type']}")
