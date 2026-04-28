import 'package:flutter/material.dart';
import '../../../core/theme/app_spacing.dart';
import '../breakpoints.dart';

/// An adaptive container that adjusts its properties based on screen size.
/// 
/// This container automatically adapts its padding, margins, and sizing
/// based on the current breakpoint, providing consistent spacing and
/// layout behavior across all screen sizes.
/// 
/// Example usage:
/// ```dart
/// AdaptiveContainer(
///   child: MenuItemCard(item: item),
/// )
/// ```
class AdaptiveContainer extends StatelessWidget {
  /// Creates an adaptive container widget.
  /// 
  /// Args:
  ///   child: The widget to contain.
  ///   padding: Custom padding (optional, uses responsive defaults).
  ///   margin: Custom margin (optional, uses responsive defaults).
  ///   width: Custom width (optional, uses responsive defaults).
  ///   height: Custom height (optional).
  ///   decoration: Custom decoration (optional).
  ///   constraints: Custom constraints (optional).
  ///   alignment: How to align the child within the container.
  ///   key: Optional widget key for identification.
  const AdaptiveContainer({
    super.key,
    required this.child,
    this.padding,
    this.margin,
    this.width,
    this.height,
    this.decoration,
    this.constraints,
    this.alignment,
  });

  /// The child widget to contain.
  final Widget child;

  /// Custom padding around the child.
  final EdgeInsetsGeometry? padding;

  /// Custom margin around the container.
  final EdgeInsetsGeometry? margin;

  /// Custom width of the container.
  final double? width;

  /// Custom height of the container.
  final double? height;

  /// Custom decoration for the container.
  final BoxDecoration? decoration;

  /// Custom constraints for the container.
  final BoxConstraints? constraints;

  /// How to align the child within the container.
  final AlignmentGeometry? alignment;

  @override
  Widget build(BuildContext context) {
    final breakpoint = BreakpointConfig.getCurrentBreakpoint(context);
    final spacingMultiplier = BreakpointConfig.getSpacingMultiplier(context);
    
    // Calculate responsive padding and margin
    final effectivePadding = padding ?? _getResponsivePadding(breakpoint, spacingMultiplier);
    final effectiveMargin = margin ?? _getResponsiveMargin(breakpoint, spacingMultiplier);
    final effectiveWidth = width ?? _getResponsiveWidth(context, breakpoint);
    final effectiveConstraints = constraints ?? _getResponsiveConstraints(breakpoint);
    
    return Container(
      width: effectiveWidth,
      height: height,
      padding: effectivePadding,
      margin: effectiveMargin,
      decoration: decoration,
      constraints: effectiveConstraints,
      alignment: alignment,
      child: child,
    );
  }

  /// Gets responsive padding based on breakpoint.
  /// 
  /// Args:
  ///   breakpoint: The current breakpoint.
  ///   spacingMultiplier: The spacing multiplier for the breakpoint.
  /// 
  /// Returns:
  ///   Appropriate padding for the breakpoint.
  EdgeInsetsGeometry _getResponsivePadding(Breakpoint breakpoint, double spacingMultiplier) {
    switch (breakpoint) {
      case Breakpoint.mobile:
        return EdgeInsets.all(AppPadding.screen * spacingMultiplier);
      case Breakpoint.mobileLarge:
        return EdgeInsets.all(AppPadding.card * spacingMultiplier);
      case Breakpoint.tablet:
        return EdgeInsets.all(AppPadding.section * spacingMultiplier);
      case Breakpoint.desktop:
      case Breakpoint.desktopXL:
        return EdgeInsets.all(AppPadding.section * spacingMultiplier);
    }
  }

  /// Gets responsive margin based on breakpoint.
  /// 
  /// Args:
  ///   breakpoint: The current breakpoint.
  ///   spacingMultiplier: The spacing multiplier for the breakpoint.
  /// 
  /// Returns:
  ///   Appropriate margin for the breakpoint.
  EdgeInsetsGeometry _getResponsiveMargin(Breakpoint breakpoint, double spacingMultiplier) {
    switch (breakpoint) {
      case Breakpoint.mobile:
        return EdgeInsets.all(AppMargin.component * spacingMultiplier);
      case Breakpoint.mobileLarge:
        return EdgeInsets.all(AppMargin.component * spacingMultiplier);
      case Breakpoint.tablet:
        return EdgeInsets.all(AppMargin.section * spacingMultiplier);
      case Breakpoint.desktop:
      case Breakpoint.desktopXL:
        return EdgeInsets.all(AppMargin.page * spacingMultiplier);
    }
  }

  /// Gets responsive width based on breakpoint.
  /// 
  /// Args:
  ///   context: The build context.
  ///   breakpoint: The current breakpoint.
  /// 
  /// Returns:
  ///   Appropriate width for the breakpoint or null for full width.
  double? _getResponsiveWidth(BuildContext context, Breakpoint breakpoint) {
    final screenWidth = MediaQuery.of(context).size.width;
    
    switch (breakpoint) {
      case Breakpoint.mobile:
      case Breakpoint.mobileLarge:
        return null; // Full width on mobile
      case Breakpoint.tablet:
        return screenWidth * 0.9; // 90% width on tablet
      case Breakpoint.desktop:
        return screenWidth * 0.8; // 80% width on desktop
      case Breakpoint.desktopXL:
        return screenWidth * 0.7; // 70% width on extra large desktop
    }
  }

  /// Gets responsive constraints based on breakpoint.
  /// 
  /// Args:
  ///   breakpoint: The current breakpoint.
  /// 
  /// Returns:
  ///   Appropriate constraints for the breakpoint.
  BoxConstraints _getResponsiveConstraints(Breakpoint breakpoint) {
    switch (breakpoint) {
      case Breakpoint.mobile:
        return const BoxConstraints(
          minHeight: AccessibilitySpacing.minimumTouchTarget,
        );
      case Breakpoint.mobileLarge:
        return const BoxConstraints(
          minHeight: AccessibilitySpacing.minimumTouchTarget,
        );
      case Breakpoint.tablet:
        return const BoxConstraints(
          minHeight: 48.0,
          maxWidth: 800.0,
        );
      case Breakpoint.desktop:
        return const BoxConstraints(
          minHeight: 48.0,
          maxWidth: 1200.0,
        );
      case Breakpoint.desktopXL:
        return const BoxConstraints(
          minHeight: 48.0,
          maxWidth: 1600.0,
        );
    }
  }
}

/// An adaptive card container with responsive styling.
/// 
/// This widget provides a card-like container that adapts its appearance
/// and spacing based on the current breakpoint. It includes elevation,
/// rounded corners, and responsive padding.
/// 
/// Example usage:
/// ```dart
/// AdaptiveCard(
///   child: MenuItemDetails(item: item),
/// )
/// ```
class AdaptiveCard extends StatelessWidget {
  /// Creates an adaptive card widget.
  /// 
  /// Args:
  ///   child: The widget to contain in the card.
  ///   elevation: Custom elevation (optional, uses responsive defaults).
  ///   borderRadius: Custom border radius (optional, uses responsive defaults).
  ///   padding: Custom padding (optional, uses responsive defaults).
  ///   margin: Custom margin (optional, uses responsive defaults).
  ///   color: Custom background color (optional).
  ///   shadowColor: Custom shadow color (optional).
  ///   key: Optional widget key for identification.
  const AdaptiveCard({
    super.key,
    required this.child,
    this.elevation,
    this.borderRadius,
    this.padding,
    this.margin,
    this.color,
    this.shadowColor,
  });

  /// The child widget to contain in the card.
  final Widget child;

  /// Custom elevation for the card.
  final double? elevation;

  /// Custom border radius for the card.
  final BorderRadiusGeometry? borderRadius;

  /// Custom padding inside the card.
  final EdgeInsetsGeometry? padding;

  /// Custom margin around the card.
  final EdgeInsetsGeometry? margin;

  /// Custom background color for the card.
  final Color? color;

  /// Custom shadow color for the card.
  final Color? shadowColor;

  @override
  Widget build(BuildContext context) {
    final breakpoint = BreakpointConfig.getCurrentBreakpoint(context);
    final spacingMultiplier = BreakpointConfig.getSpacingMultiplier(context);
    
    // Calculate responsive properties
    final effectiveElevation = elevation ?? _getResponsiveElevation(breakpoint);
    final effectiveBorderRadius = borderRadius ?? _getResponsiveBorderRadius(breakpoint);
    final effectivePadding = padding ?? EdgeInsets.all(RestaurantSpacing.cardPadding * spacingMultiplier);
    final effectiveMargin = margin ?? EdgeInsets.all(RestaurantSpacing.cardGap * spacingMultiplier);
    
    return Container(
      margin: effectiveMargin,
      child: Material(
        elevation: effectiveElevation,
        borderRadius: effectiveBorderRadius,
        color: color ?? Theme.of(context).cardColor,
        shadowColor: shadowColor,
        child: Padding(
          padding: effectivePadding,
          child: child,
        ),
      ),
    );
  }

  /// Gets responsive elevation based on breakpoint.
  /// 
  /// Args:
  ///   breakpoint: The current breakpoint.
  /// 
  /// Returns:
  ///   Appropriate elevation for the breakpoint.
  double _getResponsiveElevation(Breakpoint breakpoint) {
    switch (breakpoint) {
      case Breakpoint.mobile:
      case Breakpoint.mobileLarge:
        return 2.0; // Subtle elevation on mobile
      case Breakpoint.tablet:
        return 4.0; // Medium elevation on tablet
      case Breakpoint.desktop:
      case Breakpoint.desktopXL:
        return 6.0; // Higher elevation on desktop
    }
  }

  /// Gets responsive border radius based on breakpoint.
  /// 
  /// Args:
  ///   breakpoint: The current breakpoint.
  /// 
  /// Returns:
  ///   Appropriate border radius for the breakpoint.
  BorderRadiusGeometry _getResponsiveBorderRadius(Breakpoint breakpoint) {
    switch (breakpoint) {
      case Breakpoint.mobile:
      case Breakpoint.mobileLarge:
        return BorderRadius.circular(RestaurantSpacing.cardRadius);
      case Breakpoint.tablet:
        return BorderRadius.circular(RestaurantSpacing.cardRadius * 1.5);
      case Breakpoint.desktop:
      case Breakpoint.desktopXL:
        return BorderRadius.circular(RestaurantSpacing.cardRadius * 2.0);
    }
  }
}
