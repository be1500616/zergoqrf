/// Integration tests for complete app flows.
///
/// Tests end-to-end user journeys and app integration
/// following Flutter integration testing best practices.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:zergo_frontend/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('App Integration Tests', () {
    testWidgets('complete app launch flow', (tester) async {
      // Arrange
      app.main();
      await tester.pumpAndSettle();

      // Assert - App launches successfully
      expect(find.byType(app.ZergoApp), findsOneWidget);
      expect(find.text('Welcome to ZERGO QR'), findsOneWidget);

      // Assert - Essential UI elements are present
      expect(find.text('ZERGO QR'), findsOneWidget); // AppBar title
      expect(find.text('Check session'), findsOneWidget); // Button
      expect(find.byType(ElevatedButton), findsOneWidget);
    });

    testWidgets('app navigation and interaction flow', (tester) async {
      // Arrange
      app.main();
      await tester.pumpAndSettle();

      // Act - Interact with session check button
      final sessionButton = find.text('Check session');
      expect(sessionButton, findsOneWidget);

      await tester.tap(sessionButton);
      await tester.pumpAndSettle();

      // Assert - App handles interaction without crashes
      expect(find.byType(app.ZergoApp), findsOneWidget);
    });

    testWidgets('app UI responsiveness', (tester) async {
      // Arrange
      app.main();
      await tester.pumpAndSettle();

      // Test portrait orientation
      expect(find.text('Welcome to ZERGO QR'), findsOneWidget);
      expect(find.text('Check session'), findsOneWidget);

      // Act - Rotate to landscape
      await tester.binding.setSurfaceSize(const Size(800, 400));
      await tester.pumpAndSettle();

      // Assert - UI still works in landscape
      expect(find.text('Welcome to ZERGO QR'), findsOneWidget);
      expect(find.text('Check session'), findsOneWidget);

      // Reset orientation
      await tester.binding.setSurfaceSize(null);
      await tester.pumpAndSettle();
    });

    group('Performance Tests', () {
      testWidgets('app starts within acceptable time', (tester) async {
        final stopwatch = Stopwatch()..start();

        app.main();
        await tester.pumpAndSettle();

        stopwatch.stop();

        // Assert app starts within 5 seconds
        expect(stopwatch.elapsedMilliseconds, lessThan(5000));

        // Verify UI is ready
        expect(find.text('Welcome to ZERGO QR'), findsOneWidget);
      });

      testWidgets('button interactions are responsive', (tester) async {
        app.main();
        await tester.pumpAndSettle();

        final stopwatch = Stopwatch()..start();

        await tester.tap(find.text('Check session'));
        await tester.pumpAndSettle();

        stopwatch.stop();

        // Assert interaction completes within reasonable time
        expect(stopwatch.elapsedMilliseconds, lessThan(2000));
      });
    });

    group('Stability Tests', () {
      testWidgets('app handles multiple interactions gracefully',
          (tester) async {
        app.main();
        await tester.pumpAndSettle();

        // Perform multiple button taps
        for (int i = 0; i < 3; i++) {
          await tester.tap(find.text('Check session'));
          await tester.pumpAndSettle();

          // Verify app doesn't crash
          expect(find.byType(app.ZergoApp), findsOneWidget);
        }
      });

      testWidgets('app maintains state across rebuilds', (tester) async {
        app.main();
        await tester.pumpAndSettle();

        // Verify initial state
        expect(find.text('Welcome to ZERGO QR'), findsOneWidget);

        // Trigger rebuild
        await tester.pumpAndSettle();

        // Verify state is maintained
        expect(find.text('Welcome to ZERGO QR'), findsOneWidget);
        expect(find.text('Check session'), findsOneWidget);
      });
    });

    group('Accessibility Integration Tests', () {
      testWidgets('app is accessible', (tester) async {
        final SemanticsHandle handle = tester.ensureSemantics();

        app.main();
        await tester.pumpAndSettle();

        // Verify semantic information is available
        expect(find.byType(app.HomeScreen), findsOneWidget);

        // Test basic accessibility guidelines
        await expectLater(tester, meetsGuideline(textContrastGuideline));
        await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));

        handle.dispose();
      });
    });
  });
}
