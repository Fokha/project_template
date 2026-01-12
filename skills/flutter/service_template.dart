// ═══════════════════════════════════════════════════════════════
// FeatureName SERVICE
// Business logic and API communication
// ═══════════════════════════════════════════════════════════════
//
// Usage:
// 1. Copy this file to lib/services/feature_name_service.dart
// 2. Replace FeatureName with your feature name
// 3. Update API_BASE_URL to your API endpoint
//
// ═══════════════════════════════════════════════════════════════

import 'dart:convert';
import 'package:http/http.dart' as http;

/// FeatureName service for API communication
///
/// All methods return:
/// ```dart
/// {
///   'success': true/false,
///   'data': dynamic,
///   'error': String?
/// }
/// ```
class FeatureNameService {
  // ═══════════════════════════════════════════════════════════════
  // CONFIGURATION
  // ═══════════════════════════════════════════════════════════════

  static const String _baseUrl = '{{API_BASE_URL}}';
  static const String _endpoint = '/feature_name';
  static const Duration _timeout = Duration(seconds: 30);

  // ═══════════════════════════════════════════════════════════════
  // CRUD OPERATIONS
  // ═══════════════════════════════════════════════════════════════

  /// Fetch all items
  ///
  /// Returns: `{'success': true, 'data': [...]}`
  Future<Map<String, dynamic>> fetchAll() async {
    try {
      final response = await http
          .get(Uri.parse('$_baseUrl$_endpoint'))
          .timeout(_timeout);

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }

  /// Fetch single item by ID
  ///
  /// Returns: `{'success': true, 'data': {...}}`
  Future<Map<String, dynamic>> fetchById(String id) async {
    try {
      final response = await http
          .get(Uri.parse('$_baseUrl$_endpoint/$id'))
          .timeout(_timeout);

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }

  /// Create new item
  ///
  /// Returns: `{'success': true, 'data': {...}}`
  Future<Map<String, dynamic>> create(Map<String, dynamic> data) async {
    try {
      final response = await http
          .post(
            Uri.parse('$_baseUrl$_endpoint'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(data),
          )
          .timeout(_timeout);

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }

  /// Update existing item
  ///
  /// Returns: `{'success': true, 'data': {...}}`
  Future<Map<String, dynamic>> update(
      String id, Map<String, dynamic> data) async {
    try {
      final response = await http
          .put(
            Uri.parse('$_baseUrl$_endpoint/$id'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(data),
          )
          .timeout(_timeout);

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }

  /// Delete item
  ///
  /// Returns: `{'success': true, 'data': null}`
  Future<Map<String, dynamic>> delete(String id) async {
    try {
      final response = await http
          .delete(Uri.parse('$_baseUrl$_endpoint/$id'))
          .timeout(_timeout);

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }

  // ═══════════════════════════════════════════════════════════════
  // CUSTOM OPERATIONS (Add your specific methods here)
  // ═══════════════════════════════════════════════════════════════

  /// Example: Fetch with query parameters
  Future<Map<String, dynamic>> fetchFiltered({
    String? status,
    int? limit,
    int? offset,
  }) async {
    try {
      final queryParams = <String, String>{};
      if (status != null) queryParams['status'] = status;
      if (limit != null) queryParams['limit'] = limit.toString();
      if (offset != null) queryParams['offset'] = offset.toString();

      final uri = Uri.parse('$_baseUrl$_endpoint')
          .replace(queryParameters: queryParams);

      final response = await http.get(uri).timeout(_timeout);
      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }

  /// Example: Custom action endpoint
  Future<Map<String, dynamic>> performAction(
      String id, String action, Map<String, dynamic>? params) async {
    try {
      final response = await http
          .post(
            Uri.parse('$_baseUrl$_endpoint/$id/$action'),
            headers: {'Content-Type': 'application/json'},
            body: params != null ? jsonEncode(params) : null,
          )
          .timeout(_timeout);

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }

  // ═══════════════════════════════════════════════════════════════
  // HEALTH CHECK
  // ═══════════════════════════════════════════════════════════════

  /// Test API connection
  Future<Map<String, dynamic>> healthCheck() async {
    try {
      final response = await http
          .get(Uri.parse('$_baseUrl/health'))
          .timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      }
      return {'success': false, 'error': 'API returned ${response.statusCode}'};
    } catch (e) {
      return {'success': false, 'error': 'Connection failed: $e'};
    }
  }

  // ═══════════════════════════════════════════════════════════════
  // RESPONSE HANDLING
  // ═══════════════════════════════════════════════════════════════

  /// Handle HTTP response
  Map<String, dynamic> _handleResponse(http.Response response) {
    try {
      final body = jsonDecode(response.body);

      if (response.statusCode >= 200 && response.statusCode < 300) {
        // API returns standard format
        if (body is Map && body.containsKey('success')) {
          return Map<String, dynamic>.from(body);
        }
        // API returns raw data
        return {'success': true, 'data': body, 'error': null};
      }

      // Error response
      final error = body is Map ? body['error'] ?? body['message'] : null;
      return {
        'success': false,
        'data': null,
        'error': error ?? 'Request failed with status ${response.statusCode}',
      };
    } catch (e) {
      return {
        'success': false,
        'data': null,
        'error': 'Failed to parse response: $e',
      };
    }
  }

  /// Handle exceptions
  Map<String, dynamic> _handleError(dynamic error) {
    String message;

    if (error.toString().contains('TimeoutException')) {
      message = 'Request timed out. Please try again.';
    } else if (error.toString().contains('SocketException')) {
      message = 'No internet connection.';
    } else {
      message = 'Connection error: $error';
    }

    return {'success': false, 'data': null, 'error': message};
  }
}
