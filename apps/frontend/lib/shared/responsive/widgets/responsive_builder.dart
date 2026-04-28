import 'package:flutter/material.dart';
import '../breakpoints.dart';

/// A builder widget that provides the current breakpoint context to its child.
/// 
/// This widget rebuilds whenever the screen size changes, allowing child widgets
/// to adapt their layout based on the current breakpoint. It's the foundation
/// for building responsive interfaces in the ZERGO QR application.
/// 
/// Example usage:
/// ```dart
/// ResponsiveBuilder(
///   builder: (context, breakpoint) {
///     switch (breakpoint) {
///       case Breakpoint.mobile:
///         return MobileLayout();
///       case Breakpoint.tablet:
///         return TabletLayout();
///       case Breakpoint.desktop:
///         return DesktopLayout();
///       default:
///         return DefaultLayout();
///     }
///   },
/// )
/// ```
class ResponsiveBuilder extends StatelessWidget {
  /// Creates a responsive builder widget.
  /// 
  /// Args:
  ///   builder: Function that builds the widget based on current breakpoint.
  ///   key: Optional widget key for identification.
  const ResponsiveBuilder({
    super.key,
    required this.builder,
  });

  /// Builder function that receives the current breakpoint.
  /// 
  /// This function is called whenever the screen size changes and should
  /// return a widget appropriate for the given breakpoint.
  final Widget Function(BuildContext context, Breakpoint breakpoint) builder;

  @override
  Widget build(BuildContext context) {
    final breakpoint = BreakpointConfig.getCurrentBreakpoint(context);
    return builder(context, breakpoint);
  }
}

/// A builder widget that provides detailed screen information to its child.
/// 
/// This widget extends ResponsiveBuilder by providing additional screen
/// information such as size, orientation, and platform details.
/// 
/// Example usage:
/// ```dart
/// ResponsiveScreenBuilder(
///   builder: (context, screen) {
///     if (screen.isLandscape && screen.isTablet) {
///       return LandscapeTabletLayout();
///     }
///     return screen.isMobile 
///       ? MobileLayout() 
///       : DesktopLayout();
///   },
/// )
/// ```
class ResponsiveScreenBuilder extends StatelessWidget {
  /// Creates a responsive screen builder widget.
  /// 
  /// Args:
  ///   builder: Function that builds the widget based on screen information.
  ///   key: Optional widget key for identification.
  const ResponsiveScreenBuilder({
    super.key,
    required this.builder,
  });

  /// Builder function that receives detailed screen information.
  final Widget Function(BuildContext context, ResponsiveScreenInfo screen) builder;

  @override
  Widget build(BuildContext context) {
    final screen = ResponsiveScreenInfo.fromContext(context);
    return builder(context, screen);
  }
}

/// Detailed screen information for responsive building.
/// 
/// Provides comprehensive information about the current screen including
/// breakpoint, size, orientation, and platform details.
class ResponsiveScreenInfo {
  /// Creates screen information from the given context.
  /// 
  /// Args:
  ///   context: The build context to extract screen information from.
  ResponsiveScreenInfo.fromContext(BuildContext context)
      : size = MediaQuery.of(context).size,
        breakpoint = BreakpointConfig.getCurrentBreakpoint(context),
        orientation = MediaQuery.of(context).orientation,
        devicePixelRatio = MediaQuery.of(context).devicePixelRatio,
        padding = MediaQuery.of(context).padding,
        viewInsets = MediaQuery.of(context).viewInsets;

  /// The screen size in logical pixels.
  final Size size;

  /// The current responsive breakpoint.
  final Breakpoint breakpoint;

  /// The current screen orientation.
  final Orientation orientation;

  /// The device pixel ratio.
  final double devicePixelRatio;

  /// The screen padding (safe areas).
  final EdgeInsets padding;

  /// The view insets (keyboard, etc.).
  final EdgeInsets viewInsets;

  /// Screen width in logical pixels.
  double get width => size.width;

  /// Screen height in logical pixels.
  double get height => size.height;

  /// Whether the screen is in landscape orientation.
  bool get isLandscape => orientation == Orientation.landscape;

  /// Whether the screen is in portrait orientation.
  bool get isPortrait => orientation == Orientation.portrait;

  /// Whether the current breakpoint is mobile.
  bool get isMobile => breakpoint == Breakpoint.mobile;

  /// Whether the current breakpoint is large mobile.
  bool get isMobileLarge => breakpoint == Breakpoint.mobileLarge;

  /// Whether the current breakpoint is tablet.
  bool get isTablet => breakpoint == Breakpoint.tablet;

  /// Whether the current breakpoint is desktop.
  bool get isDesktop => breakpoint == Breakpoint.desktop;

  /// Whether the current breakpoint is extra large desktop.
  bool get isDesktopXL => breakpoint == Breakpoint.desktopXL;

  /// Whether the screen is mobile-sized (mobile or mobileLarge).
  bool get isMobileSize => isMobile || isMobileLarge;

  /// Whether the screen is desktop-sized (desktop or desktopXL).
  bool get isDesktopSize => isDesktop || isDesktopXL;

  /// Whether the screen has a compact layout (mobile breakpoints).
  bool get isCompact => isMobileSize;

  /// Whether the screen has an expanded layout (tablet and above).
  bool get isExpanded => !isCompact;

  /// Gets the spacing multiplier for the current breakpoint.
  double get spacingMultiplier {
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

  /// Gets the recommended number of grid columns for the current breakpoint.
  int get gridColumns {
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
