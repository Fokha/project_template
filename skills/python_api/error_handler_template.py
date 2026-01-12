# ═══════════════════════════════════════════════════════════════
# ERROR HANDLER TEMPLATE
# Consistent error handling and responses for Flask APIs
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Import and register with your Flask app
# 2. Use custom exceptions for business logic errors
# 3. All errors return consistent JSON format
#
# ═══════════════════════════════════════════════════════════════

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from typing import Dict, Any, Optional, Type
from dataclasses import dataclass
from datetime import datetime
import logging
import traceback

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# CUSTOM EXCEPTIONS
# ═══════════════════════════════════════════════════════════════


class APIError(Exception):
    """Base exception for API errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Dict = None
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class ValidationError(APIError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str = None, details: Dict = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=400,
            details={"field": field, **(details or {})}
        )


class NotFoundError(APIError):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, identifier: Any = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        super().__init__(
            code="NOT_FOUND",
            message=message,
            status_code=404,
            details={"resource": resource, "identifier": identifier}
        )


class AuthenticationError(APIError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            code="AUTHENTICATION_ERROR",
            message=message,
            status_code=401
        )


class AuthorizationError(APIError):
    """Raised when user lacks permission."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            code="AUTHORIZATION_ERROR",
            message=message,
            status_code=403
        )


class ConflictError(APIError):
    """Raised when there's a resource conflict."""

    def __init__(self, message: str, resource: str = None):
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=409,
            details={"resource": resource}
        )


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""

    def __init__(self, limit: int, window: str = "minute"):
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message=f"Rate limit exceeded: {limit} requests per {window}",
            status_code=429,
            details={"limit": limit, "window": window}
        )


class ServiceUnavailableError(APIError):
    """Raised when a dependent service is unavailable."""

    def __init__(self, service: str, message: str = None):
        super().__init__(
            code="SERVICE_UNAVAILABLE",
            message=message or f"Service '{service}' is temporarily unavailable",
            status_code=503,
            details={"service": service}
        )


class ExternalAPIError(APIError):
    """Raised when an external API call fails."""

    def __init__(self, service: str, status_code: int = None, message: str = None):
        super().__init__(
            code="EXTERNAL_API_ERROR",
            message=message or f"External API '{service}' returned an error",
            status_code=502,
            details={"service": service, "external_status": status_code}
        )


# ═══════════════════════════════════════════════════════════════
# ERROR RESPONSE FORMAT
# ═══════════════════════════════════════════════════════════════


@dataclass
class ErrorResponse:
    """Standard error response structure."""
    success: bool = False
    error: Dict = None
    request_id: str = None
    timestamp: str = None

    @classmethod
    def from_exception(
        cls,
        code: str,
        message: str,
        status_code: int,
        details: Dict = None,
        request_id: str = None
    ) -> 'ErrorResponse':
        return cls(
            success=False,
            error={
                "code": code,
                "message": message,
                "status_code": status_code,
                "details": details or {},
            },
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat(),
        )

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "error": self.error,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
        }


# ═══════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════════════════════════


def register_error_handlers(app: Flask):
    """Register all error handlers with Flask app."""

    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        """Handle custom API errors."""
        request_id = getattr(request, 'request_id', None)

        logger.warning(
            f"API Error: {error.code} - {error.message}",
            extra={
                "error_code": error.code,
                "status_code": error.status_code,
                "details": error.details,
                "request_id": request_id,
            }
        )

        response = ErrorResponse.from_exception(
            code=error.code,
            message=error.message,
            status_code=error.status_code,
            details=error.details,
            request_id=request_id,
        )

        return jsonify(response.to_dict()), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Handle Werkzeug HTTP exceptions."""
        request_id = getattr(request, 'request_id', None)

        # Map HTTP errors to codes
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            408: "REQUEST_TIMEOUT",
            409: "CONFLICT",
            413: "PAYLOAD_TOO_LARGE",
            415: "UNSUPPORTED_MEDIA_TYPE",
            422: "UNPROCESSABLE_ENTITY",
            429: "TOO_MANY_REQUESTS",
            500: "INTERNAL_SERVER_ERROR",
            502: "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE",
            504: "GATEWAY_TIMEOUT",
        }

        code = code_map.get(error.code, "HTTP_ERROR")

        logger.warning(
            f"HTTP Exception: {error.code} - {error.description}",
            extra={"request_id": request_id}
        )

        response = ErrorResponse.from_exception(
            code=code,
            message=error.description,
            status_code=error.code,
            request_id=request_id,
        )

        return jsonify(response.to_dict()), error.code

    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception):
        """Handle unexpected exceptions."""
        request_id = getattr(request, 'request_id', None)

        # Log full traceback for debugging
        logger.exception(
            f"Unhandled exception: {str(error)}",
            extra={"request_id": request_id}
        )

        # Don't expose internal details in production
        if app.debug:
            message = str(error)
            details = {"traceback": traceback.format_exc()}
        else:
            message = "An unexpected error occurred"
            details = {}

        response = ErrorResponse.from_exception(
            code="INTERNAL_SERVER_ERROR",
            message=message,
            status_code=500,
            details=details,
            request_id=request_id,
        )

        return jsonify(response.to_dict()), 500


# ═══════════════════════════════════════════════════════════════
# REQUEST ID MIDDLEWARE
# ═══════════════════════════════════════════════════════════════


def add_request_id_middleware(app: Flask):
    """Add request ID to all requests for tracing."""
    import uuid

    @app.before_request
    def add_request_id():
        # Use provided ID or generate new one
        request.request_id = request.headers.get(
            'X-Request-ID',
            str(uuid.uuid4())[:8]
        )

    @app.after_request
    def include_request_id(response):
        response.headers['X-Request-ID'] = request.request_id
        return response


# ═══════════════════════════════════════════════════════════════
# ERROR LOGGING FORMATTER
# ═══════════════════════════════════════════════════════════════


class ErrorContextFilter(logging.Filter):
    """Add error context to log records."""

    def filter(self, record):
        # Add request context if available
        try:
            record.request_id = getattr(request, 'request_id', '-')
            record.endpoint = request.endpoint or '-'
            record.method = request.method
            record.path = request.path
        except RuntimeError:
            # Outside request context
            record.request_id = '-'
            record.endpoint = '-'
            record.method = '-'
            record.path = '-'
        return True


def setup_error_logging(app: Flask, log_level: int = logging.INFO):
    """Configure structured logging for errors."""

    # Create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(request_id)s] '
        '%(method)s %(path)s - %(message)s'
    )

    # Setup handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.addFilter(ErrorContextFilter())

    # Configure app logger
    app.logger.handlers = []
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)

    # Configure root logger
    logging.root.handlers = []
    logging.root.addHandler(handler)
    logging.root.setLevel(log_level)


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)
    app.debug = True

    # Register error handlers
    register_error_handlers(app)
    add_request_id_middleware(app)
    setup_error_logging(app)

    # Example endpoints demonstrating errors
    @app.route('/api/users/<int:user_id>')
    def get_user(user_id):
        if user_id == 0:
            raise NotFoundError("User", user_id)
        if user_id == -1:
            raise ValidationError("User ID must be positive", field="user_id")
        if user_id == 999:
            raise AuthorizationError("Cannot access this user")
        return jsonify({"id": user_id, "name": "Test User"})

    @app.route('/api/error')
    def trigger_error():
        # This will be caught by generic handler
        raise RuntimeError("Something went wrong!")

    @app.route('/api/external')
    def call_external():
        raise ExternalAPIError("payment-gateway", status_code=500)

    print("Error Handler Demo Endpoints:")
    print("  GET /api/users/1     -> Success")
    print("  GET /api/users/0     -> NotFoundError")
    print("  GET /api/users/-1    -> ValidationError")
    print("  GET /api/users/999   -> AuthorizationError")
    print("  GET /api/error       -> Generic Exception")
    print("  GET /api/external    -> ExternalAPIError")

    # app.run(debug=True, port=5050)
