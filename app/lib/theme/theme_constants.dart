/// Theme Constants for Fokha Project Template
///
/// This file contains all hardcoded fonts, colors, spacing, and theme values.
/// Import this file in all widgets to ensure consistent styling across the app.
///
/// Usage:
///   import 'package:app/theme/theme_constants.dart';
library;
///
///   Text('Hello', style: TextStyle(
///     fontFamily: AppTheme.fontFamily,
///     fontSize: AppTheme.fontSizeMd,
///     color: AppTheme.textPrimary,
///   ))

import 'package:flutter/material.dart';

/// Main theme constants class
class AppTheme {
  // ═══════════════════════════════════════════════════════════════════════════
  // TYPOGRAPHY - Hardcoded Fonts
  // ═══════════════════════════════════════════════════════════════════════════

  /// Primary font for body text and UI elements
  static const String fontFamily = 'Inter';

  /// Monospace font for code, numbers, and technical content
  static const String monoFontFamily = 'JetBrains Mono';

  /// Display font for headings and titles
  static const String displayFontFamily = 'Poppins';

  // ═══════════════════════════════════════════════════════════════════════════
  // FONT SIZES - Hardcoded Values
  // ═══════════════════════════════════════════════════════════════════════════

  /// Extra small text (10px) - Labels, captions
  static const double fontSizeXs = 10.0;

  /// Small text (12px) - Secondary labels
  static const double fontSizeSm = 12.0;

  /// Medium text (14px) - Body text
  static const double fontSizeMd = 14.0;

  /// Large text (16px) - Emphasized body
  static const double fontSizeLg = 16.0;

  /// Extra large text (20px) - Subheadings
  static const double fontSizeXl = 20.0;

  /// 2X large text (24px) - Headings
  static const double fontSize2xl = 24.0;

  /// 3X large text (32px) - Large headings
  static const double fontSize3xl = 32.0;

  /// 4X large text (40px) - Display text
  static const double fontSize4xl = 40.0;

  // ═══════════════════════════════════════════════════════════════════════════
  // FONT WEIGHTS
  // ═══════════════════════════════════════════════════════════════════════════

  static const FontWeight fontWeightLight = FontWeight.w300;
  static const FontWeight fontWeightRegular = FontWeight.w400;
  static const FontWeight fontWeightMedium = FontWeight.w500;
  static const FontWeight fontWeightSemiBold = FontWeight.w600;
  static const FontWeight fontWeightBold = FontWeight.w700;

  // ═══════════════════════════════════════════════════════════════════════════
  // LINE HEIGHTS
  // ═══════════════════════════════════════════════════════════════════════════

  static const double lineHeightTight = 1.2;
  static const double lineHeightNormal = 1.5;
  static const double lineHeightRelaxed = 1.75;

  // ═══════════════════════════════════════════════════════════════════════════
  // COLOR PALETTE - Primary Colors
  // ═══════════════════════════════════════════════════════════════════════════

  /// Primary brand color - Blue
  static const Color primary = Color(0xFF2196F3);
  static const Color primaryLight = Color(0xFF64B5F6);
  static const Color primaryDark = Color(0xFF1976D2);

  /// Secondary accent color - Orange
  static const Color secondary = Color(0xFFFF9800);
  static const Color secondaryLight = Color(0xFFFFB74D);
  static const Color secondaryDark = Color(0xFFF57C00);

  // ═══════════════════════════════════════════════════════════════════════════
  // COLOR PALETTE - Semantic Colors
  // ═══════════════════════════════════════════════════════════════════════════

  /// Success - Green (completed, positive)
  static const Color success = Color(0xFF4CAF50);
  static const Color successLight = Color(0xFF81C784);
  static const Color successDark = Color(0xFF388E3C);

  /// Warning - Amber (attention needed)
  static const Color warning = Color(0xFFFFC107);
  static const Color warningLight = Color(0xFFFFD54F);
  static const Color warningDark = Color(0xFFFFA000);

  /// Error - Red (errors, negative)
  static const Color error = Color(0xFFF44336);
  static const Color errorLight = Color(0xFFE57373);
  static const Color errorDark = Color(0xFFD32F2F);

  /// Info - Light blue (informational)
  static const Color info = Color(0xFF03A9F4);
  static const Color infoLight = Color(0xFF4FC3F7);
  static const Color infoDark = Color(0xFF0288D1);

  // ═══════════════════════════════════════════════════════════════════════════
  // COLOR PALETTE - Dark Theme Background Colors
  // ═══════════════════════════════════════════════════════════════════════════

  /// Dark theme backgrounds
  static const Color backgroundDark = Color(0xFF121212);
  static const Color surfaceDark = Color(0xFF1E1E1E);
  static const Color cardDark = Color(0xFF2D2D2D);
  static const Color dividerDark = Color(0xFF424242);

  // ═══════════════════════════════════════════════════════════════════════════
  // COLOR PALETTE - Light Theme Background Colors
  // ═══════════════════════════════════════════════════════════════════════════

  /// Light theme backgrounds
  static const Color backgroundLight = Color(0xFFFAFAFA);
  static const Color surfaceLight = Color(0xFFFFFFFF);
  static const Color cardLight = Color(0xFFFFFFFF);
  static const Color dividerLight = Color(0xFFE0E0E0);

  // ═══════════════════════════════════════════════════════════════════════════
  // COLOR PALETTE - Text Colors
  // ═══════════════════════════════════════════════════════════════════════════

  /// Dark theme text colors
  static const Color textPrimaryDark = Color(0xFFFFFFFF);
  static const Color textSecondaryDark = Color(0xFFB3B3B3);
  static const Color textDisabledDark = Color(0xFF666666);

  /// Light theme text colors
  static const Color textPrimaryLight = Color(0xFF212121);
  static const Color textSecondaryLight = Color(0xFF757575);
  static const Color textDisabledLight = Color(0xFFBDBDBD);

  // ═══════════════════════════════════════════════════════════════════════════
  // SPACING SYSTEM - Multiples of 4
  // ═══════════════════════════════════════════════════════════════════════════

  /// Extra extra small (2px)
  static const double spacing2xs = 2.0;

  /// Extra small (4px)
  static const double spacingXs = 4.0;

  /// Small (8px)
  static const double spacingSm = 8.0;

  /// Medium (16px)
  static const double spacingMd = 16.0;

  /// Large (24px)
  static const double spacingLg = 24.0;

  /// Extra large (32px)
  static const double spacingXl = 32.0;

  /// 2X large (48px)
  static const double spacing2xl = 48.0;

  /// 3X large (64px)
  static const double spacing3xl = 64.0;

  // ═══════════════════════════════════════════════════════════════════════════
  // BORDER RADIUS
  // ═══════════════════════════════════════════════════════════════════════════

  /// Small radius (4px) - Buttons, inputs
  static const double radiusSm = 4.0;

  /// Medium radius (8px) - Cards, containers
  static const double radiusMd = 8.0;

  /// Large radius (12px) - Modals, dialogs
  static const double radiusLg = 12.0;

  /// Extra large radius (16px) - Large cards
  static const double radiusXl = 16.0;

  /// Full radius for circular elements
  static const double radiusFull = 9999.0;

  // ═══════════════════════════════════════════════════════════════════════════
  // BORDER RADIUS - BorderRadius Objects
  // ═══════════════════════════════════════════════════════════════════════════

  static final BorderRadius borderRadiusSm = BorderRadius.circular(radiusSm);
  static final BorderRadius borderRadiusMd = BorderRadius.circular(radiusMd);
  static final BorderRadius borderRadiusLg = BorderRadius.circular(radiusLg);
  static final BorderRadius borderRadiusXl = BorderRadius.circular(radiusXl);

  // ═══════════════════════════════════════════════════════════════════════════
  // SHADOWS
  // ═══════════════════════════════════════════════════════════════════════════

  /// Light shadow for cards
  static final List<BoxShadow> shadowSm = [
    BoxShadow(
      color: Colors.black.withOpacity(0.05),
      blurRadius: 4,
      offset: const Offset(0, 2),
    ),
  ];

  /// Medium shadow for elevated elements
  static final List<BoxShadow> shadowMd = [
    BoxShadow(
      color: Colors.black.withOpacity(0.1),
      blurRadius: 8,
      offset: const Offset(0, 4),
    ),
  ];

  /// Large shadow for modals/dialogs
  static final List<BoxShadow> shadowLg = [
    BoxShadow(
      color: Colors.black.withOpacity(0.15),
      blurRadius: 16,
      offset: const Offset(0, 8),
    ),
  ];

  // ═══════════════════════════════════════════════════════════════════════════
  // BUTTON SIZES
  // ═══════════════════════════════════════════════════════════════════════════

  /// Small button height (32px)
  static const double buttonHeightSm = 32.0;

  /// Medium button height (40px)
  static const double buttonHeightMd = 40.0;

  /// Large button height (48px)
  static const double buttonHeightLg = 48.0;

  // ═══════════════════════════════════════════════════════════════════════════
  // ICON SIZES
  // ═══════════════════════════════════════════════════════════════════════════

  /// Small icon (16px)
  static const double iconSizeSm = 16.0;

  /// Medium icon (24px)
  static const double iconSizeMd = 24.0;

  /// Large icon (32px)
  static const double iconSizeLg = 32.0;

  /// Extra large icon (48px)
  static const double iconSizeXl = 48.0;

  // ═══════════════════════════════════════════════════════════════════════════
  // ANIMATION DURATIONS
  // ═══════════════════════════════════════════════════════════════════════════

  /// Fast animation (100ms)
  static const Duration durationFast = Duration(milliseconds: 100);

  /// Normal animation (200ms)
  static const Duration durationNormal = Duration(milliseconds: 200);

  /// Slow animation (300ms)
  static const Duration durationSlow = Duration(milliseconds: 300);

  // ═══════════════════════════════════════════════════════════════════════════
  // BREAKPOINTS
  // ═══════════════════════════════════════════════════════════════════════════

  /// Mobile breakpoint (600px)
  static const double breakpointMobile = 600.0;

  /// Tablet breakpoint (900px)
  static const double breakpointTablet = 900.0;

  /// Desktop breakpoint (1200px)
  static const double breakpointDesktop = 1200.0;

  // ═══════════════════════════════════════════════════════════════════════════
  // THEME DATA - Dark Theme
  // ═══════════════════════════════════════════════════════════════════════════

  static ThemeData get darkTheme => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    fontFamily: fontFamily,

    // Color scheme
    colorScheme: const ColorScheme.dark(
      primary: primary,
      secondary: secondary,
      surface: surfaceDark,
      error: error,
    ),

    // Scaffold
    scaffoldBackgroundColor: backgroundDark,

    // App bar
    appBarTheme: const AppBarTheme(
      backgroundColor: surfaceDark,
      foregroundColor: textPrimaryDark,
      elevation: 0,
      centerTitle: true,
      titleTextStyle: TextStyle(
        fontFamily: displayFontFamily,
        fontSize: fontSizeXl,
        fontWeight: fontWeightSemiBold,
        color: textPrimaryDark,
      ),
    ),

    // Cards
    cardTheme: CardThemeData(
      color: cardDark,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: borderRadiusMd,
      ),
    ),

    // Buttons
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primary,
        foregroundColor: Colors.white,
        minimumSize: const Size(0, buttonHeightMd),
        padding: const EdgeInsets.symmetric(
          horizontal: spacingMd,
          vertical: spacingSm,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: borderRadiusSm,
        ),
        textStyle: const TextStyle(
          fontFamily: fontFamily,
          fontSize: fontSizeMd,
          fontWeight: fontWeightMedium,
        ),
      ),
    ),

    // Text buttons
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: primary,
        textStyle: const TextStyle(
          fontFamily: fontFamily,
          fontSize: fontSizeMd,
          fontWeight: fontWeightMedium,
        ),
      ),
    ),

    // Input decoration
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: surfaceDark,
      contentPadding: const EdgeInsets.symmetric(
        horizontal: spacingMd,
        vertical: spacingSm,
      ),
      border: OutlineInputBorder(
        borderRadius: borderRadiusSm,
        borderSide: const BorderSide(color: dividerDark),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: borderRadiusSm,
        borderSide: const BorderSide(color: dividerDark),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: borderRadiusSm,
        borderSide: const BorderSide(color: primary, width: 2),
      ),
      labelStyle: const TextStyle(
        fontFamily: fontFamily,
        fontSize: fontSizeMd,
        color: textSecondaryDark,
      ),
      hintStyle: const TextStyle(
        fontFamily: fontFamily,
        fontSize: fontSizeMd,
        color: textDisabledDark,
      ),
    ),

    // Divider
    dividerTheme: const DividerThemeData(
      color: dividerDark,
      thickness: 1,
    ),

    // Text theme
    textTheme: const TextTheme(
      displayLarge: TextStyle(
        fontFamily: displayFontFamily,
        fontSize: fontSize4xl,
        fontWeight: fontWeightBold,
        color: textPrimaryDark,
      ),
      displayMedium: TextStyle(
        fontFamily: displayFontFamily,
        fontSize: fontSize3xl,
        fontWeight: fontWeightBold,
        color: textPrimaryDark,
      ),
      displaySmall: TextStyle(
        fontFamily: displayFontFamily,
        fontSize: fontSize2xl,
        fontWeight: fontWeightSemiBold,
        color: textPrimaryDark,
      ),
      headlineMedium: TextStyle(
        fontFamily: displayFontFamily,
        fontSize: fontSizeXl,
        fontWeight: fontWeightSemiBold,
        color: textPrimaryDark,
      ),
      titleLarge: TextStyle(
        fontFamily: fontFamily,
        fontSize: fontSizeLg,
        fontWeight: fontWeightMedium,
        color: textPrimaryDark,
      ),
      bodyLarge: TextStyle(
        fontFamily: fontFamily,
        fontSize: fontSizeMd,
        fontWeight: fontWeightRegular,
        color: textPrimaryDark,
      ),
      bodyMedium: TextStyle(
        fontFamily: fontFamily,
        fontSize: fontSizeSm,
        fontWeight: fontWeightRegular,
        color: textSecondaryDark,
      ),
      labelLarge: TextStyle(
        fontFamily: fontFamily,
        fontSize: fontSizeMd,
        fontWeight: fontWeightMedium,
        color: textPrimaryDark,
      ),
    ),
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // THEME DATA - Light Theme
  // ═══════════════════════════════════════════════════════════════════════════

  static ThemeData get lightTheme => ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    fontFamily: fontFamily,

    // Color scheme
    colorScheme: const ColorScheme.light(
      primary: primary,
      secondary: secondary,
      surface: surfaceLight,
      error: error,
    ),

    // Scaffold
    scaffoldBackgroundColor: backgroundLight,

    // App bar
    appBarTheme: const AppBarTheme(
      backgroundColor: surfaceLight,
      foregroundColor: textPrimaryLight,
      elevation: 0,
      centerTitle: true,
      titleTextStyle: TextStyle(
        fontFamily: displayFontFamily,
        fontSize: fontSizeXl,
        fontWeight: fontWeightSemiBold,
        color: textPrimaryLight,
      ),
    ),

    // Cards
    cardTheme: CardThemeData(
      color: cardLight,
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: borderRadiusMd,
      ),
    ),

    // Buttons
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primary,
        foregroundColor: Colors.white,
        minimumSize: const Size(0, buttonHeightMd),
        padding: const EdgeInsets.symmetric(
          horizontal: spacingMd,
          vertical: spacingSm,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: borderRadiusSm,
        ),
        textStyle: const TextStyle(
          fontFamily: fontFamily,
          fontSize: fontSizeMd,
          fontWeight: fontWeightMedium,
        ),
      ),
    ),

    // Text buttons
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: primary,
        textStyle: const TextStyle(
          fontFamily: fontFamily,
          fontSize: fontSizeMd,
          fontWeight: fontWeightMedium,
        ),
      ),
    ),

    // Input decoration
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: surfaceLight,
      contentPadding: const EdgeInsets.symmetric(
        horizontal: spacingMd,
        vertical: spacingSm,
      ),
      border: OutlineInputBorder(
        borderRadius: borderRadiusSm,
        borderSide: const BorderSide(color: dividerLight),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: borderRadiusSm,
        borderSide: const BorderSide(color: dividerLight),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: borderRadiusSm,
        borderSide: const BorderSide(color: primary, width: 2),
      ),
      labelStyle: const TextStyle(
        fontFamily: fontFamily,
        fontSize: fontSizeMd,
        color: textSecondaryLight,
      ),
      hintStyle: const TextStyle(
        fontFamily: fontFamily,
        fontSize: fontSizeMd,
        color: textDisabledLight,
      ),
    ),

    // Divider
    dividerTheme: const DividerThemeData(
      color: dividerLight,
      thickness: 1,
    ),

    // Text theme
    textTheme: const TextTheme(
      displayLarge: TextStyle(
        fontFamily: displayFontFamily,
        fontSize: fontSize4xl,
        fontWeight: fontWeightBold,
        color: textPrimaryLight,
      ),
      displayMedium: TextStyle(
        fontFamily: displayFontFamily,
        fontSize: fontSize3xl,
        fontWeight: fontWeightBold,
        color: textPrimaryLight,
      ),
      displaySmall: TextStyle(
        fontFamily: displayFontFamily,
        fontSize: fontSize2xl,
        fontWeight: fontWeightSemiBold,
        color: textPrimaryLight,
      ),
      headlineMedium: TextStyle(
        fontFamily: displayFontFamily,
        fontSize: fontSizeXl,
        fontWeight: fontWeightSemiBold,
        color: textPrimaryLight,
      ),
      titleLarge: TextStyle(
        fontFamily: fontFamily,
        fontSize: fontSizeLg,
        fontWeight: fontWeightMedium,
        color: textPrimaryLight,
      ),
      bodyLarge: TextStyle(
        fontFamily: fontFamily,
        fontSize: fontSizeMd,
        fontWeight: fontWeightRegular,
        color: textPrimaryLight,
      ),
      bodyMedium: TextStyle(
        fontFamily: fontFamily,
        fontSize: fontSizeSm,
        fontWeight: fontWeightRegular,
        color: textSecondaryLight,
      ),
      labelLarge: TextStyle(
        fontFamily: fontFamily,
        fontSize: fontSizeMd,
        fontWeight: fontWeightMedium,
        color: textPrimaryLight,
      ),
    ),
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXTENSION METHODS
// ═══════════════════════════════════════════════════════════════════════════════

/// Extension for easier access to theme colors based on brightness
extension ThemeColorExtension on BuildContext {
  /// Get text primary color based on current theme
  Color get textPrimary => Theme.of(this).brightness == Brightness.dark
      ? AppTheme.textPrimaryDark
      : AppTheme.textPrimaryLight;

  /// Get text secondary color based on current theme
  Color get textSecondary => Theme.of(this).brightness == Brightness.dark
      ? AppTheme.textSecondaryDark
      : AppTheme.textSecondaryLight;

  /// Get background color based on current theme
  Color get background => Theme.of(this).brightness == Brightness.dark
      ? AppTheme.backgroundDark
      : AppTheme.backgroundLight;

  /// Get surface color based on current theme
  Color get surface => Theme.of(this).brightness == Brightness.dark
      ? AppTheme.surfaceDark
      : AppTheme.surfaceLight;

  /// Get card color based on current theme
  Color get cardColor => Theme.of(this).brightness == Brightness.dark
      ? AppTheme.cardDark
      : AppTheme.cardLight;

  /// Get divider color based on current theme
  Color get dividerColor => Theme.of(this).brightness == Brightness.dark
      ? AppTheme.dividerDark
      : AppTheme.dividerLight;

  /// Check if dark mode
  bool get isDarkMode => Theme.of(this).brightness == Brightness.dark;
}

// ═══════════════════════════════════════════════════════════════════════════════
// TRADING-SPECIFIC COLORS (Optional for Trading Apps)
// ═══════════════════════════════════════════════════════════════════════════════

/// Trading-specific color extensions
class TradingColors {
  /// Buy/Long color - Green
  static const Color buy = Color(0xFF4CAF50);

  /// Sell/Short color - Red
  static const Color sell = Color(0xFFF44336);

  /// Neutral color - Gray
  static const Color neutral = Color(0xFF9E9E9E);

  /// Profit color - Green
  static const Color profit = Color(0xFF4CAF50);

  /// Loss color - Red
  static const Color loss = Color(0xFFF44336);

  /// Bullish candle - Green
  static const Color bullish = Color(0xFF26A69A);

  /// Bearish candle - Red
  static const Color bearish = Color(0xFFEF5350);

  /// Strong signal - Blue
  static const Color strongSignal = Color(0xFF2196F3);

  /// Weak signal - Orange
  static const Color weakSignal = Color(0xFFFF9800);
}
