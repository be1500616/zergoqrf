import 'package:flutter/material.dart';

/// ZERGO QR Animation System
/// 
/// Provides consistent animation durations, curves, and configurations
/// for professional micro-interactions and transitions throughout the app.
class AppAnimations {
  /// Private constructor to prevent instantiation
  AppAnimations._();

  // Animation Durations
  static const Duration instant = Duration.zero;
  static const Duration fast = Duration(milliseconds: 150);
  static const Duration normal = Duration(milliseconds: 250);
  static const Duration slow = Duration(milliseconds: 400);
  static const Duration extraSlow = Duration(milliseconds: 600);

  // Standard Animation Curves
  static const Curve standard = Curves.easeInOut;
  static const Curve decelerate = Curves.easeOut;
  static const Curve accelerate = Curves.easeIn;
  static const Curve emphasize = Curves.easeInOutCubic;
  static const Curve bounce = Curves.elasticOut;

  // Interactive Feedback Animations
  static const Duration buttonPress = fast;
  static const double buttonPressScale = 0.98;
  
  static const Duration cardHover = normal;
  static const double cardHoverElevation = 8.0;
  
  static const Duration formFieldFocus = fast;
  
  // Loading Animation Configurations
  static const Duration shimmerPeriod = Duration(milliseconds: 1500);
  static const Duration spinnerRotation = Duration(milliseconds: 1000);
  
  // Page Transition Configurations
  static const Duration pageTransition = Duration(milliseconds: 300);
  static const Curve pageTransitionCurve = Curves.easeInOutCubic;
  
  // Stagger Animation Configurations
  static const Duration staggerDelay = Duration(milliseconds: 50);
  static const Duration staggerItemDuration = Duration(milliseconds: 200);
  
  // Success/Error Feedback
  static const Duration successFeedback = slow;
  static const Duration errorShake = Duration(milliseconds: 300);
  static const int errorShakeCount = 3;
  
  // Floating Action Button
  static const Duration fabScale = normal;
  static const Duration fabRotation = Duration(milliseconds: 200);
  
  // Search Bar Animations
  static const Duration searchBarExpand = normal;
  static const Duration searchBarFocus = fast;
  
  // Menu Animations
  static const Duration menuItemAppear = Duration(milliseconds: 100);
  static const Duration menuCategorySwitch = normal;
  
  // Cart Animations
  static const Duration addToCart = Duration(milliseconds: 400);
  static const Duration cartBadgeScale = Duration(milliseconds: 200);
  
  // Order Status Animations
  static const Duration statusChange = slow;
  static const Duration progressIndicator = Duration(milliseconds: 800);
}

/// Animation Configuration Presets
class AnimationPresets {
  /// Button press animation configuration
  static AnimationConfiguration get buttonPress => AnimationConfiguration(
    duration: AppAnimations.buttonPress,
    curve: AppAnimations.standard,
    scale: AppAnimations.buttonPressScale,
  );
  
  /// Card hover animation configuration
  static AnimationConfiguration get cardHover => AnimationConfiguration(
    duration: AppAnimations.cardHover,
    curve: AppAnimations.decelerate,
    elevation: AppAnimations.cardHoverElevation,
  );
  
  /// Form field focus animation configuration
  static AnimationConfiguration get formFieldFocus => AnimationConfiguration(
    duration: AppAnimations.formFieldFocus,
    curve: AppAnimations.standard,
  );
  
  /// Success feedback animation configuration
  static AnimationConfiguration get successFeedback => AnimationConfiguration(
    duration: AppAnimations.successFeedback,
    curve: AppAnimations.bounce,
  );
  
  /// Error shake animation configuration
  static AnimationConfiguration get errorShake => AnimationConfiguration(
    duration: AppAnimations.errorShake,
    curve: Curves.elasticInOut,
    repeatCount: AppAnimations.errorShakeCount,
  );
  
  /// Page transition animation configuration
  static AnimationConfiguration get pageTransition => AnimationConfiguration(
    duration: AppAnimations.pageTransition,
    curve: AppAnimations.pageTransitionCurve,
  );
  
  /// Stagger animation configuration
  static AnimationConfiguration get staggerAnimation => AnimationConfiguration(
    duration: AppAnimations.staggerItemDuration,
    curve: AppAnimations.decelerate,
    delay: AppAnimations.staggerDelay,
  );
}

/// Animation configuration data class
class AnimationConfiguration {
  const AnimationConfiguration({
    required this.duration,
    required this.curve,
    this.scale,
    this.elevation,
    this.repeatCount,
    this.delay,
  });

  final Duration duration;
  final Curve curve;
  final double? scale;
  final double? elevation;
  final int? repeatCount;
  final Duration? delay;
}

/// Responsive animation scaling based on device performance
class ResponsiveAnimations {
  /// Scale animation duration based on device performance
  static Duration scaleDuration(Duration baseDuration, {bool reduceMotion = false}) {
    if (reduceMotion) {
      return Duration(milliseconds: (baseDuration.inMilliseconds * 0.5).round());
    }
    return baseDuration;
  }
  
  /// Get appropriate animation curve for device performance
  static Curve getPerformanceCurve(Curve baseCurve, {bool reduceMotion = false}) {
    if (reduceMotion) {
      return Curves.linear;
    }
    return baseCurve;
  }
  
  /// Check if device should use reduced motion
  static bool shouldReduceMotion(BuildContext context) {
    return MediaQuery.of(context).disableAnimations;
  }
}

/// Animation utility functions
class AnimationUtils {
  /// Create a staggered animation controller
  static AnimationController createStaggeredController({
    required TickerProvider vsync,
    required int itemCount,
    Duration? itemDuration,
    Duration? staggerDelay,
  }) {
    final totalDuration = Duration(
      milliseconds: (itemDuration ?? AppAnimations.staggerItemDuration).inMilliseconds +
          ((staggerDelay ?? AppAnimations.staggerDelay).inMilliseconds * itemCount),
    );
    
    return AnimationController(
      duration: totalDuration,
      vsync: vsync,
    );
  }
  
  /// Create a bounce animation
  static Animation<double> createBounceAnimation(AnimationController controller) {
    return Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: controller,
      curve: Curves.elasticOut,
    ));
  }
  
  /// Create a scale animation
  static Animation<double> createScaleAnimation(
    AnimationController controller, {
    double begin = 0.0,
    double end = 1.0,
    Curve curve = Curves.easeInOut,
  }) {
    return Tween<double>(
      begin: begin,
      end: end,
    ).animate(CurvedAnimation(
      parent: controller,
      curve: curve,
    ));
  }
  
  /// Create a slide animation
  static Animation<Offset> createSlideAnimation(
    AnimationController controller, {
    Offset begin = const Offset(0.0, 1.0),
    Offset end = Offset.zero,
    Curve curve = Curves.easeInOut,
  }) {
    return Tween<Offset>(
      begin: begin,
      end: end,
    ).animate(CurvedAnimation(
      parent: controller,
      curve: curve,
    ));
  }
  
  /// Create a fade animation
  static Animation<double> createFadeAnimation(
    AnimationController controller, {
    double begin = 0.0,
    double end = 1.0,
    Curve curve = Curves.easeInOut,
  }) {
    return Tween<double>(
      begin: begin,
      end: end,
    ).animate(CurvedAnimation(
      parent: controller,
      curve: curve,
    ));
  }
}
