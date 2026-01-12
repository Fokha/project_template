# ═══════════════════════════════════════════════════════════════
# {{FEATURE_NAME}} BLUEPRINT
# Flask Blueprint for modular API organization
# ═══════════════════════════════════════════════════════════════
#
# Usage:
# 1. Copy this file to your project
# 2. Replace {{FEATURE_NAME}} with your feature name
# 3. Register in main app: app.register_blueprint({{feature_name}}_bp)
#
# ═══════════════════════════════════════════════════════════════

from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# ═══════════════════════════════════════════════════════════════
# BLUEPRINT SETUP
# ═══════════════════════════════════════════════════════════════

{{feature_name}}_bp = Blueprint('{{feature_name}}', __name__, url_prefix='/{{feature_name}}')
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════


def success_response(data: Any, message: Optional[str] = None) -> Dict:
    """Return standard success response."""
    response = {
        'success': True,
        'data': data,
        'error': None,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    if message:
        response['message'] = message
    return response


def error_response(error: str, status_code: int = 400) -> tuple:
    """Return standard error response."""
    return jsonify({
        'success': False,
        'data': None,
        'error': error,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), status_code


def get_json_or_error():
    """Get JSON body or return error."""
    data = request.get_json()
    if data is None:
        return None, error_response('Request body must be JSON', 400)
    return data, None


# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════


@{{feature_name}}_bp.route('', methods=['GET'])
def list_items():
    """
    List all items.

    GET /{{feature_name}}

    Query Parameters:
        limit (int): Max items to return (default: 100)
        offset (int): Items to skip (default: 0)
        status (str): Filter by status

    Returns:
        {
            "success": true,
            "data": [...]
        }
    """
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        status = request.args.get('status')

        # TODO: Implement your data fetching logic
        items = []  # Replace with actual query

        return jsonify(success_response({
            'items': items,
            'count': len(items),
            'limit': limit,
            'offset': offset
        }))

    except Exception as e:
        logger.error(f"Error listing items: {e}")
        return error_response(str(e), 500)


@{{feature_name}}_bp.route('/<item_id>', methods=['GET'])
def get_item(item_id: str):
    """
    Get single item by ID.

    GET /{{feature_name}}/<item_id>

    Returns:
        {
            "success": true,
            "data": {...}
        }
    """
    try:
        # TODO: Implement your data fetching logic
        item = None  # Replace with actual query

        if item is None:
            return error_response(f'Item {item_id} not found', 404)

        return jsonify(success_response(item))

    except Exception as e:
        logger.error(f"Error getting item {item_id}: {e}")
        return error_response(str(e), 500)


@{{feature_name}}_bp.route('', methods=['POST'])
def create_item():
    """
    Create new item.

    POST /{{feature_name}}

    Request Body:
        {
            "name": "Item name",
            "description": "Optional description"
        }

    Returns:
        {
            "success": true,
            "data": {...}
        }
    """
    try:
        data, error = get_json_or_error()
        if error:
            return error

        # Validate required fields
        if 'name' not in data:
            return error_response('name is required', 400)

        # TODO: Implement your creation logic
        new_item = {
            'id': 'generated_id',
            'name': data['name'],
            'description': data.get('description'),
            'created_at': datetime.utcnow().isoformat()
        }

        logger.info(f"Created item: {new_item['id']}")
        return jsonify(success_response(new_item)), 201

    except Exception as e:
        logger.error(f"Error creating item: {e}")
        return error_response(str(e), 500)


@{{feature_name}}_bp.route('/<item_id>', methods=['PUT'])
def update_item(item_id: str):
    """
    Update existing item.

    PUT /{{feature_name}}/<item_id>

    Request Body:
        {
            "name": "New name",
            "description": "New description"
        }

    Returns:
        {
            "success": true,
            "data": {...}
        }
    """
    try:
        data, error = get_json_or_error()
        if error:
            return error

        # TODO: Check if item exists
        # TODO: Implement your update logic

        updated_item = {
            'id': item_id,
            'name': data.get('name'),
            'updated_at': datetime.utcnow().isoformat()
        }

        logger.info(f"Updated item: {item_id}")
        return jsonify(success_response(updated_item))

    except Exception as e:
        logger.error(f"Error updating item {item_id}: {e}")
        return error_response(str(e), 500)


@{{feature_name}}_bp.route('/<item_id>', methods=['DELETE'])
def delete_item(item_id: str):
    """
    Delete item.

    DELETE /{{feature_name}}/<item_id>

    Returns:
        {
            "success": true,
            "data": null
        }
    """
    try:
        # TODO: Check if item exists
        # TODO: Implement your delete logic

        logger.info(f"Deleted item: {item_id}")
        return jsonify(success_response(None, f'Item {item_id} deleted'))

    except Exception as e:
        logger.error(f"Error deleting item {item_id}: {e}")
        return error_response(str(e), 500)


# ═══════════════════════════════════════════════════════════════
# CUSTOM ENDPOINTS (Add your specific operations here)
# ═══════════════════════════════════════════════════════════════


@{{feature_name}}_bp.route('/<item_id>/action', methods=['POST'])
def perform_action(item_id: str):
    """
    Perform custom action on item.

    POST /{{feature_name}}/<item_id>/action

    Request Body:
        {
            "action": "action_name",
            "params": {...}
        }
    """
    try:
        data, error = get_json_or_error()
        if error:
            return error

        action = data.get('action')
        params = data.get('params', {})

        # TODO: Implement your action logic
        result = {'action': action, 'status': 'completed'}

        return jsonify(success_response(result))

    except Exception as e:
        logger.error(f"Error performing action on {item_id}: {e}")
        return error_response(str(e), 500)


# ═══════════════════════════════════════════════════════════════
# ERROR HANDLERS (Optional - Blueprint-level)
# ═══════════════════════════════════════════════════════════════


@{{feature_name}}_bp.errorhandler(404)
def not_found(error):
    return error_response('Resource not found', 404)


@{{feature_name}}_bp.errorhandler(500)
def internal_error(error):
    return error_response('Internal server error', 500)
