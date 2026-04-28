/// GetX Controller testing examples.
///
/// Demonstrates testing patterns for GetX controllers,
/// reactive state management, and dependency injection.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';

import '../helpers/test_helpers.dart';

/// Mock controller for testing
class MockController extends GetxController {
  final RxInt _counter = 0.obs;
  final RxBool _isLoading = false.obs;
  final RxString _message = ''.obs;

  int get counter => _counter.value;
  bool get isLoading => _isLoading.value;
  String get message => _message.value;

  void increment() {
    _counter.value++;
  }

  Future<void> loadData() async {
    _isLoading.value = true;
    _message.value = 'Loading...';

    // Simulate async operation
    await Future.delayed(const Duration(milliseconds: 100));

    _isLoading.value = false;
    _message.value = 'Data loaded successfully';
  }

  void reset() {
    _counter.value = 0;
    _isLoading.value = false;
    _message.value = '';
  }
}

void main() {
  group('GetX Controller Testing', () {
    late MockController controller;

    setUp(() {
      controller = GetXTestHelpers.setupController(MockController());
    });

    tearDown(() {
      GetXTestHelpers.disposeController<MockController>();
    });

    group('Reactive State Testing', () {
      test('should increment counter reactively', () async {
        // Arrange
        expect(controller.counter, 0);

        // Act & Assert with reactive testing
        await GetXTestHelpers.testReactiveState(
          controller._counter,
          1,
          () => controller.increment(),
        );

        expect(controller.counter, 1);
      });

      test('should handle loading state correctly', () async {
        // Arrange
        expect(controller.isLoading, false);
        expect(controller.message, '');

        // Act
        final loadFuture = controller.loadData();

        // Assert initial loading state
        expect(controller.isLoading, true);
        expect(controller.message, 'Loading...');

        // Wait for completion
        await loadFuture;

        // Assert final state
        expect(controller.isLoading, false);
        expect(controller.message, 'Data loaded successfully');
      });
    });

    group('Controller Method Testing', () {
      test('should reset all values', () async {
        // Arrange
        controller.increment();
        await controller.loadData();

        expect(controller.counter, 1);
        expect(controller.message, 'Data loaded successfully');

        // Act
        await GetXTestHelpers.testControllerMethod(
          controller,
          () async => controller.reset(),
        );

        // Assert
        expect(controller.counter, 0);
        expect(controller.isLoading, false);
        expect(controller.message, '');
      });
    });

    group('Controller Lifecycle Testing', () {
      test('should initialize correctly', () {
        // Assert controller is properly initialized
        expect(controller.initialized, true);
        expect(Get.isRegistered<MockController>(), true);
      });

      test('should dispose correctly', () {
        // Act
        GetXTestHelpers.disposeController<MockController>();

        // Assert
        expect(Get.isRegistered<MockController>(), false);
      });
    });

    group('Dependency Injection Testing', () {
      test('should work with dependencies', () {
        // Arrange - start fresh
        Get.reset();

        const mockService = 'mock_service_instance';
        Get.put<String>(mockService, tag: 'service');

        final controllerWithDeps = GetXTestHelpers.setupController(
          MockController(),
          resetGetX: false, // Don't reset since we just set up dependencies
        );

        // Assert
        expect(Get.find<String>(tag: 'service'), mockService);
        expect(controllerWithDeps.initialized, true);
      });
    });
  });

  group('API Contract Testing Examples', () {
    test('should validate user response contract', () {
      // Arrange
      final mockUserResponse = TestDataFactory.createUserData(
        id: 'user123',
        email: 'test@example.com',
      );

      // Act & Assert
      ApiContractHelpers.validateResponseContract(
        mockUserResponse,
        ApiContractHelpers.getUserResponseSchema(),
      );
    });

    test('should validate error response contract', () {
      // Arrange
      final mockErrorResponse = {
        'error': 'ValidationError',
        'message': 'Invalid input provided',
        'status_code': 400,
      };

      // Act & Assert
      ApiContractHelpers.validateResponseContract(
        mockErrorResponse,
        ApiContractHelpers.getErrorResponseSchema(),
      );
    });

    test('should detect contract violations', () {
      // Arrange
      final invalidResponse = {
        'id': 'user123',
        'email': 'test@example.com',
        // Missing required fields
      };

      // Act & Assert
      expect(
        () => ApiContractHelpers.validateResponseContract(
          invalidResponse,
          ApiContractHelpers.getUserResponseSchema(),
        ),
        throwsA(isA<TestFailure>()),
      );
    });
  });
}
