/// Golden tests for UI components.
///
/// Tests visual appearance and layout of UI components
/// to catch unintended visual regressions.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:golden_toolkit/golden_toolkit.dart';
import 'package:zergo_frontend/main.dart';

void main() {
  group('Golden Tests', () {
    setUpAll(() async {
      // Load fonts for golden tests
      await loadAppFonts();
    });

    group('HomeScreen Golden Tests', () {
      testGoldens('HomeScreen renders correctly', (tester) async {
        // Arrange
        final homeScreen = await tester.pumpWidgetBuilder(
          const HomeScreen(),
          wrapper: materialAppWrapper(),
        );

        // Act & Assert
        await screenMatchesGolden(tester, 'home_screen_default');
      });

      testGoldens('HomeScreen renders on different screen sizes',
          (tester) async {
        final builder = DeviceBuilder()
          ..overrideDevicesForAllScenarios(devices: [
            Device.phone,
            Device.iphone11,
            Device.tabletPortrait,
            Device.tabletLandscape,
          ])
          ..addScenario(
            name: 'Home Screen',
            widget: const HomeScreen(),
          );

        await tester.pumpDeviceBuilder(builder);
        await screenMatchesGolden(tester, 'home_screen_multiple_devices');
      });

      testGoldens('HomeScreen with different themes', (tester) async {
        final builder = GoldenBuilder.grid(
          columns: 2,
          widthToHeightRatio: 1,
        )
          ..addScenario(
            'Light Theme',
            MaterialApp(
              theme: ThemeData.light(),
              home: const HomeScreen(),
            ),
          )
          ..addScenario(
            'Dark Theme',
            MaterialApp(
              theme: ThemeData.dark(),
              home: const HomeScreen(),
            ),
          );

        await tester.pumpWidgetBuilder(builder.build());
        await screenMatchesGolden(tester, 'home_screen_themes');
      });

      testGoldens('HomeScreen button states', (tester) async {
        final builder = GoldenBuilder.grid(
          columns: 2,
          widthToHeightRatio: 1.5,
        )
          ..addScenario(
            'Normal Button',
            MaterialApp(
              home: Scaffold(
                body: Center(
                  child: ElevatedButton(
                    onPressed: () {},
                    child: const Text('Check session'),
                  ),
                ),
              ),
            ),
          )
          ..addScenario(
            'Disabled Button',
            const MaterialApp(
              home: Scaffold(
                body: Center(
                  child: ElevatedButton(
                    onPressed: null,
                    child: Text('Check session'),
                  ),
                ),
              ),
            ),
          );

        await tester.pumpWidgetBuilder(builder.build());
        await screenMatchesGolden(tester, 'home_screen_button_states');
      });
    });

    group('App Bar Golden Tests', () {
      testGoldens('AppBar renders correctly', (tester) async {
        await tester.pumpWidgetBuilder(
          Scaffold(
            appBar: AppBar(title: const Text('ZERGO QR')),
            body: const Center(child: Text('Content')),
          ),
          wrapper: materialAppWrapper(),
        );

        await screenMatchesGolden(tester, 'app_bar_default');
      });

      testGoldens('AppBar with different styles', (tester) async {
        final builder = GoldenBuilder.column()
          ..addScenario(
            'Default AppBar',
            MaterialApp(
              home: Scaffold(
                appBar: AppBar(title: const Text('ZERGO QR')),
                body: const SizedBox.shrink(),
              ),
            ),
          )
          ..addScenario(
            'Colored AppBar',
            MaterialApp(
              home: Scaffold(
                appBar: AppBar(
                  title: const Text('ZERGO QR'),
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                ),
                body: const SizedBox.shrink(),
              ),
            ),
          );

        await tester.pumpWidgetBuilder(builder.build());
        await screenMatchesGolden(tester, 'app_bar_styles');
      });
    });

    group('Layout Golden Tests', () {
      testGoldens('Center layout with column', (tester) async {
        await tester.pumpWidgetBuilder(
          const MaterialApp(
            home: Scaffold(
              body: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text('Welcome to ZERGO QR'),
                    SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: null,
                      child: Text('Check session'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );

        await screenMatchesGolden(tester, 'center_column_layout');
      });
    });

    group('Responsive Golden Tests', () {
      testGoldens('Responsive layout across devices', (tester) async {
        final builder = DeviceBuilder()
          ..overrideDevicesForAllScenarios(devices: [
            Device.phone,
            Device.tabletPortrait,
            Device.tabletLandscape,
          ])
          ..addScenario(
            name: 'Responsive Layout',
            widget: const HomeScreen(),
          );

        await tester.pumpDeviceBuilder(builder);
        await screenMatchesGolden(tester, 'responsive_layout');
      });
    });

    group('Accessibility Golden Tests', () {
      testGoldens('High contrast theme', (tester) async {
        await tester.pumpWidgetBuilder(
          const HomeScreen(),
          wrapper: materialAppWrapper(
            theme: ThemeData.from(
              colorScheme: const ColorScheme.highContrastLight(),
              useMaterial3: true,
            ),
          ),
        );

        await screenMatchesGolden(tester, 'high_contrast_theme');
      });

      testGoldens('Large text scale', (tester) async {
        await tester.pumpWidgetBuilder(
          const MediaQuery(
            data: MediaQueryData(
              textScaler: TextScaler.linear(2.0),
            ),
            child: HomeScreen(),
          ),
          wrapper: materialAppWrapper(),
        );

        await screenMatchesGolden(tester, 'large_text_scale');
      });
    });
  });
}
