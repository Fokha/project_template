# ═══════════════════════════════════════════════════════════════
# ENDPOINT TEMPLATE
# Standard Flask endpoint patterns with request/response handling
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy endpoint patterns to your Flask app
# 2. Customize request validation and response format
# 3. Add authentication decorators as needed
#
# ═══════════════════════════════════════════════════════════════

from flask import Blueprint, request, jsonify, g
from functools import wraps
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# STANDARD RESPONSE FORMAT
# ═══════════════════════════════════════════════════════════════


@dataclass
class APIResponse:
    """Standard API response structure."""
    success: bool
    data: Any = None
    error: str = None
    message: str = None
    timestamp: str = None

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "message": self.message,
            "timestamp": self.timestamp or datetime.utcnow().isoformat(),
        }


def success_response(data: Any = None, message: str = None, status: int = 200):
    """Create a successful response."""
    response = APIResponse(
        success=True,
        data=data,
        message=message,
    )
    return jsonify(response.to_dict()), status


def error_response(error: str, message: str = None, status: int = 400):
    """Create an error response."""
    response = APIResponse(
        success=False,
        error=error,
        message=message,
    )
    return jsonify(response.to_dict()), status


# ═══════════════════════════════════════════════════════════════
# ENDPOINT DECORATORS
# ═══════════════════════════════════════════════════════════════


def require_json(f: Callable) -> Callable:
    """Decorator to require JSON content type."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.is_json:
            return error_response(
                "INVALID_CONTENT_TYPE",
                "Content-Type must be application/json",
                415
            )
        return f(*args, **kwargs)
    return decorated


def require_fields(*fields: str) -> Callable:
    """Decorator to require specific fields in request body."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            data = request.get_json(silent=True) or {}
            missing = [field for field in fields if field not in data]
            if missing:
                return error_response(
                    "MISSING_FIELDS",
                    f"Missing required fields: {', '.join(missing)}",
                    400
                )
            return f(*args, **kwargs)
        return decorated
    return decorator


def validate_params(**validators: Callable) -> Callable:
    """Decorator to validate query parameters."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            errors = []
            for param, validator in validators.items():
                value = request.args.get(param)
                if value is not None:
                    try:
                        if not validator(value):
                            errors.append(f"Invalid value for {param}")
                    except Exception:
                        errors.append(f"Invalid value for {param}")
            if errors:
                return error_response("VALIDATION_ERROR", "; ".join(errors), 400)
            return f(*args, **kwargs)
        return decorated
    return decorator


def rate_limit(requests_per_minute: int = 60) -> Callable:
    """Simple rate limiting decorator (use Redis for production)."""
    from collections import defaultdict
    import time

    request_counts = defaultdict(list)

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get client identifier
            client_id = request.headers.get('X-API-Key') or request.remote_addr
            now = time.time()
            minute_ago = now - 60

            # Clean old requests
            request_counts[client_id] = [
                t for t in request_counts[client_id] if t > minute_ago
            ]

            # Check limit
            if len(request_counts[client_id]) >= requests_per_minute:
                return error_response(
                    "RATE_LIMIT_EXCEEDED",
                    f"Rate limit: {requests_per_minute} requests/minute",
                    429
                )

            request_counts[client_id].append(now)
            return f(*args, **kwargs)
        return decorated
    return decorator


# ═══════════════════════════════════════════════════════════════
# BLUEPRINT EXAMPLE
# ═══════════════════════════════════════════════════════════════


# Create blueprint
example_bp = Blueprint('example', __name__, url_prefix='/api/v1/example')


@example_bp.route('/items', methods=['GET'])
def list_items():
    """
    GET /api/v1/example/items

    Query Parameters:
        - limit (int): Max items to return (default: 10)
        - offset (int): Skip N items (default: 0)
        - sort (str): Sort field (default: created_at)

    Returns:
        List of items with pagination info
    """
    try:
        # Parse query parameters
        limit = min(int(request.args.get('limit', 10)), 100)
        offset = int(request.args.get('offset', 0))
        sort = request.args.get('sort', 'created_at')

        # Simulate data fetch
        items = [
            {"id": i, "name": f"Item {i}", "created_at": datetime.utcnow().isoformat()}
            for i in range(offset, offset + limit)
        ]

        return success_response({
            "items": items,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": 100,  # Would come from DB
            }
        })

    except ValueError as e:
        return error_response("INVALID_PARAMETER", str(e), 400)
    except Exception as e:
        logger.exception("Error listing items")
        return error_response("INTERNAL_ERROR", "An error occurred", 500)


@example_bp.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id: int):
    """
    GET /api/v1/example/items/<id>

    Path Parameters:
        - item_id (int): Item ID

    Returns:
        Single item details
    """
    try:
        # Simulate item lookup
        if item_id < 0 or item_id > 100:
            return error_response("NOT_FOUND", f"Item {item_id} not found", 404)

        item = {
            "id": item_id,
            "name": f"Item {item_id}",
            "description": "Sample item",
            "created_at": datetime.utcnow().isoformat(),
        }

        return success_response(item)

    except Exception as e:
        logger.exception(f"Error getting item {item_id}")
        return error_response("INTERNAL_ERROR", "An error occurred", 500)


@example_bp.route('/items', methods=['POST'])
@require_json
@require_fields('name')
def create_item():
    """
    POST /api/v1/example/items

    Request Body:
        {
            "name": "Item name",
            "description": "Optional description"
        }

    Returns:
        Created item with ID
    """
    try:
        data = request.get_json()

        # Validate
        name = data.get('name', '').strip()
        if len(name) < 1 or len(name) > 100:
            return error_response(
                "VALIDATION_ERROR",
                "Name must be 1-100 characters",
                400
            )

        # Simulate creation
        item = {
            "id": 101,  # Would be generated
            "name": name,
            "description": data.get('description', ''),
            "created_at": datetime.utcnow().isoformat(),
        }

        return success_response(item, "Item created successfully", 201)

    except Exception as e:
        logger.exception("Error creating item")
        return error_response("INTERNAL_ERROR", "An error occurred", 500)


@example_bp.route('/items/<int:item_id>', methods=['PUT'])
@require_json
def update_item(item_id: int):
    """
    PUT /api/v1/example/items/<id>

    Path Parameters:
        - item_id (int): Item ID

    Request Body:
        {
            "name": "Updated name",
            "description": "Updated description"
        }

    Returns:
        Updated item
    """
    try:
        if item_id < 0 or item_id > 100:
            return error_response("NOT_FOUND", f"Item {item_id} not found", 404)

        data = request.get_json()

        # Simulate update
        item = {
            "id": item_id,
            "name": data.get('name', f"Item {item_id}"),
            "description": data.get('description', ''),
            "updated_at": datetime.utcnow().isoformat(),
        }

        return success_response(item, "Item updated successfully")

    except Exception as e:
        logger.exception(f"Error updating item {item_id}")
        return error_response("INTERNAL_ERROR", "An error occurred", 500)


@example_bp.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id: int):
    """
    DELETE /api/v1/example/items/<id>

    Path Parameters:
        - item_id (int): Item ID

    Returns:
        Confirmation message
    """
    try:
        if item_id < 0 or item_id > 100:
            return error_response("NOT_FOUND", f"Item {item_id} not found", 404)

        # Simulate deletion
        return success_response(
            {"id": item_id},
            "Item deleted successfully"
        )

    except Exception as e:
        logger.exception(f"Error deleting item {item_id}")
        return error_response("INTERNAL_ERROR", "An error occurred", 500)


# ═══════════════════════════════════════════════════════════════
# ASYNC-STYLE ENDPOINT (for long operations)
# ═══════════════════════════════════════════════════════════════


@example_bp.route('/tasks', methods=['POST'])
@require_json
@require_fields('type')
def create_task():
    """
    POST /api/v1/example/tasks

    Creates an async task and returns task ID for polling.

    Request Body:
        {
            "type": "analysis",
            "params": {...}
        }

    Returns:
        Task ID for status polling
    """
    try:
        data = request.get_json()

        # Create task (would be queued to background worker)
        task_id = "task_" + datetime.utcnow().strftime("%Y%m%d%H%M%S")

        return success_response({
            "task_id": task_id,
            "status": "pending",
            "status_url": f"/api/v1/example/tasks/{task_id}",
        }, "Task created", 202)

    except Exception as e:
        logger.exception("Error creating task")
        return error_response("INTERNAL_ERROR", "An error occurred", 500)


@example_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id: str):
    """
    GET /api/v1/example/tasks/<task_id>

    Poll task status.

    Returns:
        Task status and result if complete
    """
    try:
        # Simulate task lookup
        return success_response({
            "task_id": task_id,
            "status": "completed",  # pending, running, completed, failed
            "progress": 100,
            "result": {"message": "Task completed successfully"},
        })

    except Exception as e:
        logger.exception(f"Error getting task {task_id}")
        return error_response("INTERNAL_ERROR", "An error occurred", 500)


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(example_bp)

    print("Registered endpoints:")
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            print(f"  {rule.methods - {'HEAD', 'OPTIONS'}} {rule.rule}")

    # Run dev server
    # app.run(debug=True, port=5050)
