/// Connectivity Service Template
///
/// Network status monitoring with automatic reconnection handling
/// Features: Real-time connectivity status, connection quality, retry logic
///
/// Usage:
/// 1. Add connectivity_plus to pubspec.yaml
/// 2. Initialize in main.dart or use via Riverpod provider
/// 3. Listen to connectivity changes for offline-first features

import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Connection quality levels
enum ConnectionQuality {
  none,
  poor,
  moderate,
  good,
  excellent,
}

/// Connectivity status model
class ConnectivityStatus {
  final bool isConnected;
  final ConnectivityResult type;
  final ConnectionQuality quality;
  final DateTime lastChecked;

  ConnectivityStatus({
    required this.isConnected,
    required this.type,
    this.quality = ConnectionQuality.none,
    DateTime? lastChecked,
  }) : lastChecked = lastChecked ?? DateTime.now();

  factory ConnectivityStatus.disconnected() {
    return ConnectivityStatus(
      isConnected: false,
      type: ConnectivityResult.none,
      quality: ConnectionQuality.none,
    );
  }

  factory ConnectivityStatus.connected(ConnectivityResult type) {
    return ConnectivityStatus(
      isConnected: true,
      type: type,
      quality: _estimateQuality(type),
    );
  }

  static ConnectionQuality _estimateQuality(ConnectivityResult type) {
    switch (type) {
      case ConnectivityResult.wifi:
        return ConnectionQuality.excellent;
      case ConnectivityResult.ethernet:
        return ConnectionQuality.excellent;
      case ConnectivityResult.mobile:
        return ConnectionQuality.good;
      case ConnectivityResult.vpn:
        return ConnectionQuality.moderate;
      case ConnectivityResult.bluetooth:
        return ConnectionQuality.poor;
      case ConnectivityResult.other:
        return ConnectionQuality.moderate;
      case ConnectivityResult.none:
        return ConnectionQuality.none;
    }
  }

  String get typeString {
    switch (type) {
      case ConnectivityResult.wifi:
        return 'WiFi';
      case ConnectivityResult.ethernet:
        return 'Ethernet';
      case ConnectivityResult.mobile:
        return 'Mobile Data';
      case ConnectivityResult.vpn:
        return 'VPN';
      case ConnectivityResult.bluetooth:
        return 'Bluetooth';
      case ConnectivityResult.other:
        return 'Other';
      case ConnectivityResult.none:
        return 'No Connection';
    }
  }
}

/// Connectivity service for monitoring network status
class ConnectivityService {
  final Connectivity _connectivity;
  final _statusController = StreamController<ConnectivityStatus>.broadcast();
  StreamSubscription<List<ConnectivityResult>>? _subscription;
  ConnectivityStatus _currentStatus = ConnectivityStatus.disconnected();

  // Callbacks
  Function()? onConnected;
  Function()? onDisconnected;
  Function(ConnectivityStatus)? onStatusChanged;

  ConnectivityService({Connectivity? connectivity})
      : _connectivity = connectivity ?? Connectivity();

  /// Current connectivity status
  ConnectivityStatus get currentStatus => _currentStatus;

  /// Stream of connectivity status changes
  Stream<ConnectivityStatus> get statusStream => _statusController.stream;

  /// Whether currently connected
  bool get isConnected => _currentStatus.isConnected;

  /// Initialize and start monitoring
  Future<void> initialize() async {
    // Get initial status
    final results = await _connectivity.checkConnectivity();
    _updateStatus(results);

    // Listen for changes
    _subscription = _connectivity.onConnectivityChanged.listen(_updateStatus);
  }

  /// Update status from connectivity results
  void _updateStatus(List<ConnectivityResult> results) {
    final wasConnected = _currentStatus.isConnected;

    // Use the best available connection
    final bestResult = _getBestConnection(results);

    if (bestResult == ConnectivityResult.none) {
      _currentStatus = ConnectivityStatus.disconnected();
    } else {
      _currentStatus = ConnectivityStatus.connected(bestResult);
    }

    _statusController.add(_currentStatus);
    onStatusChanged?.call(_currentStatus);

    // Trigger connect/disconnect callbacks
    if (!wasConnected && _currentStatus.isConnected) {
      onConnected?.call();
    } else if (wasConnected && !_currentStatus.isConnected) {
      onDisconnected?.call();
    }
  }

  /// Get the best available connection from multiple results
  ConnectivityResult _getBestConnection(List<ConnectivityResult> results) {
    if (results.isEmpty || results.contains(ConnectivityResult.none)) {
      return ConnectivityResult.none;
    }

    // Priority: ethernet > wifi > mobile > vpn > other > bluetooth
    if (results.contains(ConnectivityResult.ethernet)) {
      return ConnectivityResult.ethernet;
    }
    if (results.contains(ConnectivityResult.wifi)) {
      return ConnectivityResult.wifi;
    }
    if (results.contains(ConnectivityResult.mobile)) {
      return ConnectivityResult.mobile;
    }
    if (results.contains(ConnectivityResult.vpn)) {
      return ConnectivityResult.vpn;
    }
    if (results.contains(ConnectivityResult.other)) {
      return ConnectivityResult.other;
    }
    if (results.contains(ConnectivityResult.bluetooth)) {
      return ConnectivityResult.bluetooth;
    }

    return results.first;
  }

  /// Force check connectivity
  Future<ConnectivityStatus> checkConnectivity() async {
    final results = await _connectivity.checkConnectivity();
    _updateStatus(results);
    return _currentStatus;
  }

  /// Execute action when connected (with retry)
  Future<T?> executeWhenConnected<T>(
    Future<T> Function() action, {
    int maxRetries = 3,
    Duration retryDelay = const Duration(seconds: 2),
  }) async {
    for (int i = 0; i < maxRetries; i++) {
      if (isConnected) {
        try {
          return await action();
        } catch (e) {
          if (i == maxRetries - 1) rethrow;
        }
      }

      // Wait and check again
      await Future.delayed(retryDelay);
      await checkConnectivity();
    }

    return null;
  }

  /// Wait for connection
  Future<void> waitForConnection({Duration? timeout}) async {
    if (isConnected) return;

    final completer = Completer<void>();
    StreamSubscription<ConnectivityStatus>? subscription;

    subscription = statusStream.listen((status) {
      if (status.isConnected) {
        subscription?.cancel();
        if (!completer.isCompleted) {
          completer.complete();
        }
      }
    });

    if (timeout != null) {
      Future.delayed(timeout, () {
        subscription?.cancel();
        if (!completer.isCompleted) {
          completer.completeError(
            TimeoutException('Connection timeout', timeout),
          );
        }
      });
    }

    return completer.future;
  }

  /// Dispose resources
  void dispose() {
    _subscription?.cancel();
    _statusController.close();
  }
}

/// Connectivity state notifier for Riverpod
class ConnectivityNotifier extends StateNotifier<ConnectivityStatus> {
  final ConnectivityService _service;
  StreamSubscription<ConnectivityStatus>? _subscription;

  ConnectivityNotifier(this._service) : super(ConnectivityStatus.disconnected()) {
    _init();
  }

  Future<void> _init() async {
    await _service.initialize();
    state = _service.currentStatus;

    _subscription = _service.statusStream.listen((status) {
      state = status;
    });
  }

  bool get isConnected => state.isConnected;

  Future<void> refresh() async {
    state = await _service.checkConnectivity();
  }

  @override
  void dispose() {
    _subscription?.cancel();
    _service.dispose();
    super.dispose();
  }
}

/// Provider for connectivity service
final connectivityServiceProvider = Provider<ConnectivityService>((ref) {
  final service = ConnectivityService();
  ref.onDispose(() => service.dispose());
  return service;
});

/// State provider for connectivity status
final connectivityProvider =
    StateNotifierProvider<ConnectivityNotifier, ConnectivityStatus>((ref) {
  final service = ref.watch(connectivityServiceProvider);
  return ConnectivityNotifier(service);
});

/// Simple boolean provider for connection status
final isConnectedProvider = Provider<bool>((ref) {
  return ref.watch(connectivityProvider).isConnected;
});
