/// Test helpers and utilities for Flutter testing.
///
/// This module provides common testing utilities following
/// clean architecture and Flutter testing best practices.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';

/// Test data factories
class TestDataFactory {
  /// Create test user data
  static Map<String, dynamic> createUserData({
    String? id,
    String? email,
    String? phone,
  }) {
    return {
      'id': id ?? 'test-user-id',
      'email': email ?? 'test@example.com',
      'phone': phone ?? '+1234567890',
      'is_active': true,
      'created_at': '2024-01-01T00:00:00Z',
      'updated_at': '2024-01-01T00:00:00Z',
    };
  }

  /// Create test restaurant data
  static Map<String, dynamic> createRestaurantData({
    String? id,
    String? name,
    String? address,
  }) {
    return {
      'id': id ?? 'test-restaurant-id',
      'name': name ?? 'Test Restaurant',
      'address': address ?? '123 Test St, Test City, TC 12345',
      'phone': '+1234567890',
      'email': 'restaurant@test.com',
      'is_active': true,
      'created_at': '2024-01-01T00:00:00Z',
      'updated_at': '2024-01-01T00:00:00Z',
    };
  }

  /// Create test order data
  static Map<String, dynamic> createOrderData({
    String? id,
    String? restaurantId,
    String? tableNumber,
  }) {
    return {
      'id': id ?? 'test-order-id',
      'restaurant_id': restaurantId ?? 'test-restaurant-id',
      'table_number': tableNumber ?? 'A1',
      'customer_name': 'John Doe',
      'customer_phone': '+1234567890',
      'status': 'pending',
      'total_amount': 29.99,
      'items': [
        {
          'id': 'item1',
          'name': 'Test Burger',
          'price': 15.99,
          'quantity': 1,
        },
        {
          'id': 'item2',
          'name': 'Test Drink',
          'price': 4.99,
          'quantity': 1,
        },
      ],
      'created_at': '2024-01-01T00:00:00Z',
      'updated_at': '2024-01-01T00:00:00Z',
    };
  }
}

/// Widget test helpers
class WidgetTestHelpers {
  /// Pump widget with GetX dependencies
  static Future<void> pumpWidgetWithGetX(
    WidgetTester tester,
    Widget widget, {
    List<TestBind>? bindings,
  }) async {
    // Reset GetX state
    Get.reset();

    // Setup bindings if provided
    if (bindings != null) {
      for (final binding in bindings) {
        Get.put(binding.dependency, tag: binding.tag);
      }
    }

    await tester.pumpWidget(
      GetMaterialApp(
        home: widget,
      ),
    );
  }

  /// Find widget by text
  static Finder findTextWidget(String text) {
    return find.text(text);
  }

  /// Find widget by key
  static Finder findByKey(Key key) {
    return find.byKey(key);
  }

  /// Find widget by type
  static Finder findByType<T extends Widget>() {
    return find.byType(T);
  }

  /// Verify widget exists and is visible
  static void expectWidgetVisible(Finder finder) {
    expect(finder, findsOneWidget);
  }

  /// Verify widget does not exist
  static void expectWidgetNotFound(Finder finder) {
    expect(finder, findsNothing);
  }

  /// Tap on widget and settle
  static Future<void> tapAndSettle(
    WidgetTester tester,
    Finder finder,
  ) async {
    await tester.tap(finder);
    await tester.pumpAndSettle();
  }
}

/// GetX Controller testing utilities
class GetXTestHelpers {
  /// Setup GetX controller for testing
  static T setupController<T extends GetxController>(
    T controller, {
    List<TestBind>? dependencies,
    bool resetGetX = true,
  }) {
    // Reset GetX state if requested
    if (resetGetX) {
      Get.reset();
    }

    // Setup dependencies if provided
    if (dependencies != null) {
      for (final dependency in dependencies) {
        Get.put(dependency.dependency, tag: dependency.tag);
      }
    }

    // Put the controller
    Get.put<T>(controller);

    return controller;
  }

  /// Test controller reactive state changes
  static Future<void> testReactiveState<T>(
    Rx<T> observable,
    T expectedValue,
    VoidCallback action,
  ) async {
    // Setup expectation
    final completer = expectAsync0(() {});

    // Listen for changes
    final subscription = observable.listen((value) {
      if (value == expectedValue) {
        completer();
      }
    });

    try {
      // Trigger action
      action();

      // Wait a tick for reactive updates
      await Future.delayed(Duration.zero);
    } finally {
      subscription.cancel();
    }
  }

  /// Test controller method calls
  static Future<void> testControllerMethod(
    GetxController controller,
    Future<void> Function() method,
  ) async {
    // Ensure controller is ready
    if (!controller.initialized) {
      controller.onInit();
    }

    // Call method
    await method();

    // Process any pending updates
    await Future.delayed(Duration.zero);
  }

  /// Dispose controller after test
  static void disposeController<T extends GetxController>() {
    if (Get.isRegistered<T>()) {
      Get.delete<T>();
    }
  }
}

/// API Contract testing utilities
class ApiContractHelpers {
  /// Validate API response contract
  static void validateResponseContract(
    Map<String, dynamic> response,
    Map<String, Type> expectedSchema,
  ) {
    for (final entry in expectedSchema.entries) {
      final key = entry.key;
      final expectedType = entry.value;

      expect(response.containsKey(key), true,
          reason: 'Response missing required field: $key');

      final actualValue = response[key];
      expect(actualValue.runtimeType, expectedType,
          reason: 'Field $key has incorrect type');
    }
  }

  /// Test API request/response format
  static Map<String, Type> getUserResponseSchema() {
    return {
      'id': String,
      'email': String,
      'is_active': bool,
      'created_at': String,
      'updated_at': String,
    };
  }

  /// Test API error response format
  static Map<String, Type> getErrorResponseSchema() {
    return {
      'error': String,
      'message': String,
      'status_code': int,
    };
  }
}

/// Test binding class for dependency injection
class TestBind {
  final dynamic dependency;
  final String? tag;

  TestBind(this.dependency, {this.tag});
}
