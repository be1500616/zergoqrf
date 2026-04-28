import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'breakpoints.dart';
import 'screen_size.dart';

/// Test utilities for responsive widgets and layouts.
/// 
/// This class provides helper methods and predefined device configurations
/// for testing responsive behavior across different screen sizes and
/// breakpoints. It ensures consistent testing of responsive components.
/// 
/// Example usage:
/// ```dart
/// testWidgets('should show mobile layout on mobile screen', (tester) async {
///   await tester.pumpWidget(
///     ResponsiveTestUtils.wrapWithMediaQuery(
///       child: MyResponsiveWidget(),
///       deviceConfig: ResponsiveTestUtils.mobileDevice,
///     ),
///   );
///   
///   expect(find.byType(MobileLayout), findsOneWidget);
/// });
/// ```
class ResponsiveTestUtils {
  /// Private constructor to prevent instantiation.
  const ResponsiveTestUtils._();

  // Predefined device configurations for testing

  /// iPhone SE (1st generation) - Small mobile device
  static const DeviceConfig iphoneSE = DeviceConfig(
    name: 'iPhone SE',
    size: Size(320, 568),
    devicePixelRatio: 2.0,
    breakpoint: Breakpoint.mobile,
  );

  /// iPhone 12 - Standard mobile device
  static const DeviceConfig iphone12 = DeviceConfig(
    name: 'iPhone 12',
    size: Size(390, 844),
    devicePixelRatio: 3.0,
    breakpoint: Breakpoint.mobile,
  );

  /// iPhone 12 Pro Max - Large mobile device
  static const DeviceConfig iphone12ProMax = DeviceConfig(
    name: 'iPhone 12 Pro Max',
    size: Size(428, 926),
    devicePixelRatio: 3.0,
    breakpoint: Breakpoint.mobileLarge,
  );

  /// iPad Mini - Small tablet device
  static const DeviceConfig ipadMini = DeviceConfig(
    name: 'iPad Mini',
    size: Size(768, 1024),
    devicePixelRatio: 2.0,
    breakpoint: Breakpoint.tablet,
  );

  /// iPad Pro 11" - Standard tablet device
  static const DeviceConfig ipadPro11 = DeviceConfig(
    name: 'iPad Pro 11"',
    size: Size(834, 1194),
    devicePixelRatio: 2.0,
    breakpoint: Breakpoint.tablet,
  );

  /// iPad Pro 12.9" - Large tablet device
  static const DeviceConfig ipadPro129 = DeviceConfig(
    name: 'iPad Pro 12.9"',
    size: Size(1024, 1366),
    devicePixelRatio: 2.0,
    breakpoint: Breakpoint.tablet,
  );

  /// MacBook Air - Standard desktop device
  static const DeviceConfig macbookAir = DeviceConfig(
    name: 'MacBook Air',
    size: Size(1280, 832),
    devicePixelRatio: 2.0,
    breakpoint: Breakpoint.desktop,
  );

  /// MacBook Pro 16" - Large desktop device
  static const DeviceConfig macbookPro16 = DeviceConfig(
    name: 'MacBook Pro 16"',
    size: Size(1728, 1117),
    devicePixelRatio: 2.0,
    breakpoint: Breakpoint.desktopXL,
  );

  /// 4K Monitor - Extra large desktop device
  static const DeviceConfig monitor4K = DeviceConfig(
    name: '4K Monitor',
    size: Size(3840, 2160),
    devicePixelRatio: 1.0,
    breakpoint: Breakpoint.desktopXL,
  );

  // Convenience getters for common device types

  /// Standard mobile device configuration.
  static const DeviceConfig mobileDevice = iphone12;

  /// Large mobile device configuration.
  static const DeviceConfig largeMobileDevice = iphone12ProMax;

  /// Standard tablet device configuration.
  static const DeviceConfig tabletDevice = ipadPro11;

  /// Standard desktop device configuration.
  static const DeviceConfig desktopDevice = macbookAir;

  /// Extra large desktop device configuration.
  static const DeviceConfig xlDesktopDevice = macbookPro16;

  /// All predefined device configurations for comprehensive testing.
  static const List<DeviceConfig> allDevices = [
    iphoneSE,
    iphone12,
    iphone12ProMax,
    ipadMini,
    ipadPro11,
    ipadPro129,
    macbookAir,
    macbookPro16,
    monitor4K,
  ];

  /// Device configurations grouped by breakpoint.
  static const Map<Breakpoint, List<DeviceConfig>> devicesByBreakpoint = {
    Breakpoint.mobile: [iphoneSE, iphone12],
    Breakpoint.mobileLarge: [iphone12ProMax],
    Breakpoint.tablet: [ipadMini, ipadPro11, ipadPro129],
    Breakpoint.desktop: [macbookAir],
    Breakpoint.desktopXL: [macbookPro16, monitor4K],
  };

  /// Wraps a widget with MediaQuery for testing responsive behavior.
  /// 
  /// Args:
  ///   child: The widget to test.
  ///   deviceConfig: The device configuration to simulate.
  ///   orientation: The screen orientation (optional).
  ///   padding: Custom padding for safe areas (optional).
  ///   viewInsets: Custom view insets for keyboard (optional).
  /// 
  /// Returns:
  ///   A MaterialApp with the configured MediaQuery.
  static Widget wrapWithMediaQuery({
    required Widget child,
    required DeviceConfig deviceConfig,
    Orientation orientation = Orientation.portrait,
    EdgeInsets padding = EdgeInsets.zero,
    EdgeInsets viewInsets = EdgeInsets.zero,
  }) {
    final size = orientation == Orientation.portrait
        ? deviceConfig.size
        : Size(deviceConfig.size.height, deviceConfig.size.width);

    return MaterialApp(
      home: MediaQuery(
        data: MediaQueryData.fromView(
          WidgetsBinding.instance.platformDispatcher.views.first,
        ).copyWith(
          size: size,
          devicePixelRatio: deviceConfig.devicePixelRatio,
          padding: padding,
          viewInsets: viewInsets,
        ),
        child: child,
      ),
    );
  }

  /// Creates a ScreenSize instance for testing.
  /// 
  /// Args:
  ///   deviceConfig: The device configuration to simulate.
  ///   orientation: The screen orientation (optional).
  ///   padding: Custom padding for safe areas (optional).
  ///   viewInsets: Custom view insets for keyboard (optional).
  /// 
  /// Returns:
  ///   A ScreenSize instance with the specified configuration.
  static ScreenSize createScreenSize({
    required DeviceConfig deviceConfig,
    Orientation orientation = Orientation.portrait,
    EdgeInsets padding = EdgeInsets.zero,
    EdgeInsets viewInsets = EdgeInsets.zero,
  }) {
    final size = orientation == Orientation.portrait
        ? deviceConfig.size
        : Size(deviceConfig.size.height, deviceConfig.size.width);

    return ScreenSize.fromValues(
      size: size,
      devicePixelRatio: deviceConfig.devicePixelRatio,
      orientation: orientation,
      padding: padding,
      viewInsets: viewInsets,
    );
  }

  /// Tests a widget across all predefined device configurations.
  /// 
  /// This method runs the provided test function for each device
  /// configuration, ensuring comprehensive responsive testing.
  /// 
  /// Args:
  ///   description: Description of the test.
  ///   testFunction: The test function to run for each device.
  ///   devices: List of devices to test (optional, defaults to all devices).
  static void testAcrossDevices(
    String description,
    Future<void> Function(WidgetTester tester, DeviceConfig device) testFunction, {
    List<DeviceConfig> devices = allDevices,
  }) {
    for (final device in devices) {
      testWidgets('$description - ${device.name}', (tester) async {
        await testFunction(tester, device);
      });
    }
  }

  /// Tests a widget across all breakpoints.
  /// 
  /// This method runs the provided test function for one representative
  /// device from each breakpoint, ensuring breakpoint-specific testing.
  /// 
  /// Args:
  ///   description: Description of the test.
  ///   testFunction: The test function to run for each breakpoint.
  static void testAcrossBreakpoints(
    String description,
    Future<void> Function(WidgetTester tester, DeviceConfig device, Breakpoint breakpoint) testFunction,
  ) {
    final representativeDevices = {
      Breakpoint.mobile: mobileDevice,
      Breakpoint.mobileLarge: largeMobileDevice,
      Breakpoint.tablet: tabletDevice,
      Breakpoint.desktop: desktopDevice,
      Breakpoint.desktopXL: xlDesktopDevice,
    };

    for (final entry in representativeDevices.entries) {
      final breakpoint = entry.key;
      final device = entry.value;
      
      testWidgets('$description - ${breakpoint.name}', (tester) async {
        await testFunction(tester, device, breakpoint);
      });
    }
  }

  /// Verifies that a breakpoint is correctly detected for a device.
  /// 
  /// Args:
  ///   tester: The widget tester.
  ///   deviceConfig: The device configuration to test.
  ///   expectedBreakpoint: The expected breakpoint for the device.
  static Future<void> verifyBreakpoint(
    WidgetTester tester,
    DeviceConfig deviceConfig,
    Breakpoint expectedBreakpoint,
  ) async {
    late Breakpoint actualBreakpoint;
    
    await tester.pumpWidget(
      wrapWithMediaQuery(
        deviceConfig: deviceConfig,
        child: Builder(
          builder: (context) {
            actualBreakpoint = BreakpointConfig.getCurrentBreakpoint(context);
            return const SizedBox.shrink();
          },
        ),
      ),
    );

    expect(actualBreakpoint, equals(expectedBreakpoint));
  }
}

/// Configuration for a test device.
/// 
/// This class encapsulates the properties of a device for testing
/// responsive behavior, including screen size, pixel ratio, and
/// expected breakpoint.
class DeviceConfig {
  /// Creates a device configuration.
  /// 
  /// Args:
  ///   name: Human-readable name of the device.
  ///   size: Screen size in logical pixels.
  ///   devicePixelRatio: Device pixel ratio.
  ///   breakpoint: Expected breakpoint for this device.
  const DeviceConfig({
    required this.name,
    required this.size,
    required this.devicePixelRatio,
    required this.breakpoint,
  });

  /// Human-readable name of the device.
  final String name;

  /// Screen size in logical pixels.
  final Size size;

  /// Device pixel ratio.
  final double devicePixelRatio;

  /// Expected breakpoint for this device.
  final Breakpoint breakpoint;

  /// Screen width in logical pixels.
  double get width => size.width;

  /// Screen height in logical pixels.
  double get height => size.height;

  /// Whether this device represents a mobile breakpoint.
  bool get isMobile => breakpoint == Breakpoint.mobile || breakpoint == Breakpoint.mobileLarge;

  /// Whether this device represents a tablet breakpoint.
  bool get isTablet => breakpoint == Breakpoint.tablet;

  /// Whether this device represents a desktop breakpoint.
  bool get isDesktop => breakpoint == Breakpoint.desktop || breakpoint == Breakpoint.desktopXL;

  @override
  String toString() => 'DeviceConfig($name, ${size.width}x${size.height}, $breakpoint)';

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is DeviceConfig &&
          runtimeType == other.runtimeType &&
          name == other.name &&
          size == other.size &&
          devicePixelRatio == other.devicePixelRatio &&
          breakpoint == other.breakpoint;

  @override
  int get hashCode => Object.hash(name, size, devicePixelRatio, breakpoint);
}
