import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'app_colors.dart';
import 'app_typography.dart';
import 'theme_extensions.dart';

/// ZERGO QR App Theme System
/// 
/// Main theme configuration that combines colors, typography, and spacing
/// into cohesive light and dark ThemeData objects optimized for restaurant
/// management and diner-facing experiences.
class AppTheme {
  /// Private constructor to prevent instantiation
  AppTheme._();

  /// Light theme configuration
  static ThemeData get light => ThemeData(
    useMaterial3: true,
    colorScheme: AppColors.lightColorScheme,
    textTheme: AppTypography.lightTextTheme,
    
    // App Bar Theme
    appBarTheme: AppBarTheme(
      centerTitle: true,
      elevation: 0,
      surfaceTintColor: Colors.transparent,
      backgroundColor: AppColors.lightColorScheme.surface,
      foregroundColor: AppColors.lightColorScheme.onSurface,
      systemOverlayStyle: const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.dark,
        statusBarBrightness: Brightness.light,
      ),
    ),

    // Card Theme
    cardTheme: CardTheme(
      elevation: 1,
      shadowColor: AppColors.lightColorScheme.shadow.withOpacity(0.1),
      surfaceTintColor: AppColors.lightColorScheme.surfaceTint,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),

    // Elevated Button Theme
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        textStyle: AppTypography.lightTextTheme.labelLarge,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      ),
    ),

    // Outlined Button Theme
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        textStyle: AppTypography.lightTextTheme.labelLarge,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        side: BorderSide(
          color: AppColors.lightColorScheme.outline,
          width: 1,
        ),
      ),
    ),

    // Text Button Theme
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        textStyle: AppTypography.lightTextTheme.labelLarge,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),
    ),

    // Floating Action Button Theme
    floatingActionButtonTheme: FloatingActionButtonThemeData(
      elevation: 6,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
    ),

    // Bottom Navigation Bar Theme
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      type: BottomNavigationBarType.fixed,
      elevation: 8,
      backgroundColor: AppColors.lightColorScheme.surface,
      selectedItemColor: AppColors.lightColorScheme.primary,
      unselectedItemColor: AppColors.lightColorScheme.onSurfaceVariant,
      selectedLabelStyle: AppTypography.lightTextTheme.labelSmall,
      unselectedLabelStyle: AppTypography.lightTextTheme.labelSmall,
    ),

    // Navigation Rail Theme
    navigationRailTheme: NavigationRailThemeData(
      backgroundColor: AppColors.lightColorScheme.surface,
      selectedIconTheme: IconThemeData(
        color: AppColors.lightColorScheme.onSecondaryContainer,
      ),
      selectedLabelTextStyle: AppTypography.lightTextTheme.labelMedium?.copyWith(
        color: AppColors.lightColorScheme.onSurface,
      ),
      unselectedIconTheme: IconThemeData(
        color: AppColors.lightColorScheme.onSurfaceVariant,
      ),
      unselectedLabelTextStyle: AppTypography.lightTextTheme.labelMedium?.copyWith(
        color: AppColors.lightColorScheme.onSurfaceVariant,
      ),
    ),

    // Input Decoration Theme
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.lightColorScheme.surfaceVariant.withOpacity(0.4),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(
          color: AppColors.lightColorScheme.outline,
        ),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(
          color: AppColors.lightColorScheme.outline,
        ),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(
          color: AppColors.lightColorScheme.primary,
          width: 2,
        ),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(
          color: AppColors.lightColorScheme.error,
        ),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(
          color: AppColors.lightColorScheme.error,
          width: 2,
        ),
      ),
      labelStyle: AppTypography.lightTextTheme.bodyMedium,
      hintStyle: AppTypography.lightTextTheme.bodyMedium?.copyWith(
        color: AppColors.lightColorScheme.onSurfaceVariant,
      ),
    ),

    // Dialog Theme
    dialogTheme: DialogTheme(
      elevation: 6,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      titleTextStyle: AppTypography.lightTextTheme.headlineSmall,
      contentTextStyle: AppTypography.lightTextTheme.bodyMedium,
    ),

    // Snack Bar Theme
    snackBarTheme: SnackBarThemeData(
      backgroundColor: AppColors.lightColorScheme.inverseSurface,
      contentTextStyle: AppTypography.lightTextTheme.bodyMedium?.copyWith(
        color: AppColors.lightColorScheme.onInverseSurface,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      behavior: SnackBarBehavior.floating,
      actionTextColor: AppColors.lightColorScheme.inversePrimary,
    ),

    // Chip Theme
    chipTheme: ChipThemeData(
      backgroundColor: AppColors.lightColorScheme.surfaceVariant,
      selectedColor: AppColors.lightColorScheme.secondaryContainer,
      disabledColor: AppColors.lightColorScheme.surfaceVariant.withOpacity(0.38),
      side: BorderSide.none,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      labelStyle: AppTypography.lightTextTheme.labelMedium,
    ),

    // List Tile Theme
    listTileTheme: ListTileThemeData(
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      titleTextStyle: AppTypography.lightTextTheme.bodyLarge,
      subtitleTextStyle: AppTypography.lightTextTheme.bodyMedium?.copyWith(
        color: AppColors.lightColorScheme.onSurfaceVariant,
      ),
    ),

    // Drawer Theme
    drawerTheme: DrawerThemeData(
      backgroundColor: AppColors.lightColorScheme.surface,
      surfaceTintColor: AppColors.lightColorScheme.surfaceTint,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.only(
          topRight: Radius.circular(16),
          bottomRight: Radius.circular(16),
        ),
      ),
    ),

    // Extensions
    extensions: const [
      RestaurantColorsExtension.light,
      RestaurantSpacingExtension.standard,
    ],
  );

  /// Dark theme configuration
  static ThemeData get dark => ThemeData(
    useMaterial3: true,
    colorScheme: AppColors.darkColorScheme,
    textTheme: AppTypography.darkTextTheme,
    
    // App Bar Theme
    appBarTheme: AppBarTheme(
      centerTitle: true,
      elevation: 0,
      surfaceTintColor: Colors.transparent,
      backgroundColor: AppColors.darkColorScheme.surface,
      foregroundColor: AppColors.darkColorScheme.onSurface,
      systemOverlayStyle: const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
        statusBarBrightness: Brightness.dark,
      ),
    ),

    // Card Theme
    cardTheme: CardTheme(
      elevation: 1,
      shadowColor: AppColors.darkColorScheme.shadow.withOpacity(0.2),
      surfaceTintColor: AppColors.darkColorScheme.surfaceTint,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),

    // Elevated Button Theme
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        textStyle: AppTypography.darkTextTheme.labelLarge,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      ),
    ),

    // Outlined Button Theme
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        textStyle: AppTypography.darkTextTheme.labelLarge,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        side: BorderSide(
          color: AppColors.darkColorScheme.outline,
          width: 1,
        ),
      ),
    ),

    // Text Button Theme
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        textStyle: AppTypography.darkTextTheme.labelLarge,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),
    ),

    // Floating Action Button Theme
    floatingActionButtonTheme: FloatingActionButtonThemeData(
      elevation: 6,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
    ),

    // Bottom Navigation Bar Theme
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      type: BottomNavigationBarType.fixed,
      elevation: 8,
      backgroundColor: AppColors.darkColorScheme.surface,
      selectedItemColor: AppColors.darkColorScheme.primary,
      unselectedItemColor: AppColors.darkColorScheme.onSurfaceVariant,
      selectedLabelStyle: AppTypography.darkTextTheme.labelSmall,
      unselectedLabelStyle: AppTypography.darkTextTheme.labelSmall,
    ),

    // Navigation Rail Theme
    navigationRailTheme: NavigationRailThemeData(
      backgroundColor: AppColors.darkColorScheme.surface,
      selectedIconTheme: IconThemeData(
        color: AppColors.darkColorScheme.onSecondaryContainer,
      ),
      selectedLabelTextStyle: AppTypography.darkTextTheme.labelMedium?.copyWith(
        color: AppColors.darkColorScheme.onSurface,
      ),
      unselectedIconTheme: IconThemeData(
        color: AppColors.darkColorScheme.onSurfaceVariant,
      ),
      unselectedLabelTextStyle: AppTypography.darkTextTheme.labelMedium?.copyWith(
        color: AppColors.darkColorScheme.onSurfaceVariant,
      ),
    ),

    // Input Decoration Theme
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.darkColorScheme.surfaceVariant.withOpacity(0.4),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(
          color: AppColors.darkColorScheme.outline,
        ),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(
          color: AppColors.darkColorScheme.outline,
        ),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(
          color: AppColors.darkColorScheme.primary,
          width: 2,
        ),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(
          color: AppColors.darkColorScheme.error,
        ),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(
          color: AppColors.darkColorScheme.error,
          width: 2,
        ),
      ),
      labelStyle: AppTypography.darkTextTheme.bodyMedium,
      hintStyle: AppTypography.darkTextTheme.bodyMedium?.copyWith(
        color: AppColors.darkColorScheme.onSurfaceVariant,
      ),
    ),

    // Dialog Theme
    dialogTheme: DialogTheme(
      elevation: 6,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      titleTextStyle: AppTypography.darkTextTheme.headlineSmall,
      contentTextStyle: AppTypography.darkTextTheme.bodyMedium,
    ),

    // Snack Bar Theme
    snackBarTheme: SnackBarThemeData(
      backgroundColor: AppColors.darkColorScheme.inverseSurface,
      contentTextStyle: AppTypography.darkTextTheme.bodyMedium?.copyWith(
        color: AppColors.darkColorScheme.onInverseSurface,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      behavior: SnackBarBehavior.floating,
      actionTextColor: AppColors.darkColorScheme.inversePrimary,
    ),

    // Chip Theme
    chipTheme: ChipThemeData(
      backgroundColor: AppColors.darkColorScheme.surfaceVariant,
      selectedColor: AppColors.darkColorScheme.secondaryContainer,
      disabledColor: AppColors.darkColorScheme.surfaceVariant.withOpacity(0.38),
      side: BorderSide.none,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      labelStyle: AppTypography.darkTextTheme.labelMedium,
    ),

    // List Tile Theme
    listTileTheme: ListTileThemeData(
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      titleTextStyle: AppTypography.darkTextTheme.bodyLarge,
      subtitleTextStyle: AppTypography.darkTextTheme.bodyMedium?.copyWith(
        color: AppColors.darkColorScheme.onSurfaceVariant,
      ),
    ),

    // Drawer Theme
    drawerTheme: DrawerThemeData(
      backgroundColor: AppColors.darkColorScheme.surface,
      surfaceTintColor: AppColors.darkColorScheme.surfaceTint,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.only(
          topRight: Radius.circular(16),
          bottomRight: Radius.circular(16),
        ),
      ),
    ),

    // Extensions
    extensions: const [
      RestaurantColorsExtension.dark,
      RestaurantSpacingExtension.standard,
    ],
  );
}