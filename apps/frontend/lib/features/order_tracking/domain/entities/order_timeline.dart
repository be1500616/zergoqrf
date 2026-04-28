/// Order timeline domain entity.
/// 
/// This entity represents the complete timeline of events for an order,
/// providing a chronological view of all status changes and activities.
import 'package:equatable/equatable.dart';

/// Order timeline entity containing chronological events.
class OrderTimeline extends Equatable {
  /// Creates an order timeline entity.
  /// 
  /// Args:
  ///   orderId: Order identifier
  ///   events: List of timeline events
  ///   createdAt: Timeline creation timestamp
  ///   lastUpdated: Last update timestamp
  ///   totalEvents: Total number of events
  ///   durationMinutes: Total timeline duration in minutes
  const OrderTimeline({
    required this.orderId,
    required this.events,
    required this.createdAt,
    required this.lastUpdated,
    required this.totalEvents,
    required this.durationMinutes,
  });

  /// Order identifier
  final String orderId;

  /// List of timeline events in chronological order
  final List<TimelineEvent> events;

  /// Timeline creation timestamp
  final DateTime createdAt;

  /// Last update timestamp
  final DateTime lastUpdated;

  /// Total number of events
  final int totalEvents;

  /// Total timeline duration in minutes
  final int durationMinutes;

  /// Get the latest event
  TimelineEvent? get latestEvent {
    if (events.isEmpty) return null;
    return events.last;
  }

  /// Get events by type
  List<TimelineEvent> getEventsByType(TimelineEventType type) {
    return events.where((event) => event.type == type).toList();
  }

  /// Get status change events
  List<TimelineEvent> get statusChangeEvents {
    return getEventsByType(TimelineEventType.statusChange);
  }

  /// Get notification events
  List<TimelineEvent> get notificationEvents {
    return getEventsByType(TimelineEventType.notification);
  }

  /// Get item update events
  List<TimelineEvent> get itemUpdateEvents {
    return getEventsByType(TimelineEventType.itemUpdate);
  }

  /// Get formatted timeline for display
  List<FormattedTimelineEvent> get formattedEvents {
    return events.map((event) => FormattedTimelineEvent(
      time: _formatTime(event.timestamp),
      title: event.title,
      description: event.description,
      type: event.type,
      icon: event.icon,
      isImportant: event.isImportant,
    )).toList();
  }

  /// Format time for display
  String _formatTime(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    } else {
      return '${timestamp.day}/${timestamp.month} ${timestamp.hour}:${timestamp.minute.toString().padLeft(2, '0')}';
    }
  }

  /// Create a copy with updated fields
  OrderTimeline copyWith({
    String? orderId,
    List<TimelineEvent>? events,
    DateTime? createdAt,
    DateTime? lastUpdated,
    int? totalEvents,
    int? durationMinutes,
  }) {
    return OrderTimeline(
      orderId: orderId ?? this.orderId,
      events: events ?? this.events,
      createdAt: createdAt ?? this.createdAt,
      lastUpdated: lastUpdated ?? this.lastUpdated,
      totalEvents: totalEvents ?? this.totalEvents,
      durationMinutes: durationMinutes ?? this.durationMinutes,
    );
  }

  @override
  List<Object?> get props => [
        orderId,
        events,
        createdAt,
        lastUpdated,
        totalEvents,
        durationMinutes,
      ];
}

/// Timeline event entity
class TimelineEvent extends Equatable {
  /// Creates a timeline event entity.
  const TimelineEvent({
    required this.id,
    required this.orderId,
    required this.type,
    required this.title,
    required this.description,
    required this.timestamp,
    this.icon = 'info',
    this.isImportant = false,
    this.metadata = const {},
  });

  /// Event ID
  final String id;

  /// Order ID
  final String orderId;

  /// Event type
  final TimelineEventType type;

  /// Event title
  final String title;

  /// Event description
  final String description;

  /// Event timestamp
  final DateTime timestamp;

  /// Event icon identifier
  final String icon;

  /// Whether this is an important event
  final bool isImportant;

  /// Additional event metadata
  final Map<String, dynamic> metadata;

  /// Get relative time string
  String get relativeTime {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes} minutes ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours} hours ago';
    } else {
      return '${difference.inDays} days ago';
    }
  }

  /// Get formatted timestamp
  String get formattedTimestamp {
    return '${timestamp.hour.toString().padLeft(2, '0')}:${timestamp.minute.toString().padLeft(2, '0')}';
  }

  @override
  List<Object?> get props => [
        id,
        orderId,
        type,
        title,
        description,
        timestamp,
        icon,
        isImportant,
        metadata,
      ];
}

/// Timeline event type enumeration
enum TimelineEventType {
  statusChange,
  itemUpdate,
  notification,
  payment,
  general;

  /// Get human-readable display name
  String get displayName {
    switch (this) {
      case TimelineEventType.statusChange:
        return 'Status Change';
      case TimelineEventType.itemUpdate:
        return 'Item Update';
      case TimelineEventType.notification:
        return 'Notification';
      case TimelineEventType.payment:
        return 'Payment';
      case TimelineEventType.general:
        return 'General';
    }
  }

  /// Get default icon for event type
  String get defaultIcon {
    switch (this) {
      case TimelineEventType.statusChange:
        return 'update';
      case TimelineEventType.itemUpdate:
        return 'restaurant';
      case TimelineEventType.notification:
        return 'notifications';
      case TimelineEventType.payment:
        return 'payment';
      case TimelineEventType.general:
        return 'info';
    }
  }

  /// Get color for event type
  String get colorHex {
    switch (this) {
      case TimelineEventType.statusChange:
        return '#3B82F6'; // Blue
      case TimelineEventType.itemUpdate:
        return '#F59E0B'; // Amber
      case TimelineEventType.notification:
        return '#10B981'; // Emerald
      case TimelineEventType.payment:
        return '#8B5CF6'; // Violet
      case TimelineEventType.general:
        return '#6B7280'; // Gray
    }
  }
}

/// Formatted timeline event for display
class FormattedTimelineEvent extends Equatable {
  /// Creates a formatted timeline event.
  const FormattedTimelineEvent({
    required this.time,
    required this.title,
    required this.description,
    required this.type,
    required this.icon,
    this.isImportant = false,
  });

  /// Formatted time string
  final String time;

  /// Event title
  final String title;

  /// Event description
  final String description;

  /// Event type
  final TimelineEventType type;

  /// Event icon
  final String icon;

  /// Whether this is an important event
  final bool isImportant;

  @override
  List<Object?> get props => [
        time,
        title,
        description,
        type,
        icon,
        isImportant,
      ];
}

/// Timeline builder utility for creating timeline events
class TimelineBuilder {
  /// Create a status change event
  static TimelineEvent createStatusChangeEvent({
    required String orderId,
    required String fromStatus,
    required String toStatus,
    required DateTime timestamp,
    String? changedBy,
    String? reason,
  }) {
    return TimelineEvent(
      id: '${orderId}_status_${timestamp.millisecondsSinceEpoch}',
      orderId: orderId,
      type: TimelineEventType.statusChange,
      title: 'Order ${toStatus.toLowerCase()}',
      description: _getStatusChangeDescription(fromStatus, toStatus),
      timestamp: timestamp,
      icon: _getStatusIcon(toStatus),
      isImportant: _isImportantStatusChange(toStatus),
      metadata: {
        'from_status': fromStatus,
        'to_status': toStatus,
        'changed_by': changedBy,
        'reason': reason,
      },
    );
  }

  /// Create an item update event
  static TimelineEvent createItemUpdateEvent({
    required String orderId,
    required String itemName,
    required String status,
    required DateTime timestamp,
    String? assignedTo,
    String? notes,
  }) {
    return TimelineEvent(
      id: '${orderId}_item_${timestamp.millisecondsSinceEpoch}',
      orderId: orderId,
      type: TimelineEventType.itemUpdate,
      title: '$itemName ${status.toLowerCase()}',
      description: _getItemUpdateDescription(itemName, status),
      timestamp: timestamp,
      icon: 'restaurant',
      isImportant: status == 'ready',
      metadata: {
        'item_name': itemName,
        'status': status,
        'assigned_to': assignedTo,
        'notes': notes,
      },
    );
  }

  /// Create a notification event
  static TimelineEvent createNotificationEvent({
    required String orderId,
    required String channel,
    required String status,
    required DateTime timestamp,
    String? recipient,
  }) {
    return TimelineEvent(
      id: '${orderId}_notification_${timestamp.millisecondsSinceEpoch}',
      orderId: orderId,
      type: TimelineEventType.notification,
      title: '${channel.toUpperCase()} notification $status',
      description: _getNotificationDescription(channel, status),
      timestamp: timestamp,
      icon: 'notifications',
      isImportant: false,
      metadata: {
        'channel': channel,
        'status': status,
        'recipient': recipient,
      },
    );
  }

  static String _getStatusChangeDescription(String fromStatus, String toStatus) {
    final descriptions = {
      'placed_confirmed': 'Your order has been confirmed and is being prepared',
      'confirmed_preparing': 'Kitchen has started preparing your order',
      'preparing_ready': 'Your order is ready for pickup',
      'ready_completed': 'Order has been completed successfully',
      'placed_cancelled': 'Order has been cancelled',
      'confirmed_cancelled': 'Order has been cancelled',
      'preparing_cancelled': 'Order has been cancelled during preparation',
    };

    final key = '${fromStatus}_$toStatus';
    return descriptions[key] ?? 'Order status changed from $fromStatus to $toStatus';
  }

  static String _getItemUpdateDescription(String itemName, String status) {
    switch (status.toLowerCase()) {
      case 'preparing':
        return 'Kitchen started preparing $itemName';
      case 'ready':
        return '$itemName is ready to serve';
      case 'served':
        return '$itemName has been served';
      case 'cancelled':
        return '$itemName has been cancelled';
      default:
        return '$itemName status updated to $status';
    }
  }

  static String _getNotificationDescription(String channel, String status) {
    switch (status.toLowerCase()) {
      case 'sent':
        return 'Notification sent via $channel';
      case 'delivered':
        return 'Notification delivered via $channel';
      case 'failed':
        return 'Notification failed to send via $channel';
      default:
        return 'Notification $status via $channel';
    }
  }

  static String _getStatusIcon(String status) {
    switch (status.toLowerCase()) {
      case 'placed':
        return 'receipt';
      case 'confirmed':
        return 'check_circle';
      case 'preparing':
        return 'restaurant';
      case 'ready':
        return 'done_all';
      case 'completed':
        return 'celebration';
      case 'cancelled':
        return 'cancel';
      default:
        return 'info';
    }
  }

  static bool _isImportantStatusChange(String status) {
    return ['confirmed', 'ready', 'completed', 'cancelled'].contains(status.toLowerCase());
  }
}
