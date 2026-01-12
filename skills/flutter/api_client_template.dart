// ignore_for_file: avoid_print

// ═══════════════════════════════════════════════════════════════
// API CLIENT TEMPLATE
// HTTP client with retry, caching, and error handling
// ═══════════════════════════════════════════════════════════════
//
// Usage:
// 1. Copy to your project's lib/services/ directory
// 2. Replace ApiName with your API name (e.g., Trading)
// 3. Replace {{API_BASE_URL}} with your base URL
// 4. Customize endpoints and models
//
// ═══════════════════════════════════════════════════════════════

import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

// ═══════════════════════════════════════════════════════════════
// API CONFIGURATION
// ═══════════════════════════════════════════════════════════════

class ApiConfig {
  static const String baseUrl = '{{API_BASE_URL}}';
  static const Duration timeout = Duration(seconds: 30);
  static const int maxRetries = 3;
  static const Duration retryDelay = Duration(seconds: 1);

  // Headers
  static Map<String, String> get defaultHeaders => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
}

// ═══════════════════════════════════════════════════════════════
// API EXCEPTIONS
// ═══════════════════════════════════════════════════════════════

class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic data;

  ApiException(this.message, {this.statusCode, this.data});

  @override
  String toString() => 'ApiException: $message (status: $statusCode)';
}

class NetworkException extends ApiException {
  NetworkException([String? message])
    : super(message ?? 'Network error occurred');
}

class TimeoutException extends ApiException {
  TimeoutException([String? message])
    : super(message ?? 'Request timed out');
}

class ServerException extends ApiException {
  ServerException(int statusCode, [String? message])
    : super(message ?? 'Server error', statusCode: statusCode);
}

class ValidationException extends ApiException {
  final Map<String, dynamic>? errors;

  ValidationException(super.message, {this.errors})
    : super(statusCode: 400);
}

// ═══════════════════════════════════════════════════════════════
// API RESPONSE WRAPPER
// ═══════════════════════════════════════════════════════════════

class ApiResponse<T> {
  final bool success;
  final T? data;
  final String? message;
  final Map<String, dynamic>? errors;
  final int statusCode;

  ApiResponse({
    required this.success,
    this.data,
    this.message,
    this.errors,
    required this.statusCode,
  });

  factory ApiResponse.success(T data, {int statusCode = 200}) {
    return ApiResponse(
      success: true,
      data: data,
      statusCode: statusCode,
    );
  }

  factory ApiResponse.error(String message, {
    int statusCode = 500,
    Map<String, dynamic>? errors,
  }) {
    return ApiResponse(
      success: false,
      message: message,
      errors: errors,
      statusCode: statusCode,
    );
  }
}

// ═══════════════════════════════════════════════════════════════
// HTTP CLIENT WITH RETRY
// ═══════════════════════════════════════════════════════════════

class HttpClientWithRetry {
  final http.Client _client;
  final int maxRetries;
  final Duration retryDelay;

  HttpClientWithRetry({
    http.Client? client,
    this.maxRetries = ApiConfig.maxRetries,
    this.retryDelay = ApiConfig.retryDelay,
  }) : _client = client ?? http.Client();

  Future<http.Response> get(
    Uri url, {
    Map<String, String>? headers,
  }) async {
    return _executeWithRetry(
      () => _client.get(url, headers: headers),
    );
  }

  Future<http.Response> post(
    Uri url, {
    Map<String, String>? headers,
    Object? body,
  }) async {
    return _executeWithRetry(
      () => _client.post(url, headers: headers, body: body),
    );
  }

  Future<http.Response> put(
    Uri url, {
    Map<String, String>? headers,
    Object? body,
  }) async {
    return _executeWithRetry(
      () => _client.put(url, headers: headers, body: body),
    );
  }

  Future<http.Response> delete(
    Uri url, {
    Map<String, String>? headers,
  }) async {
    return _executeWithRetry(
      () => _client.delete(url, headers: headers),
    );
  }

  Future<http.Response> _executeWithRetry(
    Future<http.Response> Function() request,
  ) async {
    int attempts = 0;

    while (true) {
      try {
        attempts++;
        final response = await request().timeout(ApiConfig.timeout);

        // Retry on server errors (5xx)
        if (response.statusCode >= 500 && attempts < maxRetries) {
          await Future.delayed(retryDelay * attempts);
          continue;
        }

        return response;
      } on SocketException {
        if (attempts >= maxRetries) {
          throw NetworkException();
        }
        await Future.delayed(retryDelay * attempts);
      } on TimeoutException {
        if (attempts >= maxRetries) {
          throw TimeoutException();
        }
        await Future.delayed(retryDelay * attempts);
      }
    }
  }

  void close() {
    _client.close();
  }
}

// ═══════════════════════════════════════════════════════════════
// RESPONSE CACHE
// ═══════════════════════════════════════════════════════════════

class ResponseCache {
  final Map<String, _CacheEntry> _cache = {};
  final Duration defaultTtl;

  ResponseCache({this.defaultTtl = const Duration(minutes: 5)});

  T? get<T>(String key) {
    final entry = _cache[key];
    if (entry == null) return null;

    if (entry.isExpired) {
      _cache.remove(key);
      return null;
    }

    return entry.data as T?;
  }

  void set<T>(String key, T data, {Duration? ttl}) {
    _cache[key] = _CacheEntry(
      data: data,
      expiresAt: DateTime.now().add(ttl ?? defaultTtl),
    );
  }

  void remove(String key) {
    _cache.remove(key);
  }

  void clear() {
    _cache.clear();
  }

  void clearExpired() {
    _cache.removeWhere((_, entry) => entry.isExpired);
  }
}

class _CacheEntry {
  final dynamic data;
  final DateTime expiresAt;

  _CacheEntry({required this.data, required this.expiresAt});

  bool get isExpired => DateTime.now().isAfter(expiresAt);
}

// ═══════════════════════════════════════════════════════════════
// BASE API CLIENT
// ═══════════════════════════════════════════════════════════════

abstract class BaseApiClient {
  final HttpClientWithRetry _httpClient;
  final ResponseCache _cache;
  final String baseUrl;
  String? _authToken;

  BaseApiClient({
    String? baseUrl,
    HttpClientWithRetry? httpClient,
    ResponseCache? cache,
  }) : baseUrl = baseUrl ?? ApiConfig.baseUrl,
       _httpClient = httpClient ?? HttpClientWithRetry(),
       _cache = cache ?? ResponseCache();

  // Authentication
  void setAuthToken(String token) {
    _authToken = token;
  }

  void clearAuthToken() {
    _authToken = null;
  }

  // Headers
  Map<String, String> get _headers {
    final headers = Map<String, String>.from(ApiConfig.defaultHeaders);
    if (_authToken != null) {
      headers['Authorization'] = 'Bearer $_authToken';
    }
    return headers;
  }

  // URL builder
  Uri _buildUrl(String endpoint, {Map<String, dynamic>? queryParams}) {
    final uri = Uri.parse('$baseUrl$endpoint');
    if (queryParams != null && queryParams.isNotEmpty) {
      return uri.replace(queryParameters: queryParams.map(
        (key, value) => MapEntry(key, value.toString()),
      ));
    }
    return uri;
  }

  // Response parser
  dynamic _parseResponse(http.Response response) {
    if (response.body.isEmpty) return null;

    try {
      return jsonDecode(response.body);
    } catch (e) {
      return response.body;
    }
  }

  // Error handler
  Never _handleError(http.Response response) {
    final data = _parseResponse(response);
    final message = data is Map ? data['message'] ?? data['error'] : 'Unknown error';

    switch (response.statusCode) {
      case 400:
        throw ValidationException(
          message,
          errors: data is Map ? data['errors'] : null,
        );
      case 401:
        throw ApiException('Unauthorized', statusCode: 401);
      case 403:
        throw ApiException('Forbidden', statusCode: 403);
      case 404:
        throw ApiException('Not found', statusCode: 404);
      case 429:
        throw ApiException('Too many requests', statusCode: 429);
      default:
        throw ServerException(response.statusCode, message);
    }
  }

  // HTTP methods
  Future<T> get<T>(
    String endpoint, {
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
    bool useCache = false,
    Duration? cacheTtl,
  }) async {
    final url = _buildUrl(endpoint, queryParams: queryParams);
    final cacheKey = url.toString();

    // Check cache
    if (useCache) {
      final cached = _cache.get<T>(cacheKey);
      if (cached != null) return cached;
    }

    final response = await _httpClient.get(url, headers: _headers);

    if (response.statusCode >= 200 && response.statusCode < 300) {
      final data = _parseResponse(response);
      final result = fromJson != null ? fromJson(data) : data as T;

      // Store in cache
      if (useCache) {
        _cache.set(cacheKey, result, ttl: cacheTtl);
      }

      return result;
    }

    _handleError(response);
  }

  Future<T> post<T>(
    String endpoint, {
    dynamic body,
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
  }) async {
    final url = _buildUrl(endpoint, queryParams: queryParams);
    final response = await _httpClient.post(
      url,
      headers: _headers,
      body: body != null ? jsonEncode(body) : null,
    );

    if (response.statusCode >= 200 && response.statusCode < 300) {
      final data = _parseResponse(response);
      return fromJson != null ? fromJson(data) : data as T;
    }

    _handleError(response);
  }

  Future<T> put<T>(
    String endpoint, {
    dynamic body,
    Map<String, dynamic>? queryParams,
    T Function(dynamic)? fromJson,
  }) async {
    final url = _buildUrl(endpoint, queryParams: queryParams);
    final response = await _httpClient.put(
      url,
      headers: _headers,
      body: body != null ? jsonEncode(body) : null,
    );

    if (response.statusCode >= 200 && response.statusCode < 300) {
      final data = _parseResponse(response);
      return fromJson != null ? fromJson(data) : data as T;
    }

    _handleError(response);
  }

  Future<void> delete(
    String endpoint, {
    Map<String, dynamic>? queryParams,
  }) async {
    final url = _buildUrl(endpoint, queryParams: queryParams);
    final response = await _httpClient.delete(url, headers: _headers);

    if (response.statusCode < 200 || response.statusCode >= 300) {
      _handleError(response);
    }
  }

  // Cache management
  void invalidateCache([String? key]) {
    if (key != null) {
      _cache.remove(key);
    } else {
      _cache.clear();
    }
  }

  void dispose() {
    _httpClient.close();
    _cache.clear();
  }
}

// ═══════════════════════════════════════════════════════════════
// EXAMPLE: ApiName API CLIENT
// ═══════════════════════════════════════════════════════════════

class ApiNameApiClient extends BaseApiClient {
  ApiNameApiClient({super.baseUrl});

  // Health check
  Future<Map<String, dynamic>> healthCheck() async {
    return get('/health', useCache: true, cacheTtl: const Duration(seconds: 10));
  }

  // CRUD operations example
  Future<List<Map<String, dynamic>>> getItems({
    int page = 1,
    int perPage = 20,
  }) async {
    final response = await get<Map<String, dynamic>>(
      '/items',
      queryParams: {'page': page, 'per_page': perPage},
    );
    return List<Map<String, dynamic>>.from(response['items'] ?? []);
  }

  Future<Map<String, dynamic>> getItem(String id) async {
    return get('/items/$id');
  }

  Future<Map<String, dynamic>> createItem(Map<String, dynamic> data) async {
    return post('/items', body: data);
  }

  Future<Map<String, dynamic>> updateItem(String id, Map<String, dynamic> data) async {
    return put('/items/$id', body: data);
  }

  Future<void> deleteItem(String id) async {
    return delete('/items/$id');
  }
}

// ═══════════════════════════════════════════════════════════════
// USAGE EXAMPLE
// ═══════════════════════════════════════════════════════════════

void main() async {
  final client = ApiNameApiClient(baseUrl: 'http://localhost:5050');

  try {
    // Health check
    final health = await client.healthCheck();
    print('API Status: ${health['status']}');

    // Get items with pagination
    final items = await client.getItems(page: 1, perPage: 10);
    print('Got ${items.length} items');

    // Create item
    final newItem = await client.createItem({
      'name': 'Test Item',
      'value': 42,
    });
    print('Created: ${newItem['id']}');

    // Update item
    final updated = await client.updateItem(newItem['id'], {
      'name': 'Updated Item',
    });
    print('Updated: ${updated['name']}');

    // Delete item
    await client.deleteItem(newItem['id']);
    print('Deleted');

  } on ValidationException catch (e) {
    print('Validation error: ${e.message}');
    print('Errors: ${e.errors}');
  } on NetworkException catch (e) {
    print('Network error: ${e.message}');
  } on ApiException catch (e) {
    print('API error: ${e.message} (${e.statusCode})');
  } finally {
    client.dispose();
  }
}
