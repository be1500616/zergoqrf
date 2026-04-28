/// Order tracking domain entity.
/// 
/// This entity represents the complete order tracking information including
/// current status, timeline, and real-time updates.
import 'package:equatable/equatable.dart';

import 'order_timeline.dart';
import 'order_status_update.dart';
import 'notification_preference.dart';

/// Order tracking entity containing comprehensive tracking information.
class OrderTracking extends Equatable {
  /// Creates an order tracking entity.
  /// 
  /// Args:
  ///   orderId: Unique order identifier
  ///   orderNumber: Human-readable order number
  ///   restaurantId: Restaurant identifier
  ///   currentStatus: Current order status
  ///   estimatedCompletionTime: Estimated completion time
  ///   statusHistory: List of status updates
  ///   timeline: Order timeline with events
  ///   itemTracking: Individual item tracking information
  ///   notificationsSent: List of notifications sent
  ///   lastUpdated: Last update timestamp
  const OrderTracking({
    required this.orderId,
    required this.orderNumber,
    required this.restaurantId,
    required this.currentStatus,
    this.estimatedCompletionTime,
    this.statusHistory = const [],
    this.timeline,
    this.itemTracking = const [],
    this.notificationsSent = const [],
    required this.lastUpdated,
  });

  /// Unique order identifier
  final String orderId;

  /// Human-readable order number (e.g., "ORD-20240115-0001")
  final String orderNumber;

  /// Restaurant identifier
  final String restaurantId;

  /// Current order status
  final OrderStatus currentStatus;

  /// Estimated completion time
  final DateTime? estimatedCompletionTime;

  /// List of status updates in chronological order
  final List<OrderStatusUpdate> statusHistory;

  /// Order timeline with detailed events
  final OrderTimeline? timeline;

  /// Individual item tracking information
  final List<OrderItemTracking> itemTracking;

  /// List of notifications sent for this order
  final List<NotificationHistory> notificationsSent;

  /// Last update timestamp
  final DateTime lastUpdated;

  /// Get the latest status update
  OrderStatusUpdate? get latestStatusUpdate {
    if (statusHistory.isEmpty) return null;
    return statusHistory.last;
  }

  /// Get estimated time remaining in minutes
  int? get estimatedTimeRemainingMinutes {
    if (estimatedCompletionTime == null) return null;
    final now = DateTime.now();
    if (estimatedCompletionTime!.isBefore(now)) return 0;
    return estimatedCompletionTime!.difference(now).inMinutes;
  }

  /// Check if order is overdue
  bool get isOverdue {
    if (estimatedCompletionTime == null) return false;
    return DateTime.now().isAfter(estimatedCompletionTime!) && 
           !currentStatus.isTerminal;
  }

  /// Get overall progress percentage (0.0 to 1.0)
  double get overallProgress {
    if (itemTracking.isEmpty) {
      return currentStatus.progressValue;
    }

    final totalItems = itemTracking.length;
    final completedItems = itemTracking
        .where((item) => item.status.isCompleted)
        .length;

    return totalItems > 0 ? completedItems / totalItems : 0.0;
  }

  /// Get items by status
  List<OrderItemTracking> getItemsByStatus(OrderItemStatus status) {
    return itemTracking.where((item) => item.status == status).toList();
  }

  /// Get pending items count
  int get pendingItemsCount => getItemsByStatus(OrderItemStatus.pending).length;

  /// Get preparing items count
  int get preparingItemsCount => getItemsByStatus(OrderItemStatus.preparing).length;

  /// Get ready items count
  int get readyItemsCount => getItemsByStatus(OrderItemStatus.ready).length;

  /// Get served items count
  int get servedItemsCount => getItemsByStatus(OrderItemStatus.served).length;

  /// Get next recommended action for kitchen staff
  String get nextAction {
    if (pendingItemsCount > 0) {
      return 'Start preparing $pendingItemsCount pending items';
    } else if (preparingItemsCount > 0) {
      return 'Continue preparing $preparingItemsCount items';
    } else if (readyItemsCount > 0) {
      return 'Serve $readyItemsCount ready items';
    } else if (currentStatus == OrderStatus.completed) {
      return 'Order complete';
    } else {
      return 'Review order status';
    }
  }

  /// Get status summary for display
  String get statusSummary {
    if (currentStatus == OrderStatus.completed) {
      return 'All items served';
    }

    final statusParts = <String>[];
    if (preparingItemsCount > 0) {
      statusParts.add('$preparingItemsCount preparing');
    }
    if (readyItemsCount > 0) {
      statusParts.add('$readyItemsCount ready');
    }
    if (pendingItemsCount > 0) {
      statusParts.add('$pendingItemsCount pending');
    }

    return statusParts.isNotEmpty ? statusParts.join(', ') : 'No active items';
  }

  /// Create a copy with updated fields
  OrderTracking copyWith({
    String? orderId,
    String? orderNumber,
    String? restaurantId,
    OrderStatus? currentStatus,
    DateTime? estimatedCompletionTime,
    List<OrderStatusUpdate>? statusHistory,
    OrderTimeline? timeline,
    List<OrderItemTracking>? itemTracking,
    List<NotificationHistory>? notificationsSent,
    DateTime? lastUpdated,
  }) {
    return OrderTracking(
      orderId: orderId ?? this.orderId,
      orderNumber: orderNumber ?? this.orderNumber,
      restaurantId: restaurantId ?? this.restaurantId,
      currentStatus: currentStatus ?? this.currentStatus,
      estimatedCompletionTime: estimatedCompletionTime ?? this.estimatedCompletionTime,
      statusHistory: statusHistory ?? this.statusHistory,
      timeline: timeline ?? this.timeline,
      itemTracking: itemTracking ?? this.itemTracking,
      notificationsSent: notificationsSent ?? this.notificationsSent,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }

  @override
  List<Object?> get props => [
        orderId,
        orderNumber,
        restaurantId,
        currentStatus,
        estimatedCompletionTime,
        statusHistory,
        timeline,
        itemTracking,
        notificationsSent,
        lastUpdated,
      ];
}

/// Order status enumeration
enum OrderStatus {
  placed,
  confirmed,
  preparing,
  ready,
  completed,
  cancelled;

  /// Get human-readable display name
  String get displayName {
    switch (this) {
      case OrderStatus.placed:
        return 'Placed';
      case OrderStatus.confirmed:
        return 'Confirmed';
      case OrderStatus.preparing:
        return 'Preparing';
      case OrderStatus.ready:
        return 'Ready';
      case OrderStatus.completed:
        return 'Completed';
      case OrderStatus.cancelled:
        return 'Cancelled';
    }
  }

  /// Get progress value (0.0 to 1.0)
  double get progressValue {
    switch (this) {
      case OrderStatus.placed:
        return 0.1;
      case OrderStatus.confirmed:
        return 0.25;
      case OrderStatus.preparing:
        return 0.5;
      case OrderStatus.ready:
        return 0.8;
      case OrderStatus.completed:
        return 1.0;
      case OrderStatus.cancelled:
        return 0.0;
    }
  }

  /// Check if status is terminal (no further changes expected)
  bool get isTerminal {
    return this == OrderStatus.completed || this == OrderStatus.cancelled;
  }

  /// Get status color for UI display
  String get colorHex {
    switch (this) {
      case OrderStatus.placed:
        return '#6B7280'; // Gray
      case OrderStatus.confirmed:
        return '#3B82F6'; // Blue
      case OrderStatus.preparing:
        return '#F59E0B'; // Amber
      case OrderStatus.ready:
        return '#10B981'; // Emerald
      case OrderStatus.completed:
        return '#059669'; // Green
      case OrderStatus.cancelled:
        return '#EF4444'; // Red
    }
  }
}

/// Order item status enumeration
enum OrderItemStatus {
  pending,
  preparing,
  ready,
  served,
  cancelled;

  /// Get human-readable display name
  String get displayName {
    switch (this) {
      case OrderItemStatus.pending:
        return 'Pending';
      case OrderItemStatus.preparing:
        return 'Preparing';
      case OrderItemStatus.ready:
        return 'Ready';
      case OrderItemStatus.served:
        return 'Served';
      case OrderItemStatus.cancelled:
        return 'Cancelled';
    }
  }

  /// Check if item is completed
  bool get isCompleted {
    return this == OrderItemStatus.served || this == OrderItemStatus.cancelled;
  }

  /// Get status color for UI display
  String get colorHex {
    switch (this) {
      case OrderItemStatus.pending:
        return '#6B7280'; // Gray
      case OrderItemStatus.preparing:
        return '#F59E0B'; // Amber
      case OrderItemStatus.ready:
        return '#10B981'; // Emerald
      case OrderItemStatus.served:
        return '#059669'; // Green
      case OrderItemStatus.cancelled:
        return '#EF4444'; // Red
    }
  }
}

/// Order item tracking entity
class OrderItemTracking extends Equatable {
  /// Creates an order item tracking entity.
  const OrderItemTracking({
    required this.id,
    required this.orderId,
    required this.orderItemId,
    required this.itemName,
    required this.status,
    this.previousStatus,
    this.assignedTo,
    this.estimatedReadyTime,
    this.actualReadyTime,
    this.preparationNotes,
    this.qualityCheckPassed,
    this.qualityNotes,
    this.changedBy,
    required this.changedAt,
    required this.createdAt,
  });

  /// Tracking ID
  final String id;

  /// Order ID
  final String orderId;

  /// Order item ID
  final String orderItemId;

  /// Item name
  final String itemName;

  /// Current status
  final OrderItemStatus status;

  /// Previous status
  final OrderItemStatus? previousStatus;

  /// Assigned staff member
  final String? assignedTo;

  /// Estimated ready time
  final DateTime? estimatedReadyTime;

  /// Actual ready time
  final DateTime? actualReadyTime;

  /// Preparation notes
  final String? preparationNotes;

  /// Quality check result
  final bool? qualityCheckPassed;

  /// Quality check notes
  final String? qualityNotes;

  /// User who made the last change
  final String? changedBy;

  /// Last change timestamp
  final DateTime changedAt;

  /// Creation timestamp
  final DateTime createdAt;

  /// Check if item is overdue
  bool get isOverdue {
    if (estimatedReadyTime == null || status.isCompleted) return false;
    return DateTime.now().isAfter(estimatedReadyTime!);
  }

  /// Get preparation duration in minutes
  int? get preparationDurationMinutes {
    if (actualReadyTime == null) return null;
    return actualReadyTime!.difference(createdAt).inMinutes;
  }

  @override
  List<Object?> get props => [
        id,
        orderId,
        orderItemId,
        itemName,
        status,
        previousStatus,
        assignedTo,
        estimatedReadyTime,
        actualReadyTime,
        preparationNotes,
        qualityCheckPassed,
        qualityNotes,
        changedBy,
        changedAt,
        createdAt,
      ];
}

/// Notification history entity
class NotificationHistory extends Equatable {
  /// Creates a notification history entity.
  const NotificationHistory({
    required this.id,
    required this.orderId,
    required this.channel,
    required this.recipient,
    this.subject,
    required this.messageContent,
    required this.status,
    this.sentAt,
    this.deliveredAt,
    this.openedAt,
    this.clickedAt,
    this.errorMessage,
    this.retryCount = 0,
    this.maxRetries = 3,
    required this.createdAt,
  });

  /// Notification ID
  final String id;

  /// Order ID
  final String orderId;

  /// Notification channel
  final NotificationChannel channel;

  /// Recipient identifier
  final String recipient;

  /// Message subject
  final String? subject;

  /// Message content
  final String messageContent;

  /// Notification status
  final NotificationStatus status;

  /// Sent timestamp
  final DateTime? sentAt;

  /// Delivered timestamp
  final DateTime? deliveredAt;

  /// Opened timestamp
  final DateTime? openedAt;

  /// Clicked timestamp
  final DateTime? clickedAt;

  /// Error message if failed
  final String? errorMessage;

  /// Retry count
  final int retryCount;

  /// Maximum retries allowed
  final int maxRetries;

  /// Creation timestamp
  final DateTime createdAt;

  /// Check if notification can be retried
  bool get canRetry {
    return status == NotificationStatus.failed && retryCount < maxRetries;
  }

  /// Get delivery time in seconds
  int? get deliveryTimeSeconds {
    if (sentAt == null || deliveredAt == null) return null;
    return deliveredAt!.difference(sentAt!).inSeconds;
  }

  @override
  List<Object?> get props => [
        id,
        orderId,
        channel,
        recipient,
        subject,
        messageContent,
        status,
        sentAt,
        deliveredAt,
        openedAt,
        clickedAt,
        errorMessage,
        retryCount,
        maxRetries,
        createdAt,
      ];
}

/// Notification channel enumeration
enum NotificationChannel {
  email,
  whatsapp,
  sms,
  push;

  /// Get human-readable display name
  String get displayName {
    switch (this) {
      case NotificationChannel.email:
        return 'Email';
      case NotificationChannel.whatsapp:
        return 'WhatsApp';
      case NotificationChannel.sms:
        return 'SMS';
      case NotificationChannel.push:
        return 'Push Notification';
    }
  }
}

/// Notification status enumeration
enum NotificationStatus {
  pending,
  sent,
  delivered,
  failed,
  bounced,
  opened,
  clicked;

  /// Get human-readable display name
  String get displayName {
    switch (this) {
      case NotificationStatus.pending:
        return 'Pending';
      case NotificationStatus.sent:
        return 'Sent';
      case NotificationStatus.delivered:
        return 'Delivered';
      case NotificationStatus.failed:
        return 'Failed';
      case NotificationStatus.bounced:
        return 'Bounced';
      case NotificationStatus.opened:
        return 'Opened';
      case NotificationStatus.clicked:
        return 'Clicked';
    }
  }

  /// Check if status indicates success
  bool get isSuccessful {
    return this == NotificationStatus.delivered ||
           this == NotificationStatus.opened ||
           this == NotificationStatus.clicked;
  }
}
