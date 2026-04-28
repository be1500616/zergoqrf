import 'package:flutter/material.dart';

/// ZERGO QR Color System following Material Design 3
///
/// Provides comprehensive color schemes for both light and dark themes
/// optimized for restaurant management and diner-facing experiences.
class AppColors {
  /// Light theme color scheme
  static const lightColorScheme = ColorScheme(
    brightness: Brightness.light,

    // Primary colors - Main brand color for restaurant management
    primary: Color(0xFF2E7D32),
    onPrimary: Color(0xFFFFFFFF),
    primaryContainer: Color(0xFFB8F5BC),
    onPrimaryContainer: Color(0xFF00210A),

    // Secondary colors - Accent for actions and highlights
    secondary: Color(0xFFFF6F00),
    onSecondary: Color(0xFFFFFFFF),
    secondaryContainer: Color(0xFFFFCC9A),
    onSecondaryContainer: Color(0xFF2B1700),

    // Tertiary colors - Supporting elements
    tertiary: Color(0xFF795548),
    onTertiary: Color(0xFFFFFFFF),
    tertiaryContainer: Color(0xFFFFDBC9),
    onTertiaryContainer: Color(0xFF2B160A),

    // Error colors - Alerts and validation
    error: Color(0xFFD32F2F),
    onError: Color(0xFFFFFFFF),
    errorContainer: Color(0xFFFFDAD6),
    onErrorContainer: Color(0xFF410002),
    surface: Color(0xFFFCFDF6),
    onSurface: Color(0xFF1A1C18),
    surfaceContainerHighest: Color(0xFFDDE5DA),
    onSurfaceVariant: Color(0xFF424940),

    // Outline and shadows
    outline: Color(0xFF727970),
    outlineVariant: Color(0xFFC1C9BE),
    shadow: Color(0xFF000000),
    scrim: Color(0xFF000000),

    // Inverse colors for contrast
    inverseSurface: Color(0xFF2F312D),
    onInverseSurface: Color(0xFFF0F1EB),
    inversePrimary: Color(0xFF9DD9A1),

    // Surface tints
    surfaceTint: Color(0xFF2E7D32),
  );

  /// Dark theme color scheme
  static const darkColorScheme = ColorScheme(
    brightness: Brightness.dark,

    // Primary colors - Adapted for dark theme
    primary: Color(0xFF9DD9A1),
    onPrimary: Color(0xFF003910),
    primaryContainer: Color(0xFF165B1C),
    onPrimaryContainer: Color(0xFFB8F5BC),

    // Secondary colors - Warmer tones for dark theme
    secondary: Color(0xFFFFB86C),
    onSecondary: Color(0xFF472A00),
    secondaryContainer: Color(0xFF653F00),
    onSecondaryContainer: Color(0xFFFFCC9A),

    // Tertiary colors - Adjusted for visibility
    tertiary: Color(0xFFE7BFA9),
    onTertiary: Color(0xFF42291E),
    tertiaryContainer: Color(0xFF5A3F33),
    onTertiaryContainer: Color(0xFFFFDBC9),

    // Error colors - Softer for dark theme
    error: Color(0xFFFFB4AB),
    onError: Color(0xFF690005),
    errorContainer: Color(0xFF93000A),
    onErrorContainer: Color(0xFFFFDAD6),
    surface: Color(0xFF111210),
    onSurface: Color(0xFFE2E3DD),
    surfaceContainerHighest: Color(0xFF424940),
    onSurfaceVariant: Color(0xFFC1C9BE),

    // Outline and shadows
    outline: Color(0xFF8B938A),
    outlineVariant: Color(0xFF424940),
    shadow: Color(0xFF000000),
    scrim: Color(0xFF000000),

    // Inverse colors
    inverseSurface: Color(0xFFE2E3DD),
    onInverseSurface: Color(0xFF2F312D),
    inversePrimary: Color(0xFF2E7D32),

    // Surface tints
    surfaceTint: Color(0xFF9DD9A1),
  );

  /// Primary brand color for non-theme-aware contexts
  ///
  /// Note: For theme-aware widgets, prefer using Theme.of(context).colorScheme.primary
  /// This static property is provided for backward compatibility and contexts where
  /// BuildContext is not available.
  static const primary = Color(0xFF2E7D32);

  /// Custom semantic colors for restaurant-specific needs
  static const success = Color(0xFF4CAF50);
  static const warning = Color(0xFFFF9800);
  static const info = Color(0xFF2196F3);
  static const error = Color(0xFFD32F2F);

  /// Order status colors
  static const orderPending = Color(0xFFFF9800);
  static const orderConfirmed = Color(0xFF2196F3);
  static const orderPreparing = Color(0xFFFF6F00);
  static const orderReady = Color(0xFF4CAF50);
  static const orderCompleted = Color(0xFF9E9E9E);
  static const orderCancelled = Color(0xFFD32F2F);

  /// Table status colors
  static const tableAvailable = Color(0xFF4CAF50);
  static const tableOccupied = Color(0xFFFF9800);
  static const tableReserved = Color(0xFF2196F3);
  static const tableCleaning = Color(0xFF9E9E9E);

  /// QR code and branding colors
  static const qrCodeBackground = Color(0xFFFFFFFF);
  static const qrCodeForeground = Color(0xFF000000);
  static const brandGradientStart = Color(0xFF2E7D32);
  static const brandGradientEnd = Color(0xFF4CAF50);
}
