/// Theme Service Template
///
/// Dynamic theme management with light/dark mode and custom themes
/// Features: System theme detection, persistence, custom colors
///
/// Usage:
/// 1. Initialize in main.dart with ProviderScope
/// 2. Wrap MaterialApp with Consumer to use theme
/// 3. Use themeProvider to toggle theme mode

import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Theme mode options
enum AppThemeMode {
  light,
  dark,
  system,
}

/// Custom color scheme
class AppColors {
  final Color primary;
  final Color secondary;
  final Color accent;
  final Color background;
  final Color surface;
  final Color error;
  final Color onPrimary;
  final Color onSecondary;
  final Color onBackground;
  final Color onSurface;
  final Color onError;

  const AppColors({
    required this.primary,
    required this.secondary,
    required this.accent,
    required this.background,
    required this.surface,
    required this.error,
    required this.onPrimary,
    required this.onSecondary,
    required this.onBackground,
    required this.onSurface,
    required this.onError,
  });

  /// Default light colors
  static const AppColors lightDefault = AppColors(
    primary: Color(0xFF6200EE),
    secondary: Color(0xFF03DAC6),
    accent: Color(0xFF03DAC6),
    background: Color(0xFFFAFAFA),
    surface: Colors.white,
    error: Color(0xFFB00020),
    onPrimary: Colors.white,
    onSecondary: Colors.black,
    onBackground: Colors.black87,
    onSurface: Colors.black87,
    onError: Colors.white,
  );

  /// Default dark colors
  static const AppColors darkDefault = AppColors(
    primary: Color(0xFFBB86FC),
    secondary: Color(0xFF03DAC6),
    accent: Color(0xFF03DAC6),
    background: Color(0xFF121212),
    surface: Color(0xFF1E1E1E),
    error: Color(0xFFCF6679),
    onPrimary: Colors.black,
    onSecondary: Colors.black,
    onBackground: Colors.white,
    onSurface: Colors.white,
    onError: Colors.black,
  );
}

/// Theme state
class ThemeState {
  final AppThemeMode mode;
  final AppColors lightColors;
  final AppColors darkColors;
  final String fontFamily;
  final bool useMaterial3;

  const ThemeState({
    this.mode = AppThemeMode.system,
    this.lightColors = AppColors.lightDefault,
    this.darkColors = AppColors.darkDefault,
    this.fontFamily = 'Roboto',
    this.useMaterial3 = true,
  });

  ThemeState copyWith({
    AppThemeMode? mode,
    AppColors? lightColors,
    AppColors? darkColors,
    String? fontFamily,
    bool? useMaterial3,
  }) {
    return ThemeState(
      mode: mode ?? this.mode,
      lightColors: lightColors ?? this.lightColors,
      darkColors: darkColors ?? this.darkColors,
      fontFamily: fontFamily ?? this.fontFamily,
      useMaterial3: useMaterial3 ?? this.useMaterial3,
    );
  }

  /// Get the appropriate colors based on brightness
  AppColors getColors(Brightness brightness) {
    return brightness == Brightness.dark ? darkColors : lightColors;
  }

  /// Resolve actual theme mode considering system preference
  ThemeMode get resolvedThemeMode {
    switch (mode) {
      case AppThemeMode.light:
        return ThemeMode.light;
      case AppThemeMode.dark:
        return ThemeMode.dark;
      case AppThemeMode.system:
        return ThemeMode.system;
    }
  }

  /// Check if dark mode is active
  bool get isDark {
    if (mode == AppThemeMode.dark) return true;
    if (mode == AppThemeMode.light) return false;
    // System mode - check platform brightness
    return SchedulerBinding.instance.platformDispatcher.platformBrightness ==
        Brightness.dark;
  }

  /// Build light theme data
  ThemeData get lightTheme => _buildTheme(Brightness.light);

  /// Build dark theme data
  ThemeData get darkTheme => _buildTheme(Brightness.dark);

  ThemeData _buildTheme(Brightness brightness) {
    final colors = getColors(brightness);
    final isDarkMode = brightness == Brightness.dark;

    final colorScheme = ColorScheme(
      brightness: brightness,
      primary: colors.primary,
      onPrimary: colors.onPrimary,
      secondary: colors.secondary,
      onSecondary: colors.onSecondary,
      error: colors.error,
      onError: colors.onError,
      surface: colors.surface,
      onSurface: colors.onSurface,
    );

    return ThemeData(
      useMaterial3: useMaterial3,
      colorScheme: colorScheme,
      brightness: brightness,
      fontFamily: fontFamily,
      scaffoldBackgroundColor: colors.background,
      appBarTheme: AppBarTheme(
        backgroundColor: colors.surface,
        foregroundColor: colors.onSurface,
        elevation: isDarkMode ? 0 : 1,
        centerTitle: true,
      ),
      cardTheme: CardTheme(
        color: colors.surface,
        elevation: isDarkMode ? 2 : 1,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: colors.primary,
          foregroundColor: colors.onPrimary,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: colors.primary,
          side: BorderSide(color: colors.primary),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: colors.primary,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: isDarkMode ? colors.surface : colors.background,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: colors.onSurface.withValues(alpha: 0.2)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: colors.onSurface.withValues(alpha: 0.2)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: colors.primary, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: colors.error),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      ),
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: colors.surface,
        selectedItemColor: colors.primary,
        unselectedItemColor: colors.onSurface.withValues(alpha: 0.6),
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: colors.primary,
        foregroundColor: colors.onPrimary,
      ),
      dialogTheme: DialogTheme(
        backgroundColor: colors.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: isDarkMode ? colors.surface : Colors.grey[800],
        contentTextStyle: TextStyle(color: isDarkMode ? colors.onSurface : Colors.white),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      dividerTheme: DividerThemeData(
        color: colors.onSurface.withValues(alpha: 0.12),
        thickness: 1,
      ),
      listTileTheme: ListTileThemeData(
        iconColor: colors.onSurface.withValues(alpha: 0.7),
        textColor: colors.onSurface,
      ),
      chipTheme: ChipThemeData(
        backgroundColor: colors.surface,
        selectedColor: colors.primary.withValues(alpha: 0.2),
        labelStyle: TextStyle(color: colors.onSurface),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    );
  }
}

/// Theme notifier for state management
class ThemeNotifier extends StateNotifier<ThemeState> {
  static const _themeModeKey = 'theme_mode';
  static const _fontFamilyKey = 'font_family';
  static const _useMaterial3Key = 'use_material3';

  ThemeNotifier() : super(const ThemeState()) {
    _loadSavedTheme();
  }

  /// Load saved theme preferences
  Future<void> _loadSavedTheme() async {
    final prefs = await SharedPreferences.getInstance();

    final modeIndex = prefs.getInt(_themeModeKey) ?? 2; // Default: system
    final fontFamily = prefs.getString(_fontFamilyKey) ?? 'Roboto';
    final useMaterial3 = prefs.getBool(_useMaterial3Key) ?? true;

    state = state.copyWith(
      mode: AppThemeMode.values[modeIndex],
      fontFamily: fontFamily,
      useMaterial3: useMaterial3,
    );
  }

  /// Set theme mode
  Future<void> setThemeMode(AppThemeMode mode) async {
    state = state.copyWith(mode: mode);

    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_themeModeKey, mode.index);
  }

  /// Toggle between light and dark mode
  Future<void> toggleTheme() async {
    final newMode = state.isDark ? AppThemeMode.light : AppThemeMode.dark;
    await setThemeMode(newMode);
  }

  /// Set font family
  Future<void> setFontFamily(String fontFamily) async {
    state = state.copyWith(fontFamily: fontFamily);

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_fontFamilyKey, fontFamily);
  }

  /// Set Material 3 usage
  Future<void> setUseMaterial3(bool use) async {
    state = state.copyWith(useMaterial3: use);

    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_useMaterial3Key, use);
  }

  /// Set custom light colors
  void setLightColors(AppColors colors) {
    state = state.copyWith(lightColors: colors);
  }

  /// Set custom dark colors
  void setDarkColors(AppColors colors) {
    state = state.copyWith(darkColors: colors);
  }

  /// Reset to defaults
  Future<void> resetToDefaults() async {
    state = const ThemeState();

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_themeModeKey);
    await prefs.remove(_fontFamilyKey);
    await prefs.remove(_useMaterial3Key);
  }
}

/// Theme provider
final themeProvider = StateNotifierProvider<ThemeNotifier, ThemeState>((ref) {
  return ThemeNotifier();
});

/// Convenience providers
final themeModeProvider = Provider<AppThemeMode>((ref) {
  return ref.watch(themeProvider).mode;
});

final isDarkModeProvider = Provider<bool>((ref) {
  return ref.watch(themeProvider).isDark;
});

final lightThemeProvider = Provider<ThemeData>((ref) {
  return ref.watch(themeProvider).lightTheme;
});

final darkThemeProvider = Provider<ThemeData>((ref) {
  return ref.watch(themeProvider).darkTheme;
});

/// Theme switcher widget
class ThemeSwitcher extends ConsumerWidget {
  const ThemeSwitcher({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeState = ref.watch(themeProvider);

    return PopupMenuButton<AppThemeMode>(
      icon: Icon(
        themeState.isDark ? Icons.dark_mode : Icons.light_mode,
      ),
      onSelected: (mode) {
        ref.read(themeProvider.notifier).setThemeMode(mode);
      },
      itemBuilder: (context) => [
        PopupMenuItem(
          value: AppThemeMode.light,
          child: Row(
            children: [
              const Icon(Icons.light_mode),
              const SizedBox(width: 12),
              const Text('Light'),
              if (themeState.mode == AppThemeMode.light)
                const Padding(
                  padding: EdgeInsets.only(left: 8),
                  child: Icon(Icons.check, size: 18),
                ),
            ],
          ),
        ),
        PopupMenuItem(
          value: AppThemeMode.dark,
          child: Row(
            children: [
              const Icon(Icons.dark_mode),
              const SizedBox(width: 12),
              const Text('Dark'),
              if (themeState.mode == AppThemeMode.dark)
                const Padding(
                  padding: EdgeInsets.only(left: 8),
                  child: Icon(Icons.check, size: 18),
                ),
            ],
          ),
        ),
        PopupMenuItem(
          value: AppThemeMode.system,
          child: Row(
            children: [
              const Icon(Icons.settings_brightness),
              const SizedBox(width: 12),
              const Text('System'),
              if (themeState.mode == AppThemeMode.system)
                const Padding(
                  padding: EdgeInsets.only(left: 8),
                  child: Icon(Icons.check, size: 18),
                ),
            ],
          ),
        ),
      ],
    );
  }
}

/// Simple theme toggle button
class ThemeToggleButton extends ConsumerWidget {
  const ThemeToggleButton({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isDark = ref.watch(isDarkModeProvider);

    return IconButton(
      icon: Icon(isDark ? Icons.light_mode : Icons.dark_mode),
      onPressed: () {
        ref.read(themeProvider.notifier).toggleTheme();
      },
      tooltip: isDark ? 'Switch to light mode' : 'Switch to dark mode',
    );
  }
}
