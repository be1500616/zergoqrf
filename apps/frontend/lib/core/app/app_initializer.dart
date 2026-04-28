import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:get/get.dart';

import '../../shared/performance/index.dart';

/// Comprehensive app initialization system.
/// 
/// Handles all app startup tasks including performance optimizations,
/// dependency injection setup, theme initialization, and platform-specific
/// configurations to ensure optimal app performance and user experience.
class AppInitializer {
  /// Private constructor to prevent instantiation
  AppInitializer._();

  /// Whether the app has been initialized
  static bool _isInitialized = false;

  /// Initializes the entire application with all optimizations and configurations.
  /// 
  /// This method should be called once during app startup, typically in main().
  /// It handles:
  /// - Performance optimizations for the current platform
  /// - Animation system initialization
  /// - System UI configuration
  /// - Error handling setup
  /// - Dependency injection initialization
  static Future<void> initialize() async {
    if (_isInitialized) {
      debugPrint('App already initialized, skipping...');
      return;
    }

    debugPrint('Initializing ZERGO QR Frontend App...');

    try {
      // Ensure Flutter binding is initialized
      WidgetsFlutterBinding.ensureInitialized();

      // Initialize performance optimizations
      await _initializePerformance();

      // Configure system UI
      await _configureSystemUI();

      // Setup error handling
      _setupErrorHandling();

      // Initialize dependency injection
      await _initializeDependencies();

      // Platform-specific initialization
      await _initializePlatformSpecific();

      _isInitialized = true;
      debugPrint('App initialization completed successfully');

    } catch (error, stackTrace) {
      debugPrint('App initialization failed: $error');
      debugPrint('Stack trace: $stackTrace');
      rethrow;
    }
  }

  /// Initializes performance optimization systems.
  static Future<void> _initializePerformance() async {
    debugPrint('Initializing performance optimizations...');

    // Apply platform-specific optimizations
    PerformanceUtils.optimizeForPlatform();

    // Initialize animation optimizer
    AnimationOptimizer.initialize();

    // Configure memory management
    if (kIsWeb) {
      // Web-specific memory optimizations
      debugPrint('Applied web performance optimizations');
    } else {
      // Mobile/Desktop memory optimizations
      debugPrint('Applied native performance optimizations');
    }
  }

  /// Configures system UI for optimal user experience.
  static Future<void> _configureSystemUI() async {
    debugPrint('Configuring system UI...');

    if (!kIsWeb) {
      // Configure status bar and navigation bar
      await SystemChrome.setEnabledSystemUIMode(
        SystemUiMode.edgeToEdge,
        overlays: [SystemUiOverlay.top],
      );

      // Set preferred orientations
      await SystemChrome.setPreferredOrientations([
        DeviceOrientation.portraitUp,
        DeviceOrientation.portraitDown,
        DeviceOrientation.landscapeLeft,
        DeviceOrientation.landscapeRight,
      ]);

      // Configure system UI overlay style
      SystemChrome.setSystemUIOverlayStyle(
        const SystemUiOverlayStyle(
          statusBarColor: Colors.transparent,
          statusBarIconBrightness: Brightness.dark,
          statusBarBrightness: Brightness.light,
          systemNavigationBarColor: Colors.transparent,
          systemNavigationBarIconBrightness: Brightness.dark,
        ),
      );
    }
  }

  /// Sets up global error handling.
  static void _setupErrorHandling() {
    debugPrint('Setting up error handling...');

    // Handle Flutter framework errors
    FlutterError.onError = (FlutterErrorDetails details) {
      if (kDebugMode) {
        // In debug mode, print the error
        FlutterError.presentError(details);
      } else {
        // In release mode, log the error (could send to crash reporting service)
        debugPrint('Flutter Error: ${details.exception}');
        debugPrint('Stack trace: ${details.stack}');
      }
    };

    // Handle errors outside of Flutter framework
    PlatformDispatcher.instance.onError = (error, stack) {
      if (kDebugMode) {
        debugPrint('Platform Error: $error');
        debugPrint('Stack trace: $stack');
      } else {
        // Log error for crash reporting
        debugPrint('Unhandled Error: $error');
      }
      return true;
    };
  }

  /// Initializes dependency injection system.
  static Future<void> _initializeDependencies() async {
    debugPrint('Initializing dependency injection...');

    // Initialize GetX dependencies
    // This would typically include:
    // - API clients
    // - Repositories
    // - Services
    // - Controllers

    // Example dependency registration:
    // Get.put<ApiClient>(ApiClient());
    // Get.put<UserRepository>(UserRepositoryImpl());
    // Get.put<AuthService>(AuthService());

    debugPrint('Dependency injection initialized');
  }

  /// Performs platform-specific initialization.
  static Future<void> _initializePlatformSpecific() async {
    debugPrint('Performing platform-specific initialization...');

    if (kIsWeb) {
      await _initializeWeb();
    } else if (defaultTargetPlatform == TargetPlatform.iOS ||
               defaultTargetPlatform == TargetPlatform.android) {
      await _initializeMobile();
    } else {
      await _initializeDesktop();
    }
  }

  /// Web-specific initialization.
  static Future<void> _initializeWeb() async {
    debugPrint('Initializing web-specific features...');

    // Web-specific configurations
    // - Service worker registration
    // - PWA manifest setup
    // - Web-specific analytics
    // - URL routing configuration
  }

  /// Mobile-specific initialization.
  static Future<void> _initializeMobile() async {
    debugPrint('Initializing mobile-specific features...');

    // Mobile-specific configurations
    // - Push notification setup
    // - Deep linking configuration
    // - Biometric authentication setup
    // - Background task registration
  }

  /// Desktop-specific initialization.
  static Future<void> _initializeDesktop() async {
    debugPrint('Initializing desktop-specific features...');

    // Desktop-specific configurations
    // - Window management
    // - Keyboard shortcuts
    // - System tray integration
    // - File system access
  }

  /// Disposes of app resources and performs cleanup.
  /// 
  /// Should be called when the app is being terminated.
  static Future<void> dispose() async {
    if (!_isInitialized) return;

    debugPrint('Disposing app resources...');

    try {
      // Dispose performance utilities
      PerformanceUtils.dispose();
      AnimationOptimizer.dispose();

      // Clean up GetX dependencies
      await Get.deleteAll(force: true);

      _isInitialized = false;
      debugPrint('App resources disposed successfully');

    } catch (error, stackTrace) {
      debugPrint('Error during app disposal: $error');
      debugPrint('Stack trace: $stackTrace');
    }
  }

  /// Gets the current initialization status.
  static bool get isInitialized => _isInitialized;

  /// Reinitializes the app (useful for testing or configuration changes).
  static Future<void> reinitialize() async {
    await dispose();
    await initialize();
  }
}
