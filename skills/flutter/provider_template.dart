// ═══════════════════════════════════════════════════════════════
// FEATURE PROVIDER TEMPLATE
// State management using ChangeNotifier pattern
// ═══════════════════════════════════════════════════════════════
//
// Usage:
// 1. Copy this file to lib/providers/your_feature_provider.dart
// 2. Replace "FeatureName" with your feature name
// 3. Replace "FeatureModel" with your model class
// 4. Add to providers list in main.dart:
//    ChangeNotifierProvider(create: (_) => FeatureNameProvider()),
//
// ═══════════════════════════════════════════════════════════════

import 'package:flutter/foundation.dart';

// ═══════════════════════════════════════════════════════════════
// EXAMPLE MODEL (Replace with your model import)
// Import: import '../models/your_model.dart';
// ═══════════════════════════════════════════════════════════════

class FeatureModel {
  final String id;
  final String name;
  final String status;
  final DateTime createdAt;

  FeatureModel({
    required this.id,
    required this.name,
    this.status = 'active',
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory FeatureModel.fromJson(Map<String, dynamic> json) {
    return FeatureModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      status: json['status'] ?? 'active',
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'status': status,
        'created_at': createdAt.toIso8601String(),
      };
}

// ═══════════════════════════════════════════════════════════════
// EXAMPLE SERVICE (Replace with your service import)
// Import: import '../services/your_service.dart';
// ═══════════════════════════════════════════════════════════════

class FeatureService {
  // Replace with actual API calls
  Future<Map<String, dynamic>> fetchAll() async {
    // Example: return await apiClient.get('/items');
    await Future.delayed(const Duration(milliseconds: 500));
    return {
      'success': true,
      'data': [
        {'id': '1', 'name': 'Item 1', 'status': 'active'},
        {'id': '2', 'name': 'Item 2', 'status': 'active'},
      ]
    };
  }

  Future<Map<String, dynamic>> create(Map<String, dynamic> data) async {
    await Future.delayed(const Duration(milliseconds: 300));
    return {'success': true, 'data': {...data, 'id': DateTime.now().millisecondsSinceEpoch.toString()}};
  }

  Future<Map<String, dynamic>> update(String id, Map<String, dynamic> data) async {
    await Future.delayed(const Duration(milliseconds: 300));
    return {'success': true, 'data': data};
  }

  Future<Map<String, dynamic>> delete(String id) async {
    await Future.delayed(const Duration(milliseconds: 300));
    return {'success': true};
  }
}

// ═══════════════════════════════════════════════════════════════
// PROVIDER IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════

/// FeatureName state management provider
///
/// Manages:
/// - Loading states
/// - Data caching
/// - Error handling
/// - Refresh functionality
class FeatureNameProvider extends ChangeNotifier {
  // ═══════════════════════════════════════════════════════════════
  // DEPENDENCIES
  // ═══════════════════════════════════════════════════════════════

  final FeatureService _service = FeatureService();

  // ═══════════════════════════════════════════════════════════════
  // STATE
  // ═══════════════════════════════════════════════════════════════

  /// Current data
  List<FeatureModel> _items = [];
  List<FeatureModel> get items => _items;

  /// Selected item (if applicable)
  FeatureModel? _selected;
  FeatureModel? get selected => _selected;

  /// Loading state
  bool _isLoading = false;
  bool get isLoading => _isLoading;

  /// Error state
  String? _error;
  String? get error => _error;
  bool get hasError => _error != null;

  /// Last refresh time
  DateTime? _lastRefresh;
  DateTime? get lastRefresh => _lastRefresh;

  // ═══════════════════════════════════════════════════════════════
  // INITIALIZATION
  // ═══════════════════════════════════════════════════════════════

  FeatureNameProvider() {
    // Optional: Auto-load data on creation
    // loadData();
  }

  // ═══════════════════════════════════════════════════════════════
  // PUBLIC METHODS
  // ═══════════════════════════════════════════════════════════════

  /// Load all data from service
  Future<void> loadData() async {
    _setLoading(true);
    _clearError();

    try {
      final result = await _service.fetchAll();

      if (result['success'] == true) {
        _items = (result['data'] as List)
            .map((json) => FeatureModel.fromJson(json))
            .toList();
        _lastRefresh = DateTime.now();
      } else {
        _setError(result['error'] ?? 'Failed to load data');
      }
    } catch (e) {
      _setError('Connection error: $e');
    } finally {
      _setLoading(false);
    }
  }

  /// Refresh data (alias for loadData with clear)
  Future<void> refresh() async {
    _items = [];
    notifyListeners();
    await loadData();
  }

  /// Select an item
  void selectItem(FeatureModel? item) {
    _selected = item;
    notifyListeners();
  }

  /// Add new item
  Future<bool> addItem(FeatureModel item) async {
    _setLoading(true);
    _clearError();

    try {
      final result = await _service.create(item.toJson());

      if (result['success'] == true) {
        _items.add(FeatureModel.fromJson(result['data']));
        notifyListeners();
        return true;
      } else {
        _setError(result['error'] ?? 'Failed to add item');
        return false;
      }
    } catch (e) {
      _setError('Connection error: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Update existing item
  Future<bool> updateItem(String id, FeatureModel item) async {
    _setLoading(true);
    _clearError();

    try {
      final result = await _service.update(id, item.toJson());

      if (result['success'] == true) {
        final index = _items.indexWhere((i) => i.id == id);
        if (index >= 0) {
          _items[index] = FeatureModel.fromJson(result['data']);
          notifyListeners();
        }
        return true;
      } else {
        _setError(result['error'] ?? 'Failed to update item');
        return false;
      }
    } catch (e) {
      _setError('Connection error: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Delete item
  Future<bool> deleteItem(String id) async {
    _setLoading(true);
    _clearError();

    try {
      final result = await _service.delete(id);

      if (result['success'] == true) {
        _items.removeWhere((i) => i.id == id);
        if (_selected?.id == id) _selected = null;
        notifyListeners();
        return true;
      } else {
        _setError(result['error'] ?? 'Failed to delete item');
        return false;
      }
    } catch (e) {
      _setError('Connection error: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Clear error state
  void clearError() {
    _clearError();
  }

  // ═══════════════════════════════════════════════════════════════
  // PRIVATE METHODS
  // ═══════════════════════════════════════════════════════════════

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  void _setError(String message) {
    _error = message;
    notifyListeners();
  }

  void _clearError() {
    _error = null;
    // Don't notify - typically called before an operation
  }

  // ═══════════════════════════════════════════════════════════════
  // COMPUTED PROPERTIES (Optional)
  // ═══════════════════════════════════════════════════════════════

  /// Count of items
  int get itemCount => _items.length;

  /// Check if data is stale (older than 5 minutes)
  bool get isStale {
    if (_lastRefresh == null) return true;
    return DateTime.now().difference(_lastRefresh!).inMinutes > 5;
  }

  /// Filter items (example)
  List<FeatureModel> filterByStatus(String status) {
    return _items.where((item) => item.status == status).toList();
  }
}
