import 'package:flutter/material.dart';
import 'app_colors.dart';
import 'app_spacing.dart';

/// Custom theme extensions for restaurant-specific styling needs
/// that aren't covered by standard Material Design components.

/// Restaurant-specific color extension for semantic colors
@immutable
class RestaurantColorsExtension extends ThemeExtension<RestaurantColorsExtension> {
  const RestaurantColorsExtension({
    required this.success,
    required this.warning,
    required this.info,
    required this.orderPending,
    required this.orderConfirmed,
    required this.orderPreparing,
    required this.orderReady,
    required this.orderCompleted,
    required this.orderCancelled,
    required this.tableAvailable,
    required this.tableOccupied,
    required this.tableReserved,
    required this.tableCleaning,
  });

  final Color success;
  final Color warning;
  final Color info;
  final Color orderPending;
  final Color orderConfirmed;
  final Color orderPreparing;
  final Color orderReady;
  final Color orderCompleted;
  final Color orderCancelled;
  final Color tableAvailable;
  final Color tableOccupied;
  final Color tableReserved;
  final Color tableCleaning;

  @override
  RestaurantColorsExtension copyWith({
    Color? success,
    Color? warning,
    Color? info,
    Color? orderPending,
    Color? orderConfirmed,
    Color? orderPreparing,
    Color? orderReady,
    Color? orderCompleted,
    Color? orderCancelled,
    Color? tableAvailable,
    Color? tableOccupied,
    Color? tableReserved,
    Color? tableCleaning,
  }) {
    return RestaurantColorsExtension(
      success: success ?? this.success,
      warning: warning ?? this.warning,
      info: info ?? this.info,
      orderPending: orderPending ?? this.orderPending,
      orderConfirmed: orderConfirmed ?? this.orderConfirmed,
      orderPreparing: orderPreparing ?? this.orderPreparing,
      orderReady: orderReady ?? this.orderReady,
      orderCompleted: orderCompleted ?? this.orderCompleted,
      orderCancelled: orderCancelled ?? this.orderCancelled,
      tableAvailable: tableAvailable ?? this.tableAvailable,
      tableOccupied: tableOccupied ?? this.tableOccupied,
      tableReserved: tableReserved ?? this.tableReserved,
      tableCleaning: tableCleaning ?? this.tableCleaning,
    );
  }

  @override
  RestaurantColorsExtension lerp(
    ThemeExtension<RestaurantColorsExtension>? other,
    double t,
  ) {
    if (other is! RestaurantColorsExtension) {
      return this;
    }
    return RestaurantColorsExtension(
      success: Color.lerp(success, other.success, t)!,
      warning: Color.lerp(warning, other.warning, t)!,
      info: Color.lerp(info, other.info, t)!,
      orderPending: Color.lerp(orderPending, other.orderPending, t)!,
      orderConfirmed: Color.lerp(orderConfirmed, other.orderConfirmed, t)!,
      orderPreparing: Color.lerp(orderPreparing, other.orderPreparing, t)!,
      orderReady: Color.lerp(orderReady, other.orderReady, t)!,
      orderCompleted: Color.lerp(orderCompleted, other.orderCompleted, t)!,
      orderCancelled: Color.lerp(orderCancelled, other.orderCancelled, t)!,
      tableAvailable: Color.lerp(tableAvailable, other.tableAvailable, t)!,
      tableOccupied: Color.lerp(tableOccupied, other.tableOccupied, t)!,
      tableReserved: Color.lerp(tableReserved, other.tableReserved, t)!,
      tableCleaning: Color.lerp(tableCleaning, other.tableCleaning, t)!,
    );
  }

  /// Light theme restaurant colors extension
  static const light = RestaurantColorsExtension(
    success: AppColors.success,
    warning: AppColors.warning,
    info: AppColors.info,
    orderPending: AppColors.orderPending,
    orderConfirmed: AppColors.orderConfirmed,
    orderPreparing: AppColors.orderPreparing,
    orderReady: AppColors.orderReady,
    orderCompleted: AppColors.orderCompleted,
    orderCancelled: AppColors.orderCancelled,
    tableAvailable: AppColors.tableAvailable,
    tableOccupied: AppColors.tableOccupied,
    tableReserved: AppColors.tableReserved,
    tableCleaning: AppColors.tableCleaning,
  );

  /// Dark theme restaurant colors extension (same colors work well in dark theme)
  static const dark = light;
}

/// Restaurant-specific spacing extension for easy access
@immutable 
class RestaurantSpacingExtension extends ThemeExtension<RestaurantSpacingExtension> {
  const RestaurantSpacingExtension({
    required this.menuCategoryGap,
    required this.menuItemGap,
    required this.orderItemGap,
    required this.tableGap,
    required this.dashboardCardGap,
    required this.qrCodeMargin,
  });

  final double menuCategoryGap;
  final double menuItemGap;
  final double orderItemGap;
  final double tableGap;
  final double dashboardCardGap;
  final double qrCodeMargin;

  @override
  RestaurantSpacingExtension copyWith({
    double? menuCategoryGap,
    double? menuItemGap,
    double? orderItemGap,
    double? tableGap,
    double? dashboardCardGap,
    double? qrCodeMargin,
  }) {
    return RestaurantSpacingExtension(
      menuCategoryGap: menuCategoryGap ?? this.menuCategoryGap,
      menuItemGap: menuItemGap ?? this.menuItemGap,
      orderItemGap: orderItemGap ?? this.orderItemGap,
      tableGap: tableGap ?? this.tableGap,
      dashboardCardGap: dashboardCardGap ?? this.dashboardCardGap,
      qrCodeMargin: qrCodeMargin ?? this.qrCodeMargin,
    );
  }

  @override
  RestaurantSpacingExtension lerp(
    ThemeExtension<RestaurantSpacingExtension>? other,
    double t,
  ) {
    if (other is! RestaurantSpacingExtension) {
      return this;
    }
    return RestaurantSpacingExtension(
      menuCategoryGap: (menuCategoryGap * (1 - t)) + (other.menuCategoryGap * t),
      menuItemGap: (menuItemGap * (1 - t)) + (other.menuItemGap * t),
      orderItemGap: (orderItemGap * (1 - t)) + (other.orderItemGap * t),
      tableGap: (tableGap * (1 - t)) + (other.tableGap * t),
      dashboardCardGap: (dashboardCardGap * (1 - t)) + (other.dashboardCardGap * t),
      qrCodeMargin: (qrCodeMargin * (1 - t)) + (other.qrCodeMargin * t),
    );
  }

  /// Standard spacing extension for all screen sizes
  static const standard = RestaurantSpacingExtension(
    menuCategoryGap: RestaurantSpacing.menuCategoryGap,
    menuItemGap: RestaurantSpacing.menuItemGap,
    orderItemGap: RestaurantSpacing.orderItemGap,
    tableGap: RestaurantSpacing.tableGap,
    dashboardCardGap: RestaurantSpacing.dashboardCardGap,
    qrCodeMargin: RestaurantSpacing.qrCodeMargin,
  );
}

/// Extension methods for easy access to custom theme extensions
extension ThemeExtensions on ThemeData {
  /// Get restaurant colors extension
  RestaurantColorsExtension get restaurantColors =>
      extension<RestaurantColorsExtension>() ??
      RestaurantColorsExtension.light;

  /// Get restaurant spacing extension  
  RestaurantSpacingExtension get restaurantSpacing =>
      extension<RestaurantSpacingExtension>() ??
      RestaurantSpacingExtension.standard;
}

/// Context extensions for easy theme access
extension BuildContextThemeExtensions on BuildContext {
  /// Get restaurant colors from theme
  RestaurantColorsExtension get restaurantColors =>
      Theme.of(this).restaurantColors;

  /// Get restaurant spacing from theme
  RestaurantSpacingExtension get restaurantSpacing =>
      Theme.of(this).restaurantSpacing;

  /// Get app spacing values
  AppSpacing get spacing => AppSpacing();

  /// Get responsive spacing based on screen width
  double responsiveSpacing(double baseSpacing) {
    final screenWidth = MediaQuery.of(this).size.width;
    return ResponsiveSpacing.getSpacing(baseSpacing, screenWidth);
  }
}