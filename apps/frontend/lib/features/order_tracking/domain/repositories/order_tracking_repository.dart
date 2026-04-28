/// Order tracking repository interface.
/// 
/// This interface defines the contract for order tracking data operations,
/// including fetching tracking information, subscribing to real-time updates,
/// and managing notification preferences.
import '../entities/order_tracking.dart';
import '../entities/order_timeline.dart';
import '../entities/order_status_update.dart';
import '../entities/notification_preference.dart';

/// Abstract repository interface for order tracking operations.
abstract class OrderTrackingRepository {
  /// Fetch comprehensive order tracking information.
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
  Future<OrderTracking> getOrderTracking(
    String orderId, {
    bool includeNotifications = true,
  });

  /// Fetch order tracking by order number.
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
  Future<OrderTracking> getOrderTrackingByNumber(
    String orderNumber, {
    bool includeNotifications = true,
  });

  /// Fetch multiple orders for kitchen display.
  /// 
  /// Args:
  ///   restaurantId: Restaurant identifier
  ///   activeOnly: Whether to only include active orders
  ///   limit: Maximum number of orders to return
  /// 
  /// Returns:
  ///   Future that resolves to list of OrderTracking entities
  Future<List<OrderTracking>> getKitchenOrders(
    String restaurantId, {
    bool activeOnly = true,
    int limit = 50,
  });

  /// Update order status.
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
  ///   Future that resolves to updated OrderStatusUpdate entity
  /// 
  /// Throws:
  ///   OrderTrackingException: If update fails or invalid transition
  Future<OrderStatusUpdate> updateOrderStatus(
    String orderId,
    String newStatus, {
    DateTime? estimatedCompletionTime,
    String? preparationNotes,
    String? changeReason,
    bool notifyCustomer = true,
  });

  /// Bulk update order status for multiple orders.
  /// 
  /// Args:
  ///   orderIds: List of order identifiers
  ///   newStatus: New status for all orders
  ///   preparationNotes: Optional preparation notes
  ///   notifyCustomers: Whether to notify customers
  /// 
  /// Returns:
  ///   Future that resolves to list of updated OrderStatusUpdate entities
  Future<List<OrderStatusUpdate>> bulkUpdateOrderStatus(
    List<String> orderIds,
    String newStatus, {
    String? preparationNotes,
    bool notifyCustomers = true,
  });

  /// Update individual order item status.
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
  ///   Future that resolves to updated OrderItemTracking entity
  Future<OrderItemTracking> updateOrderItemStatus(
    String orderId,
    String itemId,
    OrderItemStatus newStatus, {
    String? preparationNotes,
    DateTime? estimatedReadyTime,
    bool? qualityCheckPassed,
    String? qualityNotes,
  });

  /// Send notification to customer.
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
  Future<List<NotificationHistory>> sendNotification(
    String orderId,
    NotificationTrigger trigger, {
    List<NotificationChannel> channels = const [],
    String? customMessage,
    String? customSubject,
    bool immediate = false,
  });

  /// Get notification preferences for a customer.
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
  Future<NotificationPreference> getNotificationPreferences(
    String restaurantId,
    String customerIdentifier,
  );

  /// Update notification preferences for a customer.
  /// 
  /// Args:
  ///   preferences: Updated notification preferences
  /// 
  /// Returns:
  ///   Future that resolves to updated NotificationPreference entity
  Future<NotificationPreference> updateNotificationPreferences(
    NotificationPreference preferences,
  );

  /// Subscribe to real-time order updates.
  /// 
  /// Args:
  ///   orderId: Order identifier
  ///   onUpdate: Callback function for handling updates
  /// 
  /// Returns:
  ///   Stream of RealtimeStatusUpdate events
  Stream<RealtimeStatusUpdate> subscribeToOrderUpdates(
    String orderId,
  );

  /// Subscribe to real-time kitchen updates for a restaurant.
  /// 
  /// Args:
  ///   restaurantId: Restaurant identifier
  /// 
  /// Returns:
  ///   Stream of RealtimeStatusUpdate events for all restaurant orders
  Stream<RealtimeStatusUpdate> subscribeToKitchenUpdates(
    String restaurantId,
  );

  /// Unsubscribe from real-time updates.
  /// 
  /// Args:
  ///   subscriptionId: Subscription identifier
  /// 
  /// Returns:
  ///   Future that completes when unsubscribed
  Future<void> unsubscribeFromUpdates(String subscriptionId);

  /// Get notification delivery metrics.
  /// 
  /// Args:
  ///   restaurantId: Restaurant identifier
  ///   startDate: Start date for metrics
  ///   endDate: End date for metrics
  /// 
  /// Returns:
  ///   Future that resolves to notification metrics
  Future<NotificationMetrics> getNotificationMetrics(
    String restaurantId,
    DateTime startDate,
    DateTime endDate,
  );

  /// Retry failed notifications.
  /// 
  /// Args:
  ///   maxRetries: Maximum retry attempts
  /// 
  /// Returns:
  ///   Future that resolves to list of retried notifications
  Future<List<NotificationHistory>> retryFailedNotifications({
    int maxRetries = 3,
  });

  /// Get order timeline with detailed events.
  /// 
  /// Args:
  ///   orderId: Order identifier
  /// 
  /// Returns:
  ///   Future that resolves to OrderTimeline entity
  Future<OrderTimeline> getOrderTimeline(String orderId);

  /// Add custom event to order timeline.
  /// 
  /// Args:
  ///   orderId: Order identifier
  ///   eventType: Type of timeline event
  ///   title: Event title
  ///   description: Event description
  ///   metadata: Optional event metadata
  /// 
  /// Returns:
  ///   Future that resolves to updated OrderTimeline entity
  Future<OrderTimeline> addTimelineEvent(
    String orderId,
    TimelineEventType eventType,
    String title,
    String description, {
    Map<String, dynamic> metadata = const {},
  });
}

/// Notification delivery metrics entity
class NotificationMetrics {
  /// Creates notification metrics entity.
  const NotificationMetrics({
    required this.restaurantId,
    required this.dateRangeStart,
    required this.dateRangeEnd,
    required this.totalNotifications,
    required this.notificationsByChannel,
    required this.deliverySuccessRate,
    this.averageDeliveryTimeSeconds,
    required this.failedNotifications,
    required this.bouncedNotifications,
    required this.openedNotifications,
    required this.clickedNotifications,
    required this.engagementRate,
    required this.costBreakdown,
    required this.totalCost,
  });

  /// Restaurant identifier
  final String restaurantId;

  /// Start date for metrics
  final DateTime dateRangeStart;

  /// End date for metrics
  final DateTime dateRangeEnd;

  /// Total notifications sent
  final int totalNotifications;

  /// Notifications by channel
  final Map<String, int> notificationsByChannel;

  /// Delivery success rate (0.0 to 1.0)
  final double deliverySuccessRate;

  /// Average delivery time in seconds
  final double? averageDeliveryTimeSeconds;

  /// Number of failed notifications
  final int failedNotifications;

  /// Number of bounced notifications
  final int bouncedNotifications;

  /// Number of opened notifications
  final int openedNotifications;

  /// Number of clicked notifications
  final int clickedNotifications;

  /// Engagement rate (0.0 to 1.0)
  final double engagementRate;

  /// Cost breakdown by channel
  final Map<String, double> costBreakdown;

  /// Total cost
  final double totalCost;

  /// Get success percentage
  int get successPercentage => (deliverySuccessRate * 100).round();

  /// Get engagement percentage
  int get engagementPercentage => (engagementRate * 100).round();

  /// Get most used channel
  String? get mostUsedChannel {
    if (notificationsByChannel.isEmpty) return null;
    
    return notificationsByChannel.entries
        .reduce((a, b) => a.value > b.value ? a : b)
        .key;
  }

  /// Get average cost per notification
  double get averageCostPerNotification {
    return totalNotifications > 0 ? totalCost / totalNotifications : 0.0;
  }
}

/// Order tracking exception for error handling
class OrderTrackingException implements Exception {
  /// Creates an order tracking exception.
  const OrderTrackingException(
    this.message, {
    this.code,
    this.details,
  });

  /// Error message
  final String message;

  /// Error code
  final String? code;

  /// Additional error details
  final Map<String, dynamic>? details;

  @override
  String toString() {
    return 'OrderTrackingException: $message${code != null ? ' (Code: $code)' : ''}';
  }
}
