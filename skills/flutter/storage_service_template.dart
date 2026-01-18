/// Dual-Layer Storage Service Template
///
/// Combines SharedPreferences (simple) + Hive (complex data)
/// Features: Type-safe operations, lazy initialization, generic methods
///
/// Usage:
/// 1. Add shared_preferences and hive_flutter to pubspec.yaml
/// 2. Initialize in main.dart: await StorageService.initialize()
/// 3. Use via Riverpod provider

import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Abstract storage interface
abstract class BaseStorage {
  Future<void> setValue<T>(String key, T value);
  Future<T?> getValue<T>(String key);
  Future<bool> hasKey(String key);
  Future<void> remove(String key);
  Future<void> clear();
}

/// SharedPreferences storage for simple key-value pairs
class PreferencesStorage implements BaseStorage {
  SharedPreferences? _prefs;

  Future<SharedPreferences> get prefs async {
    _prefs ??= await SharedPreferences.getInstance();
    return _prefs!;
  }

  @override
  Future<void> setValue<T>(String key, T value) async {
    final p = await prefs;
    if (value is String) {
      await p.setString(key, value);
    } else if (value is int) {
      await p.setInt(key, value);
    } else if (value is double) {
      await p.setDouble(key, value);
    } else if (value is bool) {
      await p.setBool(key, value);
    } else if (value is List<String>) {
      await p.setStringList(key, value);
    } else {
      // Fallback to JSON for complex types
      await p.setString(key, json.encode(value));
    }
  }

  @override
  Future<T?> getValue<T>(String key) async {
    final p = await prefs;
    final value = p.get(key);

    if (value == null) return null;

    if (T == String || T == int || T == double || T == bool) {
      return value as T?;
    } else if (value is String) {
      // Try to decode JSON
      try {
        return json.decode(value) as T?;
      } catch (_) {
        return value as T?;
      }
    }

    return value as T?;
  }

  @override
  Future<bool> hasKey(String key) async {
    final p = await prefs;
    return p.containsKey(key);
  }

  @override
  Future<void> remove(String key) async {
    final p = await prefs;
    await p.remove(key);
  }

  @override
  Future<void> clear() async {
    final p = await prefs;
    await p.clear();
  }
}

/// Hive storage for complex data and larger datasets
class HiveStorage implements BaseStorage {
  static const String _defaultBoxName = 'app_storage';
  final Map<String, Box> _boxes = {};

  /// Initialize Hive
  static Future<void> initialize() async {
    await Hive.initFlutter();
  }

  /// Get or open a box
  Future<Box<T>> _getBox<T>(String boxName) async {
    if (_boxes.containsKey(boxName) && _boxes[boxName]!.isOpen) {
      return _boxes[boxName] as Box<T>;
    }

    final box = await Hive.openBox<T>(boxName);
    _boxes[boxName] = box;
    return box;
  }

  @override
  Future<void> setValue<T>(String key, T value, {String? boxName}) async {
    final box = await _getBox<T>(boxName ?? _defaultBoxName);
    await box.put(key, value);
  }

  @override
  Future<T?> getValue<T>(String key, {String? boxName}) async {
    final box = await _getBox<T>(boxName ?? _defaultBoxName);
    return box.get(key);
  }

  @override
  Future<bool> hasKey(String key, {String? boxName}) async {
    final box = await _getBox(boxName ?? _defaultBoxName);
    return box.containsKey(key);
  }

  @override
  Future<void> remove(String key, {String? boxName}) async {
    final box = await _getBox(boxName ?? _defaultBoxName);
    await box.delete(key);
  }

  @override
  Future<void> clear({String? boxName}) async {
    final box = await _getBox(boxName ?? _defaultBoxName);
    await box.clear();
  }

  /// Get all keys in a box
  Future<List<String>> getKeys({String? boxName}) async {
    final box = await _getBox(boxName ?? _defaultBoxName);
    return box.keys.cast<String>().toList();
  }

  /// Get all values in a box
  Future<List<T>> getAll<T>({String? boxName}) async {
    final box = await _getBox<T>(boxName ?? _defaultBoxName);
    return box.values.toList();
  }

  /// Watch for changes
  Stream<BoxEvent> watch({String? boxName, String? key}) async* {
    final box = await _getBox(boxName ?? _defaultBoxName);
    yield* box.watch(key: key);
  }

  /// Close all boxes
  Future<void> closeAll() async {
    for (final box in _boxes.values) {
      if (box.isOpen) await box.close();
    }
    _boxes.clear();
  }
}

/// Combined storage service using both Preferences and Hive
class StorageService {
  final PreferencesStorage _preferences;
  final HiveStorage _hive;

  StorageService({
    PreferencesStorage? preferences,
    HiveStorage? hive,
  })  : _preferences = preferences ?? PreferencesStorage(),
        _hive = hive ?? HiveStorage();

  /// Initialize all storage systems
  static Future<void> initialize() async {
    await HiveStorage.initialize();
  }

  // ============ PREFERENCES (simple key-value) ============

  /// Save to preferences
  Future<void> savePreference<T>(String key, T value) async {
    await _preferences.setValue(key, value);
  }

  /// Get from preferences
  Future<T?> getPreference<T>(String key) async {
    return await _preferences.getValue<T>(key);
  }

  /// Remove from preferences
  Future<void> removePreference(String key) async {
    await _preferences.remove(key);
  }

  // ============ HIVE (complex data) ============

  /// Save to Hive
  Future<void> saveData<T>(String key, T value, {String? boxName}) async {
    await _hive.setValue(key, value, boxName: boxName);
  }

  /// Get from Hive
  Future<T?> getData<T>(String key, {String? boxName}) async {
    return await _hive.getValue<T>(key, boxName: boxName);
  }

  /// Remove from Hive
  Future<void> removeData(String key, {String? boxName}) async {
    await _hive.remove(key, boxName: boxName);
  }

  /// Get all data from a box
  Future<List<T>> getAllData<T>({String? boxName}) async {
    return await _hive.getAll<T>(boxName: boxName);
  }

  /// Watch for changes
  Stream<BoxEvent> watchData({String? boxName, String? key}) {
    return _hive.watch(boxName: boxName, key: key);
  }

  // ============ CONVENIENCE METHODS ============

  /// Save user session
  Future<void> saveSession(Map<String, dynamic> session) async {
    await _preferences.setValue('user_session', json.encode(session));
  }

  /// Get user session
  Future<Map<String, dynamic>?> getSession() async {
    final sessionStr = await _preferences.getValue<String>('user_session');
    if (sessionStr == null) return null;
    return json.decode(sessionStr) as Map<String, dynamic>;
  }

  /// Clear session
  Future<void> clearSession() async {
    await _preferences.remove('user_session');
  }

  /// Save app settings
  Future<void> saveSettings(Map<String, dynamic> settings) async {
    await _hive.setValue('app_settings', settings, boxName: 'settings');
  }

  /// Get app settings
  Future<Map<String, dynamic>?> getSettings() async {
    return await _hive.getValue<Map<String, dynamic>>('app_settings', boxName: 'settings');
  }

  /// Check first launch
  Future<bool> isFirstLaunch() async {
    final launched = await _preferences.getValue<bool>('first_launch_done');
    return launched != true;
  }

  /// Mark first launch done
  Future<void> markFirstLaunchDone() async {
    await _preferences.setValue('first_launch_done', true);
  }

  /// Clear all storage
  Future<void> clearAll() async {
    await _preferences.clear();
    await _hive.clear();
  }

  /// Close storage (call on app exit)
  Future<void> close() async {
    await _hive.closeAll();
  }
}

/// Provider
final storageServiceProvider = Provider<StorageService>((ref) {
  final service = StorageService();
  ref.onDispose(() => service.close());
  return service;
});

/// Session provider
final sessionProvider = FutureProvider<Map<String, dynamic>?>((ref) async {
  final storage = ref.watch(storageServiceProvider);
  return storage.getSession();
});

/// Settings provider
final settingsProvider = FutureProvider<Map<String, dynamic>?>((ref) async {
  final storage = ref.watch(storageServiceProvider);
  return storage.getSettings();
});
