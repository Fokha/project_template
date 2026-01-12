"""
Fallback & Escalation Pattern Template
======================================
Handle failures gracefully with fallback strategies.

Use when:
- Primary actions may fail
- Graceful degradation needed
- Escalation paths required
- Retry with backoff desired

Placeholders:
- {{MAX_RETRIES}}: Maximum retry attempts
- {{ESCALATION_TIMEOUT}}: Time before escalation
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import logging
from datetime import datetime, timedelta
import time
import random

logger = logging.getLogger(__name__)

T = TypeVar('T')


class FailureType(Enum):
    TIMEOUT = "timeout"
    ERROR = "error"
    INVALID_RESPONSE = "invalid_response"
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"


class EscalationLevel(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ExecutionResult:
    """Result of an execution attempt."""
    success: bool
    result: Any = None
    error: Optional[str] = None
    failure_type: Optional[FailureType] = None
    attempts: int = 0
    duration_ms: float = 0
    fallback_used: Optional[str] = None


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on: List[FailureType] = field(default_factory=lambda: [
        FailureType.TIMEOUT,
        FailureType.ERROR,
        FailureType.RATE_LIMITED
    ])


class FallbackStrategy(ABC):
    """Abstract fallback strategy."""

    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.priority = priority

    @abstractmethod
    def can_handle(self, failure_type: FailureType, context: Dict[str, Any]) -> bool:
        """Check if this strategy can handle the failure."""
        pass

    @abstractmethod
    def execute(self, original_action: Callable, context: Dict[str, Any]) -> Any:
        """Execute fallback strategy."""
        pass


class DefaultValueFallback(FallbackStrategy):
    """Return a default value on failure."""

    def __init__(self, default_value: Any, priority: int = 0):
        super().__init__("default_value", priority)
        self.default_value = default_value

    def can_handle(self, failure_type: FailureType, context: Dict[str, Any]) -> bool:
        return True  # Can always provide default

    def execute(self, original_action: Callable, context: Dict[str, Any]) -> Any:
        return self.default_value


class AlternativeSourceFallback(FallbackStrategy):
    """Try an alternative data source."""

    def __init__(self, alternative_fn: Callable, priority: int = 1):
        super().__init__("alternative_source", priority)
        self.alternative_fn = alternative_fn

    def can_handle(self, failure_type: FailureType, context: Dict[str, Any]) -> bool:
        return failure_type in [
            FailureType.RESOURCE_UNAVAILABLE,
            FailureType.TIMEOUT,
            FailureType.ERROR
        ]

    def execute(self, original_action: Callable, context: Dict[str, Any]) -> Any:
        return self.alternative_fn(context)


class CachedResponseFallback(FallbackStrategy):
    """Return cached response if available."""

    def __init__(self, cache: Dict[str, Any], priority: int = 2):
        super().__init__("cached_response", priority)
        self.cache = cache

    def can_handle(self, failure_type: FailureType, context: Dict[str, Any]) -> bool:
        cache_key = context.get("cache_key", "")
        return cache_key in self.cache

    def execute(self, original_action: Callable, context: Dict[str, Any]) -> Any:
        cache_key = context.get("cache_key", "")
        cached = self.cache.get(cache_key)
        logger.info(f"Using cached response for {cache_key}")
        return cached


class DegradedModeFallback(FallbackStrategy):
    """Provide degraded but functional response."""

    def __init__(self, degraded_fn: Callable, priority: int = 3):
        super().__init__("degraded_mode", priority)
        self.degraded_fn = degraded_fn

    def can_handle(self, failure_type: FailureType, context: Dict[str, Any]) -> bool:
        return True

    def execute(self, original_action: Callable, context: Dict[str, Any]) -> Any:
        logger.warning("Operating in degraded mode")
        return self.degraded_fn(context)


class RetryExecutor:
    """Execute with retry logic."""

    def __init__(self, config: RetryConfig):
        self.config = config

    def execute(
        self,
        action: Callable[[], T],
        context: Dict[str, Any] = None
    ) -> Tuple[bool, T, int, Optional[FailureType]]:
        """Execute action with retries."""
        context = context or {}
        last_error = None
        last_failure_type = None

        for attempt in range(self.config.max_retries + 1):
            try:
                result = action()
                return True, result, attempt + 1, None

            except TimeoutError:
                last_failure_type = FailureType.TIMEOUT
                last_error = "Timeout"
            except ConnectionError:
                last_failure_type = FailureType.RESOURCE_UNAVAILABLE
                last_error = "Connection failed"
            except Exception as e:
                last_failure_type = FailureType.ERROR
                last_error = str(e)

            # Check if we should retry this type of failure
            if last_failure_type not in self.config.retry_on:
                break

            # Calculate delay for next retry
            if attempt < self.config.max_retries:
                delay = self._calculate_delay(attempt)
                logger.info(f"Retry {attempt + 1}/{self.config.max_retries} after {delay:.1f}s")
                time.sleep(delay)

        return False, last_error, self.config.max_retries + 1, last_failure_type

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff."""
        delay = self.config.base_delay * (self.config.exponential_base ** attempt)
        delay = min(delay, self.config.max_delay)

        if self.config.jitter:
            delay = delay * (0.5 + random.random())

        return delay


class Escalator:
    """Handle escalation of failures."""

    def __init__(self):
        self.handlers: Dict[EscalationLevel, List[Callable]] = {
            level: [] for level in EscalationLevel
        }
        self.escalation_history: List[Dict[str, Any]] = []

    def register_handler(
        self,
        level: EscalationLevel,
        handler: Callable[[Dict[str, Any]], None]
    ):
        """Register an escalation handler."""
        self.handlers[level].append(handler)

    def escalate(
        self,
        level: EscalationLevel,
        context: Dict[str, Any],
        failure_info: Dict[str, Any]
    ):
        """Escalate a failure."""
        escalation = {
            "level": level.name,
            "context": context,
            "failure": failure_info,
            "timestamp": datetime.now().isoformat()
        }
        self.escalation_history.append(escalation)

        logger.warning(f"Escalating to level {level.name}: {failure_info.get('error', 'Unknown')}")

        for handler in self.handlers[level]:
            try:
                handler(escalation)
            except Exception as e:
                logger.error(f"Escalation handler failed: {e}")


class FallbackChain:
    """
    Chain of fallback strategies with retry and escalation.

    Example:
        chain = FallbackChain()
        chain.add_fallback(CachedResponseFallback(cache))
        chain.add_fallback(AlternativeSourceFallback(alt_fn))
        chain.add_fallback(DefaultValueFallback({"status": "unknown"}))

        result = chain.execute(primary_action, context)
    """

    def __init__(
        self,
        retry_config: RetryConfig = None,
        escalator: Optional[Escalator] = None
    ):
        self.fallbacks: List[FallbackStrategy] = []
        self.retry_executor = RetryExecutor(retry_config or RetryConfig())
        self.escalator = escalator
        self.execution_log: List[ExecutionResult] = []

    def add_fallback(self, strategy: FallbackStrategy) -> "FallbackChain":
        """Add a fallback strategy."""
        self.fallbacks.append(strategy)
        self.fallbacks.sort(key=lambda s: s.priority)
        return self

    def execute(
        self,
        action: Callable,
        context: Dict[str, Any] = None
    ) -> ExecutionResult:
        """Execute action with fallbacks."""
        context = context or {}
        start_time = time.time()

        # Try primary action with retries
        success, result, attempts, failure_type = self.retry_executor.execute(
            action, context
        )

        if success:
            return ExecutionResult(
                success=True,
                result=result,
                attempts=attempts,
                duration_ms=(time.time() - start_time) * 1000
            )

        # Primary failed, try fallbacks
        logger.warning(f"Primary action failed after {attempts} attempts: {result}")

        for fallback in self.fallbacks:
            if fallback.can_handle(failure_type, context):
                try:
                    fallback_result = fallback.execute(action, context)
                    return ExecutionResult(
                        success=True,
                        result=fallback_result,
                        attempts=attempts,
                        duration_ms=(time.time() - start_time) * 1000,
                        fallback_used=fallback.name
                    )
                except Exception as e:
                    logger.warning(f"Fallback {fallback.name} failed: {e}")
                    continue

        # All fallbacks failed, escalate
        if self.escalator:
            self.escalator.escalate(
                EscalationLevel.HIGH,
                context,
                {"error": result, "failure_type": failure_type.value if failure_type else "unknown"}
            )

        return ExecutionResult(
            success=False,
            error=str(result),
            failure_type=failure_type,
            attempts=attempts,
            duration_ms=(time.time() - start_time) * 1000
        )


class TradingFallbackChain(FallbackChain):
    """Fallback chain specialized for trading operations."""

    def __init__(self, cache: Dict[str, Any] = None):
        super().__init__(
            retry_config=RetryConfig(
                max_retries=3,
                base_delay=0.5,
                max_delay=10.0
            )
        )
        self.cache = cache or {}

        # Add trading-specific fallbacks
        self.add_fallback(CachedResponseFallback(self.cache, priority=1))
        self.add_fallback(DefaultValueFallback(
            {"signal": "NEUTRAL", "confidence": 0, "reason": "Fallback - no signal"},
            priority=10
        ))

    def with_alternative_source(self, alt_fn: Callable) -> "TradingFallbackChain":
        """Add an alternative data source."""
        self.add_fallback(AlternativeSourceFallback(alt_fn, priority=2))
        return self


class CircuitBreaker:
    """
    Circuit breaker pattern for preventing cascade failures.

    States:
    - CLOSED: Normal operation
    - OPEN: Failing fast, not attempting actions
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"
        self.half_open_calls = 0

    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":
            # Check if recovery timeout passed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    self.half_open_calls = 0
                    return True
            return False

        if self.state == "HALF_OPEN":
            return self.half_open_calls < self.half_open_max_calls

        return True

    def record_success(self):
        """Record a successful execution."""
        if self.state == "HALF_OPEN":
            self.half_open_calls += 1
            if self.half_open_calls >= self.half_open_max_calls:
                # Recovered
                self.state = "CLOSED"
                self.failures = 0
                logger.info("Circuit breaker CLOSED - service recovered")
        else:
            self.failures = 0

    def record_failure(self):
        """Record a failed execution."""
        self.failures += 1
        self.last_failure_time = datetime.now()

        if self.state == "HALF_OPEN":
            # Failed during recovery test
            self.state = "OPEN"
            logger.warning("Circuit breaker OPEN - recovery failed")
        elif self.failures >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker OPEN after {self.failures} failures")


def with_fallback(
    fallback_value: Any,
    max_retries: int = 3,
    log_errors: bool = True
):
    """Decorator for adding fallback to functions."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if log_errors:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        if log_errors:
                            logger.error(f"All attempts failed, using fallback")
                        return fallback_value
            return fallback_value
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    # Simulated flaky API call
    call_count = [0]

    def flaky_api_call():
        call_count[0] += 1
        if call_count[0] < 3:
            raise ConnectionError("Service unavailable")
        return {"signal": "BUY", "confidence": 0.85}

    # Create fallback chain
    cache = {"XAUUSD": {"signal": "HOLD", "confidence": 0.5, "cached": True}}

    chain = TradingFallbackChain(cache)
    chain.with_alternative_source(
        lambda ctx: {"signal": "NEUTRAL", "confidence": 0.3, "source": "alternative"}
    )

    # Execute with fallbacks
    result = chain.execute(flaky_api_call, {"cache_key": "XAUUSD"})

    print(f"Success: {result.success}")
    print(f"Result: {result.result}")
    print(f"Attempts: {result.attempts}")
    print(f"Fallback Used: {result.fallback_used}")
    print(f"Duration: {result.duration_ms:.1f}ms")
