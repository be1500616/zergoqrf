/// Unit tests for main app components.
///
/// Tests the core application setup, routing, and initialization
/// following clean architecture testing principles.
library;

import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:zergo_frontend/main.dart';

import '../helpers/test_helpers.dart';

void main() {
  setUpAll(() async {
    TestWidgetsFlutterBinding.ensureInitialized();
    // Mock SharedPreferences for plugins used by Supabase
    SharedPreferences.setMockInitialValues({});
    await dotenv.load(fileName: '.env');
    final url = dotenv.env['SUPABASE_URL'] ?? '';
    final anon = dotenv.env['SUPABASE_ANON_KEY'] ?? '';
    if (url.isNotEmpty && anon.isNotEmpty) {
      await Supabase.initialize(url: url, anonKey: anon);
    }
  });
  group('ZergoApp Tests', () {
    setUp(() {
      // Reset GetX state before each test
      Get.reset();
    });

    tearDown(() {
      // Clean up after each test
      Get.reset();
    });

    testWidgets('should create app with correct structure', (tester) async {
      // Arrange & Act
      await tester.pumpWidget(const ZergoApp());
      await tester.pumpAndSettle();

      // Assert
      expect(find.byType(ZergoApp), findsOneWidget);
    });

    testWidgets('should display home screen on initial route', (tester) async {
      // Arrange & Act
      await tester.pumpWidget(const ZergoApp());
      await tester.pumpAndSettle();

      // Assert
      expect(find.byType(HomeScreen), findsOneWidget);
      expect(find.text('Welcome to ZERGO QR'), findsOneWidget);
    });
  });

  group('HomeScreen Unit Tests', () {
    setUp(() {
      Get.reset();
    });

    tearDown(() {
      Get.reset();
    });

    testWidgets('should display welcome message and check session button',
        (tester) async {
      // Arrange & Act
      await WidgetTestHelpers.pumpWidgetWithGetX(
        tester,
        const HomeScreen(),
      );

      // Assert
      WidgetTestHelpers.expectWidgetVisible(
          WidgetTestHelpers.findTextWidget('Welcome to ZERGO QR'));
      WidgetTestHelpers.expectWidgetVisible(
          WidgetTestHelpers.findTextWidget('Check session'));
    });

    testWidgets('should have app bar with title', (tester) async {
      // Arrange & Act
      await WidgetTestHelpers.pumpWidgetWithGetX(
        tester,
        const HomeScreen(),
      );

      // Assert
      WidgetTestHelpers.expectWidgetVisible(
          WidgetTestHelpers.findByType<AppBar>());
      WidgetTestHelpers.expectWidgetVisible(
          WidgetTestHelpers.findTextWidget('ZERGO QR'));
    });

    testWidgets('should display session button', (tester) async {
      // Arrange & Act
      await WidgetTestHelpers.pumpWidgetWithGetX(
        tester,
        const HomeScreen(),
      );

      // Assert
      final sessionButton =
          find.widgetWithText(ElevatedButton, 'Check session');
      expect(sessionButton, findsOneWidget);
    });

    testWidgets('button should be functional', (tester) async {
      // Arrange
      await WidgetTestHelpers.pumpWidgetWithGetX(
        tester,
        const HomeScreen(),
      );

      // Act
      final button = find.byType(ElevatedButton);
      expect(button, findsOneWidget);

      // Verify button is tappable
      final elevatedButton = tester.widget<ElevatedButton>(button);
      expect(elevatedButton.onPressed, isNotNull);
    });
  });

  group('Test Data Factory Tests', () {
    test('should create valid user data', () {
      // Act
      final userData = TestDataFactory.createUserData();

      // Assert
      expect(userData, isA<Map<String, dynamic>>());
      expect(userData['id'], isNotNull);
      expect(userData['email'], isNotNull);
      expect(userData['phone'], isNotNull);
      expect(userData['is_active'], isTrue);
    });

    test('should create user data with custom values', () {
      // Arrange
      const customId = 'custom-id';
      const customEmail = 'custom@test.com';

      // Act
      final userData = TestDataFactory.createUserData(
        id: customId,
        email: customEmail,
      );

      // Assert
      expect(userData['id'], equals(customId));
      expect(userData['email'], equals(customEmail));
    });

    test('should create valid restaurant data', () {
      // Act
      final restaurantData = TestDataFactory.createRestaurantData();

      // Assert
      expect(restaurantData, isA<Map<String, dynamic>>());
      expect(restaurantData['id'], isNotNull);
      expect(restaurantData['name'], isNotNull);
      expect(restaurantData['address'], isNotNull);
      expect(restaurantData['is_active'], isTrue);
    });

    test('should create valid order data', () {
      // Act
      final orderData = TestDataFactory.createOrderData();

      // Assert
      expect(orderData, isA<Map<String, dynamic>>());
      expect(orderData['id'], isNotNull);
      expect(orderData['restaurant_id'], isNotNull);
      expect(orderData['table_number'], isNotNull);
      expect(orderData['status'], equals('pending'));
      expect(orderData['items'], isA<List>());
      expect(orderData['items'].length, equals(2));
    });
  });
}
