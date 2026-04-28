/// Test configuration for Flutter tests.
///
/// This file configures the test environment and provides
/// global setup for all Flutter tests.
library;

import 'dart:async';
import 'package:golden_toolkit/golden_toolkit.dart';

/// Configure test environment
Future<void> testExecutable(FutureOr<void> Function() testMain) async {
  return GoldenToolkit.runWithConfiguration(
    () async {
      // Load fonts for golden tests
      await loadAppFonts();

      // Run the actual tests
      await testMain();
    },
    config: GoldenToolkitConfiguration(
      // Enable skipping on CI if needed
      skipGoldenAssertion: () => false,

      // Configure default device for golden tests
      defaultDevices: const [
        Device.phone,
        Device.tabletPortrait,
      ],
    ),
  );
}
