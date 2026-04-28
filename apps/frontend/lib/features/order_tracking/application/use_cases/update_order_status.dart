/// Update order status use case.
/// 
/// This use case handles updating order status with proper validation,
/// business rule enforcement, and error handling.
import 'package:flutter/foundation.dart';

import '../../domain/entities/order_tracking.dart';
import '../../domain/entities/order_status_update.dart';
import '../../domain/entities/notification_preference.dart';
import '../../domain/repositories/order_tracking_repository.dart';

/// Use case for updating order status.
class UpdateOrderStatusUseCase {
  /// Creates an update order status use case.
  /// 
  /// Args:
  ///   repository: Order tracking repository
  const UpdateOrderStatusUseCase({
    required OrderTrackingRepository repository,
  }) : _repository = repository;

  final OrderTrackingRepository _repository;

  /// Execute the use case to update order status.
  /// 
  /// Args:
  ///   orderId: Order identifier
  ///   newStatus: New order status
  ///   estimatedCompletionTime: Optional estimated completion time
  ///   preparationNotes: Optional preparation notes
  ///   changeReason: Optional reason for the change
  ///   notifyCustomer: Whether to notify customer
  /// 
  /// Returns:
  ///   Future that resolves to OrderStatusUpdate entity
  /// 
  /// Throws:
  ///   OrderTrackingException: If update fails or invalid transition
  ///   ArgumentError: If parameters are invalid
  Future<OrderStatusUpdate> execute(
    String orderId,
    String newStatus, {
    DateTime? estimatedCompletionTime,
    String? preparationNotes,
    String? changeReason,
    bool notifyCustomer = true,
  }) async {
    // Validate input
    _validateInput(orderId, newStatus, estimatedCompletionTime);

    try {
      debugPrint('UpdateOrderStatusUseCase: Updating order $orderId to $newStatus');

      // Update status through repository
      final statusUpdate = await _repository.updateOrderStatus(
        orderId,
        newStatus,
        estimatedCompletionTime: estimatedCompletionTime,
        preparationNotes: preparationNotes,
        changeReason: changeReason,
        notifyCustomer: notifyCustomer,
      );

      // Validate response
      _validateStatusUpdate(statusUpdate);

      debugPrint('UpdateOrderStatusUseCase: Successfully updated order status');
      return statusUpdate;
    } catch (e) {
      debugPrint('UpdateOrderStatusUseCase: Error updating order status - $e');
      rethrow;
    }
  }

  /// Execute bulk status update for multiple orders.
  /// 
  /// Args:
  ///   orderIds: List of order identifiers
  ///   newStatus: New status for all orders
  ///   preparationNotes: Optional preparation notes
  ///   notifyCustomers: Whether to notify customers
  /// 
  /// Returns:
  ///   Future that resolves to list of OrderStatusUpdate entities
  /// 
  /// Throws:
  ///   OrderTrackingException: If update fails
  ///   ArgumentError: If parameters are invalid
  Future<List<OrderStatusUpdate>> executeBulk(
    List<String> orderIds,
    String newStatus, {
    String? preparationNotes,
    bool notifyCustomers = true,
  }) async {
    // Validate input
    _validateBulkInput(orderIds, newStatus);

    try {
      debugPrint('UpdateOrderStatusUseCase: Bulk updating ${orderIds.length} orders to $newStatus');

      // Perform bulk update through repository
      final statusUpdates = await _repository.bulkUpdateOrderStatus(
        orderIds,
        newStatus,
        preparationNotes: preparationNotes,
        notifyCustomers: notifyCustomers,
      );

      // Validate response
      _validateBulkStatusUpdates(statusUpdates, orderIds);

      debugPrint('UpdateOrderStatusUseCase: Successfully bulk updated ${statusUpdates.length} orders');
      return statusUpdates;
    } catch (e) {
      debugPrint('UpdateOrderStatusUseCase: Error bulk updating orders - $e');
      rethrow;
    }
  }

  /// Execute order item status update.
  /// 
  /// Args:
  ///   orderId: Order identifier
  ///   itemId: Order item identifier
  ///   newStatus: New item status
  ///   preparationNotes: Optional preparation notes
  ///   estimatedReadyTime: Optional estimated ready time
  ///   qualityCheckPassed: Optional quality check result
  ///   qualityNotes: Optional quality check notes
  /// 
  /// Returns:
  ///   Future that resolves to OrderItemTracking entity
  /// 
  /// Throws:
  ///   OrderTrackingException: If update fails
  ///   ArgumentError: If parameters are invalid
  Future<OrderItemTracking> executeItemStatus(
    String orderId,
    String itemId,
    OrderItemStatus newStatus, {
    String? preparationNotes,
    DateTime? estimatedReadyTime,
    bool? qualityCheckPassed,
    String? qualityNotes,
  }) async {
    // Validate input
    _validateItemInput(orderId, itemId, newStatus, estimatedReadyTime);

    try {
      debugPrint('UpdateOrderStatusUseCase: Updating item $itemId to ${newStatus.name}');

      // Update item status through repository
      final itemTracking = await _repository.updateOrderItemStatus(
        orderId,
        itemId,
        newStatus,
        preparationNotes: preparationNotes,
        estimatedReadyTime: estimatedReadyTime,
        qualityCheckPassed: qualityCheckPassed,
        qualityNotes: qualityNotes,
      );

      // Validate response
      _validateItemTracking(itemTracking);

      debugPrint('UpdateOrderStatusUseCase: Successfully updated item status');
      return itemTracking;
    } catch (e) {
      debugPrint('UpdateOrderStatusUseCase: Error updating item status - $e');
      rethrow;
    }
  }

  /// Send notification for order update.
  /// 
  /// Args:
  ///   orderId: Order identifier
  ///   trigger: Notification trigger
  ///   channels: List of notification channels
  ///   customMessage: Optional custom message
  ///   customSubject: Optional custom subject
  ///   immediate: Whether to send immediately
  /// 
  /// Returns:
  ///   Future that resolves to list of NotificationHistory entities
  /// 
  /// Throws:
  ///   OrderTrackingException: If notification fails
  ///   ArgumentError: If parameters are invalid
  Future<List<NotificationHistory>> executeNotification(
    String orderId,
    NotificationTrigger trigger, {
    List<NotificationChannel> channels = const [],
    String? customMessage,
    String? customSubject,
    bool immediate = false,
  }) async {
    // Validate input
    _validateNotificationInput(orderId, trigger, channels);

    try {
      debugPrint('UpdateOrderStatusUseCase: Sending ${trigger.name} notification for order $orderId');

      // Send notification through repository
      final notifications = await _repository.sendNotification(
        orderId,
        trigger,
        channels: channels,
        customMessage: customMessage,
        customSubject: customSubject,
        immediate: immediate,
      );

      // Validate response
      _validateNotifications(notifications);

      debugPrint('UpdateOrderStatusUseCase: Successfully sent ${notifications.length} notifications');
      return notifications;
    } catch (e) {
      debugPrint('UpdateOrderStatusUseCase: Error sending notification - $e');
      rethrow;
    }
  }

  /// Validate input parameters for status update.
  /// 
  /// Args:
  ///   orderId: Order identifier
  ///   newStatus: New order status
  ///   estimatedCompletionTime: Optional estimated completion time
  /// 
  /// Throws:
  ///   ArgumentError: If parameters are invalid
  void _validateInput(
    String orderId,
    String newStatus,
    DateTime? estimatedCompletionTime,
  ) {
    if (orderId.isEmpty) {
      throw ArgumentError('Order ID cannot be empty');
    }

    if (newStatus.isEmpty) {
      throw ArgumentError('New status cannot be empty');
    }

    // Validate status value
    final validStatuses = ['placed', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled'];
    if (!validStatuses.contains(newStatus.toLowerCase())) {
      throw ArgumentError('Invalid status: $newStatus');
    }

    // Validate estimated completion time
    if (estimatedCompletionTime != null) {
      final now = DateTime.now();
      if (estimatedCompletionTime.isBefore(now.subtract(const Duration(minutes: 1)))) {
        throw ArgumentError('Estimated completion time cannot be in the past');
      }

      // Reasonable upper bound (24 hours from now)
      if (estimatedCompletionTime.isAfter(now.add(const Duration(hours: 24)))) {
        throw ArgumentError('Estimated completion time is too far in the future');
      }
    }
  }

  /// Validate input parameters for bulk update.
  /// 
  /// Args:
  ///   orderIds: List of order identifiers
  ///   newStatus: New order status
  /// 
  /// Throws:
  ///   ArgumentError: If parameters are invalid
  void _validateBulkInput(List<String> orderIds, String newStatus) {
    if (orderIds.isEmpty) {
      throw ArgumentError('Order IDs list cannot be empty');
    }

    if (orderIds.length > 50) {
      throw ArgumentError('Cannot update more than 50 orders at once');
    }

    for (final orderId in orderIds) {
      if (orderId.isEmpty) {
        throw ArgumentError('Order ID cannot be empty');
      }
    }

    // Check for duplicates
    final uniqueIds = orderIds.toSet();
    if (uniqueIds.length != orderIds.length) {
      throw ArgumentError('Duplicate order IDs found in list');
    }

    if (newStatus.isEmpty) {
      throw ArgumentError('New status cannot be empty');
    }

    // Validate status value
    final validStatuses = ['placed', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled'];
    if (!validStatuses.contains(newStatus.toLowerCase())) {
      throw ArgumentError('Invalid status: $newStatus');
    }
  }

  /// Validate input parameters for item status update.
  /// 
  /// Args:
  ///   orderId: Order identifier
  ///   itemId: Order item identifier
  ///   newStatus: New item status
  ///   estimatedReadyTime: Optional estimated ready time
  /// 
  /// Throws:
  ///   ArgumentError: If parameters are invalid
  void _validateItemInput(
    String orderId,
    String itemId,
    OrderItemStatus newStatus,
    DateTime? estimatedReadyTime,
  ) {
    if (orderId.isEmpty) {
      throw ArgumentError('Order ID cannot be empty');
    }

    if (itemId.isEmpty) {
      throw ArgumentError('Item ID cannot be empty');
    }

    // Validate estimated ready time
    if (estimatedReadyTime != null) {
      final now = DateTime.now();
      if (estimatedReadyTime.isBefore(now.subtract(const Duration(minutes: 1)))) {
        throw ArgumentError('Estimated ready time cannot be in the past');
      }

      // Reasonable upper bound (4 hours from now)
      if (estimatedReadyTime.isAfter(now.add(const Duration(hours: 4)))) {
        throw ArgumentError('Estimated ready time is too far in the future');
      }
    }
  }

  /// Validate input parameters for notification.
  /// 
  /// Args:
  ///   orderId: Order identifier
  ///   trigger: Notification trigger
  ///   channels: List of notification channels
  /// 
  /// Throws:
  ///   ArgumentError: If parameters are invalid
  void _validateNotificationInput(
    String orderId,
    NotificationTrigger trigger,
    List<NotificationChannel> channels,
  ) {
    if (orderId.isEmpty) {
      throw ArgumentError('Order ID cannot be empty');
    }

    if (channels.length > 4) {
      throw ArgumentError('Cannot send to more than 4 channels at once');
    }

    // Check for duplicate channels
    final uniqueChannels = channels.toSet();
    if (uniqueChannels.length != channels.length) {
      throw ArgumentError('Duplicate notification channels found');
    }
  }

  /// Validate status update response.
  /// 
  /// Args:
  ///   statusUpdate: Status update to validate
  /// 
  /// Throws:
  ///   ArgumentError: If response is invalid
  void _validateStatusUpdate(OrderStatusUpdate statusUpdate) {
    if (statusUpdate.id.isEmpty) {
      throw ArgumentError('Status update must have a valid ID');
    }

    if (statusUpdate.orderId.isEmpty) {
      throw ArgumentError('Status update must have a valid order ID');
    }

    if (statusUpdate.status.isEmpty) {
      throw ArgumentError('Status update must have a valid status');
    }
  }

  /// Validate bulk status updates response.
  /// 
  /// Args:
  ///   statusUpdates: List of status updates to validate
  ///   originalOrderIds: Original list of order IDs
  /// 
  /// Throws:
  ///   ArgumentError: If response is invalid
  void _validateBulkStatusUpdates(
    List<OrderStatusUpdate> statusUpdates,
    List<String> originalOrderIds,
  ) {
    if (statusUpdates.isEmpty) {
      throw ArgumentError('Bulk update must return at least one status update');
    }

    // Check that we don't have more updates than requested
    if (statusUpdates.length > originalOrderIds.length) {
      throw ArgumentError('Bulk update returned more updates than requested');
    }

    // Validate each status update
    for (final statusUpdate in statusUpdates) {
      _validateStatusUpdate(statusUpdate);
      
      // Check that the order ID was in the original request
      if (!originalOrderIds.contains(statusUpdate.orderId)) {
        throw ArgumentError('Bulk update returned update for unexpected order: ${statusUpdate.orderId}');
      }
    }

    // Log if some updates failed
    if (statusUpdates.length < originalOrderIds.length) {
      final successfulIds = statusUpdates.map((u) => u.orderId).toSet();
      final failedIds = originalOrderIds.where((id) => !successfulIds.contains(id)).toList();
      debugPrint('UpdateOrderStatusUseCase: Some bulk updates failed for orders: $failedIds');
    }
  }

  /// Validate item tracking response.
  /// 
  /// Args:
  ///   itemTracking: Item tracking to validate
  /// 
  /// Throws:
  ///   ArgumentError: If response is invalid
  void _validateItemTracking(OrderItemTracking itemTracking) {
    if (itemTracking.id.isEmpty) {
      throw ArgumentError('Item tracking must have a valid ID');
    }

    if (itemTracking.orderId.isEmpty) {
      throw ArgumentError('Item tracking must have a valid order ID');
    }

    if (itemTracking.orderItemId.isEmpty) {
      throw ArgumentError('Item tracking must have a valid order item ID');
    }

    if (itemTracking.itemName.isEmpty) {
      throw ArgumentError('Item tracking must have a valid item name');
    }
  }

  /// Validate notifications response.
  /// 
  /// Args:
  ///   notifications: List of notifications to validate
  /// 
  /// Throws:
  ///   ArgumentError: If response is invalid
  void _validateNotifications(List<NotificationHistory> notifications) {
    if (notifications.isEmpty) {
      debugPrint('UpdateOrderStatusUseCase: No notifications were sent');
      return;
    }

    for (final notification in notifications) {
      if (notification.id.isEmpty) {
        throw ArgumentError('Notification must have a valid ID');
      }

      if (notification.orderId.isEmpty) {
        throw ArgumentError('Notification must have a valid order ID');
      }

      if (notification.recipient.isEmpty) {
        throw ArgumentError('Notification must have a valid recipient');
      }

      if (notification.messageContent.isEmpty) {
        throw ArgumentError('Notification must have valid message content');
      }
    }
  }
}
