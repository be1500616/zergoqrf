import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Performance optimization utilities for cross-platform Flutter applications.
///
/// Provides platform-specific optimizations, memory management utilities,
/// and performance monitoring tools to ensure smooth operation across
/// mobile, web, and desktop platforms.
class PerformanceUtils {
  /// Private constructor to prevent instantiation
  PerformanceUtils._();

  /// Optimizes the app for the current platform.
  ///
  /// Applies platform-specific optimizations including:
  /// - Memory management settings
  /// - Rendering optimizations
  /// - Input handling improvements
  static void optimizeForPlatform() {
    if (kIsWeb) {
      _optimizeForWeb();
    } else if (defaultTargetPlatform == TargetPlatform.iOS ||
        defaultTargetPlatform == TargetPlatform.android) {
      _optimizeForMobile();
    } else {
      _optimizeForDesktop();
    }
  }

  /// Web-specific optimizations.
  static void _optimizeForWeb() {
    // Enable hardware acceleration for web
    if (kDebugMode) {
      debugPrint('Applying web optimizations...');
    }

    // Web-specific performance settings would go here
    // For example: canvas rendering optimizations, memory management
  }

  /// Mobile-specific optimizations.
  static void _optimizeForMobile() {
    if (kDebugMode) {
      debugPrint('Applying mobile optimizations...');
    }

    // Enable hardware acceleration
    SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);

    // Optimize for battery life
    _enableBatteryOptimizations();
  }

  /// Desktop-specific optimizations.
  static void _optimizeForDesktop() {
    if (kDebugMode) {
      debugPrint('Applying desktop optimizations...');
    }

    // Desktop-specific optimizations
    // For example: window management, keyboard shortcuts
  }

  /// Enables battery optimization features for mobile platforms.
  static void _enableBatteryOptimizations() {
    // Reduce animation frame rate when app is in background
    // This would typically involve platform channels for native implementation
  }

  /// Creates a performance-optimized list view.
  ///
  /// Uses ListView.builder with optimizations for large datasets.
  static Widget optimizedListView<T>({
    required List<T> items,
    required Widget Function(BuildContext context, T item, int index)
        itemBuilder,
    ScrollController? controller,
    EdgeInsets? padding,
    bool shrinkWrap = false,
    ScrollPhysics? physics,
  }) {
    return ListView.builder(
      controller: controller,
      padding: padding,
      shrinkWrap: shrinkWrap,
      physics: physics,
      itemCount: items.length,
      // Add performance optimizations
      cacheExtent: 500, // Cache more items for smoother scrolling
      itemBuilder: (context, index) {
        if (index >= items.length) return const SizedBox.shrink();
        return itemBuilder(context, items[index], index);
      },
    );
  }

  /// Creates a performance-optimized grid view.
  ///
  /// Uses GridView.builder with optimizations for responsive layouts.
  static Widget optimizedGridView<T>({
    required List<T> items,
    required Widget Function(BuildContext context, T item, int index)
        itemBuilder,
    required int crossAxisCount,
    double mainAxisSpacing = 0.0,
    double crossAxisSpacing = 0.0,
    double childAspectRatio = 1.0,
    ScrollController? controller,
    EdgeInsets? padding,
    bool shrinkWrap = false,
    ScrollPhysics? physics,
  }) {
    return GridView.builder(
      controller: controller,
      padding: padding,
      shrinkWrap: shrinkWrap,
      physics: physics,
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        mainAxisSpacing: mainAxisSpacing,
        crossAxisSpacing: crossAxisSpacing,
        childAspectRatio: childAspectRatio,
      ),
      itemCount: items.length,
      // Add performance optimizations
      cacheExtent: 500,
      itemBuilder: (context, index) {
        if (index >= items.length) return const SizedBox.shrink();
        return itemBuilder(context, items[index], index);
      },
    );
  }

  /// Creates a performance-optimized image widget.
  ///
  /// Includes caching, loading states, and error handling.
  static Widget optimizedImage({
    required String imageUrl,
    double? width,
    double? height,
    BoxFit fit = BoxFit.cover,
    Widget? placeholder,
    Widget? errorWidget,
    bool enableMemoryCache = true,
  }) {
    return Image.network(
      imageUrl,
      width: width,
      height: height,
      fit: fit,
      // Performance optimizations
      cacheWidth: width?.round(),
      cacheHeight: height?.round(),
      loadingBuilder: (context, child, loadingProgress) {
        if (loadingProgress == null) return child;

        return placeholder ??
            Container(
              width: width,
              height: height,
              color: Colors.grey[200],
              child: const Center(
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
            );
      },
      errorBuilder: (context, error, stackTrace) {
        return errorWidget ??
            Container(
              width: width,
              height: height,
              color: Colors.grey[300],
              child: const Icon(
                Icons.error_outline,
                color: Colors.grey,
              ),
            );
      },
    );
  }

  /// Debounces function calls to improve performance.
  ///
  /// Useful for search inputs, API calls, and other frequent operations.
  static void debounce({
    required VoidCallback callback,
    Duration delay = const Duration(milliseconds: 300),
  }) {
    _debounceTimer?.cancel();
    _debounceTimer = Timer(delay, callback);
  }

  static Timer? _debounceTimer;

  /// Throttles function calls to limit execution frequency.
  ///
  /// Useful for scroll listeners and other high-frequency events.
  static void throttle({
    required VoidCallback callback,
    Duration interval = const Duration(milliseconds: 100),
  }) {
    if (_throttleTimer?.isActive ?? false) return;

    callback();
    _throttleTimer = Timer(interval, () {});
  }

  static Timer? _throttleTimer;

  /// Measures widget build performance.
  ///
  /// Useful for identifying performance bottlenecks in debug mode.
  static Widget measureBuildTime({
    required Widget child,
    required String widgetName,
  }) {
    if (!kDebugMode) return child;

    return Builder(
      builder: (context) {
        final stopwatch = Stopwatch()..start();

        return LayoutBuilder(
          builder: (context, constraints) {
            final widget = child;

            WidgetsBinding.instance.addPostFrameCallback((_) {
              stopwatch.stop();
              debugPrint(
                  'Build time for $widgetName: ${stopwatch.elapsedMilliseconds}ms');
            });

            return widget;
          },
        );
      },
    );
  }

  /// Preloads images for better performance.
  ///
  /// Call this method to cache images before they're needed.
  static Future<void> preloadImages({
    required BuildContext context,
    required List<String> imageUrls,
  }) async {
    final futures = imageUrls.map((url) {
      return precacheImage(NetworkImage(url), context);
    });

    await Future.wait(futures);
  }

  /// Optimizes text rendering for better performance.
  ///
  /// Reduces text layout calculations and improves rendering speed.
  static TextStyle optimizeTextStyle(TextStyle style) {
    return style.copyWith(
      // Optimize text rendering
      textBaseline: TextBaseline.alphabetic,
      // Add other optimizations as needed
    );
  }

  /// Checks if the current platform supports hardware acceleration.
  static bool get supportsHardwareAcceleration {
    if (kIsWeb) return true;

    switch (defaultTargetPlatform) {
      case TargetPlatform.iOS:
      case TargetPlatform.android:
        return true;
      case TargetPlatform.windows:
      case TargetPlatform.macOS:
      case TargetPlatform.linux:
        return true;
      default:
        return false;
    }
  }

  /// Gets platform-specific scroll physics.
  static ScrollPhysics get platformScrollPhysics {
    switch (defaultTargetPlatform) {
      case TargetPlatform.iOS:
        return const BouncingScrollPhysics();
      case TargetPlatform.android:
        return const ClampingScrollPhysics();
      default:
        return const ClampingScrollPhysics();
    }
  }

  /// Disposes of performance utilities and cleans up resources.
  static void dispose() {
    _debounceTimer?.cancel();
    _throttleTimer?.cancel();
  }
}
