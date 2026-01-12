# ═══════════════════════════════════════════════════════════════
# LOGGING TEMPLATE
# Structured logging setup for Flask APIs
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy to your project
# 2. Call setup_logging() in your app initialization
# 3. Use logger instances throughout your code
#
# ═══════════════════════════════════════════════════════════════

import logging
import logging.handlers
import json
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from functools import wraps
import time
import traceback


# ═══════════════════════════════════════════════════════════════
# STRUCTURED LOG FORMATTER
# ═══════════════════════════════════════════════════════════════


class JSONFormatter(logging.Formatter):
    """Format log records as JSON for log aggregation systems."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'pathname', 'process', 'processName', 'relativeCreated',
                'stack_info', 'exc_info', 'exc_text', 'thread', 'threadName',
                'message', 'asctime'
            ]:
                log_data[key] = value

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored console output for development."""

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"

        # Format time
        record.asctime = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')

        return super().format(record)


class RequestFormatter(logging.Formatter):
    """Include request context in logs."""

    def format(self, record: logging.LogRecord) -> str:
        # Try to get Flask request context
        try:
            from flask import request, g
            record.request_id = getattr(g, 'request_id', '-')
            record.method = request.method
            record.path = request.path
            record.remote_addr = request.remote_addr
        except (ImportError, RuntimeError):
            record.request_id = '-'
            record.method = '-'
            record.path = '-'
            record.remote_addr = '-'

        return super().format(record)


# ═══════════════════════════════════════════════════════════════
# LOGGING CONFIGURATION
# ═══════════════════════════════════════════════════════════════


@dataclass
class LogConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "text"  # text, json
    log_dir: str = "logs"
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    include_request_context: bool = True


def setup_logging(
    app=None,
    config: LogConfig = None
) -> logging.Logger:
    """
    Setup logging for the application.

    Args:
        app: Flask app instance (optional)
        config: LogConfig instance

    Returns:
        Root logger instance
    """
    config = config or LogConfig()

    # Create logs directory
    log_dir = Path(config.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.level.upper()))

    # Clear existing handlers
    root_logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    if config.format == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        # Colored output for development
        if sys.stdout.isatty():
            formatter = ColoredFormatter(
                '%(asctime)s %(levelname)s [%(name)s] %(message)s'
            )
        else:
            formatter = RequestFormatter(
                '%(asctime)s %(levelname)s [%(request_id)s] %(name)s - %(message)s'
            ) if config.include_request_context else logging.Formatter(
                '%(asctime)s %(levelname)s [%(name)s] %(message)s'
            )
        console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)

    # File handler for all logs
    all_log_file = log_dir / "app.log"
    file_handler = logging.handlers.RotatingFileHandler(
        all_log_file,
        maxBytes=config.max_bytes,
        backupCount=config.backup_count,
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)

    # Error file handler
    error_log_file = log_dir / "error.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=config.max_bytes,
        backupCount=config.backup_count,
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(error_handler)

    # Flask-specific setup
    if app:
        app.logger.handlers = []
        for handler in root_logger.handlers:
            app.logger.addHandler(handler)
        app.logger.setLevel(root_logger.level)

    logging.info(f"Logging initialized: level={config.level}, format={config.format}")

    return root_logger


# ═══════════════════════════════════════════════════════════════
# LOGGING DECORATORS
# ═══════════════════════════════════════════════════════════════


def log_function_call(logger: logging.Logger = None):
    """
    Decorator to log function calls with timing.

    Example:
        @log_function_call()
        def process_data(data):
            ...
    """
    def decorator(f):
        nonlocal logger
        if logger is None:
            logger = logging.getLogger(f.__module__)

        @wraps(f)
        def decorated(*args, **kwargs):
            func_name = f.__qualname__

            # Log entry
            logger.debug(
                f"Entering {func_name}",
                extra={"function": func_name, "args_count": len(args)}
            )

            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time

                logger.debug(
                    f"Exiting {func_name}",
                    extra={
                        "function": func_name,
                        "duration_ms": round(duration * 1000, 2),
                        "success": True
                    }
                )
                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.exception(
                    f"Exception in {func_name}: {str(e)}",
                    extra={
                        "function": func_name,
                        "duration_ms": round(duration * 1000, 2),
                        "success": False,
                        "error": str(e)
                    }
                )
                raise

        return decorated
    return decorator


def log_endpoint(logger: logging.Logger = None):
    """
    Decorator to log Flask endpoint calls.

    Example:
        @app.route('/api/data')
        @log_endpoint()
        def get_data():
            ...
    """
    def decorator(f):
        nonlocal logger
        if logger is None:
            logger = logging.getLogger('api')

        @wraps(f)
        def decorated(*args, **kwargs):
            from flask import request

            start_time = time.time()
            endpoint = request.endpoint or f.__name__

            logger.info(
                f"Request: {request.method} {request.path}",
                extra={
                    "endpoint": endpoint,
                    "method": request.method,
                    "path": request.path,
                    "query_string": request.query_string.decode(),
                    "remote_addr": request.remote_addr,
                }
            )

            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time

                # Extract status code
                status_code = 200
                if isinstance(result, tuple):
                    status_code = result[1] if len(result) > 1 else 200

                logger.info(
                    f"Response: {status_code} ({duration*1000:.0f}ms)",
                    extra={
                        "endpoint": endpoint,
                        "status_code": status_code,
                        "duration_ms": round(duration * 1000, 2),
                    }
                )
                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.exception(
                    f"Endpoint error: {str(e)}",
                    extra={
                        "endpoint": endpoint,
                        "duration_ms": round(duration * 1000, 2),
                        "error": str(e),
                    }
                )
                raise

        return decorated
    return decorator


# ═══════════════════════════════════════════════════════════════
# CONTEXT MANAGER FOR OPERATION LOGGING
# ═══════════════════════════════════════════════════════════════


class LogOperation:
    """
    Context manager for logging operations with timing.

    Example:
        with LogOperation(logger, "database_query", symbol="XAUUSD"):
            result = db.query(...)
    """

    def __init__(
        self,
        logger: logging.Logger,
        operation: str,
        level: int = logging.INFO,
        **extra
    ):
        self.logger = logger
        self.operation = operation
        self.level = level
        self.extra = extra
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        self.logger.log(
            self.level,
            f"Starting: {self.operation}",
            extra={"operation": self.operation, **self.extra}
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time

        if exc_type:
            self.logger.error(
                f"Failed: {self.operation} - {str(exc_val)}",
                extra={
                    "operation": self.operation,
                    "duration_ms": round(duration * 1000, 2),
                    "success": False,
                    "error": str(exc_val),
                    **self.extra
                }
            )
        else:
            self.logger.log(
                self.level,
                f"Completed: {self.operation} ({duration*1000:.0f}ms)",
                extra={
                    "operation": self.operation,
                    "duration_ms": round(duration * 1000, 2),
                    "success": True,
                    **self.extra
                }
            )

        return False  # Don't suppress exceptions


# ═══════════════════════════════════════════════════════════════
# AUDIT LOGGER
# ═══════════════════════════════════════════════════════════════


class AuditLogger:
    """
    Specialized logger for audit trails.

    Logs important business events for compliance.
    """

    def __init__(self, log_file: str = "logs/audit.log"):
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)

        # Dedicated file handler
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=10,
        )
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)

    def log(
        self,
        action: str,
        resource: str,
        resource_id: Any = None,
        user: str = None,
        details: Dict = None,
        success: bool = True
    ):
        """Log an audit event."""
        self.logger.info(
            f"AUDIT: {action} on {resource}",
            extra={
                "audit": True,
                "action": action,
                "resource": resource,
                "resource_id": resource_id,
                "user": user,
                "details": details or {},
                "success": success,
            }
        )

    def trade_opened(self, symbol: str, direction: str, volume: float, user: str = None):
        self.log("TRADE_OPENED", "trade", details={
            "symbol": symbol,
            "direction": direction,
            "volume": volume,
        }, user=user)

    def trade_closed(self, symbol: str, profit: float, user: str = None):
        self.log("TRADE_CLOSED", "trade", details={
            "symbol": symbol,
            "profit": profit,
        }, user=user)

    def config_changed(self, setting: str, old_value: Any, new_value: Any, user: str = None):
        self.log("CONFIG_CHANGED", "config", details={
            "setting": setting,
            "old_value": old_value,
            "new_value": new_value,
        }, user=user)


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    # Setup logging
    config = LogConfig(level="DEBUG", format="text")
    setup_logging(config=config)

    logger = logging.getLogger(__name__)

    print("=" * 60)
    print("LOGGING TEMPLATE DEMO")
    print("=" * 60)

    # Basic logging
    print("\n--- Basic Logging ---")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    # Logging with extra fields
    print("\n--- Extra Fields ---")
    logger.info("Processing request", extra={
        "symbol": "XAUUSD",
        "confidence": 0.85,
        "user_id": 123,
    })

    # Function logging decorator
    print("\n--- Function Decorator ---")

    @log_function_call()
    def process_data(data):
        time.sleep(0.1)
        return {"processed": True}

    result = process_data({"input": "test"})

    # Operation context manager
    print("\n--- Operation Context Manager ---")

    with LogOperation(logger, "data_analysis", symbol="XAUUSD"):
        time.sleep(0.05)

    # Audit logging
    print("\n--- Audit Logging ---")
    audit = AuditLogger("logs/audit.log")
    audit.trade_opened("XAUUSD", "BUY", 0.1, user="system")
    audit.trade_closed("XAUUSD", 150.50, user="system")

    # Exception logging
    print("\n--- Exception Logging ---")
    try:
        raise ValueError("Something went wrong")
    except Exception:
        logger.exception("Caught an exception")

    print("\nCheck logs/ directory for log files")
