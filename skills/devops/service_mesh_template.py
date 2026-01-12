"""
Service Mesh & Resilience Template
==================================
Patterns for service-to-service communication and resilience.

Use when:
- Microservices communication needed
- Service discovery required
- Circuit breakers needed
- Load balancing required

Placeholders:
- {{SERVICE_TIMEOUT}}: Default service timeout
- {{RETRY_ATTEMPTS}}: Default retry attempts
"""

from typing import Any, Callable, Dict, List, Optional, TypeVar
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime, timedelta
import logging
import time
import random
import threading
from collections import deque

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration."""
    name: str
    host: str
    port: int
    weight: int = 100
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_check: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


@dataclass
class ServiceCall:
    """Record of a service call."""
    service: str
    endpoint: str
    method: str
    status_code: int
    duration_ms: float
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None


class ServiceRegistry:
    """Service registry for service discovery."""

    def __init__(self):
        self.services: Dict[str, List[ServiceEndpoint]] = {}
        self._lock = threading.Lock()

    def register(self, service_name: str, endpoint: ServiceEndpoint):
        """Register a service endpoint."""
        with self._lock:
            if service_name not in self.services:
                self.services[service_name] = []
            self.services[service_name].append(endpoint)
            logger.info(f"Registered {service_name} at {endpoint.url}")

    def deregister(self, service_name: str, endpoint: ServiceEndpoint):
        """Deregister a service endpoint."""
        with self._lock:
            if service_name in self.services:
                self.services[service_name] = [
                    e for e in self.services[service_name]
                    if e.url != endpoint.url
                ]

    def get_endpoints(self, service_name: str) -> List[ServiceEndpoint]:
        """Get all endpoints for a service."""
        with self._lock:
            return self.services.get(service_name, []).copy()

    def get_healthy_endpoints(self, service_name: str) -> List[ServiceEndpoint]:
        """Get healthy endpoints for a service."""
        endpoints = self.get_endpoints(service_name)
        return [e for e in endpoints if e.status == ServiceStatus.HEALTHY]


class LoadBalancer(ABC):
    """Abstract load balancer."""

    @abstractmethod
    def select(self, endpoints: List[ServiceEndpoint]) -> Optional[ServiceEndpoint]:
        """Select an endpoint."""
        pass


class RoundRobinBalancer(LoadBalancer):
    """Round-robin load balancer."""

    def __init__(self):
        self._counters: Dict[str, int] = {}
        self._lock = threading.Lock()

    def select(self, endpoints: List[ServiceEndpoint]) -> Optional[ServiceEndpoint]:
        if not endpoints:
            return None

        key = ",".join(e.url for e in endpoints)

        with self._lock:
            if key not in self._counters:
                self._counters[key] = 0

            index = self._counters[key] % len(endpoints)
            self._counters[key] += 1

        return endpoints[index]


class WeightedBalancer(LoadBalancer):
    """Weighted load balancer."""

    def select(self, endpoints: List[ServiceEndpoint]) -> Optional[ServiceEndpoint]:
        if not endpoints:
            return None

        total_weight = sum(e.weight for e in endpoints)
        if total_weight == 0:
            return random.choice(endpoints)

        r = random.randint(1, total_weight)
        cumulative = 0

        for endpoint in endpoints:
            cumulative += endpoint.weight
            if r <= cumulative:
                return endpoint

        return endpoints[-1]


class CircuitBreaker:
    """Circuit breaker for service resilience."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self.state = CircuitState.CLOSED
        self.failures = 0
        self.successes = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
        self._lock = threading.Lock()

    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True

            if self.state == CircuitState.OPEN:
                if self.last_failure_time:
                    elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                    if elapsed >= self.recovery_timeout:
                        self.state = CircuitState.HALF_OPEN
                        self.half_open_calls = 0
                        return True
                return False

            if self.state == CircuitState.HALF_OPEN:
                return self.half_open_calls < self.half_open_max_calls

            return True

    def record_success(self):
        """Record successful call."""
        with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.successes += 1
                if self.successes >= self.half_open_max_calls:
                    self.state = CircuitState.CLOSED
                    self.failures = 0
                    self.successes = 0
                    logger.info("Circuit breaker CLOSED")
            else:
                self.failures = 0

    def record_failure(self):
        """Record failed call."""
        with self._lock:
            self.failures += 1
            self.last_failure_time = datetime.now()

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                logger.warning("Circuit breaker OPEN (recovery failed)")
            elif self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(f"Circuit breaker OPEN after {self.failures} failures")


class RetryPolicy:
    """Retry policy configuration."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential: bool = True,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential = exponential
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Get delay for retry attempt."""
        if self.exponential:
            delay = self.base_delay * (2 ** attempt)
        else:
            delay = self.base_delay

        delay = min(delay, self.max_delay)

        if self.jitter:
            delay = delay * (0.5 + random.random())

        return delay


class ServiceClient:
    """
    Resilient service client.

    Example:
        registry = ServiceRegistry()
        registry.register("api", ServiceEndpoint("api", "localhost", 5050))

        client = ServiceClient(registry)
        result = client.call("api", "/health")
    """

    def __init__(
        self,
        registry: ServiceRegistry,
        load_balancer: LoadBalancer = None,
        retry_policy: RetryPolicy = None,
        timeout: float = 30.0
    ):
        self.registry = registry
        self.load_balancer = load_balancer or RoundRobinBalancer()
        self.retry_policy = retry_policy or RetryPolicy()
        self.timeout = timeout

        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.call_history: deque = deque(maxlen=1000)
        self._lock = threading.Lock()

    def call(
        self,
        service_name: str,
        path: str,
        method: str = "GET",
        data: Any = None,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Call a service with resilience."""
        # Get circuit breaker for service
        circuit = self._get_circuit_breaker(service_name)

        if not circuit.can_execute():
            raise Exception(f"Circuit breaker OPEN for {service_name}")

        # Get endpoints
        endpoints = self.registry.get_healthy_endpoints(service_name)
        if not endpoints:
            endpoints = self.registry.get_endpoints(service_name)

        if not endpoints:
            raise Exception(f"No endpoints for service: {service_name}")

        last_error = None

        for attempt in range(self.retry_policy.max_retries + 1):
            endpoint = self.load_balancer.select(endpoints)
            if not endpoint:
                raise Exception("No endpoint selected")

            start_time = time.time()

            try:
                # Simulate HTTP call (replace with actual HTTP client)
                result = self._http_call(endpoint, path, method, data, headers)

                duration_ms = (time.time() - start_time) * 1000
                circuit.record_success()

                self._record_call(ServiceCall(
                    service=service_name,
                    endpoint=endpoint.url,
                    method=method,
                    status_code=200,
                    duration_ms=duration_ms,
                    success=True
                ))

                return result

            except Exception as e:
                last_error = e
                duration_ms = (time.time() - start_time) * 1000

                self._record_call(ServiceCall(
                    service=service_name,
                    endpoint=endpoint.url,
                    method=method,
                    status_code=500,
                    duration_ms=duration_ms,
                    success=False,
                    error=str(e)
                ))

                if attempt < self.retry_policy.max_retries:
                    delay = self.retry_policy.get_delay(attempt)
                    logger.warning(f"Retry {attempt + 1} for {service_name} after {delay:.1f}s")
                    time.sleep(delay)

        # All retries failed
        circuit.record_failure()
        raise Exception(f"Service call failed after {self.retry_policy.max_retries + 1} attempts: {last_error}")

    def _get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service."""
        with self._lock:
            if service_name not in self.circuit_breakers:
                self.circuit_breakers[service_name] = CircuitBreaker()
            return self.circuit_breakers[service_name]

    def _http_call(
        self,
        endpoint: ServiceEndpoint,
        path: str,
        method: str,
        data: Any,
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Make HTTP call (placeholder)."""
        # In real implementation, use requests or httpx
        url = f"{endpoint.url}{path}"

        # Simulate call
        if random.random() < 0.1:  # 10% failure rate for demo
            raise ConnectionError("Connection refused")

        return {"status": "ok", "url": url}

    def _record_call(self, call: ServiceCall):
        """Record service call."""
        self.call_history.append(call)

    def get_stats(self, service_name: str = None) -> Dict[str, Any]:
        """Get call statistics."""
        calls = list(self.call_history)

        if service_name:
            calls = [c for c in calls if c.service == service_name]

        if not calls:
            return {"total": 0}

        successful = [c for c in calls if c.success]
        durations = [c.duration_ms for c in calls]

        return {
            "total": len(calls),
            "successful": len(successful),
            "failed": len(calls) - len(successful),
            "success_rate": len(successful) / len(calls) * 100,
            "avg_duration_ms": sum(durations) / len(durations),
            "max_duration_ms": max(durations),
            "min_duration_ms": min(durations)
        }


def create_trading_service_mesh() -> tuple:
    """Create service mesh for trading system."""
    registry = ServiceRegistry()

    # Register services
    registry.register("api", ServiceEndpoint(
        name="api-1",
        host="localhost",
        port=5050,
        weight=100,
        status=ServiceStatus.HEALTHY
    ))

    registry.register("websocket", ServiceEndpoint(
        name="ws-1",
        host="localhost",
        port=8765,
        weight=100,
        status=ServiceStatus.HEALTHY
    ))

    # Create client with resilience
    client = ServiceClient(
        registry,
        load_balancer=WeightedBalancer(),
        retry_policy=RetryPolicy(max_retries=3, base_delay=0.5)
    )

    return registry, client


# Example usage
if __name__ == "__main__":
    registry, client = create_trading_service_mesh()

    # Make calls
    print("Making service calls...")
    print("-" * 50)

    for i in range(10):
        try:
            result = client.call("api", "/health")
            print(f"Call {i+1}: SUCCESS")
        except Exception as e:
            print(f"Call {i+1}: FAILED - {e}")

    # Get stats
    print("\nService Statistics:")
    print("-" * 50)
    stats = client.get_stats("api")
    print(f"Total calls: {stats['total']}")
    print(f"Success rate: {stats.get('success_rate', 0):.1f}%")
    print(f"Avg duration: {stats.get('avg_duration_ms', 0):.1f}ms")
