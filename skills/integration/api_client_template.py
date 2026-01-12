"""
API Client Template
===================
Patterns for external API integration.

Use when:
- Consuming external APIs
- Rate limiting needed
- Retry logic required
- Response caching

Placeholders:
- {{BASE_URL}}: API base URL
- {{API_KEY}}: API authentication key
"""

from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import logging
from datetime import datetime, timedelta
import time
import threading
from collections import deque

logger = logging.getLogger(__name__)

T = TypeVar('T')


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


@dataclass
class APIRequest:
    """API request configuration."""
    method: HTTPMethod
    path: str
    params: Dict[str, Any] = field(default_factory=dict)
    data: Optional[Dict[str, Any]] = None
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0


@dataclass
class APIResponse:
    """API response wrapper."""
    status_code: int
    data: Any
    headers: Dict[str, str]
    elapsed_ms: float
    from_cache: bool = False
    request_id: Optional[str] = None


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(
        self,
        requests_per_second: float,
        burst_size: int = 10
    ):
        self.rate = requests_per_second
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_update = time.time()
        self._lock = threading.Lock()

    def acquire(self, timeout: float = 30.0) -> bool:
        """Acquire a token, blocking if necessary."""
        start = time.time()

        while True:
            with self._lock:
                self._refill()

                if self.tokens >= 1:
                    self.tokens -= 1
                    return True

            if time.time() - start > timeout:
                return False

            # Wait for token
            time.sleep(1 / self.rate)

    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(
            self.burst_size,
            self.tokens + elapsed * self.rate
        )
        self.last_update = now


class ResponseCache:
    """Simple response cache."""

    def __init__(self, default_ttl: int = 60):
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get cached response."""
        with self._lock:
            entry = self.cache.get(key)
            if entry:
                if time.time() < entry["expires_at"]:
                    return entry["data"]
                del self.cache[key]
            return None

    def set(self, key: str, data: Any, ttl: Optional[int] = None):
        """Cache a response."""
        ttl = ttl or self.default_ttl
        with self._lock:
            self.cache[key] = {
                "data": data,
                "expires_at": time.time() + ttl,
                "cached_at": time.time()
            }

    def invalidate(self, pattern: Optional[str] = None):
        """Invalidate cache entries."""
        with self._lock:
            if pattern:
                self.cache = {
                    k: v for k, v in self.cache.items()
                    if pattern not in k
                }
            else:
                self.cache.clear()


class RetryStrategy:
    """Retry configuration."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential: bool = True,
        retry_codes: List[int] = None
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential = exponential
        self.retry_codes = retry_codes or [429, 500, 502, 503, 504]

    def should_retry(self, status_code: int, attempt: int) -> bool:
        """Check if should retry."""
        return status_code in self.retry_codes and attempt < self.max_retries

    def get_delay(self, attempt: int) -> float:
        """Get delay for retry attempt."""
        if self.exponential:
            delay = self.base_delay * (2 ** attempt)
        else:
            delay = self.base_delay
        return min(delay, self.max_delay)


class APIClient:
    """
    Base API client with rate limiting and caching.

    Example:
        client = APIClient(
            base_url="https://api.example.com",
            api_key="your-key"
        )

        response = client.get("/users", params={"limit": 10})
        user = client.post("/users", data={"name": "John"})
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        rate_limit: float = 10.0,  # requests per second
        cache_ttl: int = 60,
        retry_strategy: RetryStrategy = None
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.rate_limiter = RateLimiter(rate_limit)
        self.cache = ResponseCache(cache_ttl)
        self.retry_strategy = retry_strategy or RetryStrategy()
        self.request_history: deque = deque(maxlen=1000)

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _make_request(self, request: APIRequest) -> APIResponse:
        """Make HTTP request (placeholder)."""
        # This would use requests/httpx in real implementation
        url = f"{self.base_url}{request.path}"
        start = time.time()

        # Simulate request
        logger.debug(f"{request.method.value} {url}")
        elapsed = (time.time() - start) * 1000

        # Placeholder response
        return APIResponse(
            status_code=200,
            data={"status": "ok"},
            headers={},
            elapsed_ms=elapsed
        )

    def request(
        self,
        method: HTTPMethod,
        path: str,
        params: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        cache: bool = False,
        cache_ttl: int = None
    ) -> APIResponse:
        """Make API request with rate limiting and caching."""
        # Check cache for GET requests
        cache_key = f"{method.value}:{path}:{params}"
        if cache and method == HTTPMethod.GET:
            cached = self.cache.get(cache_key)
            if cached:
                return APIResponse(
                    status_code=200,
                    data=cached,
                    headers={},
                    elapsed_ms=0,
                    from_cache=True
                )

        # Rate limiting
        if not self.rate_limiter.acquire(timeout=30):
            raise Exception("Rate limit exceeded")

        request = APIRequest(
            method=method,
            path=path,
            params=params or {},
            data=data,
            headers={**self._get_headers(), **(headers or {})}
        )

        # Execute with retry
        for attempt in range(self.retry_strategy.max_retries + 1):
            try:
                response = self._make_request(request)

                # Record in history
                self.request_history.append({
                    "method": method.value,
                    "path": path,
                    "status": response.status_code,
                    "elapsed_ms": response.elapsed_ms,
                    "timestamp": datetime.now().isoformat(),
                    "from_cache": response.from_cache
                })

                if response.status_code < 400:
                    # Cache successful GET responses
                    if cache and method == HTTPMethod.GET:
                        self.cache.set(cache_key, response.data, cache_ttl)
                    return response

                # Check retry
                if self.retry_strategy.should_retry(response.status_code, attempt):
                    delay = self.retry_strategy.get_delay(attempt)
                    logger.warning(f"Retry {attempt + 1} after {delay}s")
                    time.sleep(delay)
                    continue

                return response

            except Exception as e:
                if attempt == self.retry_strategy.max_retries:
                    raise
                delay = self.retry_strategy.get_delay(attempt)
                time.sleep(delay)

        raise Exception("Max retries exceeded")

    def get(
        self,
        path: str,
        params: Dict[str, Any] = None,
        cache: bool = True,
        cache_ttl: int = None
    ) -> APIResponse:
        """GET request."""
        return self.request(HTTPMethod.GET, path, params=params, cache=cache, cache_ttl=cache_ttl)

    def post(self, path: str, data: Dict[str, Any] = None) -> APIResponse:
        """POST request."""
        return self.request(HTTPMethod.POST, path, data=data)

    def put(self, path: str, data: Dict[str, Any] = None) -> APIResponse:
        """PUT request."""
        return self.request(HTTPMethod.PUT, path, data=data)

    def delete(self, path: str) -> APIResponse:
        """DELETE request."""
        return self.request(HTTPMethod.DELETE, path)

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        history = list(self.request_history)
        if not history:
            return {"total": 0}

        elapsed_times = [h["elapsed_ms"] for h in history]
        cached = [h for h in history if h["from_cache"]]

        return {
            "total_requests": len(history),
            "cached_requests": len(cached),
            "cache_hit_rate": len(cached) / len(history) * 100 if history else 0,
            "avg_elapsed_ms": sum(elapsed_times) / len(elapsed_times),
            "max_elapsed_ms": max(elapsed_times),
            "by_status": {
                status: len([h for h in history if h["status"] == status])
                for status in set(h["status"] for h in history)
            }
        }


class TradingAPIClient(APIClient):
    """API client specialized for trading services."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        rate_limit: float = 5.0
    ):
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            rate_limit=rate_limit,
            cache_ttl=30
        )

    def get_signal(self, symbol: str) -> Dict[str, Any]:
        """Get trading signal for symbol."""
        response = self.get(f"/signal/{symbol}", cache=True, cache_ttl=60)
        return response.data

    def get_signals_batch(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get signals for multiple symbols."""
        response = self.post("/signals/batch", data={"symbols": symbols})
        return response.data

    def submit_trade(
        self,
        symbol: str,
        direction: str,
        volume: float,
        stop_loss: float,
        take_profit: float
    ) -> Dict[str, Any]:
        """Submit a trade."""
        response = self.post("/trades", data={
            "symbol": symbol,
            "direction": direction,
            "volume": volume,
            "stop_loss": stop_loss,
            "take_profit": take_profit
        })
        return response.data

    def get_positions(self) -> List[Dict[str, Any]]:
        """Get open positions."""
        response = self.get("/positions", cache=True, cache_ttl=5)
        return response.data

    def get_account(self) -> Dict[str, Any]:
        """Get account info."""
        response = self.get("/account", cache=True, cache_ttl=10)
        return response.data


def create_market_data_client(api_key: str) -> APIClient:
    """Create market data API client."""
    return APIClient(
        base_url="https://api.marketdata.example.com",
        api_key=api_key,
        rate_limit=20.0,  # 20 requests per second
        cache_ttl=5  # 5 second cache for price data
    )


# Example usage
if __name__ == "__main__":
    # Create client
    client = TradingAPIClient(
        base_url="http://localhost:5050",
        api_key="test-key"
    )

    # Make requests
    print("Making API requests...")

    # Get signal
    signal = client.get_signal("XAUUSD")
    print(f"Signal: {signal}")

    # Get positions
    positions = client.get_positions()
    print(f"Positions: {positions}")

    # Get stats
    print(f"\nClient Stats: {client.get_stats()}")
