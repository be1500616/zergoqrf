import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'breakpoints.dart';

/// Utility class for screen size detection and responsive value selection.
/// 
/// This class provides comprehensive utilities for building responsive
/// interfaces, including breakpoint detection, platform identification,
/// and conditional value selection based on screen characteristics.
/// 
/// Example usage:
/// ```dart
/// final screenSize = ScreenSize.of(context);
/// if (screenSize.isMobile) {
///   return MobileLayout();
/// } else if (screenSize.isTablet) {
///   return TabletLayout();
/// } else {
///   return DesktopLayout();
/// }
/// ```
class ScreenSize {
  /// Creates a ScreenSize instance from the given context.
  /// 
  /// Args:
  ///   context: The build context to extract screen information from.
  ScreenSize.of(BuildContext context)
      : _mediaQuery = MediaQuery.of(context),
        _breakpoint = BreakpointConfig.getCurrentBreakpoint(context);

  /// Creates a ScreenSize instance from explicit values.
  /// 
  /// This constructor is useful for testing or when you have explicit
  /// screen dimensions.
  /// 
  /// Args:
  ///   size: The screen size.
  ///   devicePixelRatio: The device pixel ratio.
  ///   orientation: The screen orientation.
  ///   padding: The screen padding (safe areas).
  ///   viewInsets: The view insets (keyboard, etc.).
  ScreenSize.fromValues({
    required Size size,
    double devicePixelRatio = 1.0,
    Orientation orientation = Orientation.portrait,
    EdgeInsets padding = EdgeInsets.zero,
    EdgeInsets viewInsets = EdgeInsets.zero,
  })  : _mediaQuery = MediaQueryData.fromView(
          WidgetsBinding.instance.platformDispatcher.views.first,
        ).copyWith(
          size: size,
          devicePixelRatio: devicePixelRatio,
          padding: padding,
          viewInsets: viewInsets,
        ),
        _breakpoint = BreakpointConfig.getBreakpointFromWidth(size.width);

  final MediaQueryData _mediaQuery;
  final Breakpoint _breakpoint;

  /// The screen size in logical pixels.
  Size get size => _mediaQuery.size;

  /// The screen width in logical pixels.
  double get width => _mediaQuery.size.width;

  /// The screen height in logical pixels.
  double get height => _mediaQuery.size.height;

  /// The current responsive breakpoint.
  Breakpoint get breakpoint => _breakpoint;

  /// The device pixel ratio.
  double get devicePixelRatio => _mediaQuery.devicePixelRatio;

  /// The screen orientation.
  Orientation get orientation => _mediaQuery.orientation;

  /// The screen padding (safe areas).
  EdgeInsets get padding => _mediaQuery.padding;

  /// The view insets (keyboard, etc.).
  EdgeInsets get viewInsets => _mediaQuery.viewInsets;

  // Breakpoint boolean helpers
  
  /// Whether the current breakpoint is mobile (0-427px).
  bool get isMobile => _breakpoint == Breakpoint.mobile;

  /// Whether the current breakpoint is large mobile (428-599px).
  bool get isMobileLarge => _breakpoint == Breakpoint.mobileLarge;

  /// Whether the current breakpoint is tablet (600-1023px).
  bool get isTablet => _breakpoint == Breakpoint.tablet;

  /// Whether the current breakpoint is desktop (1024-1439px).
  bool get isDesktop => _breakpoint == Breakpoint.desktop;

  /// Whether the current breakpoint is extra large desktop (1440px+).
  bool get isDesktopXL => _breakpoint == Breakpoint.desktopXL;

  // Grouped breakpoint helpers
  
  /// Whether the screen is mobile-sized (mobile or mobileLarge).
  bool get isMobileSize => isMobile || isMobileLarge;

  /// Whether the screen is desktop-sized (desktop or desktopXL).
  bool get isDesktopSize => isDesktop || isDesktopXL;

  /// Whether the screen has a compact layout (mobile breakpoints).
  bool get isCompact => isMobileSize;

  /// Whether the screen has an expanded layout (tablet and above).
  bool get isExpanded => !isCompact;

  // Orientation helpers
  
  /// Whether the screen is in landscape orientation.
  bool get isLandscape => orientation == Orientation.landscape;

  /// Whether the screen is in portrait orientation.
  bool get isPortrait => orientation == Orientation.portrait;

  // Platform detection helpers
  
  /// Whether the app is running on iOS.
  bool get isIOS => !kIsWeb && Platform.isIOS;

  /// Whether the app is running on Android.
  bool get isAndroid => !kIsWeb && Platform.isAndroid;

  /// Whether the app is running on the web.
  bool get isWeb => kIsWeb;

  /// Whether the app is running on a mobile platform (iOS or Android).
  bool get isMobilePlatform => isIOS || isAndroid;

  /// Whether the app is running on a desktop platform.
  bool get isDesktopPlatform => !kIsWeb && (Platform.isWindows || Platform.isMacOS || Platform.isLinux);

  // Safe area helpers
  
  /// Whether the device has a notch or safe area at the top.
  bool get hasTopNotch => padding.top > 0;

  /// Whether the device has a safe area at the bottom (home indicator).
  bool get hasBottomSafeArea => padding.bottom > 0;

  /// Whether the keyboard is currently visible.
  bool get isKeyboardVisible => viewInsets.bottom > 0;

  // Responsive value selection
  
  /// Selects a value based on the current breakpoint.
  /// 
  /// This method provides a clean way to select different values
  /// for different screen sizes. It uses a fallback strategy where
  /// if a specific breakpoint value is not provided, it falls back
  /// to the next smaller breakpoint.
  /// 
  /// Args:
  ///   mobile: Value for mobile breakpoint.
  ///   mobileLarge: Value for large mobile breakpoint (optional).
  ///   tablet: Value for tablet breakpoint (optional).
  ///   desktop: Value for desktop breakpoint (optional).
  ///   desktopXL: Value for extra large desktop breakpoint (optional).
  /// 
  /// Returns:
  ///   The appropriate value for the current breakpoint.
  /// 
  /// Example:
  /// ```dart
  /// final columns = screenSize.responsiveValue(
  ///   mobile: 1,
  ///   tablet: 2,
  ///   desktop: 3,
  /// );
  /// ```
  T responsiveValue<T>({
    required T mobile,
    T? mobileLarge,
    T? tablet,
    T? desktop,
    T? desktopXL,
  }) {
    switch (_breakpoint) {
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

  /// Selects a value based on orientation.
  /// 
  /// Args:
  ///   portrait: Value for portrait orientation.
  ///   landscape: Value for landscape orientation.
  /// 
  /// Returns:
  ///   The appropriate value for the current orientation.
  T orientationValue<T>({
    required T portrait,
    required T landscape,
  }) {
    return isPortrait ? portrait : landscape;
  }

  /// Selects a value based on platform.
  /// 
  /// Args:
  ///   mobile: Value for mobile platforms (iOS/Android).
  ///   web: Value for web platform.
  ///   desktop: Value for desktop platforms (optional, defaults to web value).
  /// 
  /// Returns:
  ///   The appropriate value for the current platform.
  T platformValue<T>({
    required T mobile,
    required T web,
    T? desktop,
  }) {
    if (isMobilePlatform) {
      return mobile;
    } else if (isWeb) {
      return web;
    } else {
      return desktop ?? web;
    }
  }

  /// Gets the spacing multiplier for the current breakpoint.
  ///
  /// Returns:
  ///   The spacing multiplier based on the current breakpoint.
  double get spacingMultiplier {
    switch (_breakpoint) {
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
  /// 
  /// Returns:
  ///   The number of columns appropriate for the current breakpoint.
  int get gridColumns {
    switch (_breakpoint) {
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

  /// Checks if the current screen is at or above a specific breakpoint.
  /// 
  /// Args:
  ///   breakpoint: The minimum breakpoint to check against.
  /// 
  /// Returns:
  ///   True if the current screen is at or above the specified breakpoint.
  bool isAtLeast(Breakpoint breakpoint) {
    return _breakpoint.index >= breakpoint.index;
  }

  /// Checks if the current screen is below a specific breakpoint.
  /// 
  /// Args:
  ///   breakpoint: The breakpoint to check against.
  /// 
  /// Returns:
  ///   True if the current screen is below the specified breakpoint.
  bool isBelow(Breakpoint breakpoint) {
    return _breakpoint.index < breakpoint.index;
  }

  @override
  String toString() {
    return 'ScreenSize('
        'size: $size, '
        'breakpoint: $_breakpoint, '
        'orientation: $orientation, '
        'platform: ${isWeb ? 'web' : (isIOS ? 'iOS' : (isAndroid ? 'Android' : 'desktop'))}'
        ')';
  }
}
