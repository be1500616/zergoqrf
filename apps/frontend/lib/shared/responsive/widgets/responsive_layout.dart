import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';

import '../breakpoints.dart';

/// A declarative widget for switching between breakpoint-specific layouts.
///
/// This widget provides a clean, declarative API for defining different
/// layouts for different screen sizes. It automatically selects the
/// appropriate layout based on the current breakpoint.
///
/// Example usage:
/// ```dart
/// ResponsiveLayout(
///   mobile: MobileMenuLayout(),
///   tablet: TabletMenuLayout(),
///   desktop: DesktopMenuLayout(),
///   fallback: DefaultMenuLayout(), // Optional fallback
/// )
/// ```
class ResponsiveLayout extends StatelessWidget {
  /// Creates a responsive layout widget.
  ///
  /// At least one layout must be provided. If a specific breakpoint layout
  /// is not provided, the widget will fall back to the next smaller breakpoint
  /// or the fallback widget.
  ///
  /// Args:
  ///   mobile: Layout for mobile breakpoint (0-427px).
  ///   mobileLarge: Layout for large mobile breakpoint (428-599px).
  ///   tablet: Layout for tablet breakpoint (600-1023px).
  ///   desktop: Layout for desktop breakpoint (1024-1439px).
  ///   desktopXL: Layout for extra large desktop breakpoint (1440px+).
  ///   fallback: Fallback layout if no specific layout is provided.
  ///   key: Optional widget key for identification.
  const ResponsiveLayout({
    super.key,
    this.mobile,
    this.mobileLarge,
    this.tablet,
    this.desktop,
    this.desktopXL,
    this.fallback,
  }) : assert(
          mobile != null ||
              mobileLarge != null ||
              tablet != null ||
              desktop != null ||
              desktopXL != null ||
              fallback != null,
          'At least one layout must be provided',
        );

  /// Layout widget for mobile breakpoint.
  final Widget? mobile;

  /// Layout widget for large mobile breakpoint.
  final Widget? mobileLarge;

  /// Layout widget for tablet breakpoint.
  final Widget? tablet;

  /// Layout widget for desktop breakpoint.
  final Widget? desktop;

  /// Layout widget for extra large desktop breakpoint.
  final Widget? desktopXL;

  /// Fallback layout widget when no specific layout is available.
  final Widget? fallback;

  @override
  Widget build(BuildContext context) {
    final breakpoint = BreakpointConfig.getCurrentBreakpoint(context);

    // Select the appropriate layout based on breakpoint
    Widget? selectedLayout = _getLayoutForBreakpoint(breakpoint);

    // If no layout found, try fallback
    selectedLayout ??= fallback;

    // If still no layout, throw an error
    if (selectedLayout == null) {
      throw FlutterError(
        'ResponsiveLayout: No layout provided for breakpoint $breakpoint '
        'and no fallback layout specified.',
      );
    }

    return selectedLayout;
  }

  /// Gets the layout widget for the specified breakpoint.
  ///
  /// Uses a fallback strategy: if the exact breakpoint layout is not available,
  /// it tries the next smaller breakpoint layout.
  ///
  /// Args:
  ///   breakpoint: The current breakpoint.
  ///
  /// Returns:
  ///   The appropriate layout widget or null if none found.
  Widget? _getLayoutForBreakpoint(Breakpoint breakpoint) {
    switch (breakpoint) {
      case Breakpoint.desktopXL:
        return desktopXL ?? desktop ?? tablet ?? mobileLarge ?? mobile;
      case Breakpoint.desktop:
        return desktop ?? tablet ?? mobileLarge ?? mobile;
      case Breakpoint.tablet:
        return tablet ?? mobileLarge ?? mobile;
      case Breakpoint.mobileLarge:
        return mobileLarge ?? mobile;
      case Breakpoint.mobile:
        return mobile;
    }
  }
}

/// A responsive layout widget that provides more granular control.
///
/// This widget allows you to define layouts based on screen width ranges
/// rather than predefined breakpoints, giving you more flexibility.
///
/// Example usage:
/// ```dart
/// ResponsiveLayoutBuilder(
///   builder: (context, constraints) {
///     if (constraints.maxWidth > 1200) {
///       return WideDesktopLayout();
///     } else if (constraints.maxWidth > 800) {
///       return StandardDesktopLayout();
///     } else {
///       return MobileLayout();
///     }
///   },
/// )
/// ```
class ResponsiveLayoutBuilder extends StatelessWidget {
  /// Creates a responsive layout builder widget.
  ///
  /// Args:
  ///   builder: Function that builds the layout based on constraints.
  ///   key: Optional widget key for identification.
  const ResponsiveLayoutBuilder({
    super.key,
    required this.builder,
  });

  /// Builder function that receives the current constraints.
  final Widget Function(BuildContext context, BoxConstraints constraints)
      builder;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: builder,
    );
  }
}

/// A responsive widget that adapts its child based on orientation.
///
/// This widget provides different layouts for portrait and landscape
/// orientations, which is particularly useful for tablet interfaces.
///
/// Example usage:
/// ```dart
/// ResponsiveOrientation(
///   portrait: PortraitMenuLayout(),
///   landscape: LandscapeMenuLayout(),
/// )
/// ```
class ResponsiveOrientation extends StatelessWidget {
  /// Creates a responsive orientation widget.
  ///
  /// Args:
  ///   portrait: Layout for portrait orientation.
  ///   landscape: Layout for landscape orientation.
  ///   key: Optional widget key for identification.
  const ResponsiveOrientation({
    super.key,
    required this.portrait,
    required this.landscape,
  });

  /// Layout widget for portrait orientation.
  final Widget portrait;

  /// Layout widget for landscape orientation.
  final Widget landscape;

  @override
  Widget build(BuildContext context) {
    final orientation = MediaQuery.of(context).orientation;

    return orientation == Orientation.portrait ? portrait : landscape;
  }
}

/// A responsive widget that combines breakpoint and orientation awareness.
///
/// This widget provides the most comprehensive responsive layout control
/// by considering both screen size and orientation.
///
/// Example usage:
/// ```dart
/// ResponsiveLayoutGrid(
///   mobilePortrait: MobilePortraitLayout(),
///   mobileLandscape: MobileLandscapeLayout(),
///   tabletPortrait: TabletPortraitLayout(),
///   tabletLandscape: TabletLandscapeLayout(),
///   desktop: DesktopLayout(), // Same for both orientations
/// )
/// ```
class ResponsiveLayoutGrid extends StatelessWidget {
  /// Creates a responsive layout grid widget.
  ///
  /// Args:
  ///   mobilePortrait: Layout for mobile portrait.
  ///   mobileLandscape: Layout for mobile landscape.
  ///   tabletPortrait: Layout for tablet portrait.
  ///   tabletLandscape: Layout for tablet landscape.
  ///   desktop: Layout for desktop (both orientations).
  ///   fallback: Fallback layout if no specific layout is provided.
  ///   key: Optional widget key for identification.
  const ResponsiveLayoutGrid({
    super.key,
    this.mobilePortrait,
    this.mobileLandscape,
    this.tabletPortrait,
    this.tabletLandscape,
    this.desktop,
    this.fallback,
  });

  /// Layout for mobile portrait orientation.
  final Widget? mobilePortrait;

  /// Layout for mobile landscape orientation.
  final Widget? mobileLandscape;

  /// Layout for tablet portrait orientation.
  final Widget? tabletPortrait;

  /// Layout for tablet landscape orientation.
  final Widget? tabletLandscape;

  /// Layout for desktop (both orientations).
  final Widget? desktop;

  /// Fallback layout when no specific layout is available.
  final Widget? fallback;

  @override
  Widget build(BuildContext context) {
    final breakpoint = BreakpointConfig.getCurrentBreakpoint(context);
    final orientation = MediaQuery.of(context).orientation;
    final isPortrait = orientation == Orientation.portrait;

    Widget? selectedLayout;

    // Select layout based on breakpoint and orientation
    switch (breakpoint) {
      case Breakpoint.mobile:
      case Breakpoint.mobileLarge:
        selectedLayout = isPortrait ? mobilePortrait : mobileLandscape;
        break;
      case Breakpoint.tablet:
        selectedLayout = isPortrait ? tabletPortrait : tabletLandscape;
        break;
      case Breakpoint.desktop:
      case Breakpoint.desktopXL:
        selectedLayout = desktop;
        break;
    }

    // Fallback strategy
    selectedLayout ??= fallback;

    if (selectedLayout == null) {
      throw FlutterError(
        'ResponsiveLayoutGrid: No layout provided for breakpoint $breakpoint '
        'with orientation $orientation and no fallback layout specified.',
      );
    }

    return selectedLayout;
  }
}
