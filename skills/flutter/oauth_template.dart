/// ============================================================================
/// OAUTH AUTHENTICATION TEMPLATE
/// ============================================================================
///
/// A comprehensive authentication template supporting multiple OAuth providers:
/// - Google Sign-In
/// - Apple Sign-In
/// - Email/Password
/// - Microsoft (MSAL)
///
/// Platforms: iOS, Android, Web, macOS
///
/// DEPENDENCIES (add to pubspec.yaml):
/// ```yaml
/// dependencies:
///   firebase_core: ^2.24.0
///   firebase_auth: ^4.16.0
///   google_sign_in: ^6.2.1
///   sign_in_with_apple: ^5.0.0
///   flutter_secure_storage: ^9.0.0
///   msal_flutter: ^2.0.0  # Microsoft Auth
///   crypto: ^3.0.3
/// ```
///
/// SETUP REQUIRED:
/// 1. Firebase Console: Enable Authentication providers
/// 2. Google Cloud Console: Create OAuth 2.0 credentials
/// 3. Apple Developer: Configure Sign in with Apple
/// 4. Azure Portal: Register app for Microsoft auth
///
/// ============================================================================

import 'dart:convert';
import 'dart:math';
import 'package:crypto/crypto.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:sign_in_with_apple/sign_in_with_apple.dart';
// import 'package:msal_flutter/msal_flutter.dart'; // Uncomment when using Microsoft

// =============================================================================
// SECTION 1: ENUMS & CONSTANTS
// =============================================================================

/// Supported authentication providers
enum AuthProvider {
  google,
  apple,
  email,
  microsoft,
  anonymous,
}

/// Authentication states
enum AuthState {
  initial,
  loading,
  authenticated,
  unauthenticated,
  error,
}

/// OAuth configuration constants
class OAuthConfig {
  // Google
  static const String googleWebClientId = 'YOUR_GOOGLE_WEB_CLIENT_ID.apps.googleusercontent.com';
  static const String googleIOSClientId = 'YOUR_GOOGLE_IOS_CLIENT_ID.apps.googleusercontent.com';

  // Microsoft Azure AD
  static const String microsoftClientId = 'YOUR_MICROSOFT_CLIENT_ID';
  static const String microsoftTenantId = 'common'; // or specific tenant
  static const String microsoftRedirectUri = 'msauth://com.yourapp/callback';
  static const List<String> microsoftScopes = ['openid', 'profile', 'email', 'User.Read'];

  // Apple
  static const String appleServiceId = 'com.yourapp.service';
  static const String appleRedirectUri = 'https://your-domain.com/callbacks/sign_in_with_apple';

  // Token storage keys
  static const String accessTokenKey = 'auth_access_token';
  static const String refreshTokenKey = 'auth_refresh_token';
  static const String userDataKey = 'auth_user_data';
  static const String providerKey = 'auth_provider';
}

// =============================================================================
// SECTION 2: USER MODEL
// =============================================================================

/// Unified user model across all auth providers
class AuthUser {
  final String uid;
  final String? email;
  final String? displayName;
  final String? photoUrl;
  final AuthProvider provider;
  final DateTime? createdAt;
  final DateTime? lastSignIn;
  final Map<String, dynamic>? metadata;

  const AuthUser({
    required this.uid,
    this.email,
    this.displayName,
    this.photoUrl,
    required this.provider,
    this.createdAt,
    this.lastSignIn,
    this.metadata,
  });

  factory AuthUser.fromFirebaseUser(User user, AuthProvider provider) {
    return AuthUser(
      uid: user.uid,
      email: user.email,
      displayName: user.displayName,
      photoUrl: user.photoURL,
      provider: provider,
      createdAt: user.metadata.creationTime,
      lastSignIn: user.metadata.lastSignInTime,
      metadata: {
        'emailVerified': user.emailVerified,
        'isAnonymous': user.isAnonymous,
        'providerId': user.providerData.map((p) => p.providerId).toList(),
      },
    );
  }

  factory AuthUser.fromJson(Map<String, dynamic> json) {
    return AuthUser(
      uid: json['uid'] as String,
      email: json['email'] as String?,
      displayName: json['displayName'] as String?,
      photoUrl: json['photoUrl'] as String?,
      provider: AuthProvider.values.firstWhere(
        (p) => p.name == json['provider'],
        orElse: () => AuthProvider.email,
      ),
      createdAt: json['createdAt'] != null
          ? DateTime.parse(json['createdAt'])
          : null,
      lastSignIn: json['lastSignIn'] != null
          ? DateTime.parse(json['lastSignIn'])
          : null,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'uid': uid,
      'email': email,
      'displayName': displayName,
      'photoUrl': photoUrl,
      'provider': provider.name,
      'createdAt': createdAt?.toIso8601String(),
      'lastSignIn': lastSignIn?.toIso8601String(),
      'metadata': metadata,
    };
  }

  AuthUser copyWith({
    String? uid,
    String? email,
    String? displayName,
    String? photoUrl,
    AuthProvider? provider,
    DateTime? createdAt,
    DateTime? lastSignIn,
    Map<String, dynamic>? metadata,
  }) {
    return AuthUser(
      uid: uid ?? this.uid,
      email: email ?? this.email,
      displayName: displayName ?? this.displayName,
      photoUrl: photoUrl ?? this.photoUrl,
      provider: provider ?? this.provider,
      createdAt: createdAt ?? this.createdAt,
      lastSignIn: lastSignIn ?? this.lastSignIn,
      metadata: metadata ?? this.metadata,
    );
  }
}

// =============================================================================
// SECTION 3: AUTH RESULT
// =============================================================================

/// Result wrapper for authentication operations
class AuthResult {
  final bool success;
  final AuthUser? user;
  final String? errorMessage;
  final String? errorCode;

  const AuthResult({
    required this.success,
    this.user,
    this.errorMessage,
    this.errorCode,
  });

  factory AuthResult.success(AuthUser user) {
    return AuthResult(success: true, user: user);
  }

  factory AuthResult.failure(String message, {String? code}) {
    return AuthResult(
      success: false,
      errorMessage: message,
      errorCode: code,
    );
  }
}

// =============================================================================
// SECTION 4: OAUTH SERVICE
// =============================================================================

/// Main OAuth authentication service
class OAuthService {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  // Google Sign-In instance
  late final GoogleSignIn _googleSignIn;

  // Microsoft MSAL instance (uncomment when using)
  // late final PublicClientApplication _msalClient;

  // Current state
  AuthState _state = AuthState.initial;
  AuthUser? _currentUser;

  // Stream controller for auth state changes
  Stream<User?> get authStateChanges => _auth.authStateChanges();

  AuthState get state => _state;
  AuthUser? get currentUser => _currentUser;
  bool get isAuthenticated => _currentUser != null;

  OAuthService() {
    _googleSignIn = GoogleSignIn(
      clientId: kIsWeb ? OAuthConfig.googleWebClientId : null,
      scopes: ['email', 'profile'],
    );

    // Initialize Microsoft (uncomment when using)
    // _initMicrosoft();
  }

  // ---------------------------------------------------------------------------
  // INITIALIZATION
  // ---------------------------------------------------------------------------

  /// Initialize the auth service and restore session
  Future<void> initialize() async {
    _state = AuthState.loading;

    try {
      // Check for existing Firebase session
      final firebaseUser = _auth.currentUser;
      if (firebaseUser != null) {
        final providerName = await _storage.read(key: OAuthConfig.providerKey);
        final provider = AuthProvider.values.firstWhere(
          (p) => p.name == providerName,
          orElse: () => AuthProvider.email,
        );
        _currentUser = AuthUser.fromFirebaseUser(firebaseUser, provider);
        _state = AuthState.authenticated;
      } else {
        _state = AuthState.unauthenticated;
      }
    } catch (e) {
      debugPrint('OAuthService init error: $e');
      _state = AuthState.unauthenticated;
    }
  }

  // ---------------------------------------------------------------------------
  // GOOGLE SIGN-IN
  // ---------------------------------------------------------------------------

  /// Sign in with Google
  Future<AuthResult> signInWithGoogle() async {
    _state = AuthState.loading;

    try {
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();

      if (googleUser == null) {
        _state = AuthState.unauthenticated;
        return AuthResult.failure('Google sign-in cancelled');
      }

      final GoogleSignInAuthentication googleAuth =
          await googleUser.authentication;

      final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      final userCredential = await _auth.signInWithCredential(credential);

      if (userCredential.user != null) {
        _currentUser = AuthUser.fromFirebaseUser(
          userCredential.user!,
          AuthProvider.google,
        );
        await _saveSession(AuthProvider.google);
        _state = AuthState.authenticated;
        return AuthResult.success(_currentUser!);
      }

      _state = AuthState.unauthenticated;
      return AuthResult.failure('Failed to sign in with Google');

    } on FirebaseAuthException catch (e) {
      _state = AuthState.error;
      return AuthResult.failure(
        _getFirebaseErrorMessage(e.code),
        code: e.code,
      );
    } catch (e) {
      _state = AuthState.error;
      return AuthResult.failure('Google sign-in failed: $e');
    }
  }

  // ---------------------------------------------------------------------------
  // APPLE SIGN-IN
  // ---------------------------------------------------------------------------

  /// Sign in with Apple
  Future<AuthResult> signInWithApple() async {
    _state = AuthState.loading;

    try {
      // Generate nonce for security
      final rawNonce = _generateNonce();
      final nonce = _sha256ofString(rawNonce);

      final appleCredential = await SignInWithApple.getAppleIDCredential(
        scopes: [
          AppleIDAuthorizationScopes.email,
          AppleIDAuthorizationScopes.fullName,
        ],
        nonce: nonce,
        webAuthenticationOptions: kIsWeb
            ? WebAuthenticationOptions(
                clientId: OAuthConfig.appleServiceId,
                redirectUri: Uri.parse(OAuthConfig.appleRedirectUri),
              )
            : null,
      );

      final oauthCredential = OAuthProvider('apple.com').credential(
        idToken: appleCredential.identityToken,
        rawNonce: rawNonce,
      );

      final userCredential = await _auth.signInWithCredential(oauthCredential);

      if (userCredential.user != null) {
        // Apple only provides name on first sign-in, so we may need to update
        String? displayName;
        if (appleCredential.givenName != null ||
            appleCredential.familyName != null) {
          displayName = [
            appleCredential.givenName,
            appleCredential.familyName,
          ].where((s) => s != null).join(' ');

          // Update Firebase profile with name
          await userCredential.user!.updateDisplayName(displayName);
        }

        _currentUser = AuthUser.fromFirebaseUser(
          userCredential.user!,
          AuthProvider.apple,
        );
        await _saveSession(AuthProvider.apple);
        _state = AuthState.authenticated;
        return AuthResult.success(_currentUser!);
      }

      _state = AuthState.unauthenticated;
      return AuthResult.failure('Failed to sign in with Apple');

    } on SignInWithAppleAuthorizationException catch (e) {
      _state = AuthState.error;
      return AuthResult.failure('Apple sign-in failed: ${e.message}');
    } on FirebaseAuthException catch (e) {
      _state = AuthState.error;
      return AuthResult.failure(
        _getFirebaseErrorMessage(e.code),
        code: e.code,
      );
    } catch (e) {
      _state = AuthState.error;
      return AuthResult.failure('Apple sign-in failed: $e');
    }
  }

  // ---------------------------------------------------------------------------
  // EMAIL/PASSWORD SIGN-IN
  // ---------------------------------------------------------------------------

  /// Sign in with email and password
  Future<AuthResult> signInWithEmail(String email, String password) async {
    _state = AuthState.loading;

    try {
      final userCredential = await _auth.signInWithEmailAndPassword(
        email: email.trim(),
        password: password,
      );

      if (userCredential.user != null) {
        _currentUser = AuthUser.fromFirebaseUser(
          userCredential.user!,
          AuthProvider.email,
        );
        await _saveSession(AuthProvider.email);
        _state = AuthState.authenticated;
        return AuthResult.success(_currentUser!);
      }

      _state = AuthState.unauthenticated;
      return AuthResult.failure('Failed to sign in');

    } on FirebaseAuthException catch (e) {
      _state = AuthState.error;
      return AuthResult.failure(
        _getFirebaseErrorMessage(e.code),
        code: e.code,
      );
    } catch (e) {
      _state = AuthState.error;
      return AuthResult.failure('Sign-in failed: $e');
    }
  }

  /// Register with email and password
  Future<AuthResult> registerWithEmail(
    String email,
    String password,
    {String? displayName}
  ) async {
    _state = AuthState.loading;

    try {
      final userCredential = await _auth.createUserWithEmailAndPassword(
        email: email.trim(),
        password: password,
      );

      if (userCredential.user != null) {
        // Update display name if provided
        if (displayName != null && displayName.isNotEmpty) {
          await userCredential.user!.updateDisplayName(displayName);
        }

        // Send email verification
        await userCredential.user!.sendEmailVerification();

        _currentUser = AuthUser.fromFirebaseUser(
          userCredential.user!,
          AuthProvider.email,
        );
        await _saveSession(AuthProvider.email);
        _state = AuthState.authenticated;
        return AuthResult.success(_currentUser!);
      }

      _state = AuthState.unauthenticated;
      return AuthResult.failure('Failed to create account');

    } on FirebaseAuthException catch (e) {
      _state = AuthState.error;
      return AuthResult.failure(
        _getFirebaseErrorMessage(e.code),
        code: e.code,
      );
    } catch (e) {
      _state = AuthState.error;
      return AuthResult.failure('Registration failed: $e');
    }
  }

  /// Send password reset email
  Future<AuthResult> sendPasswordResetEmail(String email) async {
    try {
      await _auth.sendPasswordResetEmail(email: email.trim());
      return AuthResult.success(AuthUser(
        uid: '',
        email: email,
        provider: AuthProvider.email,
      ));
    } on FirebaseAuthException catch (e) {
      return AuthResult.failure(
        _getFirebaseErrorMessage(e.code),
        code: e.code,
      );
    } catch (e) {
      return AuthResult.failure('Failed to send reset email: $e');
    }
  }

  // ---------------------------------------------------------------------------
  // MICROSOFT SIGN-IN
  // ---------------------------------------------------------------------------

  /// Sign in with Microsoft (Azure AD)
  Future<AuthResult> signInWithMicrosoft() async {
    _state = AuthState.loading;

    try {
      // Web implementation using popup
      if (kIsWeb) {
        final microsoftProvider = OAuthProvider('microsoft.com');
        microsoftProvider.addScope('email');
        microsoftProvider.addScope('profile');
        microsoftProvider.setCustomParameters({
          'tenant': OAuthConfig.microsoftTenantId,
        });

        final userCredential = await _auth.signInWithPopup(microsoftProvider);

        if (userCredential.user != null) {
          _currentUser = AuthUser.fromFirebaseUser(
            userCredential.user!,
            AuthProvider.microsoft,
          );
          await _saveSession(AuthProvider.microsoft);
          _state = AuthState.authenticated;
          return AuthResult.success(_currentUser!);
        }
      } else {
        // Mobile implementation using MSAL
        // Uncomment and implement when using msal_flutter package
        /*
        final result = await _msalClient.acquireToken(
          scopes: OAuthConfig.microsoftScopes,
        );

        if (result != null) {
          final credential = OAuthProvider('microsoft.com').credential(
            accessToken: result.accessToken,
            idToken: result.idToken,
          );

          final userCredential = await _auth.signInWithCredential(credential);

          if (userCredential.user != null) {
            _currentUser = AuthUser.fromFirebaseUser(
              userCredential.user!,
              AuthProvider.microsoft,
            );
            await _saveSession(AuthProvider.microsoft);
            _state = AuthState.authenticated;
            return AuthResult.success(_currentUser!);
          }
        }
        */

        // Fallback: Use Firebase's built-in Microsoft provider
        final microsoftProvider = OAuthProvider('microsoft.com');
        microsoftProvider.addScope('email');
        microsoftProvider.addScope('profile');

        final userCredential = await _auth.signInWithProvider(microsoftProvider);

        if (userCredential.user != null) {
          _currentUser = AuthUser.fromFirebaseUser(
            userCredential.user!,
            AuthProvider.microsoft,
          );
          await _saveSession(AuthProvider.microsoft);
          _state = AuthState.authenticated;
          return AuthResult.success(_currentUser!);
        }
      }

      _state = AuthState.unauthenticated;
      return AuthResult.failure('Failed to sign in with Microsoft');

    } on FirebaseAuthException catch (e) {
      _state = AuthState.error;
      return AuthResult.failure(
        _getFirebaseErrorMessage(e.code),
        code: e.code,
      );
    } catch (e) {
      _state = AuthState.error;
      return AuthResult.failure('Microsoft sign-in failed: $e');
    }
  }

  // ---------------------------------------------------------------------------
  // SIGN OUT
  // ---------------------------------------------------------------------------

  /// Sign out from all providers
  Future<void> signOut() async {
    _state = AuthState.loading;

    try {
      // Sign out from Google if signed in
      if (await _googleSignIn.isSignedIn()) {
        await _googleSignIn.signOut();
      }

      // Sign out from Firebase
      await _auth.signOut();

      // Clear stored session
      await _clearSession();

      _currentUser = null;
      _state = AuthState.unauthenticated;
    } catch (e) {
      debugPrint('Sign out error: $e');
      _state = AuthState.error;
    }
  }

  // ---------------------------------------------------------------------------
  // ACCOUNT MANAGEMENT
  // ---------------------------------------------------------------------------

  /// Delete user account
  Future<AuthResult> deleteAccount() async {
    try {
      final user = _auth.currentUser;
      if (user == null) {
        return AuthResult.failure('No user signed in');
      }

      await user.delete();
      await _clearSession();

      _currentUser = null;
      _state = AuthState.unauthenticated;

      return AuthResult.success(AuthUser(
        uid: '',
        provider: AuthProvider.email,
      ));
    } on FirebaseAuthException catch (e) {
      if (e.code == 'requires-recent-login') {
        return AuthResult.failure(
          'Please sign in again before deleting your account',
          code: e.code,
        );
      }
      return AuthResult.failure(_getFirebaseErrorMessage(e.code), code: e.code);
    } catch (e) {
      return AuthResult.failure('Failed to delete account: $e');
    }
  }

  /// Link additional auth provider to current account
  Future<AuthResult> linkProvider(AuthProvider provider) async {
    final user = _auth.currentUser;
    if (user == null) {
      return AuthResult.failure('No user signed in');
    }

    try {
      AuthCredential? credential;

      switch (provider) {
        case AuthProvider.google:
          final googleUser = await _googleSignIn.signIn();
          if (googleUser == null) {
            return AuthResult.failure('Google sign-in cancelled');
          }
          final googleAuth = await googleUser.authentication;
          credential = GoogleAuthProvider.credential(
            accessToken: googleAuth.accessToken,
            idToken: googleAuth.idToken,
          );
          break;

        case AuthProvider.apple:
          final rawNonce = _generateNonce();
          final nonce = _sha256ofString(rawNonce);
          final appleCredential = await SignInWithApple.getAppleIDCredential(
            scopes: [
              AppleIDAuthorizationScopes.email,
              AppleIDAuthorizationScopes.fullName,
            ],
            nonce: nonce,
          );
          credential = OAuthProvider('apple.com').credential(
            idToken: appleCredential.identityToken,
            rawNonce: rawNonce,
          );
          break;

        default:
          return AuthResult.failure('Provider linking not supported');
      }

      if (credential != null) {
        await user.linkWithCredential(credential);
        return AuthResult.success(_currentUser!);
      }

      return AuthResult.failure('Failed to link provider');
    } on FirebaseAuthException catch (e) {
      return AuthResult.failure(_getFirebaseErrorMessage(e.code), code: e.code);
    } catch (e) {
      return AuthResult.failure('Failed to link provider: $e');
    }
  }

  // ---------------------------------------------------------------------------
  // HELPER METHODS
  // ---------------------------------------------------------------------------

  /// Save session to secure storage
  Future<void> _saveSession(AuthProvider provider) async {
    await _storage.write(key: OAuthConfig.providerKey, value: provider.name);
    if (_currentUser != null) {
      await _storage.write(
        key: OAuthConfig.userDataKey,
        value: jsonEncode(_currentUser!.toJson()),
      );
    }
  }

  /// Clear stored session
  Future<void> _clearSession() async {
    await _storage.delete(key: OAuthConfig.providerKey);
    await _storage.delete(key: OAuthConfig.userDataKey);
    await _storage.delete(key: OAuthConfig.accessTokenKey);
    await _storage.delete(key: OAuthConfig.refreshTokenKey);
  }

  /// Generate secure nonce for Apple Sign-In
  String _generateNonce([int length = 32]) {
    const charset =
        '0123456789ABCDEFGHIJKLMNOPQRSTUVXYZabcdefghijklmnopqrstuvwxyz-._';
    final random = Random.secure();
    return List.generate(length, (_) => charset[random.nextInt(charset.length)])
        .join();
  }

  /// SHA256 hash for nonce
  String _sha256ofString(String input) {
    final bytes = utf8.encode(input);
    final digest = sha256.convert(bytes);
    return digest.toString();
  }

  /// Get user-friendly error message from Firebase error code
  String _getFirebaseErrorMessage(String code) {
    switch (code) {
      case 'user-not-found':
        return 'No account found with this email';
      case 'wrong-password':
        return 'Incorrect password';
      case 'email-already-in-use':
        return 'An account already exists with this email';
      case 'invalid-email':
        return 'Invalid email address';
      case 'weak-password':
        return 'Password is too weak. Use at least 6 characters';
      case 'user-disabled':
        return 'This account has been disabled';
      case 'too-many-requests':
        return 'Too many attempts. Please try again later';
      case 'operation-not-allowed':
        return 'This sign-in method is not enabled';
      case 'account-exists-with-different-credential':
        return 'An account already exists with a different sign-in method';
      case 'invalid-credential':
        return 'Invalid credentials. Please try again';
      case 'requires-recent-login':
        return 'Please sign in again to complete this action';
      case 'network-request-failed':
        return 'Network error. Check your connection';
      default:
        return 'Authentication failed. Please try again';
    }
  }
}

// =============================================================================
// SECTION 5: AUTH PROVIDER (STATE MANAGEMENT)
// =============================================================================

/// Provider for managing auth state across the app
class AuthNotifier extends ChangeNotifier {
  final OAuthService _authService = OAuthService();

  AuthState get state => _authService.state;
  AuthUser? get user => _authService.currentUser;
  bool get isAuthenticated => _authService.isAuthenticated;
  bool get isLoading => _authService.state == AuthState.loading;

  /// Initialize auth service
  Future<void> initialize() async {
    await _authService.initialize();
    notifyListeners();
  }

  /// Sign in with Google
  Future<AuthResult> signInWithGoogle() async {
    notifyListeners();
    final result = await _authService.signInWithGoogle();
    notifyListeners();
    return result;
  }

  /// Sign in with Apple
  Future<AuthResult> signInWithApple() async {
    notifyListeners();
    final result = await _authService.signInWithApple();
    notifyListeners();
    return result;
  }

  /// Sign in with email
  Future<AuthResult> signInWithEmail(String email, String password) async {
    notifyListeners();
    final result = await _authService.signInWithEmail(email, password);
    notifyListeners();
    return result;
  }

  /// Register with email
  Future<AuthResult> registerWithEmail(
    String email,
    String password,
    {String? displayName}
  ) async {
    notifyListeners();
    final result = await _authService.registerWithEmail(
      email,
      password,
      displayName: displayName,
    );
    notifyListeners();
    return result;
  }

  /// Sign in with Microsoft
  Future<AuthResult> signInWithMicrosoft() async {
    notifyListeners();
    final result = await _authService.signInWithMicrosoft();
    notifyListeners();
    return result;
  }

  /// Send password reset
  Future<AuthResult> sendPasswordReset(String email) async {
    return await _authService.sendPasswordResetEmail(email);
  }

  /// Sign out
  Future<void> signOut() async {
    await _authService.signOut();
    notifyListeners();
  }

  /// Delete account
  Future<AuthResult> deleteAccount() async {
    final result = await _authService.deleteAccount();
    notifyListeners();
    return result;
  }
}

// =============================================================================
// SECTION 6: UI WIDGETS
// =============================================================================

/// Social sign-in button widget
class SocialSignInButton extends StatelessWidget {
  final AuthProvider provider;
  final VoidCallback onPressed;
  final bool isLoading;

  const SocialSignInButton({
    super.key,
    required this.provider,
    required this.onPressed,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 50,
      child: ElevatedButton(
        onPressed: isLoading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: _getBackgroundColor(),
          foregroundColor: _getForegroundColor(),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
            side: BorderSide(color: _getBorderColor()),
          ),
        ),
        child: isLoading
            ? const SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _getIcon(),
                  const SizedBox(width: 12),
                  Text(
                    _getButtonText(),
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
      ),
    );
  }

  Widget _getIcon() {
    switch (provider) {
      case AuthProvider.google:
        return Image.network(
          'https://www.google.com/favicon.ico',
          width: 24,
          height: 24,
          errorBuilder: (_, __, ___) => const Icon(Icons.g_mobiledata, size: 24),
        );
      case AuthProvider.apple:
        return const Icon(Icons.apple, size: 24);
      case AuthProvider.microsoft:
        return const Icon(Icons.window, size: 24);
      case AuthProvider.email:
        return const Icon(Icons.email, size: 24);
      default:
        return const Icon(Icons.login, size: 24);
    }
  }

  String _getButtonText() {
    switch (provider) {
      case AuthProvider.google:
        return 'Continue with Google';
      case AuthProvider.apple:
        return 'Continue with Apple';
      case AuthProvider.microsoft:
        return 'Continue with Microsoft';
      case AuthProvider.email:
        return 'Continue with Email';
      default:
        return 'Sign In';
    }
  }

  Color _getBackgroundColor() {
    switch (provider) {
      case AuthProvider.google:
        return Colors.white;
      case AuthProvider.apple:
        return Colors.black;
      case AuthProvider.microsoft:
        return const Color(0xFF2F2F2F);
      default:
        return Colors.blue;
    }
  }

  Color _getForegroundColor() {
    switch (provider) {
      case AuthProvider.google:
        return Colors.black87;
      default:
        return Colors.white;
    }
  }

  Color _getBorderColor() {
    switch (provider) {
      case AuthProvider.google:
        return Colors.grey.shade300;
      default:
        return Colors.transparent;
    }
  }
}

/// Complete login page widget
class LoginPage extends StatefulWidget {
  final Function(AuthUser user)? onLoginSuccess;
  final VoidCallback? onRegisterTap;

  const LoginPage({
    super.key,
    this.onLoginSuccess,
    this.onRegisterTap,
  });

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _authService = OAuthService();

  bool _isLoading = false;
  bool _obscurePassword = true;
  String? _errorMessage;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleSignIn(Future<AuthResult> Function() signInMethod) async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final result = await signInMethod();

    setState(() => _isLoading = false);

    if (result.success && result.user != null) {
      widget.onLoginSuccess?.call(result.user!);
    } else {
      setState(() => _errorMessage = result.errorMessage);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 48),

              // Logo/Header
              const Icon(Icons.lock_outline, size: 64, color: Colors.blue),
              const SizedBox(height: 24),
              Text(
                'Welcome Back',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                'Sign in to continue',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: Colors.grey,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 48),

              // Error message
              if (_errorMessage != null) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.shade50,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    _errorMessage!,
                    style: TextStyle(color: Colors.red.shade700),
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 24),
              ],

              // Social sign-in buttons
              SocialSignInButton(
                provider: AuthProvider.google,
                isLoading: _isLoading,
                onPressed: () => _handleSignIn(_authService.signInWithGoogle),
              ),
              const SizedBox(height: 12),

              SocialSignInButton(
                provider: AuthProvider.apple,
                isLoading: _isLoading,
                onPressed: () => _handleSignIn(_authService.signInWithApple),
              ),
              const SizedBox(height: 12),

              SocialSignInButton(
                provider: AuthProvider.microsoft,
                isLoading: _isLoading,
                onPressed: () => _handleSignIn(_authService.signInWithMicrosoft),
              ),

              const SizedBox(height: 24),

              // Divider
              Row(
                children: [
                  const Expanded(child: Divider()),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: Text(
                      'or',
                      style: TextStyle(color: Colors.grey.shade600),
                    ),
                  ),
                  const Expanded(child: Divider()),
                ],
              ),

              const SizedBox(height: 24),

              // Email/Password form
              Form(
                key: _formKey,
                child: Column(
                  children: [
                    TextFormField(
                      controller: _emailController,
                      keyboardType: TextInputType.emailAddress,
                      decoration: const InputDecoration(
                        labelText: 'Email',
                        prefixIcon: Icon(Icons.email_outlined),
                        border: OutlineInputBorder(),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your email';
                        }
                        if (!value.contains('@')) {
                          return 'Please enter a valid email';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _passwordController,
                      obscureText: _obscurePassword,
                      decoration: InputDecoration(
                        labelText: 'Password',
                        prefixIcon: const Icon(Icons.lock_outlined),
                        border: const OutlineInputBorder(),
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscurePassword
                                ? Icons.visibility_outlined
                                : Icons.visibility_off_outlined,
                          ),
                          onPressed: () {
                            setState(() => _obscurePassword = !_obscurePassword);
                          },
                        ),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your password';
                        }
                        if (value.length < 6) {
                          return 'Password must be at least 6 characters';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 8),
                    Align(
                      alignment: Alignment.centerRight,
                      child: TextButton(
                        onPressed: () {
                          // Handle forgot password
                          if (_emailController.text.isNotEmpty) {
                            _authService.sendPasswordResetEmail(
                              _emailController.text,
                            );
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Password reset email sent'),
                              ),
                            );
                          }
                        },
                        child: const Text('Forgot Password?'),
                      ),
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      height: 50,
                      child: ElevatedButton(
                        onPressed: _isLoading
                            ? null
                            : () {
                                if (_formKey.currentState!.validate()) {
                                  _handleSignIn(
                                    () => _authService.signInWithEmail(
                                      _emailController.text,
                                      _passwordController.text,
                                    ),
                                  );
                                }
                              },
                        child: _isLoading
                            ? const CircularProgressIndicator()
                            : const Text('Sign In'),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Register link
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text("Don't have an account?"),
                  TextButton(
                    onPressed: widget.onRegisterTap,
                    child: const Text('Sign Up'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// =============================================================================
// SECTION 7: USAGE EXAMPLE
// =============================================================================

/*
USAGE EXAMPLE:

1. Initialize in main.dart:
```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();

  runApp(
    ChangeNotifierProvider(
      create: (_) => AuthNotifier()..initialize(),
      child: MyApp(),
    ),
  );
}
```

2. Check auth state:
```dart
class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer<AuthNotifier>(
      builder: (context, auth, _) {
        if (auth.isLoading) {
          return LoadingScreen();
        }
        return auth.isAuthenticated ? HomeScreen() : LoginPage();
      },
    );
  }
}
```

3. Sign in:
```dart
final result = await context.read<AuthNotifier>().signInWithGoogle();
if (result.success) {
  // Navigate to home
} else {
  // Show error: result.errorMessage
}
```

4. Sign out:
```dart
await context.read<AuthNotifier>().signOut();
```

WEB CONFIGURATION:

1. Add to web/index.html:
```html
<script src="https://www.gstatic.com/firebasejs/9.x.x/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/9.x.x/firebase-auth-compat.js"></script>
<script>
  firebase.initializeApp({
    apiKey: "...",
    authDomain: "...",
    projectId: "...",
    // etc
  });
</script>
```

2. Configure OAuth redirect domains in Firebase Console

PLATFORM-SPECIFIC SETUP:

iOS (ios/Runner/Info.plist):
```xml
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>com.googleusercontent.apps.YOUR_CLIENT_ID</string>
    </array>
  </dict>
</array>
<key>GIDClientID</key>
<string>YOUR_IOS_CLIENT_ID.apps.googleusercontent.com</string>
```

Android (android/app/build.gradle):
```gradle
defaultConfig {
    manifestPlaceholders += [
        'appAuthRedirectScheme': 'com.yourapp'
    ]
}
```
*/
