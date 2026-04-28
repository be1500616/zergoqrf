/// Order status update domain entity.
/// 
/// This entity represents a single status change event in the order lifecycle,
/// providing detailed information about when, why, and by whom the status was changed.
import 'package:equatable/equatable.dart';

/// Order status update entity representing a status change event.
class OrderStatusUpdate extends Equatable {
  /// Creates an order status update entity.
  /// 
  /// Args:
  ///   id: Unique update identifier
  ///   orderId: Order identifier
  ///   status: New status
  ///   previousStatus: Previous status
  ///   changedBy: User who made the change
  ///   changedAt: Change timestamp
  ///   estimatedCompletionTime: Estimated completion time
  ///   actualCompletionTime: Actual completion time
  ///   preparationNotes: Preparation notes
  ///   changeReason: Reason for the change
  ///   systemGenerated: Whether change was system-generated
  ///   createdAt: Creation timestamp
  const OrderStatusUpdate({
    required this.id,
    required this.orderId,
    required this.status,
    this.previousStatus,
    this.changedBy,
    required this.changedAt,
    this.estimatedCompletionTime,
    this.actualCompletionTime,
    this.preparationNotes,
    this.changeReason,
    this.systemGenerated = false,
    required this.createdAt,
  });

  /// Unique update identifier
  final String id;

  /// Order identifier
  final String orderId;

  /// New status
  final String status;

  /// Previous status
  final String? previousStatus;

  /// User who made the change
  final String? changedBy;

  /// Change timestamp
  final DateTime changedAt;

  /// Estimated completion time
  final DateTime? estimatedCompletionTime;

  /// Actual completion time
  final DateTime? actualCompletionTime;

  /// Preparation notes
  final String? preparationNotes;

  /// Reason for the change
  final String? changeReason;

  /// Whether change was system-generated
  final bool systemGenerated;

  /// Creation timestamp
  final DateTime createdAt;

  /// Check if this was a manual change
  bool get isManualChange {
    return !systemGenerated && changedBy != null;
  }

  /// Get duration since change in minutes
  int get durationSinceChangeMinutes {
    return DateTime.now().difference(changedAt).inMinutes;
  }

  /// Get human-readable change description
  String get changeDescription {
    if (previousStatus == null) {
      return 'Order $status';
    }
    return 'Status changed from $previousStatus to $status';
  }

  /// Get formatted change time
  String get formattedChangeTime {
    final now = DateTime.now();
    final difference = now.difference(changedAt);

    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes} minutes ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours} hours ago';
    } else {
      return '${changedAt.day}/${changedAt.month} at ${changedAt.hour}:${changedAt.minute.toString().padLeft(2, '0')}';
    }
  }

  /// Get estimated time remaining in minutes
  int? get estimatedTimeRemainingMinutes {
    if (estimatedCompletionTime == null) return null;
    final now = DateTime.now();
    if (estimatedCompletionTime!.isBefore(now)) return 0;
    return estimatedCompletionTime!.difference(now).inMinutes;
  }

  /// Check if estimated time has passed
  bool get isOverdue {
    if (estimatedCompletionTime == null) return false;
    return DateTime.now().isAfter(estimatedCompletionTime!);
  }

  /// Get duration from change to completion in minutes
  int? get completionDurationMinutes {
    if (actualCompletionTime == null) return null;
    return actualCompletionTime!.difference(changedAt).inMinutes;
  }

  /// Check if ETA was accurate within tolerance
  bool? isETAAccurate({int toleranceMinutes = 5}) {
    if (estimatedCompletionTime == null || actualCompletionTime == null) {
      return null;
    }
    
    final difference = (actualCompletionTime!.difference(estimatedCompletionTime!)).abs();
    return difference.inMinutes <= toleranceMinutes;
  }

  /// Get status display information
  StatusDisplayInfo get statusDisplayInfo {
    return StatusDisplayInfo.fromStatus(status);
  }

  /// Create a copy with updated fields
  OrderStatusUpdate copyWith({
    String? id,
    String? orderId,
    String? status,
    String? previousStatus,
    String? changedBy,
    DateTime? changedAt,
    DateTime? estimatedCompletionTime,
    DateTime? actualCompletionTime,
    String? preparationNotes,
    String? changeReason,
    bool? systemGenerated,
    DateTime? createdAt,
  }) {
    return OrderStatusUpdate(
      id: id ?? this.id,
      orderId: orderId ?? this.orderId,
      status: status ?? this.status,
      previousStatus: previousStatus ?? this.previousStatus,
      changedBy: changedBy ?? this.changedBy,
      changedAt: changedAt ?? this.changedAt,
      estimatedCompletionTime: estimatedCompletionTime ?? this.estimatedCompletionTime,
      actualCompletionTime: actualCompletionTime ?? this.actualCompletionTime,
      preparationNotes: preparationNotes ?? this.preparationNotes,
      changeReason: changeReason ?? this.changeReason,
      systemGenerated: systemGenerated ?? this.systemGenerated,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        orderId,
        status,
        previousStatus,
        changedBy,
        changedAt,
        estimatedCompletionTime,
        actualCompletionTime,
        preparationNotes,
        changeReason,
        systemGenerated,
        createdAt,
      ];
}

/// Status display information for UI rendering
class StatusDisplayInfo extends Equatable {
  /// Creates status display information.
  const StatusDisplayInfo({
    required this.displayName,
    required this.description,
    required this.colorHex,
    required this.icon,
    required this.progressValue,
    required this.isTerminal,
  });

  /// Human-readable display name
  final String displayName;

  /// Status description
  final String description;

  /// Color hex code for UI
  final String colorHex;

  /// Icon identifier
  final String icon;

  /// Progress value (0.0 to 1.0)
  final double progressValue;

  /// Whether this is a terminal status
  final bool isTerminal;

  /// Create status display info from status string
  factory StatusDisplayInfo.fromStatus(String status) {
    switch (status.toLowerCase()) {
      case 'placed':
        return const StatusDisplayInfo(
          displayName: 'Placed',
          description: 'Order has been placed and is awaiting confirmation',
          colorHex: '#6B7280',
          icon: 'receipt',
          progressValue: 0.1,
          isTerminal: false,
        );
      case 'confirmed':
        return const StatusDisplayInfo(
          displayName: 'Confirmed',
          description: 'Order has been confirmed and will be prepared soon',
          colorHex: '#3B82F6',
          icon: 'check_circle',
          progressValue: 0.25,
          isTerminal: false,
        );
      case 'preparing':
        return const StatusDisplayInfo(
          displayName: 'Preparing',
          description: 'Kitchen is preparing your order',
          colorHex: '#F59E0B',
          icon: 'restaurant',
          progressValue: 0.5,
          isTerminal: false,
        );
      case 'ready':
        return const StatusDisplayInfo(
          displayName: 'Ready',
          description: 'Order is ready for pickup or delivery',
          colorHex: '#10B981',
          icon: 'done_all',
          progressValue: 0.8,
          isTerminal: false,
        );
      case 'completed':
        return const StatusDisplayInfo(
          displayName: 'Completed',
          description: 'Order has been completed successfully',
          colorHex: '#059669',
          icon: 'celebration',
          progressValue: 1.0,
          isTerminal: true,
        );
      case 'cancelled':
        return const StatusDisplayInfo(
          displayName: 'Cancelled',
          description: 'Order has been cancelled',
          colorHex: '#EF4444',
          icon: 'cancel',
          progressValue: 0.0,
          isTerminal: true,
        );
      default:
        return const StatusDisplayInfo(
          displayName: 'Unknown',
          description: 'Unknown status',
          colorHex: '#6B7280',
          icon: 'help',
          progressValue: 0.0,
          isTerminal: false,
        );
    }
  }

  @override
  List<Object?> get props => [
        displayName,
        description,
        colorHex,
        icon,
        progressValue,
        isTerminal,
      ];
}

/// Real-time status update event for WebSocket/SSE
class RealtimeStatusUpdate extends Equatable {
  /// Creates a real-time status update event.
  const RealtimeStatusUpdate({
    required this.orderId,
    required this.newStatus,
    required this.previousStatus,
    this.estimatedCompletionTime,
    this.changedBy,
    required this.timestamp,
    this.eventType = 'status_updated',
  });

  /// Order identifier
  final String orderId;

  /// New status
  final String newStatus;

  /// Previous status
  final String previousStatus;

  /// Estimated completion time
  final DateTime? estimatedCompletionTime;

  /// User who made the change
  final String? changedBy;

  /// Event timestamp
  final DateTime timestamp;

  /// Event type identifier
  final String eventType;

  /// Create from JSON data
  factory RealtimeStatusUpdate.fromJson(Map<String, dynamic> json) {
    return RealtimeStatusUpdate(
      orderId: json['order_id'] as String,
      newStatus: json['new_status'] as String,
      previousStatus: json['previous_status'] as String,
      estimatedCompletionTime: json['estimated_completion_time'] != null
          ? DateTime.parse(json['estimated_completion_time'] as String)
          : null,
      changedBy: json['changed_by'] as String?,
      timestamp: DateTime.parse(json['timestamp'] as String),
      eventType: json['event_type'] as String? ?? 'status_updated',
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'order_id': orderId,
      'new_status': newStatus,
      'previous_status': previousStatus,
      'estimated_completion_time': estimatedCompletionTime?.toIso8601String(),
      'changed_by': changedBy,
      'timestamp': timestamp.toIso8601String(),
      'event_type': eventType,
    };
  }

  /// Get human-readable update message
  String get updateMessage {
    switch (newStatus.toLowerCase()) {
      case 'confirmed':
        return 'Your order has been confirmed!';
      case 'preparing':
        return 'Kitchen is now preparing your order';
      case 'ready':
        return 'Your order is ready for pickup!';
      case 'completed':
        return 'Order completed successfully';
      case 'cancelled':
        return 'Order has been cancelled';
      default:
        return 'Order status updated to $newStatus';
    }
  }

  /// Check if this update should trigger a notification
  bool get shouldNotify {
    return ['confirmed', 'ready', 'completed', 'cancelled'].contains(newStatus.toLowerCase());
  }

  @override
  List<Object?> get props => [
        orderId,
        newStatus,
        previousStatus,
        estimatedCompletionTime,
        changedBy,
        timestamp,
        eventType,
      ];
}
