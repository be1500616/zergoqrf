import 'package:flutter/material.dart';

/// ZERGO QR Responsive Breakpoint System
/// 
/// Defines standardized breakpoint constants following Material Design guidelines
/// and provides utilities for breakpoint detection and responsive behavior.

/// Enumeration of supported breakpoints for responsive design.
/// 
/// Each breakpoint represents a specific screen size range optimized for
/// different device types and interaction patterns.
enum Breakpoint {
  /// Mobile devices (0-599px)
  /// - Single-column layouts
  /// - Touch-optimized interactions
  /// - Bottom navigation priority
  /// - 44px minimum touch targets
  mobile,

  /// Large mobile devices (428-599px)
  /// - Large phones and small tablets
  /// - Optimized touch targets
  /// - Enhanced content density
  mobileLarge,

  /// Tablet devices (600-1023px)
  /// - Two-column layouts
  /// - Hybrid touch/pointer interactions
  /// - Side navigation patterns
  /// - Landscape/portrait optimization
  tablet,

  /// Desktop devices (1024-1439px)
  /// - Multi-column layouts
  /// - Pointer-optimized interactions
  /// - Enhanced information density
  /// - Keyboard navigation support
  desktop,

  /// Extra large desktop (1440px+)
  /// - Wide screen layouts
  /// - Maximum information density
  /// - Advanced multi-column grids
  /// - Enhanced productivity features
  desktopXL,
}

/// Configuration class for responsive breakpoints.
/// 
/// Provides static constants for all breakpoint values and utility methods
/// for breakpoint detection and responsive behavior.
class BreakpointConfig {
  /// Private constructor to prevent instantiation.
  const BreakpointConfig._();

  // Breakpoint constants following Material Design guidelines
  static const double mobile = 0.0;
  static const double mobileLarge = 428.0;
  static const double tablet = 600.0;
  static const double desktop = 1024.0;
  static const double desktopXL = 1440.0;

  /// Gets the current breakpoint based on screen width.
  /// 
  /// Args:
  ///   context: The build context to get screen dimensions from.
  /// 
  /// Returns:
  ///   The current [Breakpoint] enum value.
  static Breakpoint getCurrentBreakpoint(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    return getBreakpointFromWidth(width);
  }

  /// Gets the breakpoint for a specific width value.
  /// 
  /// Args:
  ///   width: The screen width in logical pixels.
  /// 
  /// Returns:
  ///   The corresponding [Breakpoint] enum value.
  static Breakpoint getBreakpointFromWidth(double width) {
    if (width >= desktopXL) {
      return Breakpoint.desktopXL;
    } else if (width >= desktop) {
      return Breakpoint.desktop;
    } else if (width >= tablet) {
      return Breakpoint.tablet;
    } else if (width >= mobileLarge) {
      return Breakpoint.mobileLarge;
    } else {
      return Breakpoint.mobile;
    }
  }

  /// Checks if the current screen matches a specific breakpoint.
  /// 
  /// Args:
  ///   context: The build context to get screen dimensions from.
  ///   breakpoint: The breakpoint to check against.
  /// 
  /// Returns:
  ///   True if the current screen matches the specified breakpoint.
  static bool isBreakpoint(BuildContext context, Breakpoint breakpoint) {
    return getCurrentBreakpoint(context) == breakpoint;
  }

  /// Checks if the current screen is at or above a specific breakpoint.
  /// 
  /// Args:
  ///   context: The build context to get screen dimensions from.
  ///   breakpoint: The minimum breakpoint to check against.
  /// 
  /// Returns:
  ///   True if the current screen is at or above the specified breakpoint.
  static bool isAtLeastBreakpoint(BuildContext context, Breakpoint breakpoint) {
    final current = getCurrentBreakpoint(context);
    return current.index >= breakpoint.index;
  }

  /// Gets the minimum width for a specific breakpoint.
  /// 
  /// Args:
  ///   breakpoint: The breakpoint to get the width for.
  /// 
  /// Returns:
  ///   The minimum width in logical pixels for the breakpoint.
  static double getBreakpointWidth(Breakpoint breakpoint) {
    switch (breakpoint) {
      case Breakpoint.mobile:
        return mobile;
      case Breakpoint.mobileLarge:
        return mobileLarge;
      case Breakpoint.tablet:
        return tablet;
      case Breakpoint.desktop:
        return desktop;
      case Breakpoint.desktopXL:
        return desktopXL;
    }
  }

  /// Gets responsive spacing multiplier for the current breakpoint.
  /// 
  /// Integrates with existing AppSpacing.ResponsiveSpacing system.
  /// 
  /// Args:
  ///   context: The build context to get screen dimensions from.
  /// 
  /// Returns:
  ///   The spacing multiplier for the current breakpoint.
  static double getSpacingMultiplier(BuildContext context) {
    final breakpoint = getCurrentBreakpoint(context);
    switch (breakpoint) {
      case Breakpoint.mobile:
      case Breakpoint.mobileLarge:
        return 0.75; // Reduced spacing for mobile
      case Breakpoint.tablet:
        return 1.0; // Standard spacing for tablet
      case Breakpoint.desktop:
      case Breakpoint.desktopXL:
        return 1.25; // Increased spacing for desktop
    }
  }

  /// Gets the number of columns for grid layouts based on breakpoint.
  /// 
  /// Args:
  ///   context: The build context to get screen dimensions from.
  /// 
  /// Returns:
  ///   The recommended number of columns for the current breakpoint.
  static int getGridColumns(BuildContext context) {
    final breakpoint = getCurrentBreakpoint(context);
    switch (breakpoint) {
      case Breakpoint.mobile:
        return 1;
      case Breakpoint.mobileLarge:
        return 2;
      case Breakpoint.tablet:
        return 3;
      case Breakpoint.desktop:
        return 4;
      case Breakpoint.desktopXL:
        return 6;
    }
  }
}
