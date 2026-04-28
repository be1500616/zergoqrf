/// Widget tests for HomeScreen component.
///
/// Tests the UI behavior and interactions of the HomeScreen
/// following Flutter widget testing best practices.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:zergo_frontend/main.dart';

import '../helpers/test_helpers.dart';

void main() {
  group('HomeScreen Widget Tests', () {
    setUp(() {
      Get.reset();
    });

    tearDown(() {
      Get.reset();
    });

    testWidgets('renders correctly with all expected elements', (tester) async {
      // Arrange & Act
      await WidgetTestHelpers.pumpWidgetWithGetX(
        tester,
        const HomeScreen(),
      );

      // Assert - Check main structural elements
      expect(find.byType(Scaffold), findsOneWidget);
      expect(find.byType(AppBar), findsOneWidget);
      expect(find.byType(Center), findsOneWidget);
      expect(find.byType(Column), findsOneWidget);

      // Assert - Check text content
      expect(find.text('ZERGO QR'), findsOneWidget); // AppBar title
      expect(find.text('Welcome to ZERGO QR'), findsOneWidget);
      expect(find.text('Check session'), findsOneWidget);

      // Assert - Check interactive elements
      expect(
          find.widgetWithText(ElevatedButton, 'Check session'), findsOneWidget);
    });

    testWidgets('has correct layout structure', (tester) async {
      // Arrange & Act
      await WidgetTestHelpers.pumpWidgetWithGetX(
        tester,
        const HomeScreen(),
      );

      // Assert - Check layout structure
      final column = tester.widget<Column>(find.byType(Column));
      expect(column.mainAxisAlignment, MainAxisAlignment.center);
      expect(column.children.length >= 2, true);
    });

    testWidgets('displays correct app bar title', (tester) async {
      // Arrange & Act
      await WidgetTestHelpers.pumpWidgetWithGetX(
        tester,
        const HomeScreen(),
      );

      // Assert
      final appBar = tester.widget<AppBar>(find.byType(AppBar));
      final title = tester.widget<Text>(find.descendant(
        of: find.byWidget(appBar),
        matching: find.byType(Text),
      ));
      expect(title.data, 'ZERGO QR');
    });

    testWidgets('welcome text is centered', (tester) async {
      // Arrange & Act
      await WidgetTestHelpers.pumpWidgetWithGetX(
        tester,
        const HomeScreen(),
      );

      // Assert
      final center = find.byType(Center);
      final welcomeText = find.text('Welcome to ZERGO QR');

      expect(
          find.descendant(
            of: center,
            matching: welcomeText,
          ),
          findsOneWidget);
    });

    testWidgets('button has correct text and is functional', (tester) async {
      // Arrange & Act
      await WidgetTestHelpers.pumpWidgetWithGetX(
        tester,
        const HomeScreen(),
      );

      // Assert
      final buttonFinder = find.widgetWithText(ElevatedButton, 'Check session');
      final button = tester.widget<ElevatedButton>(buttonFinder);

      expect(button.onPressed, isNotNull);

      // Check button text
      final buttonText = find.descendant(
        of: find.byType(ElevatedButton),
        matching: find.text('Check session'),
      );
      expect(buttonText, findsOneWidget);
    });

    group('Accessibility Tests', () {
      testWidgets('meets accessibility guidelines', (tester) async {
        // Arrange
        final SemanticsHandle handle = tester.ensureSemantics();

        // Act
        await WidgetTestHelpers.pumpWidgetWithGetX(
          tester,
          const HomeScreen(),
        );

        // Assert
        await expectLater(tester, meetsGuideline(textContrastGuideline));
        await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));

        handle.dispose();
      });
    });

    group('Responsive Layout Tests', () {
      testWidgets('adapts to different screen sizes', (tester) async {
        // Test with phone size
        await tester.binding.setSurfaceSize(const Size(400, 800));

        await WidgetTestHelpers.pumpWidgetWithGetX(
          tester,
          const HomeScreen(),
        );

        expect(find.byType(HomeScreen), findsOneWidget);
        expect(find.text('Welcome to ZERGO QR'), findsOneWidget);

        // Test with tablet size
        await tester.binding.setSurfaceSize(const Size(800, 1024));
        await tester.pumpAndSettle();

        expect(find.byType(HomeScreen), findsOneWidget);
        expect(find.text('Welcome to ZERGO QR'), findsOneWidget);

        // Reset to default size
        await tester.binding.setSurfaceSize(null);
      });
    });

    group('Widget State Tests', () {
      testWidgets('maintains state correctly', (tester) async {
        // Arrange
        await WidgetTestHelpers.pumpWidgetWithGetX(
          tester,
          const HomeScreen(),
        );

        // Verify initial state
        expect(find.text('Welcome to ZERGO QR'), findsOneWidget);
        expect(find.text('Check session'), findsOneWidget);

        // Act - Rebuild widget
        await tester.pumpAndSettle();

        // Assert - State is maintained
        expect(find.text('Welcome to ZERGO QR'), findsOneWidget);
        expect(find.text('Check session'), findsOneWidget);
      });
    });
  });
}
