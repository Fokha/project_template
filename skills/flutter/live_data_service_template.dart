/// Live Data Service Template
///
/// Multi-source API aggregation service for real-time data
/// Sources: Multiple APIs with fallback support
///
/// Usage:
/// 1. Replace {{SERVICE_NAME}} with your service name (e.g., LivePrice, LiveWeather)
/// 2. Replace {{MODEL_NAME}} with your data model (e.g., MarketSymbol, WeatherData)
/// 3. Replace {{API_ENDPOINTS}} with your API configurations
/// 4. Customize the data sources and parsing logic

import 'dart:async';
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;

/// Data model for {{MODEL_NAME}}
class {{MODEL_NAME}} {
  final String id;
  final String name;
  final String category;
  final double value;
  final double changePercent;
  final DateTime lastUpdated;

  {{MODEL_NAME}}({
    required this.id,
    required this.name,
    required this.category,
    required this.value,
    this.changePercent = 0.0,
    DateTime? lastUpdated,
  }) : lastUpdated = lastUpdated ?? DateTime.now();

  {{MODEL_NAME}} copyWith({
    String? id,
    String? name,
    String? category,
    double? value,
    double? changePercent,
    DateTime? lastUpdated,
  }) {
    return {{MODEL_NAME}}(
      id: id ?? this.id,
      name: name ?? this.name,
      category: category ?? this.category,
      value: value ?? this.value,
      changePercent: changePercent ?? this.changePercent,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }
}

/// Service for fetching live data from multiple sources
class {{SERVICE_NAME}}Service {
  final http.Client _client;
  Timer? _refreshTimer;
  final _controller = StreamController<List<{{MODEL_NAME}}>>.broadcast();

  // API endpoints - customize these
  static const String _primaryApiUrl = '{{PRIMARY_API_URL}}';
  static const String _fallbackApiUrl = '{{FALLBACK_API_URL}}';

  {{SERVICE_NAME}}Service({http.Client? client}) : _client = client ?? http.Client();

  Stream<List<{{MODEL_NAME}}>> get stream => _controller.stream;

  /// Start auto-refresh with specified interval
  void startAutoRefresh({Duration interval = const Duration(seconds: 30)}) {
    _refreshTimer?.cancel();
    _refreshTimer = Timer.periodic(interval, (_) => refresh());
    refresh(); // Initial fetch
  }

  /// Stop auto-refresh
  void stopAutoRefresh() {
    _refreshTimer?.cancel();
    _refreshTimer = null;
  }

  /// Fetch all data from multiple sources
  Future<List<{{MODEL_NAME}}>> fetchAll() async {
    final List<{{MODEL_NAME}}> results = [];

    // Fetch from primary source
    try {
      final primaryData = await _fetchFromPrimarySource();
      results.addAll(primaryData);
    } catch (e) {
      print('Primary source failed: $e');
    }

    // Fetch from fallback source if needed
    if (results.isEmpty) {
      try {
        final fallbackData = await _fetchFromFallbackSource();
        results.addAll(fallbackData);
      } catch (e) {
        print('Fallback source failed: $e');
      }
    }

    // Use defaults if all sources fail
    if (results.isEmpty) {
      results.addAll(_getDefaultData());
    }

    return results;
  }

  /// Fetch from primary API source
  Future<List<{{MODEL_NAME}}>> _fetchFromPrimarySource() async {
    final response = await _client.get(
      Uri.parse(_primaryApiUrl),
      headers: {'Accept': 'application/json'},
    ).timeout(const Duration(seconds: 10));

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return _parsePrimaryResponse(data);
    }
    throw Exception('Primary API failed: ${response.statusCode}');
  }

  /// Fetch from fallback API source
  Future<List<{{MODEL_NAME}}>> _fetchFromFallbackSource() async {
    final response = await _client.get(
      Uri.parse(_fallbackApiUrl),
      headers: {'Accept': 'application/json'},
    ).timeout(const Duration(seconds: 10));

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return _parseFallbackResponse(data);
    }
    throw Exception('Fallback API failed: ${response.statusCode}');
  }

  /// Parse response from primary API
  List<{{MODEL_NAME}}> _parsePrimaryResponse(dynamic data) {
    // Customize this based on your API response structure
    final List<{{MODEL_NAME}}> items = [];

    if (data is Map<String, dynamic>) {
      data.forEach((key, value) {
        items.add({{MODEL_NAME}}(
          id: key,
          name: key.toUpperCase(),
          category: 'primary',
          value: (value as num).toDouble(),
        ));
      });
    }

    return items;
  }

  /// Parse response from fallback API
  List<{{MODEL_NAME}}> _parseFallbackResponse(dynamic data) {
    // Customize this based on your fallback API response structure
    final List<{{MODEL_NAME}}> items = [];

    if (data is List) {
      for (final item in data) {
        items.add({{MODEL_NAME}}(
          id: item['id'] ?? '',
          name: item['name'] ?? '',
          category: item['category'] ?? 'fallback',
          value: (item['value'] as num?)?.toDouble() ?? 0.0,
        ));
      }
    }

    return items;
  }

  /// Get default data when all sources fail
  List<{{MODEL_NAME}}> _getDefaultData() {
    return [
      {{MODEL_NAME}}(id: 'default_1', name: 'Default Item 1', category: 'default', value: 0.0),
      {{MODEL_NAME}}(id: 'default_2', name: 'Default Item 2', category: 'default', value: 0.0),
    ];
  }

  /// Refresh data and emit to stream
  Future<void> refresh() async {
    try {
      final data = await fetchAll();
      _controller.add(data);
    } catch (e) {
      _controller.addError(e);
    }
  }

  void dispose() {
    stopAutoRefresh();
    _controller.close();
    _client.close();
  }
}

/// State for live data
class {{SERVICE_NAME}}State {
  final List<{{MODEL_NAME}}> items;
  final bool isLoading;
  final String? error;
  final DateTime? lastUpdated;

  const {{SERVICE_NAME}}State({
    this.items = const [],
    this.isLoading = false,
    this.error,
    this.lastUpdated,
  });

  {{SERVICE_NAME}}State copyWith({
    List<{{MODEL_NAME}}>? items,
    bool? isLoading,
    String? error,
    DateTime? lastUpdated,
  }) {
    return {{SERVICE_NAME}}State(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }
}

/// Notifier for live data state management
class {{SERVICE_NAME}}Notifier extends StateNotifier<{{SERVICE_NAME}}State> {
  final {{SERVICE_NAME}}Service _service;
  StreamSubscription? _subscription;

  {{SERVICE_NAME}}Notifier(this._service) : super(const {{SERVICE_NAME}}State()) {
    _init();
  }

  void _init() {
    state = state.copyWith(isLoading: true);

    _subscription = _service.stream.listen(
      (items) {
        state = {{SERVICE_NAME}}State(
          items: items,
          isLoading: false,
          lastUpdated: DateTime.now(),
        );
      },
      onError: (error) {
        state = state.copyWith(
          isLoading: false,
          error: error.toString(),
        );
      },
    );

    _service.startAutoRefresh();
  }

  Future<void> refresh() async {
    state = state.copyWith(isLoading: true);
    await _service.refresh();
  }

  List<{{MODEL_NAME}}> getByCategory(String category) {
    return state.items.where((i) => i.category == category).toList();
  }

  @override
  void dispose() {
    _subscription?.cancel();
    _service.dispose();
    super.dispose();
  }
}

/// Providers
final {{SERVICE_NAME_LOWER}}ServiceProvider = Provider<{{SERVICE_NAME}}Service>((ref) {
  final service = {{SERVICE_NAME}}Service();
  ref.onDispose(() => service.dispose());
  return service;
});

final {{SERVICE_NAME_LOWER}}Provider = StateNotifierProvider<{{SERVICE_NAME}}Notifier, {{SERVICE_NAME}}State>((ref) {
  final service = ref.watch({{SERVICE_NAME_LOWER}}ServiceProvider);
  return {{SERVICE_NAME}}Notifier(service);
});
