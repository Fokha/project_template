"""
Webhook Handler Template
========================
Patterns for webhook handling and processing.

Use when:
- Receiving external webhooks
- Event-driven integrations
- Third-party service callbacks
- Asynchronous notifications

Placeholders:
- {{WEBHOOK_SECRET}}: Webhook verification secret
- {{MAX_PAYLOAD_SIZE}}: Maximum payload size
"""

from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import logging
from datetime import datetime
import hashlib
import hmac
import json
import time
from collections import deque

logger = logging.getLogger(__name__)


class WebhookStatus(Enum):
    RECEIVED = "received"
    VALIDATED = "validated"
    PROCESSED = "processed"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass
class WebhookPayload:
    """Incoming webhook payload."""
    id: str
    source: str
    event_type: str
    data: Dict[str, Any]
    headers: Dict[str, str]
    timestamp: datetime = field(default_factory=datetime.now)
    raw_body: bytes = b""
    status: WebhookStatus = WebhookStatus.RECEIVED


@dataclass
class WebhookResult:
    """Result of webhook processing."""
    payload_id: str
    success: bool
    status: WebhookStatus
    response_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_ms: float = 0


class WebhookValidator(ABC):
    """Abstract webhook validator."""

    @abstractmethod
    def validate(self, payload: WebhookPayload) -> bool:
        """Validate webhook payload."""
        pass


class SignatureValidator(WebhookValidator):
    """HMAC signature validator."""

    def __init__(
        self,
        secret: str,
        header_name: str = "X-Signature",
        algorithm: str = "sha256"
    ):
        self.secret = secret.encode()
        self.header_name = header_name
        self.algorithm = algorithm

    def validate(self, payload: WebhookPayload) -> bool:
        """Validate HMAC signature."""
        signature = payload.headers.get(self.header_name)
        if not signature:
            logger.warning("Missing signature header")
            return False

        # Compute expected signature
        expected = hmac.new(
            self.secret,
            payload.raw_body,
            getattr(hashlib, self.algorithm)
        ).hexdigest()

        # Handle various signature formats
        if signature.startswith(f"{self.algorithm}="):
            signature = signature.split("=", 1)[1]

        valid = hmac.compare_digest(signature, expected)
        if not valid:
            logger.warning("Signature validation failed")

        return valid


class TimestampValidator(WebhookValidator):
    """Timestamp freshness validator."""

    def __init__(
        self,
        max_age_seconds: int = 300,
        timestamp_header: str = "X-Timestamp"
    ):
        self.max_age_seconds = max_age_seconds
        self.timestamp_header = timestamp_header

    def validate(self, payload: WebhookPayload) -> bool:
        """Validate timestamp is recent."""
        timestamp_str = payload.headers.get(self.timestamp_header)
        if not timestamp_str:
            # Try to extract from payload
            timestamp_str = payload.data.get("timestamp")

        if not timestamp_str:
            logger.warning("No timestamp found")
            return True  # Allow if no timestamp

        try:
            if isinstance(timestamp_str, (int, float)):
                ts = float(timestamp_str)
            else:
                ts = float(timestamp_str)

            age = time.time() - ts
            if age > self.max_age_seconds:
                logger.warning(f"Webhook too old: {age:.0f}s")
                return False

            return True

        except ValueError:
            logger.warning(f"Invalid timestamp: {timestamp_str}")
            return True


class WebhookHandler:
    """Handler for a specific webhook event."""

    def __init__(
        self,
        event_type: str,
        handler: Callable[[WebhookPayload], Optional[Dict[str, Any]]],
        validators: List[WebhookValidator] = None
    ):
        self.event_type = event_type
        self.handler = handler
        self.validators = validators or []


class WebhookProcessor:
    """
    Process incoming webhooks.

    Example:
        processor = WebhookProcessor(secret="my-secret")

        @processor.handler("order.created")
        def handle_order(payload):
            print(f"New order: {payload.data}")
            return {"status": "processed"}

        result = processor.process(payload)
    """

    def __init__(
        self,
        secret: Optional[str] = None,
        max_payload_size: int = 1024 * 1024  # 1MB
    ):
        self.handlers: Dict[str, WebhookHandler] = {}
        self.global_validators: List[WebhookValidator] = []
        self.max_payload_size = max_payload_size
        self.history: deque = deque(maxlen=1000)

        # Add signature validator if secret provided
        if secret:
            self.global_validators.append(SignatureValidator(secret))

    def handler(
        self,
        event_type: str,
        validators: List[WebhookValidator] = None
    ):
        """Decorator to register a webhook handler."""
        def decorator(func: Callable[[WebhookPayload], Optional[Dict[str, Any]]]):
            self.handlers[event_type] = WebhookHandler(
                event_type=event_type,
                handler=func,
                validators=validators or []
            )
            return func
        return decorator

    def add_validator(self, validator: WebhookValidator):
        """Add global validator."""
        self.global_validators.append(validator)

    def process(self, payload: WebhookPayload) -> WebhookResult:
        """Process a webhook payload."""
        start_time = time.time()

        try:
            # Size check
            if len(payload.raw_body) > self.max_payload_size:
                return WebhookResult(
                    payload_id=payload.id,
                    success=False,
                    status=WebhookStatus.REJECTED,
                    error="Payload too large"
                )

            # Global validation
            for validator in self.global_validators:
                if not validator.validate(payload):
                    payload.status = WebhookStatus.REJECTED
                    return WebhookResult(
                        payload_id=payload.id,
                        success=False,
                        status=WebhookStatus.REJECTED,
                        error="Validation failed"
                    )

            payload.status = WebhookStatus.VALIDATED

            # Find handler
            handler = self.handlers.get(payload.event_type)
            if not handler:
                logger.warning(f"No handler for event: {payload.event_type}")
                return WebhookResult(
                    payload_id=payload.id,
                    success=True,
                    status=WebhookStatus.VALIDATED,
                    response_data={"message": "No handler"}
                )

            # Handler-specific validation
            for validator in handler.validators:
                if not validator.validate(payload):
                    return WebhookResult(
                        payload_id=payload.id,
                        success=False,
                        status=WebhookStatus.REJECTED,
                        error="Handler validation failed"
                    )

            # Execute handler
            response = handler.handler(payload)
            payload.status = WebhookStatus.PROCESSED

            processing_time = (time.time() - start_time) * 1000

            result = WebhookResult(
                payload_id=payload.id,
                success=True,
                status=WebhookStatus.PROCESSED,
                response_data=response,
                processing_time_ms=processing_time
            )

            self.history.append(result)
            return result

        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            payload.status = WebhookStatus.FAILED

            return WebhookResult(
                payload_id=payload.id,
                success=False,
                status=WebhookStatus.FAILED,
                error=str(e),
                processing_time_ms=(time.time() - start_time) * 1000
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        results = list(self.history)
        if not results:
            return {"total": 0}

        successful = [r for r in results if r.success]
        processing_times = [r.processing_time_ms for r in results]

        return {
            "total": len(results),
            "successful": len(successful),
            "failed": len(results) - len(successful),
            "success_rate": len(successful) / len(results) * 100,
            "avg_processing_ms": sum(processing_times) / len(processing_times),
            "max_processing_ms": max(processing_times),
            "by_status": {
                status.value: len([r for r in results if r.status == status])
                for status in WebhookStatus
            }
        }


class WebhookRetryQueue:
    """Queue for retrying failed webhooks."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 60.0  # seconds
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.queue: List[Dict[str, Any]] = []

    def enqueue(self, payload: WebhookPayload, attempt: int = 0):
        """Add payload to retry queue."""
        if attempt >= self.max_retries:
            logger.warning(f"Max retries reached for {payload.id}")
            return

        delay = self.base_delay * (2 ** attempt)
        retry_at = time.time() + delay

        self.queue.append({
            "payload": payload,
            "attempt": attempt + 1,
            "retry_at": retry_at
        })

        logger.info(f"Queued {payload.id} for retry in {delay}s")

    def get_ready(self) -> List[Dict[str, Any]]:
        """Get payloads ready for retry."""
        now = time.time()
        ready = [item for item in self.queue if item["retry_at"] <= now]
        self.queue = [item for item in self.queue if item["retry_at"] > now]
        return ready


def create_trading_webhook_processor(secret: str) -> WebhookProcessor:
    """Create webhook processor for trading system."""
    processor = WebhookProcessor(secret)

    # Add timestamp validator
    processor.add_validator(TimestampValidator(max_age_seconds=300))

    @processor.handler("trade.opened")
    def handle_trade_opened(payload: WebhookPayload) -> Dict[str, Any]:
        data = payload.data
        logger.info(f"Trade opened: {data.get('symbol')} {data.get('direction')}")
        return {"processed": True, "action": "notified"}

    @processor.handler("trade.closed")
    def handle_trade_closed(payload: WebhookPayload) -> Dict[str, Any]:
        data = payload.data
        logger.info(f"Trade closed: {data.get('symbol')} P/L: {data.get('profit')}")
        return {"processed": True, "action": "recorded"}

    @processor.handler("signal.generated")
    def handle_signal(payload: WebhookPayload) -> Dict[str, Any]:
        data = payload.data
        logger.info(f"Signal: {data.get('symbol')} {data.get('direction')}")
        return {"processed": True, "action": "queued"}

    @processor.handler("alert.triggered")
    def handle_alert(payload: WebhookPayload) -> Dict[str, Any]:
        data = payload.data
        logger.info(f"Alert: {data.get('type')} - {data.get('message')}")
        return {"processed": True, "action": "notified"}

    return processor


# Example usage
if __name__ == "__main__":
    import uuid

    # Create processor
    processor = create_trading_webhook_processor(secret="test-secret")

    # Create test payload
    payload_data = {
        "symbol": "XAUUSD",
        "direction": "BUY",
        "volume": 0.1,
        "entry": 2000.50
    }

    raw_body = json.dumps(payload_data).encode()

    # Compute signature
    signature = hmac.new(
        b"test-secret",
        raw_body,
        hashlib.sha256
    ).hexdigest()

    payload = WebhookPayload(
        id=str(uuid.uuid4()),
        source="mt5",
        event_type="trade.opened",
        data=payload_data,
        headers={
            "X-Signature": f"sha256={signature}",
            "X-Timestamp": str(time.time())
        },
        raw_body=raw_body
    )

    # Process webhook
    print("Processing webhook...")
    result = processor.process(payload)

    print(f"\nResult:")
    print(f"  Success: {result.success}")
    print(f"  Status: {result.status.value}")
    print(f"  Response: {result.response_data}")
    print(f"  Time: {result.processing_time_ms:.2f}ms")

    # Get stats
    print(f"\nStats: {processor.get_stats()}")
