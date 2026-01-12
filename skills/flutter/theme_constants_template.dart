// ignore_for_file: prefer_const_constructors

// ═══════════════════════════════════════════════════════════════
// THEME CONSTANTS TEMPLATE
// Centralized design system for Flutter apps
// ═══════════════════════════════════════════════════════════════
//
// Usage:
// 1. Copy to your project's lib/constants/ directory
// 2. Customize colors, fonts, spacing as needed
// 3. Use throughout your app for consistent styling
//
// ═══════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';

// ═══════════════════════════════════════════════════════════════
// COLOR PALETTE
// ═══════════════════════════════════════════════════════════════

class AppColors {
  // Prevent instantiation
  AppColors._();

  // Primary colors
  static const Color primary = Color(0xFF2196F3);
  static const Color primaryLight = Color(0xFF64B5F6);
  static const Color primaryDark = Color(0xFF1976D2);

  // Secondary colors
  static const Color secondary = Color(0xFF03DAC6);
  static const Color secondaryLight = Color(0xFF67EFDC);
  static const Color secondaryDark = Color(0xFF00A895);

  // Semantic colors
  static const Color success = Color(0xFF4CAF50);
  static const Color successLight = Color(0xFFE8F5E9);
  static const Color warning = Color(0xFFFF9800);
  static const Color warningLight = Color(0xFFFFF3E0);
  static const Color error = Color(0xFFF44336);
  static const Color errorLight = Color(0xFFFFEBEE);
  static const Color info = Color(0xFF2196F3);
  static const Color infoLight = Color(0xFFE3F2FD);

  // Trading colors
  static const Color buyGreen = Color(0xFF00C853);
  static const Color sellRed = Color(0xFFFF1744);
  static const Color profit = Color(0xFF4CAF50);
  static const Color loss = Color(0xFFF44336);
  static const Color neutral = Color(0xFF9E9E9E);

  // Background colors
  static const Color backgroundLight = Color(0xFFF5F5F5);
  static const Color backgroundDark = Color(0xFF121212);
  static const Color surfaceLight = Color(0xFFFFFFFF);
  static const Color surfaceDark = Color(0xFF1E1E1E);

  // Text colors
  static const Color textPrimaryLight = Color(0xFF212121);
  static const Color textSecondaryLight = Color(0xFF757575);
  static const Color textPrimaryDark = Color(0xFFFFFFFF);
  static const Color textSecondaryDark = Color(0xFFB0B0B0);

  // Border colors
  static const Color borderLight = Color(0xFFE0E0E0);
  static const Color borderDark = Color(0xFF424242);

  // Gradient presets
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primary, primaryDark],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient successGradient = LinearGradient(
    colors: [success, Color(0xFF2E7D32)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}

// ═══════════════════════════════════════════════════════════════
// TYPOGRAPHY
// ═══════════════════════════════════════════════════════════════

class AppTypography {
  AppTypography._();

  // Font families
  static const String fontFamily = 'Roboto';
  static const String monoFontFamily = 'RobotoMono';

  // Display styles
  static const TextStyle displayLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 57,
    fontWeight: FontWeight.w400,
    letterSpacing: -0.25,
  );

  static const TextStyle displayMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 45,
    fontWeight: FontWeight.w400,
  );

  static const TextStyle displaySmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 36,
    fontWeight: FontWeight.w400,
  );

  // Headline styles
  static const TextStyle headlineLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 32,
    fontWeight: FontWeight.w600,
  );

  static const TextStyle headlineMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 28,
    fontWeight: FontWeight.w500,
  );

  static const TextStyle headlineSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 24,
    fontWeight: FontWeight.w500,
  );

  // Title styles
  static const TextStyle titleLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 22,
    fontWeight: FontWeight.w500,
  );

  static const TextStyle titleMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.15,
  );

  static const TextStyle titleSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.1,
  );

  // Body styles
  static const TextStyle bodyLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.5,
  );

  static const TextStyle bodyMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.25,
  );

  static const TextStyle bodySmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.4,
  );

  // Label styles
  static const TextStyle labelLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.1,
  );

  static const TextStyle labelMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.5,
  );

  static const TextStyle labelSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 11,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.5,
  );

  // Monospace (for code, numbers)
  static const TextStyle code = TextStyle(
    fontFamily: monoFontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w400,
  );

  static const TextStyle number = TextStyle(
    fontFamily: monoFontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w500,
  );
}

// ═══════════════════════════════════════════════════════════════
// SPACING
// ═══════════════════════════════════════════════════════════════

class AppSpacing {
  AppSpacing._();

  // Base unit (4dp)
  static const double unit = 4.0;

  // Named spacings
  static const double xxs = 2.0;
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 16.0;
  static const double lg = 24.0;
  static const double xl = 32.0;
  static const double xxl = 48.0;
  static const double xxxl = 64.0;

  // Common padding
  static const EdgeInsets paddingXs = EdgeInsets.all(xs);
  static const EdgeInsets paddingSm = EdgeInsets.all(sm);
  static const EdgeInsets paddingMd = EdgeInsets.all(md);
  static const EdgeInsets paddingLg = EdgeInsets.all(lg);

  // Horizontal padding
  static const EdgeInsets paddingHorizontalSm = EdgeInsets.symmetric(horizontal: sm);
  static const EdgeInsets paddingHorizontalMd = EdgeInsets.symmetric(horizontal: md);
  static const EdgeInsets paddingHorizontalLg = EdgeInsets.symmetric(horizontal: lg);

  // Vertical padding
  static const EdgeInsets paddingVerticalSm = EdgeInsets.symmetric(vertical: sm);
  static const EdgeInsets paddingVerticalMd = EdgeInsets.symmetric(vertical: md);
  static const EdgeInsets paddingVerticalLg = EdgeInsets.symmetric(vertical: lg);

  // Screen padding
  static const EdgeInsets screenPadding = EdgeInsets.all(md);
  static const EdgeInsets screenPaddingHorizontal = EdgeInsets.symmetric(horizontal: md);
}

// ═══════════════════════════════════════════════════════════════
// BORDER RADIUS
// ═══════════════════════════════════════════════════════════════

class AppRadius {
  AppRadius._();

  // Named radii
  static const double none = 0.0;
  static const double xs = 2.0;
  static const double sm = 4.0;
  static const double md = 8.0;
  static const double lg = 12.0;
  static const double xl = 16.0;
  static const double xxl = 24.0;
  static const double full = 999.0;

  // BorderRadius shortcuts
  static const BorderRadius radiusNone = BorderRadius.zero;
  static const BorderRadius radiusSm = BorderRadius.all(Radius.circular(sm));
  static const BorderRadius radiusMd = BorderRadius.all(Radius.circular(md));
  static const BorderRadius radiusLg = BorderRadius.all(Radius.circular(lg));
  static const BorderRadius radiusXl = BorderRadius.all(Radius.circular(xl));
  static const BorderRadius radiusFull = BorderRadius.all(Radius.circular(full));

  // Top only
  static const BorderRadius radiusTopMd = BorderRadius.vertical(top: Radius.circular(md));
  static const BorderRadius radiusTopLg = BorderRadius.vertical(top: Radius.circular(lg));

  // Bottom only
  static const BorderRadius radiusBottomMd = BorderRadius.vertical(bottom: Radius.circular(md));
  static const BorderRadius radiusBottomLg = BorderRadius.vertical(bottom: Radius.circular(lg));
}

// ═══════════════════════════════════════════════════════════════
// SHADOWS
// ═══════════════════════════════════════════════════════════════

class AppShadows {
  AppShadows._();

  static List<BoxShadow> get none => [];

  static List<BoxShadow> get sm => [
    BoxShadow(
      color: Colors.black.withOpacity(0.05),
      blurRadius: 2,
      offset: const Offset(0, 1),
    ),
  ];

  static List<BoxShadow> get md => [
    BoxShadow(
      color: Colors.black.withOpacity(0.1),
      blurRadius: 4,
      offset: const Offset(0, 2),
    ),
  ];

  static List<BoxShadow> get lg => [
    BoxShadow(
      color: Colors.black.withOpacity(0.1),
      blurRadius: 8,
      offset: const Offset(0, 4),
    ),
  ];

  static List<BoxShadow> get xl => [
    BoxShadow(
      color: Colors.black.withOpacity(0.15),
      blurRadius: 16,
      offset: const Offset(0, 8),
    ),
  ];
}

// ═══════════════════════════════════════════════════════════════
// ANIMATIONS
// ═══════════════════════════════════════════════════════════════

class AppAnimations {
  AppAnimations._();

  // Durations
  static const Duration fast = Duration(milliseconds: 150);
  static const Duration normal = Duration(milliseconds: 300);
  static const Duration slow = Duration(milliseconds: 500);

  // Curves
  static const Curve defaultCurve = Curves.easeInOut;
  static const Curve bounceCurve = Curves.bounceOut;
  static const Curve sharpCurve = Curves.easeOutCubic;
}

// ═══════════════════════════════════════════════════════════════
// THEME DATA BUILDERS
// ═══════════════════════════════════════════════════════════════

class AppTheme {
  AppTheme._();

  static ThemeData get light {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: ColorScheme.light(
        primary: AppColors.primary,
        secondary: AppColors.secondary,
        error: AppColors.error,
        surface: AppColors.surfaceLight,
      ),
      scaffoldBackgroundColor: AppColors.backgroundLight,
      cardTheme: CardThemeData(
        color: AppColors.surfaceLight,
        elevation: 1,
        shape: RoundedRectangleBorder(
          borderRadius: AppRadius.radiusMd,
        ),
      ),
      appBarTheme: const AppBarTheme(
        elevation: 0,
        centerTitle: true,
        backgroundColor: AppColors.surfaceLight,
        foregroundColor: AppColors.textPrimaryLight,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: AppRadius.radiusMd,
          ),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.backgroundLight,
        border: OutlineInputBorder(
          borderRadius: AppRadius.radiusMd,
          borderSide: const BorderSide(color: AppColors.borderLight),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: AppRadius.radiusMd,
          borderSide: const BorderSide(color: AppColors.borderLight),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: AppRadius.radiusMd,
          borderSide: const BorderSide(color: AppColors.primary, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      ),
      dividerTheme: const DividerThemeData(
        color: AppColors.borderLight,
        thickness: 1,
      ),
      textTheme: const TextTheme(
        displayLarge: AppTypography.displayLarge,
        displayMedium: AppTypography.displayMedium,
        displaySmall: AppTypography.displaySmall,
        headlineLarge: AppTypography.headlineLarge,
        headlineMedium: AppTypography.headlineMedium,
        headlineSmall: AppTypography.headlineSmall,
        titleLarge: AppTypography.titleLarge,
        titleMedium: AppTypography.titleMedium,
        titleSmall: AppTypography.titleSmall,
        bodyLarge: AppTypography.bodyLarge,
        bodyMedium: AppTypography.bodyMedium,
        bodySmall: AppTypography.bodySmall,
        labelLarge: AppTypography.labelLarge,
        labelMedium: AppTypography.labelMedium,
        labelSmall: AppTypography.labelSmall,
      ),
    );
  }

  static ThemeData get dark {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: ColorScheme.dark(
        primary: AppColors.primaryLight,
        secondary: AppColors.secondaryLight,
        error: AppColors.error,
        surface: AppColors.surfaceDark,
      ),
      scaffoldBackgroundColor: AppColors.backgroundDark,
      cardTheme: CardThemeData(
        color: AppColors.surfaceDark,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: AppRadius.radiusMd,
        ),
      ),
      appBarTheme: const AppBarTheme(
        elevation: 0,
        centerTitle: true,
        backgroundColor: AppColors.surfaceDark,
        foregroundColor: AppColors.textPrimaryDark,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: AppRadius.radiusMd,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.surfaceDark,
        border: OutlineInputBorder(
          borderRadius: AppRadius.radiusMd,
          borderSide: const BorderSide(color: AppColors.borderDark),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: AppRadius.radiusMd,
          borderSide: const BorderSide(color: AppColors.borderDark),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: AppRadius.radiusMd,
          borderSide: const BorderSide(color: AppColors.primaryLight, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      ),
      dividerTheme: const DividerThemeData(
        color: AppColors.borderDark,
        thickness: 1,
      ),
      textTheme: TextTheme(
        displayLarge: AppTypography.displayLarge.copyWith(color: AppColors.textPrimaryDark),
        displayMedium: AppTypography.displayMedium.copyWith(color: AppColors.textPrimaryDark),
        displaySmall: AppTypography.displaySmall.copyWith(color: AppColors.textPrimaryDark),
        headlineLarge: AppTypography.headlineLarge.copyWith(color: AppColors.textPrimaryDark),
        headlineMedium: AppTypography.headlineMedium.copyWith(color: AppColors.textPrimaryDark),
        headlineSmall: AppTypography.headlineSmall.copyWith(color: AppColors.textPrimaryDark),
        titleLarge: AppTypography.titleLarge.copyWith(color: AppColors.textPrimaryDark),
        titleMedium: AppTypography.titleMedium.copyWith(color: AppColors.textPrimaryDark),
        titleSmall: AppTypography.titleSmall.copyWith(color: AppColors.textPrimaryDark),
        bodyLarge: AppTypography.bodyLarge.copyWith(color: AppColors.textPrimaryDark),
        bodyMedium: AppTypography.bodyMedium.copyWith(color: AppColors.textPrimaryDark),
        bodySmall: AppTypography.bodySmall.copyWith(color: AppColors.textSecondaryDark),
        labelLarge: AppTypography.labelLarge.copyWith(color: AppColors.textPrimaryDark),
        labelMedium: AppTypography.labelMedium.copyWith(color: AppColors.textSecondaryDark),
        labelSmall: AppTypography.labelSmall.copyWith(color: AppColors.textSecondaryDark),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════
// USAGE EXAMPLE
// ═══════════════════════════════════════════════════════════════

/*
// In main.dart
void main() {
  runApp(
    MaterialApp(
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: ThemeMode.system,
      home: MyHomePage(),
    ),
  );
}

// In widgets
Container(
  padding: AppSpacing.paddingMd,
  decoration: BoxDecoration(
    color: AppColors.surfaceLight,
    borderRadius: AppRadius.radiusLg,
    boxShadow: AppShadows.md,
  ),
  child: Text(
    'Hello World',
    style: AppTypography.titleLarge,
  ),
);

// Trading colors
Text(
  '+\$150.00',
  style: AppTypography.number.copyWith(
    color: AppColors.profit,
  ),
);

// Animated container
AnimatedContainer(
  duration: AppAnimations.normal,
  curve: AppAnimations.defaultCurve,
  padding: AppSpacing.paddingMd,
  decoration: BoxDecoration(
    color: isSelected ? AppColors.primaryLight : AppColors.surfaceLight,
    borderRadius: AppRadius.radiusMd,
  ),
  child: child,
);
*/
