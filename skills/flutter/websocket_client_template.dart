// ignore_for_file: avoid_print, prefer_const_constructors

// ═══════════════════════════════════════════════════════════════
// WEBSOCKET CLIENT TEMPLATE
// Real-time data streaming with auto-reconnect
// ═══════════════════════════════════════════════════════════════
//
// Usage:
// 1. Copy to your project's lib/services/ directory
// 2. Replace FeatureName with your feature (e.g., Price)
// 3. Replace {{WS_URL}} with your WebSocket URL
// 4. Customize message handling
//
// ═══════════════════════════════════════════════════════════════

import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';

// ═══════════════════════════════════════════════════════════════
// WEBSOCKET CONFIGURATION
// ═══════════════════════════════════════════════════════════════

class WebSocketConfig {
  static const String defaultUrl = '{{WS_URL}}';
  static const Duration pingInterval = Duration(seconds: 30);
  static const Duration reconnectDelay = Duration(seconds: 3);
  static const int maxReconnectAttempts = 10;
  static const Duration connectionTimeout = Duration(seconds: 10);
}

// ═══════════════════════════════════════════════════════════════
// CONNECTION STATE
// ═══════════════════════════════════════════════════════════════

enum ConnectionState {
  disconnected,
  connecting,
  connected,
  reconnecting,
  failed,
}

// ═══════════════════════════════════════════════════════════════
// WEBSOCKET MESSAGE
// ═══════════════════════════════════════════════════════════════

class WebSocketMessage {
  final String type;
  final dynamic data;
  final DateTime timestamp;

  WebSocketMessage({
    required this.type,
    required this.data,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  factory WebSocketMessage.fromJson(Map<String, dynamic> json) {
    return WebSocketMessage(
      type: json['type'] ?? 'unknown',
      data: json['data'],
      timestamp: json['timestamp'] != null
        ? DateTime.parse(json['timestamp'])
        : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() => {
    'type': type,
    'data': data,
    'timestamp': timestamp.toIso8601String(),
  };

  @override
  String toString() => 'WebSocketMessage($type: $data)';
}

// ═══════════════════════════════════════════════════════════════
// WEBSOCKET CLIENT BASE
// ═══════════════════════════════════════════════════════════════

abstract class WebSocketClientBase {
  WebSocket? _socket;
  Timer? _pingTimer;
  Timer? _reconnectTimer;

  final String url;
  final Duration pingInterval;
  final Duration reconnectDelay;
  final int maxReconnectAttempts;

  int _reconnectAttempts = 0;
  ConnectionState _state = ConnectionState.disconnected;

  // Stream controllers
  final _stateController = StreamController<ConnectionState>.broadcast();
  final _messageController = StreamController<WebSocketMessage>.broadcast();
  final _errorController = StreamController<dynamic>.broadcast();

  // Public streams
  Stream<ConnectionState> get stateStream => _stateController.stream;
  Stream<WebSocketMessage> get messageStream => _messageController.stream;
  Stream<dynamic> get errorStream => _errorController.stream;

  ConnectionState get state => _state;
  bool get isConnected => _state == ConnectionState.connected;

  WebSocketClientBase({
    String? url,
    Duration? pingInterval,
    Duration? reconnectDelay,
    int? maxReconnectAttempts,
  }) : url = url ?? WebSocketConfig.defaultUrl,
       pingInterval = pingInterval ?? WebSocketConfig.pingInterval,
       reconnectDelay = reconnectDelay ?? WebSocketConfig.reconnectDelay,
       maxReconnectAttempts = maxReconnectAttempts ?? WebSocketConfig.maxReconnectAttempts;

  // ═══════════════════════════════════════════════════════════════
  // CONNECTION MANAGEMENT
  // ═══════════════════════════════════════════════════════════════

  Future<void> connect() async {
    if (_state == ConnectionState.connected ||
        _state == ConnectionState.connecting) {
      return;
    }

    _setState(ConnectionState.connecting);

    try {
      _socket = await WebSocket.connect(url)
        .timeout(WebSocketConfig.connectionTimeout);

      _reconnectAttempts = 0;
      _setState(ConnectionState.connected);
      _startPingTimer();
      _listenToSocket();

      onConnected();

    } catch (e) {
      debugPrint('WebSocket connection error: $e');
      _errorController.add(e);
      _scheduleReconnect();
    }
  }

  void disconnect() {
    _cancelTimers();
    _socket?.close();
    _socket = null;
    _reconnectAttempts = 0;
    _setState(ConnectionState.disconnected);
    onDisconnected();
  }

  void _scheduleReconnect() {
    if (_reconnectAttempts >= maxReconnectAttempts) {
      _setState(ConnectionState.failed);
      onConnectionFailed();
      return;
    }

    _reconnectAttempts++;
    _setState(ConnectionState.reconnecting);

    final delay = reconnectDelay * _reconnectAttempts;
    debugPrint('Reconnecting in ${delay.inSeconds}s (attempt $_reconnectAttempts/$maxReconnectAttempts)');

    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(delay, () {
      connect();
    });
  }

  void _setState(ConnectionState newState) {
    if (_state != newState) {
      _state = newState;
      _stateController.add(newState);
    }
  }

  // ═══════════════════════════════════════════════════════════════
  // MESSAGE HANDLING
  // ═══════════════════════════════════════════════════════════════

  void _listenToSocket() {
    _socket?.listen(
      (data) {
        try {
          final json = jsonDecode(data as String);
          final message = WebSocketMessage.fromJson(json);
          _messageController.add(message);
          onMessage(message);
        } catch (e) {
          debugPrint('Error parsing WebSocket message: $e');
          _errorController.add(e);
        }
      },
      onError: (error) {
        debugPrint('WebSocket error: $error');
        _errorController.add(error);
        _scheduleReconnect();
      },
      onDone: () {
        debugPrint('WebSocket closed');
        if (_state != ConnectionState.disconnected) {
          _scheduleReconnect();
        }
      },
      cancelOnError: false,
    );
  }

  void send(String type, dynamic data) {
    if (!isConnected) {
      debugPrint('Cannot send: not connected');
      return;
    }

    final message = WebSocketMessage(type: type, data: data);
    _socket?.add(jsonEncode(message.toJson()));
  }

  void sendRaw(String data) {
    if (!isConnected) {
      debugPrint('Cannot send: not connected');
      return;
    }
    _socket?.add(data);
  }

  // ═══════════════════════════════════════════════════════════════
  // PING/PONG KEEPALIVE
  // ═══════════════════════════════════════════════════════════════

  void _startPingTimer() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(pingInterval, (_) {
      if (isConnected) {
        send('ping', {'timestamp': DateTime.now().millisecondsSinceEpoch});
      }
    });
  }

  void _cancelTimers() {
    _pingTimer?.cancel();
    _reconnectTimer?.cancel();
    _pingTimer = null;
    _reconnectTimer = null;
  }

  // ═══════════════════════════════════════════════════════════════
  // LIFECYCLE CALLBACKS (Override in subclass)
  // ═══════════════════════════════════════════════════════════════

  void onConnected() {}
  void onDisconnected() {}
  void onConnectionFailed() {}
  void onMessage(WebSocketMessage message) {}

  // ═══════════════════════════════════════════════════════════════
  // CLEANUP
  // ═══════════════════════════════════════════════════════════════

  void dispose() {
    disconnect();
    _stateController.close();
    _messageController.close();
    _errorController.close();
  }
}

// ═══════════════════════════════════════════════════════════════
// SUBSCRIPTION MANAGER
// ═══════════════════════════════════════════════════════════════

class SubscriptionManager {
  final Set<String> _subscriptions = {};
  final WebSocketClientBase _client;

  SubscriptionManager(this._client);

  Set<String> get subscriptions => Set.unmodifiable(_subscriptions);

  void subscribe(String channel) {
    if (_subscriptions.add(channel)) {
      if (_client.isConnected) {
        _client.send('subscribe', {'channel': channel});
      }
    }
  }

  void unsubscribe(String channel) {
    if (_subscriptions.remove(channel)) {
      if (_client.isConnected) {
        _client.send('unsubscribe', {'channel': channel});
      }
    }
  }

  void resubscribeAll() {
    for (final channel in _subscriptions) {
      _client.send('subscribe', {'channel': channel});
    }
  }

  void clear() {
    _subscriptions.clear();
  }
}

// ═══════════════════════════════════════════════════════════════
// EXAMPLE: FEATURE WEBSOCKET CLIENT
// Replace "FeatureName" with your feature name (e.g., "Trading", "Price")
// ═══════════════════════════════════════════════════════════════

class FeatureNameWebSocketClient extends WebSocketClientBase {
  late final SubscriptionManager _subscriptions;

  // Stream controllers for specific data types
  final _priceController = StreamController<Map<String, dynamic>>.broadcast();
  final _alertController = StreamController<Map<String, dynamic>>.broadcast();

  // Public streams
  Stream<Map<String, dynamic>> get priceStream => _priceController.stream;
  Stream<Map<String, dynamic>> get alertStream => _alertController.stream;

  FeatureNameWebSocketClient({super.url}) {
    _subscriptions = SubscriptionManager(this);
  }

  // ═══════════════════════════════════════════════════════════════
  // SUBSCRIPTION METHODS
  // ═══════════════════════════════════════════════════════════════

  void subscribeToPrice(String symbol) {
    _subscriptions.subscribe('price:$symbol');
  }

  void unsubscribeFromPrice(String symbol) {
    _subscriptions.unsubscribe('price:$symbol');
  }

  void subscribeToAlerts() {
    _subscriptions.subscribe('alerts');
  }

  // ═══════════════════════════════════════════════════════════════
  // MESSAGE HANDLING
  // ═══════════════════════════════════════════════════════════════

  @override
  void onConnected() {
    debugPrint('FeatureName WebSocket connected');
    // Resubscribe to all channels
    _subscriptions.resubscribeAll();
  }

  @override
  void onDisconnected() {
    debugPrint('FeatureName WebSocket disconnected');
  }

  @override
  void onConnectionFailed() {
    debugPrint('FeatureName WebSocket connection failed after max attempts');
  }

  @override
  void onMessage(WebSocketMessage message) {
    switch (message.type) {
      case 'price':
        _handlePriceUpdate(message.data);
        break;
      case 'alert':
        _handleAlert(message.data);
        break;
      case 'pong':
        // Keepalive response
        break;
      default:
        debugPrint('Unknown message type: ${message.type}');
    }
  }

  void _handlePriceUpdate(dynamic data) {
    if (data is Map<String, dynamic>) {
      _priceController.add(data);
    }
  }

  void _handleAlert(dynamic data) {
    if (data is Map<String, dynamic>) {
      _alertController.add(data);
    }
  }

  // ═══════════════════════════════════════════════════════════════
  // REQUEST METHODS
  // ═══════════════════════════════════════════════════════════════

  void requestPrice(String symbol) {
    send('get_price', {'symbol': symbol});
  }

  void requestHistory(String symbol, {int limit = 100}) {
    send('get_history', {'symbol': symbol, 'limit': limit});
  }

  // ═══════════════════════════════════════════════════════════════
  // CLEANUP
  // ═══════════════════════════════════════════════════════════════

  @override
  void dispose() {
    _subscriptions.clear();
    _priceController.close();
    _alertController.close();
    super.dispose();
  }
}

// ═══════════════════════════════════════════════════════════════
// USAGE EXAMPLE
// ═══════════════════════════════════════════════════════════════

void main() async {
  final client = FeatureNameWebSocketClient(url: 'ws://localhost:8765');

  // Listen to connection state
  client.stateStream.listen((state) {
    print('Connection state: $state');
  });

  // Listen to price updates
  client.priceStream.listen((data) {
    print('Price update: $data');
  });

  // Listen to alerts
  client.alertStream.listen((data) {
    print('Alert: $data');
  });

  // Listen to errors
  client.errorStream.listen((error) {
    print('Error: $error');
  });

  // Connect
  await client.connect();

  // Subscribe to prices
  client.subscribeToPrice('XAUUSD');
  client.subscribeToPrice('BTCUSD');
  client.subscribeToAlerts();

  // Request current price
  client.requestPrice('XAUUSD');

  // Keep alive for demo
  await Future.delayed(Duration(minutes: 5));

  // Cleanup
  client.dispose();
}
