"""
Logging Infrastructure Template
===============================
Patterns for centralized logging infrastructure.

Use when:
- Centralized log aggregation needed
- Log analysis and search required
- Distributed system logging
- Compliance requirements

Placeholders:
- {{LOG_LEVEL}}: Default log level
- {{LOG_RETENTION_DAYS}}: Log retention period
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
import logging
import json
import sys
import traceback
import threading
from queue import Queue

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: datetime
    level: LogLevel
    message: str
    logger_name: str
    service: str = "default"
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    exception: Optional[str] = None
    stack_trace: Optional[str] = None


class LogFormatter(ABC):
    """Abstract log formatter."""

    @abstractmethod
    def format(self, entry: LogEntry) -> str:
        """Format log entry."""
        pass


class JSONFormatter(LogFormatter):
    """JSON log formatter."""

    def __init__(self, include_stack: bool = True):
        self.include_stack = include_stack

    def format(self, entry: LogEntry) -> str:
        """Format as JSON."""
        data = {
            "timestamp": entry.timestamp.isoformat(),
            "level": entry.level.name,
            "message": entry.message,
            "logger": entry.logger_name,
            "service": entry.service
        }

        if entry.trace_id:
            data["trace_id"] = entry.trace_id
        if entry.span_id:
            data["span_id"] = entry.span_id
        if entry.user_id:
            data["user_id"] = entry.user_id
        if entry.extra:
            data["extra"] = entry.extra
        if entry.exception:
            data["exception"] = entry.exception
        if self.include_stack and entry.stack_trace:
            data["stack_trace"] = entry.stack_trace

        return json.dumps(data)


class TextFormatter(LogFormatter):
    """Human-readable text formatter."""

    def __init__(self, include_timestamp: bool = True):
        self.include_timestamp = include_timestamp

    def format(self, entry: LogEntry) -> str:
        """Format as text."""
        parts = []

        if self.include_timestamp:
            parts.append(entry.timestamp.strftime("%Y-%m-%d %H:%M:%S"))

        parts.append(f"[{entry.level.name:8}]")
        parts.append(f"[{entry.service}]")
        parts.append(f"[{entry.logger_name}]")

        if entry.trace_id:
            parts.append(f"[trace:{entry.trace_id[:8]}]")

        parts.append(entry.message)

        line = " ".join(parts)

        if entry.exception:
            line += f"\nException: {entry.exception}"
        if entry.stack_trace:
            line += f"\n{entry.stack_trace}"

        return line


class LogHandler(ABC):
    """Abstract log handler."""

    def __init__(self, formatter: LogFormatter):
        self.formatter = formatter
        self.level = LogLevel.DEBUG

    @abstractmethod
    def emit(self, entry: LogEntry):
        """Emit a log entry."""
        pass

    def should_handle(self, entry: LogEntry) -> bool:
        """Check if this handler should handle the entry."""
        return entry.level.value >= self.level.value


class ConsoleHandler(LogHandler):
    """Console output handler."""

    def __init__(self, formatter: LogFormatter = None):
        super().__init__(formatter or TextFormatter())
        self._lock = threading.Lock()

    def emit(self, entry: LogEntry):
        """Emit to console."""
        if not self.should_handle(entry):
            return

        formatted = self.formatter.format(entry)
        with self._lock:
            stream = sys.stderr if entry.level.value >= LogLevel.ERROR.value else sys.stdout
            stream.write(formatted + "\n")
            stream.flush()


class FileHandler(LogHandler):
    """File output handler."""

    def __init__(
        self,
        file_path: str,
        formatter: LogFormatter = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        super().__init__(formatter or JSONFormatter())
        self.file_path = file_path
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self._lock = threading.Lock()
        self._current_size = 0

    def emit(self, entry: LogEntry):
        """Emit to file."""
        if not self.should_handle(entry):
            return

        formatted = self.formatter.format(entry) + "\n"

        with self._lock:
            self._check_rotation()
            with open(self.file_path, "a") as f:
                f.write(formatted)
                self._current_size += len(formatted)

    def _check_rotation(self):
        """Check if log rotation is needed."""
        import os
        if os.path.exists(self.file_path):
            self._current_size = os.path.getsize(self.file_path)
            if self._current_size >= self.max_bytes:
                self._rotate()

    def _rotate(self):
        """Rotate log files."""
        import os

        # Remove oldest backup
        oldest = f"{self.file_path}.{self.backup_count}"
        if os.path.exists(oldest):
            os.remove(oldest)

        # Rotate existing backups
        for i in range(self.backup_count - 1, 0, -1):
            src = f"{self.file_path}.{i}"
            dst = f"{self.file_path}.{i + 1}"
            if os.path.exists(src):
                os.rename(src, dst)

        # Rotate current file
        if os.path.exists(self.file_path):
            os.rename(self.file_path, f"{self.file_path}.1")

        self._current_size = 0


class AsyncHandler(LogHandler):
    """Async handler that queues logs."""

    def __init__(self, delegate: LogHandler, queue_size: int = 10000):
        super().__init__(delegate.formatter)
        self.delegate = delegate
        self.queue: Queue = Queue(maxsize=queue_size)
        self._running = True
        self._thread = threading.Thread(target=self._process_queue, daemon=True)
        self._thread.start()

    def emit(self, entry: LogEntry):
        """Queue log entry."""
        if not self.should_handle(entry):
            return

        try:
            self.queue.put_nowait(entry)
        except:
            # Queue full, drop log
            pass

    def _process_queue(self):
        """Process queued entries."""
        while self._running:
            try:
                entry = self.queue.get(timeout=1)
                self.delegate.emit(entry)
            except:
                continue

    def close(self):
        """Stop the async handler."""
        self._running = False
        self._thread.join(timeout=5)


class StructuredLogger:
    """
    Structured logger with context.

    Example:
        logger = StructuredLogger("trading", service="api")
        logger.add_handler(ConsoleHandler())
        logger.add_handler(FileHandler("app.log"))

        with logger.context(trace_id="abc123", user_id="user1"):
            logger.info("Processing request", extra={"endpoint": "/trade"})
    """

    def __init__(self, name: str, service: str = "default"):
        self.name = name
        self.service = service
        self.handlers: List[LogHandler] = []
        self._context: Dict[str, Any] = {}
        self._context_stack: List[Dict[str, Any]] = []

    def add_handler(self, handler: LogHandler):
        """Add a log handler."""
        self.handlers.append(handler)

    def set_level(self, level: LogLevel):
        """Set level for all handlers."""
        for handler in self.handlers:
            handler.level = level

    def context(self, **kwargs) -> "LoggerContext":
        """Create a context manager for adding context."""
        return LoggerContext(self, kwargs)

    def _push_context(self, ctx: Dict[str, Any]):
        """Push context onto stack."""
        self._context_stack.append(self._context.copy())
        self._context.update(ctx)

    def _pop_context(self):
        """Pop context from stack."""
        if self._context_stack:
            self._context = self._context_stack.pop()

    def _log(
        self,
        level: LogLevel,
        message: str,
        extra: Dict[str, Any] = None,
        exc_info: bool = False
    ):
        """Internal log method."""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=message,
            logger_name=self.name,
            service=self.service,
            trace_id=self._context.get("trace_id"),
            span_id=self._context.get("span_id"),
            user_id=self._context.get("user_id"),
            extra={**self._context.get("extra", {}), **(extra or {})}
        )

        if exc_info:
            entry.exception = str(sys.exc_info()[1])
            entry.stack_trace = traceback.format_exc()

        for handler in self.handlers:
            handler.emit(entry)

    def debug(self, message: str, **kwargs):
        self._log(LogLevel.DEBUG, message, kwargs)

    def info(self, message: str, **kwargs):
        self._log(LogLevel.INFO, message, kwargs)

    def warning(self, message: str, **kwargs):
        self._log(LogLevel.WARNING, message, kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        self._log(LogLevel.ERROR, message, kwargs, exc_info)

    def critical(self, message: str, exc_info: bool = False, **kwargs):
        self._log(LogLevel.CRITICAL, message, kwargs, exc_info)


class LoggerContext:
    """Context manager for logger context."""

    def __init__(self, logger: StructuredLogger, context: Dict[str, Any]):
        self.logger = logger
        self.context = context

    def __enter__(self):
        self.logger._push_context(self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger._pop_context()
        return False


class LogAggregator:
    """Aggregate logs from multiple sources."""

    def __init__(self):
        self.loggers: Dict[str, StructuredLogger] = {}
        self.shared_handlers: List[LogHandler] = []

    def get_logger(self, name: str, service: str = "default") -> StructuredLogger:
        """Get or create a logger."""
        key = f"{service}:{name}"
        if key not in self.loggers:
            logger = StructuredLogger(name, service)
            for handler in self.shared_handlers:
                logger.add_handler(handler)
            self.loggers[key] = logger
        return self.loggers[key]

    def add_shared_handler(self, handler: LogHandler):
        """Add handler to all loggers."""
        self.shared_handlers.append(handler)
        for logger in self.loggers.values():
            logger.add_handler(handler)


def create_trading_logging(log_dir: str) -> LogAggregator:
    """Create logging setup for trading system."""
    import os
    os.makedirs(log_dir, exist_ok=True)

    aggregator = LogAggregator()

    # Console handler with text format
    console = ConsoleHandler(TextFormatter())
    console.level = LogLevel.INFO
    aggregator.add_shared_handler(console)

    # File handler with JSON format
    file_handler = FileHandler(
        f"{log_dir}/trading.log",
        JSONFormatter(),
        max_bytes=50 * 1024 * 1024,  # 50MB
        backup_count=10
    )
    file_handler.level = LogLevel.DEBUG
    aggregator.add_shared_handler(AsyncHandler(file_handler))

    # Error-only file
    error_handler = FileHandler(
        f"{log_dir}/errors.log",
        JSONFormatter()
    )
    error_handler.level = LogLevel.ERROR
    aggregator.add_shared_handler(error_handler)

    return aggregator


# Example usage
if __name__ == "__main__":
    import tempfile

    # Create logging setup
    with tempfile.TemporaryDirectory() as log_dir:
        aggregator = create_trading_logging(log_dir)

        # Get logger
        log = aggregator.get_logger("api", "trading-api")

        # Basic logging
        log.info("Server started", port=5050, version="1.0.0")

        # With context
        with log.context(trace_id="abc123", user_id="trader1"):
            log.info("Processing request", endpoint="/signal")
            log.debug("Fetching market data", symbol="XAUUSD")

            try:
                raise ValueError("Invalid signal")
            except:
                log.error("Signal processing failed", exc_info=True)

        log.info("Request completed")

        print(f"\nLogs written to: {log_dir}")
