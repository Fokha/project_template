/// Analytics Service Template
///
/// Event tracking with multiple analytics providers
/// Features: Firebase Analytics, custom events, user properties, screen tracking
///
/// Usage:
/// 1. Add firebase_analytics to pubspec.yaml
/// 2. Initialize Firebase in main.dart
/// 3. Use via Riverpod provider for tracking events

import 'package:firebase_analytics/firebase_analytics.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Event categories for organization
enum EventCategory {
  navigation,
  userAction,
  purchase,
  engagement,
  error,
  performance,
  custom,
}

/// Analytics event model
class AnalyticsEvent {
  final String name;
  final EventCategory category;
  final Map<String, dynamic>? parameters;
  final DateTime timestamp;

  AnalyticsEvent({
    required this.name,
    this.category = EventCategory.custom,
    this.parameters,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  /// Convert to Firebase-safe parameters
  Map<String, Object>? toFirebaseParams() {
    if (parameters == null) return null;

    return parameters!.map((key, value) {
      // Firebase only accepts String, int, double, bool
      if (value is String || value is int || value is double || value is bool) {
        return MapEntry(key, value);
      }
      return MapEntry(key, value.toString());
    });
  }
}

/// User properties for analytics
class UserProperties {
  final String? userId;
  final String? userType;
  final String? subscriptionTier;
  final Map<String, String>? customProperties;

  UserProperties({
    this.userId,
    this.userType,
    this.subscriptionTier,
    this.customProperties,
  });
}

/// Analytics service for tracking events
class AnalyticsService {
  final FirebaseAnalytics _analytics;
  final bool _enabled;
  final List<AnalyticsEvent> _eventQueue = [];
  final int _maxQueueSize;

  // Callbacks for custom analytics providers
  Function(AnalyticsEvent)? onEventLogged;
  Function(String, Map<String, dynamic>?)? onScreenViewed;

  AnalyticsService({
    FirebaseAnalytics? analytics,
    bool enabled = true,
    int maxQueueSize = 100,
  })  : _analytics = analytics ?? FirebaseAnalytics.instance,
        _enabled = enabled,
        _maxQueueSize = maxQueueSize;

  /// Get analytics observer for navigation
  FirebaseAnalyticsObserver get observer => FirebaseAnalyticsObserver(
        analytics: _analytics,
        nameExtractor: (settings) => settings.name ?? 'unknown',
      );

  // ============ EVENT TRACKING ============

  /// Log a custom event
  Future<void> logEvent({
    required String name,
    EventCategory category = EventCategory.custom,
    Map<String, dynamic>? parameters,
  }) async {
    if (!_enabled) return;

    final event = AnalyticsEvent(
      name: name,
      category: category,
      parameters: parameters,
    );

    // Add to queue
    _eventQueue.add(event);
    if (_eventQueue.length > _maxQueueSize) {
      _eventQueue.removeAt(0);
    }

    // Log to Firebase
    await _analytics.logEvent(
      name: _sanitizeEventName(name),
      parameters: event.toFirebaseParams(),
    );

    // Notify callback
    onEventLogged?.call(event);
  }

  /// Log screen view
  Future<void> logScreenView({
    required String screenName,
    String? screenClass,
    Map<String, dynamic>? parameters,
  }) async {
    if (!_enabled) return;

    await _analytics.logScreenView(
      screenName: screenName,
      screenClass: screenClass,
    );

    onScreenViewed?.call(screenName, parameters);

    await logEvent(
      name: 'screen_view',
      category: EventCategory.navigation,
      parameters: {
        'screen_name': screenName,
        if (screenClass != null) 'screen_class': screenClass,
        ...?parameters,
      },
    );
  }

  /// Log user action (button tap, etc.)
  Future<void> logUserAction({
    required String action,
    String? target,
    Map<String, dynamic>? parameters,
  }) async {
    await logEvent(
      name: 'user_action',
      category: EventCategory.userAction,
      parameters: {
        'action': action,
        if (target != null) 'target': target,
        ...?parameters,
      },
    );
  }

  /// Log button click
  Future<void> logButtonClick(String buttonName, {String? screen}) async {
    await logEvent(
      name: 'button_click',
      category: EventCategory.userAction,
      parameters: {
        'button_name': buttonName,
        if (screen != null) 'screen': screen,
      },
    );
  }

  // ============ PREDEFINED EVENTS ============

  /// Log login event
  Future<void> logLogin({String? method}) async {
    await _analytics.logLogin(loginMethod: method);
    await logEvent(
      name: 'login',
      category: EventCategory.userAction,
      parameters: {'method': method ?? 'unknown'},
    );
  }

  /// Log sign up event
  Future<void> logSignUp({String? method}) async {
    await _analytics.logSignUp(signUpMethod: method ?? 'unknown');
    await logEvent(
      name: 'sign_up',
      category: EventCategory.userAction,
      parameters: {'method': method ?? 'unknown'},
    );
  }

  /// Log purchase event
  Future<void> logPurchase({
    required String itemId,
    required String itemName,
    required double value,
    required String currency,
    String? transactionId,
  }) async {
    await _analytics.logPurchase(
      currency: currency,
      value: value,
      transactionId: transactionId,
      items: [
        AnalyticsEventItem(
          itemId: itemId,
          itemName: itemName,
          price: value,
        ),
      ],
    );

    await logEvent(
      name: 'purchase',
      category: EventCategory.purchase,
      parameters: {
        'item_id': itemId,
        'item_name': itemName,
        'value': value,
        'currency': currency,
        if (transactionId != null) 'transaction_id': transactionId,
      },
    );
  }

  /// Log search event
  Future<void> logSearch(String searchTerm) async {
    await _analytics.logSearch(searchTerm: searchTerm);
    await logEvent(
      name: 'search',
      category: EventCategory.userAction,
      parameters: {'search_term': searchTerm},
    );
  }

  /// Log share event
  Future<void> logShare({
    required String contentType,
    required String itemId,
    String? method,
  }) async {
    await _analytics.logShare(
      contentType: contentType,
      itemId: itemId,
      method: method ?? 'unknown',
    );

    await logEvent(
      name: 'share',
      category: EventCategory.engagement,
      parameters: {
        'content_type': contentType,
        'item_id': itemId,
        'method': method ?? 'unknown',
      },
    );
  }

  /// Log app open
  Future<void> logAppOpen() async {
    await _analytics.logAppOpen();
    await logEvent(
      name: 'app_open',
      category: EventCategory.engagement,
    );
  }

  // ============ ERROR TRACKING ============

  /// Log error event
  Future<void> logError({
    required String errorType,
    String? errorMessage,
    String? stackTrace,
    Map<String, dynamic>? extra,
  }) async {
    await logEvent(
      name: 'error',
      category: EventCategory.error,
      parameters: {
        'error_type': errorType,
        if (errorMessage != null) 'error_message': errorMessage.substring(
          0,
          errorMessage.length > 100 ? 100 : errorMessage.length,
        ),
        ...?extra,
      },
    );
  }

  // ============ PERFORMANCE ============

  /// Log performance metric
  Future<void> logPerformance({
    required String metric,
    required int durationMs,
    Map<String, dynamic>? extra,
  }) async {
    await logEvent(
      name: 'performance',
      category: EventCategory.performance,
      parameters: {
        'metric': metric,
        'duration_ms': durationMs,
        ...?extra,
      },
    );
  }

  /// Time an operation and log it
  Future<T> timeOperation<T>(
    String operationName,
    Future<T> Function() operation,
  ) async {
    final stopwatch = Stopwatch()..start();
    try {
      return await operation();
    } finally {
      stopwatch.stop();
      await logPerformance(
        metric: operationName,
        durationMs: stopwatch.elapsedMilliseconds,
      );
    }
  }

  // ============ USER PROPERTIES ============

  /// Set user ID
  Future<void> setUserId(String? userId) async {
    await _analytics.setUserId(id: userId);
  }

  /// Set user property
  Future<void> setUserProperty({
    required String name,
    required String? value,
  }) async {
    await _analytics.setUserProperty(name: name, value: value);
  }

  /// Set multiple user properties
  Future<void> setUserProperties(UserProperties properties) async {
    if (properties.userId != null) {
      await setUserId(properties.userId);
    }
    if (properties.userType != null) {
      await setUserProperty(name: 'user_type', value: properties.userType);
    }
    if (properties.subscriptionTier != null) {
      await setUserProperty(
        name: 'subscription_tier',
        value: properties.subscriptionTier,
      );
    }
    if (properties.customProperties != null) {
      for (final entry in properties.customProperties!.entries) {
        await setUserProperty(name: entry.key, value: entry.value);
      }
    }
  }

  // ============ UTILITIES ============

  /// Get recent events (from queue)
  List<AnalyticsEvent> get recentEvents => List.unmodifiable(_eventQueue);

  /// Get events by category
  List<AnalyticsEvent> getEventsByCategory(EventCategory category) {
    return _eventQueue.where((e) => e.category == category).toList();
  }

  /// Clear event queue
  void clearEventQueue() {
    _eventQueue.clear();
  }

  /// Sanitize event name for Firebase (lowercase, underscores only)
  String _sanitizeEventName(String name) {
    return name
        .toLowerCase()
        .replaceAll(RegExp(r'[^a-z0-9_]'), '_')
        .replaceAll(RegExp(r'_+'), '_')
        .substring(0, name.length > 40 ? 40 : name.length);
  }

  /// Reset analytics data
  Future<void> resetAnalyticsData() async {
    await _analytics.resetAnalyticsData();
    clearEventQueue();
  }
}

/// Route observer for automatic screen tracking
class AnalyticsRouteObserver extends RouteObserver<PageRoute<dynamic>> {
  final AnalyticsService analytics;

  AnalyticsRouteObserver(this.analytics);

  @override
  void didPush(Route<dynamic> route, Route<dynamic>? previousRoute) {
    super.didPush(route, previousRoute);
    if (route is PageRoute) {
      _logScreenView(route);
    }
  }

  @override
  void didPop(Route<dynamic> route, Route<dynamic>? previousRoute) {
    super.didPop(route, previousRoute);
    if (previousRoute is PageRoute) {
      _logScreenView(previousRoute);
    }
  }

  void _logScreenView(PageRoute<dynamic> route) {
    final screenName = route.settings.name ?? 'unknown';
    analytics.logScreenView(screenName: screenName);
  }
}

/// Provider for analytics service
final analyticsServiceProvider = Provider<AnalyticsService>((ref) {
  return AnalyticsService();
});

/// Provider for route observer
final analyticsObserverProvider = Provider<AnalyticsRouteObserver>((ref) {
  final analytics = ref.watch(analyticsServiceProvider);
  return AnalyticsRouteObserver(analytics);
});
