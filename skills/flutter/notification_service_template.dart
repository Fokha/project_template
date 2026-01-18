/// Notification Service Template
///
/// Firebase Cloud Messaging + Local Notifications
/// Features: Push notifications, local notifications, topics, deep linking
///
/// Usage:
/// 1. Add firebase_messaging and flutter_local_notifications to pubspec.yaml
/// 2. Configure Firebase in your project
/// 3. Initialize in main.dart before runApp

import 'dart:convert';
import 'dart:io';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Background message handler - must be top-level function
@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  print('Background message: ${message.messageId}');
  // Handle background message
}

/// Notification payload model
class NotificationPayload {
  final String? title;
  final String? body;
  final Map<String, dynamic>? data;
  final String? imageUrl;
  final DateTime receivedAt;

  NotificationPayload({
    this.title,
    this.body,
    this.data,
    this.imageUrl,
    DateTime? receivedAt,
  }) : receivedAt = receivedAt ?? DateTime.now();

  factory NotificationPayload.fromRemoteMessage(RemoteMessage message) {
    return NotificationPayload(
      title: message.notification?.title,
      body: message.notification?.body,
      data: message.data,
      imageUrl: message.notification?.android?.imageUrl ??
          message.notification?.apple?.imageUrl,
    );
  }

  factory NotificationPayload.fromJson(String jsonString) {
    final data = json.decode(jsonString) as Map<String, dynamic>;
    return NotificationPayload(
      title: data['title'],
      body: data['body'],
      data: data['data'],
      imageUrl: data['imageUrl'],
    );
  }

  String toJson() => json.encode({
        'title': title,
        'body': body,
        'data': data,
        'imageUrl': imageUrl,
      });
}

/// Notification service for FCM and local notifications
class NotificationService {
  final FirebaseMessaging _messaging;
  final FlutterLocalNotificationsPlugin _localNotifications;

  // Android notification channel
  static const AndroidNotificationChannel _channel = AndroidNotificationChannel(
    'high_importance_channel',
    'High Importance Notifications',
    description: 'This channel is used for important notifications.',
    importance: Importance.high,
    playSound: true,
  );

  // Callbacks
  Function(NotificationPayload)? onNotificationTapped;
  Function(NotificationPayload)? onNotificationReceived;

  NotificationService({
    FirebaseMessaging? messaging,
    FlutterLocalNotificationsPlugin? localNotifications,
  })  : _messaging = messaging ?? FirebaseMessaging.instance,
        _localNotifications =
            localNotifications ?? FlutterLocalNotificationsPlugin();

  /// Initialize the notification service
  Future<void> initialize() async {
    // Request permission
    await _requestPermission();

    // Initialize local notifications
    await _initializeLocalNotifications();

    // Configure FCM
    await _configureFCM();

    // Get initial message (app opened from terminated state)
    final initialMessage = await _messaging.getInitialMessage();
    if (initialMessage != null) {
      _handleMessage(initialMessage, fromBackground: true);
    }
  }

  /// Request notification permission
  Future<bool> _requestPermission() async {
    final settings = await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
      announcement: false,
      carPlay: false,
      criticalAlert: false,
    );

    return settings.authorizationStatus == AuthorizationStatus.authorized ||
        settings.authorizationStatus == AuthorizationStatus.provisional;
  }

  /// Initialize local notifications
  Future<void> _initializeLocalNotifications() async {
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    const initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _localNotifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );

    // Create Android notification channel
    if (!kIsWeb && Platform.isAndroid) {
      await _localNotifications
          .resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>()
          ?.createNotificationChannel(_channel);
    }
  }

  /// Configure Firebase Cloud Messaging
  Future<void> _configureFCM() async {
    // Foreground message handling
    FirebaseMessaging.onMessage.listen((message) {
      _handleMessage(message, fromBackground: false);
      _showLocalNotification(message);
    });

    // Background/terminated message tap handling
    FirebaseMessaging.onMessageOpenedApp.listen((message) {
      _handleMessage(message, fromBackground: true);
    });

    // Set foreground notification presentation options (iOS)
    await _messaging.setForegroundNotificationPresentationOptions(
      alert: true,
      badge: true,
      sound: true,
    );
  }

  /// Handle incoming message
  void _handleMessage(RemoteMessage message, {required bool fromBackground}) {
    final payload = NotificationPayload.fromRemoteMessage(message);

    if (fromBackground) {
      onNotificationTapped?.call(payload);
    } else {
      onNotificationReceived?.call(payload);
    }
  }

  /// Handle notification tap
  void _onNotificationTapped(NotificationResponse response) {
    if (response.payload != null) {
      final payload = NotificationPayload.fromJson(response.payload!);
      onNotificationTapped?.call(payload);
    }
  }

  /// Show local notification from FCM message
  Future<void> _showLocalNotification(RemoteMessage message) async {
    final notification = message.notification;
    if (notification == null) return;

    final androidDetails = AndroidNotificationDetails(
      _channel.id,
      _channel.name,
      channelDescription: _channel.description,
      importance: Importance.high,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
    );

    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    final details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    final payload = NotificationPayload.fromRemoteMessage(message);

    await _localNotifications.show(
      message.hashCode,
      notification.title,
      notification.body,
      details,
      payload: payload.toJson(),
    );
  }

  // ============ PUBLIC METHODS ============

  /// Get FCM token
  Future<String?> getToken() async {
    return await _messaging.getToken();
  }

  /// Subscribe to topic
  Future<void> subscribeToTopic(String topic) async {
    await _messaging.subscribeToTopic(topic);
  }

  /// Unsubscribe from topic
  Future<void> unsubscribeFromTopic(String topic) async {
    await _messaging.unsubscribeFromTopic(topic);
  }

  /// Show local notification
  Future<void> showNotification({
    required int id,
    required String title,
    required String body,
    Map<String, dynamic>? data,
  }) async {
    final androidDetails = AndroidNotificationDetails(
      _channel.id,
      _channel.name,
      channelDescription: _channel.description,
      importance: Importance.high,
      priority: Priority.high,
    );

    const iosDetails = DarwinNotificationDetails();

    final details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    final payload = NotificationPayload(
      title: title,
      body: body,
      data: data,
    );

    await _localNotifications.show(id, title, body, details, payload: payload.toJson());
  }

  /// Schedule notification
  Future<void> scheduleNotification({
    required int id,
    required String title,
    required String body,
    required DateTime scheduledDate,
    Map<String, dynamic>? data,
  }) async {
    final androidDetails = AndroidNotificationDetails(
      _channel.id,
      _channel.name,
      channelDescription: _channel.description,
    );

    const iosDetails = DarwinNotificationDetails();

    final details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    final payload = NotificationPayload(
      title: title,
      body: body,
      data: data,
    );

    await _localNotifications.zonedSchedule(
      id,
      title,
      body,
      TZDateTime.from(scheduledDate, local),
      details,
      payload: payload.toJson(),
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
    );
  }

  /// Cancel notification
  Future<void> cancelNotification(int id) async {
    await _localNotifications.cancel(id);
  }

  /// Cancel all notifications
  Future<void> cancelAllNotifications() async {
    await _localNotifications.cancelAll();
  }

  /// Get pending notifications
  Future<List<PendingNotificationRequest>> getPendingNotifications() async {
    return await _localNotifications.pendingNotificationRequests();
  }
}

/// Provider for notification service
final notificationServiceProvider = Provider<NotificationService>((ref) {
  return NotificationService();
});

/// Placeholder for timezone - import from timezone package
class TZDateTime {
  static DateTime from(DateTime dateTime, dynamic location) => dateTime;
}

const local = null;
