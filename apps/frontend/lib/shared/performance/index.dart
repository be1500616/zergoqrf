/// Performance optimization utilities for Flutter applications.
/// 
/// This library provides comprehensive performance optimization tools
/// including cross-platform optimizations, animation management,
/// memory optimization, and performance monitoring utilities.
/// 
/// Key features:
/// - Platform-specific optimizations for web, mobile, and desktop
/// - Animation performance optimization and adaptive settings
/// - Memory management and resource cleanup utilities
/// - Performance monitoring and debugging tools
/// - Responsive design performance enhancements
/// 
/// Usage:
/// ```dart
/// import 'package:zergo_frontend/shared/performance/index.dart';
/// 
/// // Initialize performance optimizations
/// PerformanceUtils.optimizeForPlatform();
/// AnimationOptimizer.initialize();
/// 
/// // Use optimized widgets
/// PerformanceUtils.optimizedListView(
///   items: items,
///   itemBuilder: (context, item, index) => ItemWidget(item),
/// );
/// ```
library;

export 'animation_optimizer.dart';
export 'performance_utils.dart';
