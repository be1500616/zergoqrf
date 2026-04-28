/// Notification preference domain entity.
/// 
/// This entity represents customer notification preferences for order tracking,
/// including channel preferences, timing settings, and privacy controls.
import 'package:equatable/equatable.dart';

/// Notification preference entity for customer communication settings.
class NotificationPreference extends Equatable {
  /// Creates a notification preference entity.
  /// 
  /// Args:
  ///   id: Unique preference identifier
  ///   restaurantId: Restaurant identifier
  ///   customerPhone: Customer phone number
  ///   customerEmail: Customer email address
  ///   customerName: Customer name
  ///   emailEnabled: Whether email notifications are enabled
  ///   whatsappEnabled: Whether WhatsApp notifications are enabled
  ///   smsEnabled: Whether SMS notifications are enabled
  ///   immediateNotifications: Whether to send immediate notifications
  ///   statusChangeNotifications: Whether to send status change notifications
  ///   etaUpdateNotifications: Whether to send ETA update notifications
  ///   completionNotifications: Whether to send completion notifications
  ///   businessHoursOnly: Whether to only send during business hours
  ///   quietHoursStart: Start of quiet hours (HH:MM format)
  ///   quietHoursEnd: End of quiet hours (HH:MM format)
  ///   optOutAll: Whether customer has opted out of all notifications
  ///   privacyConsent: Whether customer has given privacy consent
  ///   createdAt: Creation timestamp
  ///   updatedAt: Last update timestamp
  const NotificationPreference({
    required this.id,
    required this.restaurantId,
    this.customerPhone,
    this.customerEmail,
    this.customerName,
    this.emailEnabled = true,
    this.whatsappEnabled = false,
    this.smsEnabled = false,
    this.immediateNotifications = true,
    this.statusChangeNotifications = true,
    this.etaUpdateNotifications = true,
    this.completionNotifications = true,
    this.businessHoursOnly = false,
    this.quietHoursStart,
    this.quietHoursEnd,
    this.optOutAll = false,
    this.privacyConsent = false,
    required this.createdAt,
    required this.updatedAt,
  });

  /// Unique preference identifier
  final String id;

  /// Restaurant identifier
  final String restaurantId;

  /// Customer phone number
  final String? customerPhone;

  /// Customer email address
  final String? customerEmail;

  /// Customer name
  final String? customerName;

  /// Whether email notifications are enabled
  final bool emailEnabled;

  /// Whether WhatsApp notifications are enabled
  final bool whatsappEnabled;

  /// Whether SMS notifications are enabled
  final bool smsEnabled;

  /// Whether to send immediate notifications
  final bool immediateNotifications;

  /// Whether to send status change notifications
  final bool statusChangeNotifications;

  /// Whether to send ETA update notifications
  final bool etaUpdateNotifications;

  /// Whether to send completion notifications
  final bool completionNotifications;

  /// Whether to only send during business hours
  final bool businessHoursOnly;

  /// Start of quiet hours (HH:MM format)
  final String? quietHoursStart;

  /// End of quiet hours (HH:MM format)
  final String? quietHoursEnd;

  /// Whether customer has opted out of all notifications
  final bool optOutAll;

  /// Whether customer has given privacy consent
  final bool privacyConsent;

  /// Creation timestamp
  final DateTime createdAt;

  /// Last update timestamp
  final DateTime updatedAt;

  /// Get enabled notification channels
  List<NotificationChannel> get enabledChannels {
    final channels = <NotificationChannel>[];
    
    if (emailEnabled && customerEmail != null) {
      channels.add(NotificationChannel.email);
    }
    if (whatsappEnabled && customerPhone != null) {
      channels.add(NotificationChannel.whatsapp);
    }
    if (smsEnabled && customerPhone != null) {
      channels.add(NotificationChannel.sms);
    }
    
    return channels;
  }

  /// Check if any notifications are enabled
  bool get hasEnabledNotifications {
    return !optOutAll && enabledChannels.isNotEmpty;
  }

  /// Check if customer has provided contact information
  bool get hasContactInfo {
    return customerEmail != null || customerPhone != null;
  }

  /// Check if current time is within quiet hours
  bool isInQuietHours([DateTime? checkTime]) {
    if (quietHoursStart == null || quietHoursEnd == null) return false;
    
    final time = checkTime ?? DateTime.now();
    final currentTime = '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
    
    // Handle quiet hours that span midnight
    if (quietHoursStart!.compareTo(quietHoursEnd!) <= 0) {
      return currentTime.compareTo(quietHoursStart!) >= 0 && 
             currentTime.compareTo(quietHoursEnd!) <= 0;
    } else {
      return currentTime.compareTo(quietHoursStart!) >= 0 || 
             currentTime.compareTo(quietHoursEnd!) <= 0;
    }
  }

  /// Check if notification should be sent based on preferences
  bool shouldSendNotification(
    NotificationTrigger trigger, {
    DateTime? currentTime,
  }) {
    // Check if opted out of all notifications
    if (optOutAll) return false;
    
    // Check if any channels are enabled
    if (enabledChannels.isEmpty) return false;
    
    // Check trigger-specific preferences
    switch (trigger) {
      case NotificationTrigger.orderConfirmed:
      case NotificationTrigger.orderPreparing:
      case NotificationTrigger.orderReady:
      case NotificationTrigger.orderCompleted:
      case NotificationTrigger.orderCancelled:
        if (!statusChangeNotifications) return false;
        break;
      case NotificationTrigger.etaUpdated:
        if (!etaUpdateNotifications) return false;
        break;
      case NotificationTrigger.itemReady:
        if (!completionNotifications) return false;
        break;
      case NotificationTrigger.custom:
        // Custom notifications follow immediate notification setting
        break;
    }
    
    // Check immediate notification preference
    if (!immediateNotifications && trigger.shouldSendImmediately) {
      return false;
    }
    
    // Check quiet hours
    if (isInQuietHours(currentTime)) return false;
    
    // Check business hours (would need business hours configuration)
    if (businessHoursOnly) {
      // This would need to be implemented with restaurant business hours
      // For now, assume business hours are 9 AM to 10 PM
      final time = currentTime ?? DateTime.now();
      if (time.hour < 9 || time.hour >= 22) return false;
    }
    
    return true;
  }

  /// Get notification preference summary
  NotificationPreferenceSummary get summary {
    return NotificationPreferenceSummary(
      totalChannels: enabledChannels.length,
      enabledChannels: enabledChannels,
      hasQuietHours: quietHoursStart != null && quietHoursEnd != null,
      quietHoursRange: quietHoursStart != null && quietHoursEnd != null
          ? '$quietHoursStart - $quietHoursEnd'
          : null,
      isOptedOut: optOutAll,
      hasPrivacyConsent: privacyConsent,
    );
  }

  /// Create a copy with updated fields
  NotificationPreference copyWith({
    String? id,
    String? restaurantId,
    String? customerPhone,
    String? customerEmail,
    String? customerName,
    bool? emailEnabled,
    bool? whatsappEnabled,
    bool? smsEnabled,
    bool? immediateNotifications,
    bool? statusChangeNotifications,
    bool? etaUpdateNotifications,
    bool? completionNotifications,
    bool? businessHoursOnly,
    String? quietHoursStart,
    String? quietHoursEnd,
    bool? optOutAll,
    bool? privacyConsent,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return NotificationPreference(
      id: id ?? this.id,
      restaurantId: restaurantId ?? this.restaurantId,
      customerPhone: customerPhone ?? this.customerPhone,
      customerEmail: customerEmail ?? this.customerEmail,
      customerName: customerName ?? this.customerName,
      emailEnabled: emailEnabled ?? this.emailEnabled,
      whatsappEnabled: whatsappEnabled ?? this.whatsappEnabled,
      smsEnabled: smsEnabled ?? this.smsEnabled,
      immediateNotifications: immediateNotifications ?? this.immediateNotifications,
      statusChangeNotifications: statusChangeNotifications ?? this.statusChangeNotifications,
      etaUpdateNotifications: etaUpdateNotifications ?? this.etaUpdateNotifications,
      completionNotifications: completionNotifications ?? this.completionNotifications,
      businessHoursOnly: businessHoursOnly ?? this.businessHoursOnly,
      quietHoursStart: quietHoursStart ?? this.quietHoursStart,
      quietHoursEnd: quietHoursEnd ?? this.quietHoursEnd,
      optOutAll: optOutAll ?? this.optOutAll,
      privacyConsent: privacyConsent ?? this.privacyConsent,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        restaurantId,
        customerPhone,
        customerEmail,
        customerName,
        emailEnabled,
        whatsappEnabled,
        smsEnabled,
        immediateNotifications,
        statusChangeNotifications,
        etaUpdateNotifications,
        completionNotifications,
        businessHoursOnly,
        quietHoursStart,
        quietHoursEnd,
        optOutAll,
        privacyConsent,
        createdAt,
        updatedAt,
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

  /// Get icon identifier
  String get icon {
    switch (this) {
      case NotificationChannel.email:
        return 'email';
      case NotificationChannel.whatsapp:
        return 'chat';
      case NotificationChannel.sms:
        return 'sms';
      case NotificationChannel.push:
        return 'notifications';
    }
  }

  /// Check if channel requires phone number
  bool get requiresPhoneNumber {
    return this == NotificationChannel.whatsapp || this == NotificationChannel.sms;
  }

  /// Check if channel requires email address
  bool get requiresEmailAddress {
    return this == NotificationChannel.email;
  }

  /// Check if channel supports rich content
  bool get supportsRichContent {
    return this == NotificationChannel.email || this == NotificationChannel.push;
  }
}

/// Notification trigger enumeration
enum NotificationTrigger {
  orderConfirmed,
  orderPreparing,
  orderReady,
  orderCompleted,
  orderCancelled,
  etaUpdated,
  itemReady,
  custom;

  /// Get human-readable display name
  String get displayName {
    switch (this) {
      case NotificationTrigger.orderConfirmed:
        return 'Order Confirmed';
      case NotificationTrigger.orderPreparing:
        return 'Order Preparing';
      case NotificationTrigger.orderReady:
        return 'Order Ready';
      case NotificationTrigger.orderCompleted:
        return 'Order Completed';
      case NotificationTrigger.orderCancelled:
        return 'Order Cancelled';
      case NotificationTrigger.etaUpdated:
        return 'ETA Updated';
      case NotificationTrigger.itemReady:
        return 'Item Ready';
      case NotificationTrigger.custom:
        return 'Custom';
    }
  }

  /// Check if trigger should send immediately
  bool get shouldSendImmediately {
    return [
      NotificationTrigger.orderConfirmed,
      NotificationTrigger.orderReady,
      NotificationTrigger.orderCancelled,
    ].contains(this);
  }

  /// Get default message template
  String get defaultMessageTemplate {
    switch (this) {
      case NotificationTrigger.orderConfirmed:
        return 'Your order #{orderNumber} has been confirmed! Estimated preparation time: {eta}';
      case NotificationTrigger.orderPreparing:
        return 'Great news! Your order #{orderNumber} is now being prepared by our kitchen team.';
      case NotificationTrigger.orderReady:
        return 'Your order #{orderNumber} is ready for pickup! Please collect it from the counter.';
      case NotificationTrigger.orderCompleted:
        return 'Thank you! Your order #{orderNumber} has been completed. We hope you enjoyed your meal!';
      case NotificationTrigger.orderCancelled:
        return 'We\'re sorry, but your order #{orderNumber} has been cancelled. Please contact us for assistance.';
      case NotificationTrigger.etaUpdated:
        return 'Update: Your order #{orderNumber} estimated completion time has been updated to {eta}';
      case NotificationTrigger.itemReady:
        return 'One of your items from order #{orderNumber} is ready: {itemName}';
      case NotificationTrigger.custom:
        return 'Order #{orderNumber}: {customMessage}';
    }
  }
}

/// Notification preference summary for display
class NotificationPreferenceSummary extends Equatable {
  /// Creates a notification preference summary.
  const NotificationPreferenceSummary({
    required this.totalChannels,
    required this.enabledChannels,
    required this.hasQuietHours,
    this.quietHoursRange,
    required this.isOptedOut,
    required this.hasPrivacyConsent,
  });

  /// Total number of enabled channels
  final int totalChannels;

  /// List of enabled channels
  final List<NotificationChannel> enabledChannels;

  /// Whether quiet hours are configured
  final bool hasQuietHours;

  /// Quiet hours range string
  final String? quietHoursRange;

  /// Whether customer has opted out
  final bool isOptedOut;

  /// Whether customer has given privacy consent
  final bool hasPrivacyConsent;

  /// Get summary text
  String get summaryText {
    if (isOptedOut) {
      return 'All notifications disabled';
    }
    
    if (totalChannels == 0) {
      return 'No notification channels enabled';
    }
    
    final channelNames = enabledChannels.map((c) => c.displayName).join(', ');
    return '$totalChannels channel${totalChannels == 1 ? '' : 's'} enabled: $channelNames';
  }

  @override
  List<Object?> get props => [
        totalChannels,
        enabledChannels,
        hasQuietHours,
        quietHoursRange,
        isOptedOut,
        hasPrivacyConsent,
      ];
}
