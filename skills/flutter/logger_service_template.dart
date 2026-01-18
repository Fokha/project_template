/// Logger Service Template
///
/// Production-ready logging with multiple levels and formatters
/// Features: Pretty printing, API logging, performance tracking
///
/// Usage:
/// 1. Initialize: final logger = LoggerService(minLevel: LogLevel.debug)
/// 2. Log: logger.info('Message'), logger.error('Error', error, stackTrace)
/// 3. API: logger.logRequest(...), logger.logResponse(...)

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Log levels
enum LogLevel {
  verbose,
  debug,
  info,
  warning,
  error,
  wtf, // What a Terrible Failure
  none,
}

/// Log entry
class LogEntry {
  final DateTime timestamp;
  final LogLevel level;
  final String message;
  final String? tag;
  final Object? error;
  final StackTrace? stackTrace;
  final Map<String, dynamic>? extra;

  LogEntry({
    DateTime? timestamp,
    required this.level,
    required this.message,
    this.tag,
    this.error,
    this.stackTrace,
    this.extra,
  }) : timestamp = timestamp ?? DateTime.now();

  @override
  String toString() {
    final buffer = StringBuffer();
    buffer.write('[${_levelEmoji(level)}] ');
    buffer.write('[${timestamp.toIso8601String()}] ');
    if (tag != null) buffer.write('[$tag] ');
    buffer.write(message);
    if (error != null) buffer.write('\nError: $error');
    if (stackTrace != null) buffer.write('\nStackTrace: $stackTrace');
    if (extra != null) buffer.write('\nExtra: $extra');
    return buffer.toString();
  }

  String _levelEmoji(LogLevel level) {
    switch (level) {
      case LogLevel.verbose:
        return '🔊';
      case LogLevel.debug:
        return '🐛';
      case LogLevel.info:
        return '💡';
      case LogLevel.warning:
        return '⚠️';
      case LogLevel.error:
        return '❌';
      case LogLevel.wtf:
        return '💀';
      case LogLevel.none:
        return '';
    }
  }
}

/// Logger service
class LoggerService {
  final LogLevel minLevel;
  final bool enabled;
  final List<LogEntry> _history = [];
  final int maxHistorySize;

  // Callbacks for external logging (e.g., Crashlytics)
  Function(LogEntry)? onLog;
  Function(Object error, StackTrace? stackTrace)? onError;

  LoggerService({
    this.minLevel = LogLevel.debug,
    this.enabled = true,
    this.maxHistorySize = 1000,
    this.onLog,
    this.onError,
  });

  /// Check if level should be logged
  bool _shouldLog(LogLevel level) {
    if (!enabled) return false;
    return level.index >= minLevel.index;
  }

  /// Log message
  void _log(LogLevel level, String message, {
    String? tag,
    Object? error,
    StackTrace? stackTrace,
    Map<String, dynamic>? extra,
  }) {
    if (!_shouldLog(level)) return;

    final entry = LogEntry(
      level: level,
      message: message,
      tag: tag,
      error: error,
      stackTrace: stackTrace,
      extra: extra,
    );

    // Add to history
    _history.add(entry);
    if (_history.length > maxHistorySize) {
      _history.removeAt(0);
    }

    // Print in debug mode
    if (kDebugMode) {
      debugPrint(entry.toString());
    }

    // Call callback
    onLog?.call(entry);

    // Report errors to external service
    if (level == LogLevel.error || level == LogLevel.wtf) {
      onError?.call(error ?? message, stackTrace);
    }
  }

  // ============ LOG METHODS ============

  /// Verbose log
  void verbose(String message, {String? tag, Map<String, dynamic>? extra}) {
    _log(LogLevel.verbose, message, tag: tag, extra: extra);
  }

  /// Debug log
  void debug(String message, {String? tag, Map<String, dynamic>? extra}) {
    _log(LogLevel.debug, message, tag: tag, extra: extra);
  }

  /// Info log
  void info(String message, {String? tag, Map<String, dynamic>? extra}) {
    _log(LogLevel.info, message, tag: tag, extra: extra);
  }

  /// Warning log
  void warning(String message, {String? tag, Object? error, Map<String, dynamic>? extra}) {
    _log(LogLevel.warning, message, tag: tag, error: error, extra: extra);
  }

  /// Error log
  void error(String message, {String? tag, Object? error, StackTrace? stackTrace, Map<String, dynamic>? extra}) {
    _log(LogLevel.error, message, tag: tag, error: error, stackTrace: stackTrace, extra: extra);
  }

  /// WTF log (critical errors)
  void wtf(String message, {String? tag, Object? error, StackTrace? stackTrace, Map<String, dynamic>? extra}) {
    _log(LogLevel.wtf, message, tag: tag, error: error, stackTrace: stackTrace, extra: extra);
  }

  // ============ SPECIALIZED LOGGING ============

  /// Log API request
  void logRequest({
    required String method,
    required String url,
    Map<String, dynamic>? headers,
    dynamic body,
  }) {
    _log(
      LogLevel.debug,
      '→ $method $url',
      tag: 'API',
      extra: {
        'method': method,
        'url': url,
        if (headers != null) 'headers': headers,
        if (body != null) 'body': body,
      },
    );
  }

  /// Log API response
  void logResponse({
    required String method,
    required String url,
    required int statusCode,
    dynamic body,
    Duration? duration,
  }) {
    final level = statusCode >= 400 ? LogLevel.warning : LogLevel.debug;
    final emoji = statusCode >= 400 ? '✗' : '✓';

    _log(
      level,
      '← $emoji $method $url [$statusCode]${duration != null ? ' (${duration.inMilliseconds}ms)' : ''}',
      tag: 'API',
      extra: {
        'method': method,
        'url': url,
        'statusCode': statusCode,
        if (body != null) 'body': body,
        if (duration != null) 'durationMs': duration.inMilliseconds,
      },
    );
  }

  /// Log navigation
  void logNavigation(String route, {Map<String, dynamic>? params}) {
    _log(
      LogLevel.info,
      '🧭 Navigate to: $route',
      tag: 'NAV',
      extra: params,
    );
  }

  /// Log user action
  void logAction(String action, {Map<String, dynamic>? params}) {
    _log(
      LogLevel.info,
      '👆 User action: $action',
      tag: 'ACTION',
      extra: params,
    );
  }

  /// Log performance metric
  void logPerformance(String name, Duration duration, {Map<String, dynamic>? extra}) {
    _log(
      LogLevel.debug,
      '⏱️ $name: ${duration.inMilliseconds}ms',
      tag: 'PERF',
      extra: {
        'name': name,
        'durationMs': duration.inMilliseconds,
        ...?extra,
      },
    );
  }

  /// Log app lifecycle
  void logLifecycle(String event) {
    _log(LogLevel.info, '📱 App lifecycle: $event', tag: 'LIFECYCLE');
  }

  // ============ UTILITIES ============

  /// Get log history
  List<LogEntry> get history => List.unmodifiable(_history);

  /// Get logs by level
  List<LogEntry> getByLevel(LogLevel level) {
    return _history.where((e) => e.level == level).toList();
  }

  /// Get logs by tag
  List<LogEntry> getByTag(String tag) {
    return _history.where((e) => e.tag == tag).toList();
  }

  /// Get recent logs
  List<LogEntry> getRecent({int count = 50}) {
    final start = _history.length > count ? _history.length - count : 0;
    return _history.sublist(start);
  }

  /// Clear history
  void clearHistory() {
    _history.clear();
  }

  /// Export logs as string
  String exportLogs() {
    return _history.map((e) => e.toString()).join('\n\n');
  }

  /// Time an operation
  Future<T> timeAsync<T>(String name, Future<T> Function() operation) async {
    final stopwatch = Stopwatch()..start();
    try {
      return await operation();
    } finally {
      stopwatch.stop();
      logPerformance(name, stopwatch.elapsed);
    }
  }

  /// Time a sync operation
  T timeSync<T>(String name, T Function() operation) {
    final stopwatch = Stopwatch()..start();
    try {
      return operation();
    } finally {
      stopwatch.stop();
      logPerformance(name, stopwatch.elapsed);
    }
  }
}

/// Provider factory for logger
final loggerProvider = Provider.family<LoggerService, LogLevel>((ref, minLevel) {
  return LoggerService(minLevel: minLevel);
});

/// Default logger provider
final defaultLoggerProvider = Provider<LoggerService>((ref) {
  return LoggerService(
    minLevel: kDebugMode ? LogLevel.debug : LogLevel.info,
  );
});
