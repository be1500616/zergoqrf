/// ZERGO QR Spacing System following Material Design 4dp Grid
/// 
/// Provides consistent spacing tokens for layout, margins, padding,
/// and component spacing across restaurant management and diner interfaces.
class AppSpacing {
  /// Base spacing unit following Material Design 4dp grid system
  static const double _baseUnit = 4.0;
  
  /// Core spacing tokens
  static const double xs = _baseUnit; // 4dp
  static const double sm = _baseUnit * 2; // 8dp  
  static const double md = _baseUnit * 4; // 16dp
  static const double lg = _baseUnit * 6; // 24dp
  static const double xl = _baseUnit * 8; // 32dp
  static const double xxl = _baseUnit * 12; // 48dp
  static const double xxxl = _baseUnit * 16; // 64dp
  
  /// Extended spacing tokens for special layouts
  static const double micro = _baseUnit * 0.5; // 2dp - for very tight spacing
  static const double huge = _baseUnit * 20; // 80dp - for hero sections
  static const double massive = _baseUnit * 24; // 96dp - for major layout sections
}

/// Padding tokens - internal spacing within components
class AppPadding {
  static const double button = AppSpacing.sm; // 8dp
  static const double card = AppSpacing.md; // 16dp
  static const double screen = AppSpacing.md; // 16dp
  static const double dialog = AppSpacing.lg; // 24dp
  static const double section = AppSpacing.xl; // 32dp
  static const double listItem = AppSpacing.md; // 16dp
  static const double form = AppSpacing.md; // 16dp
  static const double chip = AppSpacing.sm; // 8dp
  static const double iconButton = AppSpacing.xs; // 4dp
}
  
/// Margin tokens - external spacing between components
class AppMargin {
  static const double component = AppSpacing.md; // 16dp
  static const double section = AppSpacing.lg; // 24dp
  static const double page = AppSpacing.xl; // 32dp
  static const double card = AppSpacing.md; // 16dp
  static const double listItem = AppSpacing.xs; // 4dp
  static const double button = AppSpacing.sm; // 8dp
  static const double form = AppSpacing.md; // 16dp
  static const double dialog = AppSpacing.xxl; // 48dp
}
  
/// Gap tokens - spacing in Flex layouts (Row, Column, Wrap)
class AppGap {
  static const double tiny = AppSpacing.xs; // 4dp
  static const double small = AppSpacing.sm; // 8dp
  static const double medium = AppSpacing.md; // 16dp
  static const double large = AppSpacing.lg; // 24dp
  static const double extraLarge = AppSpacing.xl; // 32dp
  static const double huge = AppSpacing.xxl; // 48dp
}
  
/// Grid spacing for responsive layouts
class AppGrid {
  static const double gutter = AppSpacing.md; // 16dp - space between grid items
  static const double margin = AppSpacing.lg; // 24dp - outer margin of grid container
  static const double column = AppSpacing.md; // 16dp - internal column padding
}
  
/// Restaurant-specific spacing tokens
class RestaurantSpacing {
  /// Menu layout spacing
  static const double menuCategoryGap = AppSpacing.lg; // 24dp
  static const double menuItemGap = AppSpacing.md; // 16dp
  static const double menuItemPadding = AppSpacing.md; // 16dp
  static const double menuSectionMargin = AppSpacing.xl; // 32dp
  
  /// Order interface spacing
  static const double orderItemGap = AppSpacing.sm; // 8dp
  static const double orderSectionGap = AppSpacing.lg; // 24dp
  static const double orderSummaryPadding = AppSpacing.md; // 16dp
  static const double orderButtonSpacing = AppSpacing.sm; // 8dp
  
  /// Table management spacing
  static const double tableGap = AppSpacing.md; // 16dp
  static const double tableContentPadding = AppSpacing.sm; // 8dp
  static const double tableStatusMargin = AppSpacing.xs; // 4dp
  
  /// Dashboard layout spacing
  static const double dashboardCardGap = AppSpacing.md; // 16dp
  static const double dashboardSectionGap = AppSpacing.xxl; // 48dp
  static const double dashboardWidgetPadding = AppSpacing.md; // 16dp
  static const double dashboardHeaderMargin = AppSpacing.lg; // 24dp
  
  /// QR code spacing
  static const double qrCodeMargin = AppSpacing.lg; // 24dp
  static const double qrCodePadding = AppSpacing.md; // 16dp
  static const double qrInstructionGap = AppSpacing.sm; // 8dp
  
  /// Form spacing for restaurant setup
  static const double formFieldGap = AppSpacing.md; // 16dp
  static const double formSectionGap = AppSpacing.lg; // 24dp
  static const double formButtonMargin = AppSpacing.xl; // 32dp
  static const double formHeaderMargin = AppSpacing.lg; // 24dp
  
  /// Navigation spacing
  static const double navItemPadding = AppSpacing.sm; // 8dp
  static const double navItemGap = AppSpacing.xs; // 4dp
  static const double navSectionGap = AppSpacing.md; // 16dp
  static const double appBarPadding = AppSpacing.md; // 16dp
  
  /// Card and container spacing
  static const double cardRadius = AppSpacing.sm; // 8dp
  static const double cardPadding = AppSpacing.md; // 16dp
  static const double cardGap = AppSpacing.md; // 16dp
  static const double containerPadding = AppSpacing.md; // 16dp
}
  
/// Responsive breakpoint-based spacing modifiers
///
/// Enhanced to integrate with the new responsive breakpoint system.
/// Provides spacing multipliers for all defined breakpoints and
/// utilities for responsive spacing calculations.
class ResponsiveSpacing {
  /// Mobile spacing adjustments (reduce spacing for smaller screens)
  static const double mobileMultiplier = 0.75;

  /// Large mobile spacing adjustments
  static const double mobileLargeMultiplier = 0.85;

  /// Tablet spacing (standard spacing)
  static const double tabletMultiplier = 1.0;

  /// Desktop spacing adjustments (increase spacing for larger screens)
  static const double desktopMultiplier = 1.25;

  /// Extra large desktop spacing adjustments
  static const double desktopXLMultiplier = 1.5;

  /// Get responsive spacing value based on screen width
  ///
  /// This method maintains backward compatibility while supporting
  /// the new breakpoint system.
  ///
  /// Args:
  ///   baseSpacing: The base spacing value to multiply.
  ///   screenWidth: The screen width in logical pixels.
  ///
  /// Returns:
  ///   The responsive spacing value.
  static double getSpacing(double baseSpacing, double screenWidth) {
    if (screenWidth < 428) {
      return baseSpacing * mobileMultiplier;
    } else if (screenWidth < 600) {
      return baseSpacing * mobileLargeMultiplier;
    } else if (screenWidth < 1024) {
      return baseSpacing * tabletMultiplier;
    } else if (screenWidth < 1440) {
      return baseSpacing * desktopMultiplier;
    } else {
      return baseSpacing * desktopXLMultiplier;
    }
  }

  /// Get spacing multiplier for a specific breakpoint width
  ///
  /// Args:
  ///   screenWidth: The screen width in logical pixels.
  ///
  /// Returns:
  ///   The spacing multiplier for the given width.
  static double getMultiplier(double screenWidth) {
    if (screenWidth < 428) {
      return mobileMultiplier;
    } else if (screenWidth < 600) {
      return mobileLargeMultiplier;
    } else if (screenWidth < 1024) {
      return tabletMultiplier;
    } else if (screenWidth < 1440) {
      return desktopMultiplier;
    } else {
      return desktopXLMultiplier;
    }
  }

  /// Apply responsive spacing to a base value
  ///
  /// Args:
  ///   baseValue: The base spacing value.
  ///   screenWidth: The screen width in logical pixels.
  ///
  /// Returns:
  ///   The responsive spacing value.
  static double apply(double baseValue, double screenWidth) {
    return baseValue * getMultiplier(screenWidth);
  }
}
  
/// Animation and transition spacing
class AnimationSpacing {
  static const double slideOffset = AppSpacing.xxl; // 48dp - for slide transitions
  static const double scaleOrigin = AppSpacing.md; // 16dp - for scale transitions
  static const double fabOffset = AppSpacing.xl; // 32dp - for FAB animations
}
  
/// Accessibility spacing adjustments
class AccessibilitySpacing {
  static const double minimumTouchTarget = 44.0; // 44dp minimum touch target
  static const double touchTargetPadding = AppSpacing.sm; // 8dp around touch targets
  static const double focusIndicatorMargin = AppSpacing.xs; // 4dp for focus indicators
}