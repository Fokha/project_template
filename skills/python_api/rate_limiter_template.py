"""
Rate Limiter Template
=====================

Token bucket rate limiting with Redis or in-memory storage.

Usage:
    from services.rate_limiter import RateLimiter

    limiter = RateLimiter(requests_per_minute=60)

    if limiter.is_allowed('user_123'):
        # Process request
    else:
        # Return 429 Too Many Requests

Features:
- Token bucket algorithm
- Per-user/per-IP limiting
- Redis or in-memory backend
- Configurable windows
- Burst allowance
"""

import time
import threading
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests_per_second: float = 10
    requests_per_minute: float = 100
    requests_per_hour: float = 1000
    burst_size: int = 20  # Max burst allowance


@dataclass
class TokenBucket:
    """Token bucket state."""
    tokens: float
    last_update: float
    request_count: int = 0


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(
        self,
        requests_per_minute: float = 60,
        burst_size: int = 10,
        redis_client=None
    ):
        self.rate = requests_per_minute / 60  # tokens per second
        self.burst_size = burst_size
        self.redis = redis_client

        # In-memory storage (fallback)
        self._buckets: Dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def _get_bucket(self, key: str) -> TokenBucket:
        """Get or create token bucket for key."""
        if key not in self._buckets:
            self._buckets[key] = TokenBucket(
                tokens=self.burst_size,
                last_update=time.time()
            )
        return self._buckets[key]

    def _refill_tokens(self, bucket: TokenBucket) -> float:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - bucket.last_update

        # Add tokens based on time elapsed
        new_tokens = bucket.tokens + (elapsed * self.rate)

        # Cap at burst size
        bucket.tokens = min(new_tokens, self.burst_size)
        bucket.last_update = now

        return bucket.tokens

    def is_allowed(self, key: str, tokens_required: int = 1) -> bool:
        """Check if request is allowed."""
        if self.redis:
            return self._is_allowed_redis(key, tokens_required)
        return self._is_allowed_memory(key, tokens_required)

    def _is_allowed_memory(self, key: str, tokens_required: int) -> bool:
        """Check rate limit using in-memory storage."""
        with self._lock:
            bucket = self._get_bucket(key)
            self._refill_tokens(bucket)

            if bucket.tokens >= tokens_required:
                bucket.tokens -= tokens_required
                bucket.request_count += 1
                return True

            return False

    def _is_allowed_redis(self, key: str, tokens_required: int) -> bool:
        """Check rate limit using Redis."""
        redis_key = f"ratelimit:{key}"
        now = time.time()

        pipe = self.redis.pipeline()

        # Get current state
        pipe.hgetall(redis_key)
        result = pipe.execute()[0]

        if result:
            tokens = float(result.get(b'tokens', self.burst_size))
            last_update = float(result.get(b'last_update', now))

            # Refill tokens
            elapsed = now - last_update
            tokens = min(tokens + (elapsed * self.rate), self.burst_size)
        else:
            tokens = self.burst_size
            last_update = now

        # Check and consume
        if tokens >= tokens_required:
            tokens -= tokens_required

            # Update Redis
            pipe = self.redis.pipeline()
            pipe.hset(redis_key, mapping={
                'tokens': tokens,
                'last_update': now
            })
            pipe.expire(redis_key, 3600)  # 1 hour TTL
            pipe.execute()

            return True

        return False

    def get_remaining(self, key: str) -> Tuple[int, float]:
        """Get remaining tokens and reset time."""
        with self._lock:
            bucket = self._get_bucket(key)
            self._refill_tokens(bucket)

            # Time until next token
            if bucket.tokens < 1:
                reset_time = (1 - bucket.tokens) / self.rate
            else:
                reset_time = 0

            return int(bucket.tokens), reset_time

    def get_stats(self, key: str) -> Dict:
        """Get rate limit stats for a key."""
        remaining, reset_time = self.get_remaining(key)
        bucket = self._buckets.get(key)

        return {
            'remaining': remaining,
            'limit': self.burst_size,
            'reset_seconds': round(reset_time, 2),
            'total_requests': bucket.request_count if bucket else 0
        }

    def reset(self, key: str):
        """Reset rate limit for a key."""
        with self._lock:
            if key in self._buckets:
                del self._buckets[key]

    def cleanup_expired(self, max_age_seconds: int = 3600):
        """Remove old bucket entries."""
        now = time.time()
        with self._lock:
            expired = [
                key for key, bucket in self._buckets.items()
                if now - bucket.last_update > max_age_seconds
            ]
            for key in expired:
                del self._buckets[key]


class SlidingWindowLimiter:
    """Sliding window rate limiter (more accurate)."""

    def __init__(self, requests_per_minute: int = 60):
        self.limit = requests_per_minute
        self.window_seconds = 60
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed."""
        now = time.time()
        window_start = now - self.window_seconds

        with self._lock:
            # Remove old requests
            self._requests[key] = [
                t for t in self._requests[key]
                if t > window_start
            ]

            # Check limit
            if len(self._requests[key]) < self.limit:
                self._requests[key].append(now)
                return True

            return False

    def get_remaining(self, key: str) -> int:
        """Get remaining requests in current window."""
        now = time.time()
        window_start = now - self.window_seconds

        with self._lock:
            current = len([t for t in self._requests[key] if t > window_start])
            return max(0, self.limit - current)


# Flask decorator
def rate_limit(limiter: RateLimiter, key_func=None, tokens: int = 1):
    """Flask decorator for rate limiting."""
    from functools import wraps

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify

            # Get key (default: IP address)
            if key_func:
                key = key_func()
            else:
                key = request.remote_addr

            if not limiter.is_allowed(key, tokens):
                remaining, reset = limiter.get_remaining(key)
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': reset
                }), 429, {
                    'X-RateLimit-Remaining': str(remaining),
                    'X-RateLimit-Reset': str(int(reset)),
                    'Retry-After': str(int(reset))
                }

            # Add rate limit headers
            response = f(*args, **kwargs)
            remaining, _ = limiter.get_remaining(key)

            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(limiter.burst_size)
                response.headers['X-RateLimit-Remaining'] = str(remaining)

            return response

        return decorated_function
    return decorator


# Example usage
if __name__ == "__main__":
    # Token bucket limiter
    limiter = RateLimiter(requests_per_minute=10, burst_size=5)

    print("=== Token Bucket Rate Limiter ===")
    for i in range(15):
        allowed = limiter.is_allowed('user_1')
        stats = limiter.get_stats('user_1')
        print(f"Request {i+1}: {'Allowed' if allowed else 'Blocked'} | Remaining: {stats['remaining']}")
        time.sleep(0.1)

    print("\n=== Sliding Window Rate Limiter ===")
    sliding = SlidingWindowLimiter(requests_per_minute=5)

    for i in range(10):
        allowed = sliding.is_allowed('user_2')
        remaining = sliding.get_remaining('user_2')
        print(f"Request {i+1}: {'Allowed' if allowed else 'Blocked'} | Remaining: {remaining}")
