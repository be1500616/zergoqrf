import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

/// Animation optimization utilities for smooth cross-platform performance.
/// 
/// Provides adaptive animation settings, performance monitoring,
/// and platform-specific optimizations to ensure 60fps performance
/// across all supported platforms.
class AnimationOptimizer {
  /// Private constructor to prevent instantiation
  AnimationOptimizer._();

  /// Whether animations should be reduced for performance.
  static bool _reduceAnimations = false;

  /// Whether the device supports high refresh rate displays.
  static bool _supportsHighRefreshRate = false;

  /// Current frame rate target (60fps default).
  static double _targetFrameRate = 60.0;

  /// Initializes the animation optimizer with platform-specific settings.
  static void initialize() {
    _detectPlatformCapabilities();
    _configureAnimationSettings();
    
    if (kDebugMode) {
      _setupPerformanceMonitoring();
    }
  }

  /// Detects platform capabilities for animation optimization.
  static void _detectPlatformCapabilities() {
    if (kIsWeb) {
      // Web-specific detection
      _supportsHighRefreshRate = false; // Conservative default
      _targetFrameRate = 60.0;
    } else {
      // Mobile/Desktop detection
      _supportsHighRefreshRate = true; // Assume modern devices
      _targetFrameRate = 60.0;
    }

    // Check for reduced motion preferences
    _reduceAnimations = MediaQueryData.fromView(
      WidgetsBinding.instance.platformDispatcher.views.first
    ).disableAnimations;
  }

  /// Configures animation settings based on platform capabilities.
  static void _configureAnimationSettings() {
    if (_reduceAnimations) {
      // Disable or reduce animations for accessibility
      _targetFrameRate = 30.0;
    }
  }

  /// Sets up performance monitoring for animations in debug mode.
  static void _setupPerformanceMonitoring() {
    SchedulerBinding.instance.addTimingsCallback((timings) {
      for (final timing in timings) {
        final frameTime = timing.totalSpan.inMicroseconds / 1000.0;
        if (frameTime > 16.67) { // More than 16.67ms = below 60fps
          debugPrint('Slow frame detected: ${frameTime.toStringAsFixed(2)}ms');
        }
      }
    });
  }

  /// Creates an optimized animation controller.
  /// 
  /// Automatically adjusts duration and settings based on platform capabilities.
  static AnimationController createOptimizedController({
    required TickerProvider vsync,
    required Duration duration,
    Duration? reverseDuration,
    String? debugLabel,
    double lowerBound = 0.0,
    double upperBound = 1.0,
    AnimationBehavior animationBehavior = AnimationBehavior.normal,
  }) {
    final optimizedDuration = _optimizeDuration(duration);
    final optimizedReverseDuration = reverseDuration != null 
        ? _optimizeDuration(reverseDuration)
        : null;

    return AnimationController(
      vsync: vsync,
      duration: optimizedDuration,
      reverseDuration: optimizedReverseDuration,
      debugLabel: debugLabel,
      lowerBound: lowerBound,
      upperBound: upperBound,
      animationBehavior: animationBehavior,
    );
  }

  /// Optimizes animation duration based on platform and performance settings.
  static Duration _optimizeDuration(Duration duration) {
    if (_reduceAnimations) {
      // Reduce animation duration for accessibility
      return Duration(milliseconds: (duration.inMilliseconds * 0.5).round());
    }

    if (kIsWeb) {
      // Slightly longer durations for web to account for potential lag
      return Duration(milliseconds: (duration.inMilliseconds * 1.1).round());
    }

    return duration;
  }

  /// Creates an optimized curve for smooth animations.
  /// 
  /// Returns platform-appropriate curves for the best user experience.
  static Curve getOptimizedCurve({
    Curve defaultCurve = Curves.easeInOut,
    bool isEntranceAnimation = false,
    bool isExitAnimation = false,
  }) {
    if (_reduceAnimations) {
      return Curves.linear; // Simplest curve for reduced animations
    }

    if (kIsWeb) {
      // Use simpler curves for web to reduce computation
      if (isEntranceAnimation) return Curves.easeOut;
      if (isExitAnimation) return Curves.easeIn;
      return Curves.ease;
    }

    // Use more sophisticated curves for native platforms
    if (isEntranceAnimation) return Curves.easeOutCubic;
    if (isExitAnimation) return Curves.easeInCubic;
    return defaultCurve;
  }

  /// Creates an optimized fade transition.
  static Widget fadeTransition({
    required Animation<double> animation,
    required Widget child,
    bool alwaysIncludeSemantics = false,
  }) {
    if (_reduceAnimations) {
      // Skip fade animation if reduced animations are enabled
      return child;
    }

    return FadeTransition(
      opacity: animation,
      alwaysIncludeSemantics: alwaysIncludeSemantics,
      child: child,
    );
  }

  /// Creates an optimized slide transition.
  static Widget slideTransition({
    required Animation<Offset> position,
    required Widget child,
    TextDirection? textDirection,
    bool transformHitTests = true,
  }) {
    if (_reduceAnimations) {
      // Skip slide animation if reduced animations are enabled
      return child;
    }

    return SlideTransition(
      position: position,
      textDirection: textDirection,
      transformHitTests: transformHitTests,
      child: child,
    );
  }

  /// Creates an optimized scale transition.
  static Widget scaleTransition({
    required Animation<double> scale,
    required Widget child,
    Alignment alignment = Alignment.center,
    FilterQuality? filterQuality,
  }) {
    if (_reduceAnimations) {
      // Skip scale animation if reduced animations are enabled
      return child;
    }

    return ScaleTransition(
      scale: scale,
      alignment: alignment,
      filterQuality: filterQuality ?? FilterQuality.low,
      child: child,
    );
  }

  /// Creates an optimized rotation transition.
  static Widget rotationTransition({
    required Animation<double> turns,
    required Widget child,
    Alignment alignment = Alignment.center,
    FilterQuality? filterQuality,
  }) {
    if (_reduceAnimations) {
      // Skip rotation animation if reduced animations are enabled
      return child;
    }

    return RotationTransition(
      turns: turns,
      alignment: alignment,
      filterQuality: filterQuality ?? FilterQuality.low,
      child: child,
    );
  }

  /// Creates an optimized animated container.
  static Widget animatedContainer({
    Key? key,
    required Duration duration,
    Curve curve = Curves.linear,
    AlignmentGeometry? alignment,
    EdgeInsetsGeometry? padding,
    Color? color,
    Decoration? decoration,
    Decoration? foregroundDecoration,
    double? width,
    double? height,
    BoxConstraints? constraints,
    EdgeInsetsGeometry? margin,
    Matrix4? transform,
    AlignmentGeometry? transformAlignment,
    Widget? child,
    Clip clipBehavior = Clip.none,
    VoidCallback? onEnd,
  }) {
    final optimizedDuration = _optimizeDuration(duration);
    final optimizedCurve = getOptimizedCurve(defaultCurve: curve);

    return AnimatedContainer(
      key: key,
      duration: optimizedDuration,
      curve: optimizedCurve,
      alignment: alignment,
      padding: padding,
      color: color,
      decoration: decoration,
      foregroundDecoration: foregroundDecoration,
      width: width,
      height: height,
      constraints: constraints,
      margin: margin,
      transform: transform,
      transformAlignment: transformAlignment,
      clipBehavior: clipBehavior,
      onEnd: onEnd,
      child: child,
    );
  }

  /// Checks if animations should be reduced for the current platform/settings.
  static bool get shouldReduceAnimations => _reduceAnimations;

  /// Gets the target frame rate for the current platform.
  static double get targetFrameRate => _targetFrameRate;

  /// Gets whether the platform supports high refresh rate displays.
  static bool get supportsHighRefreshRate => _supportsHighRefreshRate;

  /// Updates animation settings based on new accessibility preferences.
  static void updateAccessibilitySettings(bool reduceAnimations) {
    _reduceAnimations = reduceAnimations;
    _configureAnimationSettings();
  }

  /// Disposes of animation optimizer resources.
  static void dispose() {
    // Clean up any resources if needed
  }
}
