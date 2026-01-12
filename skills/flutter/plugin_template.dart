// ignore_for_file: avoid_print

// ═══════════════════════════════════════════════════════════════
// PLUGIN TEMPLATE
// Extensible plugin architecture for Flutter apps
// ═══════════════════════════════════════════════════════════════
//
// Usage:
// 1. Copy to your project's lib/plugins/ directory
// 2. Replace {{PLUGIN_NAME}} with your plugin name
// 3. Implement the execute() method
// 4. Register with PluginRegistry
//
// ═══════════════════════════════════════════════════════════════

import 'dart:async';
import 'package:flutter/material.dart';

// ═══════════════════════════════════════════════════════════════
// PLUGIN TYPES
// ═══════════════════════════════════════════════════════════════

enum PluginType {
  analysis,     // Data analysis
  action,       // Perform actions
  integration,  // External integrations
  utility,      // Utility functions
  ui,           // UI components
}

enum PluginStatus {
  disabled,
  enabled,
  loading,
  error,
}

// ═══════════════════════════════════════════════════════════════
// PLUGIN RESULT
// ═══════════════════════════════════════════════════════════════

class PluginResult {
  final bool success;
  final dynamic data;
  final String? message;
  final String? error;
  final Map<String, dynamic>? metadata;

  PluginResult({
    required this.success,
    this.data,
    this.message,
    this.error,
    this.metadata,
  });

  factory PluginResult.success({dynamic data, String? message}) {
    return PluginResult(
      success: true,
      data: data,
      message: message,
    );
  }

  factory PluginResult.error(String error) {
    return PluginResult(
      success: false,
      error: error,
    );
  }

  @override
  String toString() => success
    ? 'PluginResult.success(data: $data)'
    : 'PluginResult.error($error)';
}

// ═══════════════════════════════════════════════════════════════
// PLUGIN CONTEXT
// ═══════════════════════════════════════════════════════════════

class PluginContext {
  final String input;
  final Map<String, dynamic> parameters;
  final Map<String, dynamic>? state;

  PluginContext({
    required this.input,
    this.parameters = const {},
    this.state,
  });

  T? getParam<T>(String key, {T? defaultValue}) {
    return parameters[key] as T? ?? defaultValue;
  }

  bool hasParam(String key) => parameters.containsKey(key);
}

// ═══════════════════════════════════════════════════════════════
// BASE PLUGIN
// ═══════════════════════════════════════════════════════════════

abstract class BasePlugin {
  // Plugin metadata
  String get id;
  String get name;
  String get description;
  PluginType get type;
  String get version => '1.0.0';
  IconData get icon => Icons.extension;
  List<String> get keywords => [];

  // Plugin state
  PluginStatus _status = PluginStatus.disabled;
  PluginStatus get status => _status;

  String? _lastError;
  String? get lastError => _lastError;

  // Configuration
  Map<String, dynamic> _config = {};
  Map<String, dynamic> get config => Map.unmodifiable(_config);

  // Lifecycle
  Future<void> initialize() async {
    _status = PluginStatus.loading;
    try {
      await onInitialize();
      _status = PluginStatus.enabled;
    } catch (e) {
      _lastError = e.toString();
      _status = PluginStatus.error;
      rethrow;
    }
  }

  Future<void> dispose() async {
    await onDispose();
    _status = PluginStatus.disabled;
  }

  // Override these in subclasses
  Future<void> onInitialize() async {}
  Future<void> onDispose() async {}

  // Configuration
  void configure(Map<String, dynamic> config) {
    _config = Map.from(config);
    onConfigure(config);
  }

  void onConfigure(Map<String, dynamic> config) {}

  // Execution
  Future<PluginResult> execute(PluginContext context);

  // Validation
  bool canExecute(PluginContext context) => status == PluginStatus.enabled;

  // Matching
  bool matches(String query) {
    final lowerQuery = query.toLowerCase();
    return name.toLowerCase().contains(lowerQuery) ||
           description.toLowerCase().contains(lowerQuery) ||
           keywords.any((k) => k.toLowerCase().contains(lowerQuery));
  }
}

// ═══════════════════════════════════════════════════════════════
// PLUGIN REGISTRY
// ═══════════════════════════════════════════════════════════════

class PluginRegistry {
  final Map<String, BasePlugin> _plugins = {};
  final _changeController = StreamController<List<BasePlugin>>.broadcast();

  // Singleton
  static final PluginRegistry _instance = PluginRegistry._internal();
  factory PluginRegistry() => _instance;
  PluginRegistry._internal();

  // Streams
  Stream<List<BasePlugin>> get onChange => _changeController.stream;

  // Plugin access
  List<BasePlugin> get all => _plugins.values.toList();
  List<BasePlugin> get enabled => _plugins.values.where((p) => p.status == PluginStatus.enabled).toList();

  BasePlugin? get(String id) => _plugins[id];

  List<BasePlugin> getByType(PluginType type) {
    return _plugins.values.where((p) => p.type == type).toList();
  }

  List<BasePlugin> search(String query) {
    return _plugins.values.where((p) => p.matches(query)).toList();
  }

  // Registration
  Future<void> register(BasePlugin plugin) async {
    if (_plugins.containsKey(plugin.id)) {
      throw Exception('Plugin ${plugin.id} already registered');
    }

    _plugins[plugin.id] = plugin;
    await plugin.initialize();
    _notifyChange();
  }

  Future<void> registerAll(List<BasePlugin> plugins) async {
    for (final plugin in plugins) {
      await register(plugin);
    }
  }

  Future<void> unregister(String id) async {
    final plugin = _plugins[id];
    if (plugin != null) {
      await plugin.dispose();
      _plugins.remove(id);
      _notifyChange();
    }
  }

  // Configuration
  void configure(String id, Map<String, dynamic> config) {
    _plugins[id]?.configure(config);
  }

  // Execution
  Future<PluginResult> execute(String id, PluginContext context) async {
    final plugin = _plugins[id];
    if (plugin == null) {
      return PluginResult.error('Plugin not found: $id');
    }

    if (!plugin.canExecute(context)) {
      return PluginResult.error('Plugin cannot execute: ${plugin.lastError ?? "disabled"}');
    }

    try {
      return await plugin.execute(context);
    } catch (e) {
      return PluginResult.error('Execution error: $e');
    }
  }

  // Cleanup
  Future<void> disposeAll() async {
    for (final plugin in _plugins.values) {
      await plugin.dispose();
    }
    _plugins.clear();
    _changeController.close();
  }

  void _notifyChange() {
    _changeController.add(all);
  }
}

// ═══════════════════════════════════════════════════════════════
// PLUGIN PROVIDER (for use with Provider package)
// ═══════════════════════════════════════════════════════════════

class PluginProvider extends ChangeNotifier {
  final PluginRegistry _registry = PluginRegistry();
  List<BasePlugin> _plugins = [];

  PluginProvider() {
    _plugins = _registry.all;
    _registry.onChange.listen((plugins) {
      _plugins = plugins;
      notifyListeners();
    });
  }

  List<BasePlugin> get plugins => _plugins;
  List<BasePlugin> get enabledPlugins => _registry.enabled;

  BasePlugin? getPlugin(String id) => _registry.get(id);

  List<BasePlugin> getPluginsByType(PluginType type) => _registry.getByType(type);

  List<BasePlugin> searchPlugins(String query) => _registry.search(query);

  Future<void> registerPlugin(BasePlugin plugin) async {
    await _registry.register(plugin);
  }

  Future<void> unregisterPlugin(String id) async {
    await _registry.unregister(id);
  }

  Future<PluginResult> executePlugin(String id, PluginContext context) {
    return _registry.execute(id, context);
  }

  void configurePlugin(String id, Map<String, dynamic> config) {
    _registry.configure(id, config);
    notifyListeners();
  }
}

// ═══════════════════════════════════════════════════════════════
// EXAMPLE PLUGINS
// ═══════════════════════════════════════════════════════════════

/// Calculator plugin example
class CalculatorPlugin extends BasePlugin {
  @override
  String get id => 'calculator';

  @override
  String get name => 'Calculator';

  @override
  String get description => 'Performs mathematical calculations';

  @override
  PluginType get type => PluginType.utility;

  @override
  IconData get icon => Icons.calculate;

  @override
  List<String> get keywords => ['math', 'calculate', 'compute', 'arithmetic'];

  @override
  Future<PluginResult> execute(PluginContext context) async {
    try {
      final expression = context.input.trim();

      // Simple expression parser (extend as needed)
      final result = _evaluateExpression(expression);

      return PluginResult.success(
        data: {'result': result, 'expression': expression},
        message: '$expression = $result',
      );
    } catch (e) {
      return PluginResult.error('Invalid expression: ${e.toString()}');
    }
  }

  double _evaluateExpression(String expr) {
    // Simplified - use a proper expression parser in production
    expr = expr.replaceAll(' ', '');

    // Handle simple arithmetic
    if (expr.contains('+')) {
      final parts = expr.split('+');
      return double.parse(parts[0]) + double.parse(parts[1]);
    } else if (expr.contains('-')) {
      final parts = expr.split('-');
      return double.parse(parts[0]) - double.parse(parts[1]);
    } else if (expr.contains('*')) {
      final parts = expr.split('*');
      return double.parse(parts[0]) * double.parse(parts[1]);
    } else if (expr.contains('/')) {
      final parts = expr.split('/');
      return double.parse(parts[0]) / double.parse(parts[1]);
    }

    return double.parse(expr);
  }
}

/// JSON Formatter plugin example
class JsonFormatterPlugin extends BasePlugin {
  @override
  String get id => 'json_formatter';

  @override
  String get name => 'JSON Formatter';

  @override
  String get description => 'Formats and validates JSON data';

  @override
  PluginType get type => PluginType.utility;

  @override
  IconData get icon => Icons.data_object;

  @override
  List<String> get keywords => ['json', 'format', 'pretty', 'validate'];

  int _indent = 2;

  @override
  void onConfigure(Map<String, dynamic> config) {
    _indent = config['indent'] ?? 2;
  }

  @override
  Future<PluginResult> execute(PluginContext context) async {
    try {
      final input = context.input.trim();

      // Parse JSON
      final dynamic parsed = _parseJson(input);

      // Format with indentation
      final formatted = _formatJson(parsed, _indent);

      return PluginResult.success(
        data: {
          'formatted': formatted,
          'valid': true,
          'type': parsed is List ? 'array' : 'object',
        },
        message: 'JSON formatted successfully',
      );
    } catch (e) {
      return PluginResult.error('Invalid JSON: ${e.toString()}');
    }
  }

  dynamic _parseJson(String input) {
    // Import 'dart:convert' in real implementation
    // return jsonDecode(input);
    throw UnimplementedError('Add dart:convert import');
  }

  String _formatJson(dynamic data, int indent) {
    // Import 'dart:convert' in real implementation
    // return JsonEncoder.withIndent(' ' * indent).convert(data);
    throw UnimplementedError('Add dart:convert import');
  }
}

/// Web Search plugin example
class WebSearchPlugin extends BasePlugin {
  @override
  String get id => 'web_search';

  @override
  String get name => 'Web Search';

  @override
  String get description => 'Searches the web for information';

  @override
  PluginType get type => PluginType.integration;

  @override
  IconData get icon => Icons.search;

  @override
  List<String> get keywords => ['search', 'web', 'google', 'find', 'lookup'];

  String _apiKey = '';
  String _searchEngine = 'google';

  String get searchEngine => _searchEngine;

  @override
  void onConfigure(Map<String, dynamic> config) {
    _apiKey = config['apiKey'] ?? '';
    _searchEngine = config['searchEngine'] ?? 'google';
  }

  @override
  bool canExecute(PluginContext context) {
    return super.canExecute(context) && _apiKey.isNotEmpty;
  }

  @override
  Future<PluginResult> execute(PluginContext context) async {
    if (_apiKey.isEmpty) {
      return PluginResult.error('API key not configured');
    }

    try {
      final query = context.input.trim();
      final maxResults = context.getParam<int>('maxResults', defaultValue: 10);

      // Implement actual search API call here
      final results = await _performSearch(query, maxResults!);

      return PluginResult.success(
        data: results,
        message: 'Found ${results.length} results for "$query"',
      );
    } catch (e) {
      return PluginResult.error('Search failed: ${e.toString()}');
    }
  }

  Future<List<Map<String, dynamic>>> _performSearch(String query, int maxResults) async {
    // Implement actual API call
    await Future.delayed(const Duration(milliseconds: 500));

    // Mock results
    return [
      {'title': 'Result 1', 'url': 'https://example.com/1', 'snippet': 'Description...'},
      {'title': 'Result 2', 'url': 'https://example.com/2', 'snippet': 'Description...'},
    ];
  }
}

// ═══════════════════════════════════════════════════════════════
// PLUGIN LIST WIDGET
// ═══════════════════════════════════════════════════════════════

class PluginListWidget extends StatelessWidget {
  final List<BasePlugin> plugins;
  final Function(BasePlugin)? onTap;
  final Function(BasePlugin, bool)? onToggle;

  const PluginListWidget({
    super.key,
    required this.plugins,
    this.onTap,
    this.onToggle,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: plugins.length,
      itemBuilder: (context, index) {
        final plugin = plugins[index];
        return ListTile(
          leading: CircleAvatar(
            backgroundColor: _getStatusColor(plugin.status).withOpacity(0.2),
            child: Icon(plugin.icon, color: _getStatusColor(plugin.status)),
          ),
          title: Text(plugin.name),
          subtitle: Text(plugin.description),
          trailing: onToggle != null
            ? Switch(
                value: plugin.status == PluginStatus.enabled,
                onChanged: (value) => onToggle!(plugin, value),
              )
            : _getStatusIcon(plugin.status),
          onTap: onTap != null ? () => onTap!(plugin) : null,
        );
      },
    );
  }

  Color _getStatusColor(PluginStatus status) {
    switch (status) {
      case PluginStatus.enabled: return Colors.green;
      case PluginStatus.disabled: return Colors.grey;
      case PluginStatus.loading: return Colors.blue;
      case PluginStatus.error: return Colors.red;
    }
  }

  Widget _getStatusIcon(PluginStatus status) {
    switch (status) {
      case PluginStatus.enabled:
        return const Icon(Icons.check_circle, color: Colors.green);
      case PluginStatus.disabled:
        return const Icon(Icons.pause_circle, color: Colors.grey);
      case PluginStatus.loading:
        return const SizedBox(
          width: 20,
          height: 20,
          child: CircularProgressIndicator(strokeWidth: 2),
        );
      case PluginStatus.error:
        return const Icon(Icons.error, color: Colors.red);
    }
  }
}

// ═══════════════════════════════════════════════════════════════
// USAGE EXAMPLE
// ═══════════════════════════════════════════════════════════════

void main() async {
  // Initialize registry
  final registry = PluginRegistry();

  // Register plugins
  await registry.registerAll([
    CalculatorPlugin(),
    JsonFormatterPlugin(),
    WebSearchPlugin(),
  ]);

  // Configure a plugin
  registry.configure('web_search', {
    'apiKey': 'your-api-key',
    'searchEngine': 'google',
  });

  // Execute a plugin
  final calcResult = await registry.execute(
    'calculator',
    PluginContext(input: '10 + 20'),
  );
  print('Calculator: ${calcResult.message}');

  // Search plugins
  final searchResults = registry.search('format');
  print('Found plugins: ${searchResults.map((p) => p.name).join(', ')}');

  // Get plugins by type
  final utilities = registry.getByType(PluginType.utility);
  print('Utility plugins: ${utilities.map((p) => p.name).join(', ')}');

  // Cleanup
  await registry.disposeAll();
}
