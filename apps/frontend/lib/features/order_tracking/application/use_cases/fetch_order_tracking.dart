/// Fetch order tracking use case.
/// 
/// This use case handles fetching comprehensive order tracking information
/// from the repository with proper error handling and data validation.
import 'package:flutter/foundation.dart';

import '../../domain/entities/order_tracking.dart';
import '../../domain/repositories/order_tracking_repository.dart';

/// Use case for fetching order tracking information.
class FetchOrderTrackingUseCase {
  /// Creates a fetch order tracking use case.
  /// 
  /// Args:
  ///   repository: Order tracking repository
  const FetchOrderTrackingUseCase({
    required OrderTrackingRepository repository,
  }) : _repository = repository;

  final OrderTrackingRepository _repository;

  /// Execute the use case to fetch order tracking.
  /// 
  /// Args:
  ///   orderId: Order identifier
  ///   includeNotifications: Whether to include notification history
  /// 
  /// Returns:
  ///   Future that resolves to OrderTracking entity
  /// 
  /// Throws:
  ///   OrderTrackingException: If order not found or access denied
  ///   ArgumentError: If orderId is invalid
  Future<OrderTracking> execute(
    String orderId, {
    bool includeNotifications = true,
  }) async {
    // Validate input
    if (orderId.isEmpty) {
      throw ArgumentError('Order ID cannot be empty');
    }

    try {
      debugPrint('FetchOrderTrackingUseCase: Fetching order $orderId');

      // Fetch order tracking from repository
      final orderTracking = await _repository.getOrderTracking(
        orderId,
        includeNotifications: includeNotifications,
      );

      // Validate response
      _validateOrderTracking(orderTracking);

      debugPrint('FetchOrderTrackingUseCase: Successfully fetched order tracking');
      return orderTracking;
    } catch (e) {
      debugPrint('FetchOrderTrackingUseCase: Error fetching order tracking - $e');
      rethrow;
    }
  }

  /// Execute the use case to fetch order tracking by number.
  /// 
  /// Args:
  ///   orderNumber: Human-readable order number
  ///   includeNotifications: Whether to include notification history
  /// 
  /// Returns:
  ///   Future that resolves to OrderTracking entity
  /// 
  /// Throws:
  ///   OrderTrackingException: If order not found or access denied
  ///   ArgumentError: If orderNumber is invalid
  Future<OrderTracking> executeByNumber(
    String orderNumber, {
    bool includeNotifications = true,
  }) async {
    // Validate input
    if (orderNumber.isEmpty) {
      throw ArgumentError('Order number cannot be empty');
    }

    try {
      debugPrint('FetchOrderTrackingUseCase: Fetching order by number $orderNumber');

      // Fetch order tracking from repository
      final orderTracking = await _repository.getOrderTrackingByNumber(
        orderNumber,
        includeNotifications: includeNotifications,
      );

      // Validate response
      _validateOrderTracking(orderTracking);

      debugPrint('FetchOrderTrackingUseCase: Successfully fetched order tracking by number');
      return orderTracking;
    } catch (e) {
      debugPrint('FetchOrderTrackingUseCase: Error fetching order tracking by number - $e');
      rethrow;
    }
  }

  /// Execute the use case to fetch multiple kitchen orders.
  /// 
  /// Args:
  ///   restaurantId: Restaurant identifier
  ///   activeOnly: Whether to only include active orders
  ///   limit: Maximum number of orders to return
  /// 
  /// Returns:
  ///   Future that resolves to list of OrderTracking entities
  /// 
  /// Throws:
  ///   OrderTrackingException: If fetch fails
  ///   ArgumentError: If restaurantId is invalid
  Future<List<OrderTracking>> executeKitchenOrders(
    String restaurantId, {
    bool activeOnly = true,
    int limit = 50,
  }) async {
    // Validate input
    if (restaurantId.isEmpty) {
      throw ArgumentError('Restaurant ID cannot be empty');
    }

    if (limit <= 0 || limit > 100) {
      throw ArgumentError('Limit must be between 1 and 100');
    }

    try {
      debugPrint('FetchOrderTrackingUseCase: Fetching kitchen orders for restaurant $restaurantId');

      // Fetch kitchen orders from repository
      final orders = await _repository.getKitchenOrders(
        restaurantId,
        activeOnly: activeOnly,
        limit: limit,
      );

      // Validate response
      _validateKitchenOrders(orders);

      debugPrint('FetchOrderTrackingUseCase: Successfully fetched ${orders.length} kitchen orders');
      return orders;
    } catch (e) {
      debugPrint('FetchOrderTrackingUseCase: Error fetching kitchen orders - $e');
      rethrow;
    }
  }

  /// Validate order tracking data.
  /// 
  /// Args:
  ///   orderTracking: Order tracking entity to validate
  /// 
  /// Throws:
  ///   ArgumentError: If data is invalid
  void _validateOrderTracking(OrderTracking orderTracking) {
    if (orderTracking.orderId.isEmpty) {
      throw ArgumentError('Order tracking must have a valid order ID');
    }

    if (orderTracking.orderNumber.isEmpty) {
      throw ArgumentError('Order tracking must have a valid order number');
    }

    if (orderTracking.restaurantId.isEmpty) {
      throw ArgumentError('Order tracking must have a valid restaurant ID');
    }

    // Validate status history is in chronological order
    if (orderTracking.statusHistory.length > 1) {
      for (int i = 1; i < orderTracking.statusHistory.length; i++) {
        final current = orderTracking.statusHistory[i];
        final previous = orderTracking.statusHistory[i - 1];
        
        if (current.changedAt.isBefore(previous.changedAt)) {
          debugPrint('Warning: Status history is not in chronological order');
          break;
        }
      }
    }

    // Validate item tracking consistency
    for (final itemTracking in orderTracking.itemTracking) {
      if (itemTracking.orderId != orderTracking.orderId) {
        throw ArgumentError('Item tracking order ID mismatch');
      }
    }

    // Validate notification history consistency
    for (final notification in orderTracking.notificationsSent) {
      if (notification.orderId != orderTracking.orderId) {
        throw ArgumentError('Notification history order ID mismatch');
      }
    }

    debugPrint('Order tracking validation passed');
  }

  /// Validate kitchen orders data.
  /// 
  /// Args:
  ///   orders: List of order tracking entities to validate
  /// 
  /// Throws:
  ///   ArgumentError: If data is invalid
  void _validateKitchenOrders(List<OrderTracking> orders) {
    if (orders.isEmpty) {
      debugPrint('No kitchen orders returned');
      return;
    }

    // Validate each order
    for (final order in orders) {
      try {
        _validateOrderTracking(order);
      } catch (e) {
        debugPrint('Invalid order in kitchen orders list: ${order.orderId} - $e');
        // Continue validation for other orders
      }
    }

    // Check for duplicate orders
    final orderIds = orders.map((o) => o.orderId).toSet();
    if (orderIds.length != orders.length) {
      debugPrint('Warning: Duplicate orders found in kitchen orders list');
    }

    debugPrint('Kitchen orders validation passed');
  }
}

/// Fetch order timeline use case.
class FetchOrderTimelineUseCase {
  /// Creates a fetch order timeline use case.
  /// 
  /// Args:
  ///   repository: Order tracking repository
  const FetchOrderTimelineUseCase({
    required OrderTrackingRepository repository,
  }) : _repository = repository;

  final OrderTrackingRepository _repository;

  /// Execute the use case to fetch order timeline.
  /// 
  /// Args:
  ///   orderId: Order identifier
  /// 
  /// Returns:
  ///   Future that resolves to OrderTimeline entity
  /// 
  /// Throws:
  ///   OrderTrackingException: If timeline not found
  ///   ArgumentError: If orderId is invalid
  Future<OrderTimeline> execute(String orderId) async {
    // Validate input
    if (orderId.isEmpty) {
      throw ArgumentError('Order ID cannot be empty');
    }

    try {
      debugPrint('FetchOrderTimelineUseCase: Fetching timeline for order $orderId');

      // Fetch timeline from repository
      final timeline = await _repository.getOrderTimeline(orderId);

      // Validate response
      _validateTimeline(timeline);

      debugPrint('FetchOrderTimelineUseCase: Successfully fetched timeline with ${timeline.totalEvents} events');
      return timeline;
    } catch (e) {
      debugPrint('FetchOrderTimelineUseCase: Error fetching timeline - $e');
      rethrow;
    }
  }

  /// Validate timeline data.
  /// 
  /// Args:
  ///   timeline: Order timeline entity to validate
  /// 
  /// Throws:
  ///   ArgumentError: If data is invalid
  void _validateTimeline(OrderTimeline timeline) {
    if (timeline.orderId.isEmpty) {
      throw ArgumentError('Timeline must have a valid order ID');
    }

    if (timeline.totalEvents != timeline.events.length) {
      debugPrint('Warning: Timeline event count mismatch');
    }

    // Validate events are in chronological order
    if (timeline.events.length > 1) {
      for (int i = 1; i < timeline.events.length; i++) {
        final current = timeline.events[i];
        final previous = timeline.events[i - 1];
        
        if (current.timestamp.isBefore(previous.timestamp)) {
          debugPrint('Warning: Timeline events are not in chronological order');
          break;
        }
      }
    }

    // Validate event consistency
    for (final event in timeline.events) {
      if (event.orderId != timeline.orderId) {
        throw ArgumentError('Timeline event order ID mismatch');
      }
    }

    debugPrint('Timeline validation passed');
  }
}

/// Fetch notification preferences use case.
class FetchNotificationPreferencesUseCase {
  /// Creates a fetch notification preferences use case.
  /// 
  /// Args:
  ///   repository: Order tracking repository
  const FetchNotificationPreferencesUseCase({
    required OrderTrackingRepository repository,
  }) : _repository = repository;

  final OrderTrackingRepository _repository;

  /// Execute the use case to fetch notification preferences.
  /// 
  /// Args:
  ///   restaurantId: Restaurant identifier
  ///   customerIdentifier: Customer phone or email
  /// 
  /// Returns:
  ///   Future that resolves to NotificationPreference entity
  /// 
  /// Throws:
  ///   OrderTrackingException: If preferences not found
  ///   ArgumentError: If parameters are invalid
  Future<NotificationPreference> execute(
    String restaurantId,
    String customerIdentifier,
  ) async {
    // Validate input
    if (restaurantId.isEmpty) {
      throw ArgumentError('Restaurant ID cannot be empty');
    }

    if (customerIdentifier.isEmpty) {
      throw ArgumentError('Customer identifier cannot be empty');
    }

    try {
      debugPrint('FetchNotificationPreferencesUseCase: Fetching preferences for $customerIdentifier');

      // Fetch preferences from repository
      final preferences = await _repository.getNotificationPreferences(
        restaurantId,
        customerIdentifier,
      );

      // Validate response
      _validatePreferences(preferences);

      debugPrint('FetchNotificationPreferencesUseCase: Successfully fetched preferences');
      return preferences;
    } catch (e) {
      debugPrint('FetchNotificationPreferencesUseCase: Error fetching preferences - $e');
      rethrow;
    }
  }

  /// Validate notification preferences data.
  /// 
  /// Args:
  ///   preferences: Notification preferences entity to validate
  /// 
  /// Throws:
  ///   ArgumentError: If data is invalid
  void _validatePreferences(NotificationPreference preferences) {
    if (preferences.id.isEmpty) {
      throw ArgumentError('Preferences must have a valid ID');
    }

    if (preferences.restaurantId.isEmpty) {
      throw ArgumentError('Preferences must have a valid restaurant ID');
    }

    // Validate contact information
    if (!preferences.hasContactInfo) {
      debugPrint('Warning: No contact information available for preferences');
    }

    // Validate quiet hours format
    if (preferences.quietHoursStart != null) {
      if (!_isValidTimeFormat(preferences.quietHoursStart!)) {
        throw ArgumentError('Invalid quiet hours start time format');
      }
    }

    if (preferences.quietHoursEnd != null) {
      if (!_isValidTimeFormat(preferences.quietHoursEnd!)) {
        throw ArgumentError('Invalid quiet hours end time format');
      }
    }

    debugPrint('Notification preferences validation passed');
  }

  /// Validate time format (HH:MM).
  /// 
  /// Args:
  ///   timeString: Time string to validate
  /// 
  /// Returns:
  ///   True if format is valid
  bool _isValidTimeFormat(String timeString) {
    final regex = RegExp(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$');
    return regex.hasMatch(timeString);
  }
}
