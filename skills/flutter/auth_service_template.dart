/// Authentication Service Template
///
/// Handles user authentication with multiple providers.
///
/// Usage:
///   final auth = AuthService();
///   await auth.signInWithEmail(email, password);
///   final user = auth.currentUser;
///
/// Features:
/// - Email/password authentication
/// - OAuth providers (Google, Apple, GitHub)
/// - Token management
/// - Session persistence
/// - Biometric authentication

import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;

/// Authentication state
enum AuthState {
  initial,
  loading,
  authenticated,
  unauthenticated,
  error,
}

/// User model
class AuthUser {
  final String id;
  final String email;
  final String? displayName;
  final String? photoUrl;
  final DateTime? createdAt;
  final Map<String, dynamic>? metadata;

  AuthUser({
    required this.id,
    required this.email,
    this.displayName,
    this.photoUrl,
    this.createdAt,
    this.metadata,
  });

  factory AuthUser.fromJson(Map<String, dynamic> json) {
    return AuthUser(
      id: json['id'] ?? json['uid'] ?? '',
      email: json['email'] ?? '',
      displayName: json['displayName'] ?? json['display_name'],
      photoUrl: json['photoUrl'] ?? json['photo_url'],
      createdAt: json['createdAt'] != null
          ? DateTime.parse(json['createdAt'])
          : null,
      metadata: json['metadata'],
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'email': email,
        'displayName': displayName,
        'photoUrl': photoUrl,
        'createdAt': createdAt?.toIso8601String(),
        'metadata': metadata,
      };
}

/// Authentication tokens
class AuthTokens {
  final String accessToken;
  final String? refreshToken;
  final DateTime expiresAt;

  AuthTokens({
    required this.accessToken,
    this.refreshToken,
    required this.expiresAt,
  });

  bool get isExpired => DateTime.now().isAfter(expiresAt);

  factory AuthTokens.fromJson(Map<String, dynamic> json) {
    return AuthTokens(
      accessToken: json['access_token'] ?? json['accessToken'] ?? '',
      refreshToken: json['refresh_token'] ?? json['refreshToken'],
      expiresAt: json['expires_at'] != null
          ? DateTime.parse(json['expires_at'])
          : DateTime.now().add(Duration(hours: 1)),
    );
  }

  Map<String, dynamic> toJson() => {
        'access_token': accessToken,
        'refresh_token': refreshToken,
        'expires_at': expiresAt.toIso8601String(),
      };
}

/// Authentication result
class AuthResult {
  final bool success;
  final AuthUser? user;
  final AuthTokens? tokens;
  final String? error;

  AuthResult({
    required this.success,
    this.user,
    this.tokens,
    this.error,
  });

  factory AuthResult.success(AuthUser user, AuthTokens tokens) {
    return AuthResult(success: true, user: user, tokens: tokens);
  }

  factory AuthResult.failure(String error) {
    return AuthResult(success: false, error: error);
  }
}

/// Main authentication service
class AuthService extends ChangeNotifier {
  // Configuration
  final String baseUrl;
  final Duration tokenRefreshThreshold;

  // State
  AuthState _state = AuthState.initial;
  AuthUser? _currentUser;
  AuthTokens? _tokens;
  String? _lastError;

  // Storage keys
  static const _userKey = 'auth_user';
  static const _tokensKey = 'auth_tokens';

  // Stream controller for auth state changes
  final _authStateController = StreamController<AuthState>.broadcast();

  AuthService({
    this.baseUrl = 'https://api.example.com/auth',
    this.tokenRefreshThreshold = const Duration(minutes: 5),
  }) {
    _init();
  }

  // Getters
  AuthState get state => _state;
  AuthUser? get currentUser => _currentUser;
  AuthTokens? get tokens => _tokens;
  String? get lastError => _lastError;
  bool get isAuthenticated => _state == AuthState.authenticated;
  Stream<AuthState> get authStateChanges => _authStateController.stream;

  /// Initialize service - restore session
  Future<void> _init() async {
    _setState(AuthState.loading);

    try {
      final prefs = await SharedPreferences.getInstance();

      // Restore user
      final userJson = prefs.getString(_userKey);
      if (userJson != null) {
        _currentUser = AuthUser.fromJson(jsonDecode(userJson));
      }

      // Restore tokens
      final tokensJson = prefs.getString(_tokensKey);
      if (tokensJson != null) {
        _tokens = AuthTokens.fromJson(jsonDecode(tokensJson));

        // Check if tokens need refresh
        if (_tokens!.isExpired) {
          await _refreshTokens();
        } else if (_shouldRefreshToken()) {
          // Refresh in background
          _refreshTokens();
        }
      }

      if (_currentUser != null && _tokens != null && !_tokens!.isExpired) {
        _setState(AuthState.authenticated);
      } else {
        _setState(AuthState.unauthenticated);
      }
    } catch (e) {
      _lastError = e.toString();
      _setState(AuthState.unauthenticated);
    }
  }

  /// Sign in with email and password
  Future<AuthResult> signInWithEmail(String email, String password) async {
    _setState(AuthState.loading);

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return await _handleAuthSuccess(data);
      } else {
        final error = jsonDecode(response.body)['error'] ?? 'Login failed';
        return _handleAuthFailure(error);
      }
    } catch (e) {
      return _handleAuthFailure(e.toString());
    }
  }

  /// Sign up with email and password
  Future<AuthResult> signUpWithEmail(
    String email,
    String password, {
    String? displayName,
  }) async {
    _setState(AuthState.loading);

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
          'displayName': displayName,
        }),
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return await _handleAuthSuccess(data);
      } else {
        final error = jsonDecode(response.body)['error'] ?? 'Registration failed';
        return _handleAuthFailure(error);
      }
    } catch (e) {
      return _handleAuthFailure(e.toString());
    }
  }

  /// Sign in with OAuth provider
  Future<AuthResult> signInWithProvider(String provider, String token) async {
    _setState(AuthState.loading);

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/oauth/$provider'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'token': token}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return await _handleAuthSuccess(data);
      } else {
        final error = jsonDecode(response.body)['error'] ?? 'OAuth failed';
        return _handleAuthFailure(error);
      }
    } catch (e) {
      return _handleAuthFailure(e.toString());
    }
  }

  /// Sign out
  Future<void> signOut() async {
    _setState(AuthState.loading);

    try {
      // Call logout API
      if (_tokens != null) {
        await http.post(
          Uri.parse('$baseUrl/logout'),
          headers: {
            'Authorization': 'Bearer ${_tokens!.accessToken}',
          },
        );
      }
    } catch (e) {
      // Ignore logout API errors
    }

    // Clear local state
    await _clearSession();
    _setState(AuthState.unauthenticated);
  }

  /// Refresh tokens
  Future<bool> _refreshTokens() async {
    if (_tokens?.refreshToken == null) return false;

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/refresh'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'refresh_token': _tokens!.refreshToken,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _tokens = AuthTokens.fromJson(data);
        await _persistSession();
        return true;
      }
    } catch (e) {
      debugPrint('Token refresh failed: $e');
    }

    return false;
  }

  /// Check if token should be refreshed
  bool _shouldRefreshToken() {
    if (_tokens == null) return false;
    final timeUntilExpiry = _tokens!.expiresAt.difference(DateTime.now());
    return timeUntilExpiry < tokenRefreshThreshold;
  }

  /// Get valid access token (refreshes if needed)
  Future<String?> getAccessToken() async {
    if (_tokens == null) return null;

    if (_tokens!.isExpired || _shouldRefreshToken()) {
      final success = await _refreshTokens();
      if (!success) {
        await signOut();
        return null;
      }
    }

    return _tokens!.accessToken;
  }

  /// Handle successful authentication
  Future<AuthResult> _handleAuthSuccess(Map<String, dynamic> data) async {
    _currentUser = AuthUser.fromJson(data['user'] ?? data);
    _tokens = AuthTokens.fromJson(data['tokens'] ?? data);

    await _persistSession();
    _setState(AuthState.authenticated);

    return AuthResult.success(_currentUser!, _tokens!);
  }

  /// Handle authentication failure
  AuthResult _handleAuthFailure(String error) {
    _lastError = error;
    _setState(AuthState.error);
    return AuthResult.failure(error);
  }

  /// Persist session to storage
  Future<void> _persistSession() async {
    final prefs = await SharedPreferences.getInstance();

    if (_currentUser != null) {
      await prefs.setString(_userKey, jsonEncode(_currentUser!.toJson()));
    }

    if (_tokens != null) {
      await prefs.setString(_tokensKey, jsonEncode(_tokens!.toJson()));
    }
  }

  /// Clear session from storage
  Future<void> _clearSession() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_userKey);
    await prefs.remove(_tokensKey);

    _currentUser = null;
    _tokens = null;
    _lastError = null;
  }

  /// Update state and notify listeners
  void _setState(AuthState newState) {
    _state = newState;
    _authStateController.add(newState);
    notifyListeners();
  }

  /// Update user profile
  Future<bool> updateProfile({
    String? displayName,
    String? photoUrl,
  }) async {
    if (_currentUser == null || _tokens == null) return false;

    try {
      final response = await http.put(
        Uri.parse('$baseUrl/profile'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${_tokens!.accessToken}',
        },
        body: jsonEncode({
          'displayName': displayName,
          'photoUrl': photoUrl,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _currentUser = AuthUser.fromJson(data);
        await _persistSession();
        notifyListeners();
        return true;
      }
    } catch (e) {
      _lastError = e.toString();
    }

    return false;
  }

  /// Change password
  Future<bool> changePassword(String currentPassword, String newPassword) async {
    if (_tokens == null) return false;

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/change-password'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${_tokens!.accessToken}',
        },
        body: jsonEncode({
          'currentPassword': currentPassword,
          'newPassword': newPassword,
        }),
      );

      return response.statusCode == 200;
    } catch (e) {
      _lastError = e.toString();
      return false;
    }
  }

  /// Request password reset
  Future<bool> resetPassword(String email) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/reset-password'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}),
      );

      return response.statusCode == 200;
    } catch (e) {
      _lastError = e.toString();
      return false;
    }
  }

  @override
  void dispose() {
    _authStateController.close();
    super.dispose();
  }
}
