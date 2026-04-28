import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// ZERGO QR Typography System following Material Design 3
///
/// Provides comprehensive text styles optimized for restaurant management
/// interfaces and diner-facing PWA screens with excellent readability
/// across different screen sizes and contexts.
class AppTypography {
  /// Base font family - using Google Fonts for professional typography
  static String get _fontFamily => GoogleFonts.inter().fontFamily!;
  static String get _displayFontFamily => GoogleFonts.poppins().fontFamily!;

  /// Light theme text theme
  static TextTheme get lightTextTheme => TextTheme(
        // Display styles - Used for hero text and marketing content
        displayLarge: TextStyle(
          fontFamily: _displayFontFamily,
          fontSize: 57.0,
          fontWeight: FontWeight.w400,
          height: 1.12, // 64px line height
          letterSpacing: -0.25,
        ),
        displayMedium: TextStyle(
          fontFamily: _displayFontFamily,
          fontSize: 45.0,
          fontWeight: FontWeight.w400,
          height: 1.16, // 52px line height
          letterSpacing: 0.0,
        ),
        displaySmall: TextStyle(
          fontFamily: _displayFontFamily,
          fontSize: 36.0,
          fontWeight: FontWeight.w400,
          height: 1.22, // 44px line height
          letterSpacing: 0.0,
        ),

        // Headline styles - Used for page titles and section headers
        headlineLarge: TextStyle(
          fontFamily: _fontFamily,
          fontSize: 32.0,
          fontWeight: FontWeight.w400,
          height: 1.25, // 40px line height
          letterSpacing: 0.0,
        ),
        headlineMedium: TextStyle(
          fontFamily: _fontFamily,
          fontSize: 28.0,
          fontWeight: FontWeight.w400,
          height: 1.29, // 36px line height
          letterSpacing: 0.0,
        ),
        headlineSmall: TextStyle(
          fontFamily: _fontFamily,
          fontSize: 24.0,
          fontWeight: FontWeight.w400,
          height: 1.33, // 32px line height
          letterSpacing: 0.0,
        ),

        // Title styles - Used for component titles and important UI text
        titleLarge: TextStyle(
          fontFamily: _fontFamily,
          fontSize: 22.0,
          fontWeight: FontWeight.w500,
          height: 1.27, // 28px line height
          letterSpacing: 0.0,
        ),
        titleMedium: TextStyle(
          fontFamily: _fontFamily,
          fontSize: 16.0,
          fontWeight: FontWeight.w500,
          height: 1.50, // 24px line height
          letterSpacing: 0.15,
        ),
        titleSmall: TextStyle(
          fontFamily: _fontFamily,
          fontSize: 14.0,
          fontWeight: FontWeight.w500,
          height: 1.43, // 20px line height
          letterSpacing: 0.1,
        ),

        // Body styles - Used for main content and descriptions
        bodyLarge: TextStyle(
          fontFamily: _fontFamily,
          fontSize: 16.0,
          fontWeight: FontWeight.w400,
          height: 1.50, // 24px line height
          letterSpacing: 0.5,
        ),
        bodyMedium: TextStyle(
          fontFamily: _fontFamily,
          fontSize: 14.0,
          fontWeight: FontWeight.w400,
          height: 1.43, // 20px line height
          letterSpacing: 0.25,
        ),
        bodySmall: TextStyle(
          fontFamily: _fontFamily,
          fontSize: 12.0,
          fontWeight: FontWeight.w400,
          height: 1.33, // 16px line height
          letterSpacing: 0.4,
        ),

        // Label styles - Used for buttons, tabs, and form labels
        labelLarge: TextStyle(
          fontFamily: _fontFamily,
          fontSize: 14.0,
          fontWeight: FontWeight.w500,
          height: 1.43, // 20px line height
          letterSpacing: 0.1,
        ),
        labelMedium: TextStyle(
          fontFamily: _fontFamily,
          fontSize: 12.0,
          fontWeight: FontWeight.w500,
          height: 1.33, // 16px line height
          letterSpacing: 0.5,
        ),
        labelSmall: TextStyle(
          fontFamily: _fontFamily,
          fontSize: 11.0,
          fontWeight: FontWeight.w500,
          height: 1.45, // 16px line height
          letterSpacing: 0.5,
        ),
      );

  /// Dark theme text theme - inherits from light with appropriate color adjustments
  static TextTheme get darkTextTheme => lightTextTheme;
}

/// Custom text styles for restaurant-specific use cases
class RestaurantTextStyles {
  static String get _fontFamily => GoogleFonts.inter().fontFamily!;
  static String get _displayFontFamily => GoogleFonts.poppins().fontFamily!;

  /// Menu item name styling
  static TextStyle get menuItemName => TextStyle(
        fontFamily: _fontFamily,
        fontSize: 18.0,
        fontWeight: FontWeight.w500,
        height: 1.33,
        letterSpacing: 0.15,
      );

  /// Menu item description styling
  static TextStyle get menuItemDescription => TextStyle(
        fontFamily: _fontFamily,
        fontSize: 14.0,
        fontWeight: FontWeight.w400,
        height: 1.43,
        letterSpacing: 0.25,
      );

  /// Price display styling
  static TextStyle get price => TextStyle(
        fontFamily: _fontFamily,
        fontSize: 16.0,
        fontWeight: FontWeight.w600,
        height: 1.25,
        letterSpacing: 0.1,
      );

  /// Large price display (featured items)
  static TextStyle get priceEmphasized => TextStyle(
        fontFamily: _fontFamily,
        fontSize: 20.0,
        fontWeight: FontWeight.w700,
        height: 1.20,
        letterSpacing: 0.0,
      );

  /// Order number display
  static TextStyle get orderNumber => TextStyle(
        fontFamily: _fontFamily,
        fontSize: 24.0,
        fontWeight: FontWeight.w700,
        height: 1.17,
        letterSpacing: 0.0,
      );

  /// Table number display
  static TextStyle get tableNumber => TextStyle(
        fontFamily: _fontFamily,
        fontSize: 32.0,
        fontWeight: FontWeight.w600,
        height: 1.13,
        letterSpacing: -0.5,
      );

  /// Status text styling
  static TextStyle get status => TextStyle(
        fontFamily: _fontFamily,
        fontSize: 12.0,
        fontWeight: FontWeight.w600,
        height: 1.33,
        letterSpacing: 0.5,
      );

  /// Timestamp styling
  static TextStyle get timestamp => TextStyle(
        fontFamily: _fontFamily,
        fontSize: 12.0,
        fontWeight: FontWeight.w400,
        height: 1.33,
        letterSpacing: 0.4,
      );

  /// Navigation labels for management interface
  static TextStyle get navigationLabel => TextStyle(
        fontFamily: _fontFamily,
        fontSize: 14.0,
        fontWeight: FontWeight.w500,
        height: 1.43,
        letterSpacing: 0.1,
      );

  /// QR code instruction text
  static TextStyle get qrInstruction => TextStyle(
        fontFamily: _fontFamily,
        fontSize: 16.0,
        fontWeight: FontWeight.w400,
        height: 1.50,
        letterSpacing: 0.5,
      );

  /// Restaurant name display
  static TextStyle get restaurantName => TextStyle(
        fontFamily: _displayFontFamily,
        fontSize: 28.0,
        fontWeight: FontWeight.w600,
        height: 1.14,
        letterSpacing: -0.5,
      );

  /// Category header styling
  static TextStyle get categoryHeader => TextStyle(
        fontFamily: _fontFamily,
        fontSize: 20.0,
        fontWeight: FontWeight.w600,
        height: 1.40,
        letterSpacing: 0.15,
      );
}

/// Text theme extensions for special use cases
extension AppTextThemeExtensions on TextTheme {
  /// Get menu item name style
  TextStyle get menuItemName => RestaurantTextStyles.menuItemName;

  /// Get menu item description style
  TextStyle get menuItemDescription => RestaurantTextStyles.menuItemDescription;

  /// Get price style
  TextStyle get price => RestaurantTextStyles.price;

  /// Get emphasized price style
  TextStyle get priceEmphasized => RestaurantTextStyles.priceEmphasized;

  /// Get order number style
  TextStyle get orderNumber => RestaurantTextStyles.orderNumber;

  /// Get table number style
  TextStyle get tableNumber => RestaurantTextStyles.tableNumber;

  /// Get status text style
  TextStyle get status => RestaurantTextStyles.status;

  /// Get timestamp style
  TextStyle get timestamp => RestaurantTextStyles.timestamp;

  /// Get navigation label style
  TextStyle get navigationLabel => RestaurantTextStyles.navigationLabel;

  /// Get QR instruction style
  TextStyle get qrInstruction => RestaurantTextStyles.qrInstruction;

  /// Get restaurant name style
  TextStyle get restaurantName => RestaurantTextStyles.restaurantName;

  /// Get category header style
  TextStyle get categoryHeader => RestaurantTextStyles.categoryHeader;
}
