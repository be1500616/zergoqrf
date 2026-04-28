/// Order tracking GetX controller.
/// 
/// This controller manages the state and business logic for order tracking,
/// including real-time updates, status management, and user interactions.
import 'dart:async';
import 'package:get/get.dart';
import 'package:flutter/foundation.dart';

import '../../domain/entities/order_tracking.dart';
import '../../domain/entities/order_timeline.dart';
import '../../domain/entities/order_status_update.dart';
import '../../domain/entities/notification_preference.dart';
import '../../domain/repositories/order_tracking_repository.dart';
import '../use_cases/fetch_order_tracking.dart';
import '../use_cases/subscribe_order_updates.dart';
import '../use_cases/update_order_status.dart';

/// GetX controller for order tracking functionality.
class OrderTrackingController extends GetxController {
  /// Creates an order tracking controller.
  OrderTrackingController({
    required OrderTrackingRepository repository,
    required FetchOrderTrackingUseCase fetchOrderTrackingUseCase,
    required SubscribeOrderUpdatesUseCase subscribeOrderUpdatesUseCase,
    required UpdateOrderStatusUseCase updateOrderStatusUseCase,
  })  : _repository = repository,
        _fetchOrderTrackingUseCase = fetchOrderTrackingUseCase,
        _subscribeOrderUpdatesUseCase = subscribeOrderUpdatesUseCase,
        _updateOrderStatusUseCase = updateOrderStatusUseCase;

  final OrderTrackingRepository _repository;
  final FetchOrderTrackingUseCase _fetchOrderTrackingUseCase;
  final SubscribeOrderUpdatesUseCase _subscribeOrderUpdatesUseCase;
  final UpdateOrderStatusUseCase _updateOrderStatusUseCase;

  // Reactive state variables
  final _orderTracking = Rxn<OrderTracking>();
  final _timeline = Rxn<OrderTimeline>();
  final _notificationPreferences = Rxn<NotificationPreference>();
  final _isLoading = false.obs;
  final _isRefreshing = false.obs;
  final _error = Rxn<String>();
  final _isConnected = false.obs;
  final _lastUpdateTime = Rxn<DateTime>();

  // Real-time subscription
  StreamSubscription<RealtimeStatusUpdate>? _realtimeSubscription;
  Timer? _refreshTimer;

  // Getters for reactive state
  OrderTracking? get orderTracking => _orderTracking.value;
  OrderTimeline? get timeline => _timeline.value;
  NotificationPreference? get notificationPreferences => _notificationPreferences.value;
  bool get isLoading => _isLoading.value;
  bool get isRefreshing => _isRefreshing.value;
  String? get error => _error.value;
  bool get isConnected => _isConnected.value;
  DateTime? get lastUpdateTime => _lastUpdateTime.value;

  // Computed properties
  bool get hasData => orderTracking != null;
  bool get hasError => error != null;
  bool get isOrderComplete => orderTracking?.currentStatus.isTerminal ?? false;
  double get overallProgress => orderTracking?.overallProgress ?? 0.0;
  int get estimatedTimeRemainingMinutes => orderTracking?.estimatedTimeRemainingMinutes ?? 0;
  bool get isOverdue => orderTracking?.isOverdue ?? false;
  String get nextAction => orderTracking?.nextAction ?? 'Loading...';
  String get statusSummary => orderTracking?.statusSummary ?? 'No status available';

  @override
  void onInit() {
    super.onInit();
    debugPrint('OrderTrackingController initialized');
  }

  @override
  void onClose() {
    _cleanup();
    super.onClose();
  }

  /// Fetch order tracking information.
  /// 
  /// Args:
  ///   orderId: Order identifier
  ///   includeNotifications: Whether to include notification history
  ///   forceRefresh: Whether to force refresh from server
  Future<void> fetchOrderTracking(
    String orderId, {
    bool includeNotifications = true,
    bool forceRefresh = false,
  }) async {
    try {
      if (!forceRefresh && hasData && !hasError) {
        debugPrint('Using cached order tracking data');
        return;
      }

      _setLoading(true);
      _clearError();

      debugPrint('Fetching order tracking for order: $orderId');

      final tracking = await _fetchOrderTrackingUseCase.execute(
        orderId,
        includeNotifications: includeNotifications,
      );

      _orderTracking.value = tracking;
      _lastUpdateTime.value = DateTime.now();

      // Fetch timeline separately for better performance
      await _fetchTimeline(orderId);

      // Subscribe to real-time updates
      await _subscribeToUpdates(orderId);

      debugPrint('Successfully fetched order tracking');
    } catch (e) {
      debugPrint('Error fetching order tracking: $e');
      _setError('Failed to load order tracking: ${e.toString()}');
    } finally {
      _setLoading(false);
    }
  }

  /// Fetch order tracking by order number.
  /// 
  /// Args:
  ///   orderNumber: Human-readable order number
  ///   includeNotifications: Whether to include notification history
  Future<void> fetchOrderTrackingByNumber(
    String orderNumber, {
    bool includeNotifications = true,
  }) async {
    try {
      _setLoading(true);
      _clearError();

      debugPrint('Fetching order tracking for order number: $orderNumber');

      final tracking = await _repository.getOrderTrackingByNumber(
        orderNumber,
        includeNotifications: includeNotifications,
      );

      _orderTracking.value = tracking;
      _lastUpdateTime.value = DateTime.now();

      // Fetch timeline and subscribe to updates
      await _fetchTimeline(tracking.orderId);
      await _subscribeToUpdates(tracking.orderId);

      debugPrint('Successfully fetched order tracking by number');
    } catch (e) {
      debugPrint('Error fetching order tracking by number: $e');
      _setError('Failed to load order: ${e.toString()}');
    } finally {
      _setLoading(false);
    }
  }

  /// Refresh order tracking data.
  Future<void> refreshOrderTracking() async {
    if (orderTracking == null) return;

    try {
      _setRefreshing(true);
      await fetchOrderTracking(
        orderTracking!.orderId,
        forceRefresh: true,
      );
    } finally {
      _setRefreshing(false);
    }
  }

  /// Update order status (for restaurant staff).
  /// 
  /// Args:
  ///   newStatus: New order status
  ///   estimatedCompletionTime: Optional estimated completion time
  ///   preparationNotes: Optional preparation notes
  ///   changeReason: Optional reason for the change
  ///   notifyCustomer: Whether to notify customer
  Future<bool> updateOrderStatus(
    String newStatus, {
    DateTime? estimatedCompletionTime,
    String? preparationNotes,
    String? changeReason,
    bool notifyCustomer = true,
  }) async {
    if (orderTracking == null) return false;

    try {
      _setLoading(true);
      _clearError();

      debugPrint('Updating order status to: $newStatus');

      final statusUpdate = await _updateOrderStatusUseCase.execute(
        orderTracking!.orderId,
        newStatus,
        estimatedCompletionTime: estimatedCompletionTime,
        preparationNotes: preparationNotes,
        changeReason: changeReason,
        notifyCustomer: notifyCustomer,
      );

      // Update local state
      final updatedTracking = orderTracking!.copyWith(
        currentStatus: OrderStatus.values.firstWhere(
          (status) => status.name == newStatus,
          orElse: () => orderTracking!.currentStatus,
        ),
        estimatedCompletionTime: estimatedCompletionTime,
        statusHistory: [...orderTracking!.statusHistory, statusUpdate],
        lastUpdated: DateTime.now(),
      );

      _orderTracking.value = updatedTracking;
      _lastUpdateTime.value = DateTime.now();

      debugPrint('Successfully updated order status');
      return true;
    } catch (e) {
      debugPrint('Error updating order status: $e');
      _setError('Failed to update status: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Update order item status.
  /// 
  /// Args:
  ///   itemId: Order item identifier
  ///   newStatus: New item status
  ///   preparationNotes: Optional preparation notes
  ///   estimatedReadyTime: Optional estimated ready time
  ///   qualityCheckPassed: Optional quality check result
  ///   qualityNotes: Optional quality check notes
  Future<bool> updateOrderItemStatus(
    String itemId,
    OrderItemStatus newStatus, {
    String? preparationNotes,
    DateTime? estimatedReadyTime,
    bool? qualityCheckPassed,
    String? qualityNotes,
  }) async {
    if (orderTracking == null) return false;

    try {
      _setLoading(true);
      _clearError();

      debugPrint('Updating item $itemId status to: ${newStatus.name}');

      final itemTracking = await _repository.updateOrderItemStatus(
        orderTracking!.orderId,
        itemId,
        newStatus,
        preparationNotes: preparationNotes,
        estimatedReadyTime: estimatedReadyTime,
        qualityCheckPassed: qualityCheckPassed,
        qualityNotes: qualityNotes,
      );

      // Update local state
      final updatedItemTracking = orderTracking!.itemTracking.map((item) {
        return item.orderItemId == itemId ? itemTracking : item;
      }).toList();

      final updatedTracking = orderTracking!.copyWith(
        itemTracking: updatedItemTracking,
        lastUpdated: DateTime.now(),
      );

      _orderTracking.value = updatedTracking;
      _lastUpdateTime.value = DateTime.now();

      debugPrint('Successfully updated item status');
      return true;
    } catch (e) {
      debugPrint('Error updating item status: $e');
      _setError('Failed to update item status: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Send notification to customer.
  /// 
  /// Args:
  ///   trigger: Notification trigger
  ///   channels: List of notification channels
  ///   customMessage: Optional custom message
  ///   customSubject: Optional custom subject
  ///   immediate: Whether to send immediately
  Future<bool> sendNotification(
    NotificationTrigger trigger, {
    List<NotificationChannel> channels = const [],
    String? customMessage,
    String? customSubject,
    bool immediate = false,
  }) async {
    if (orderTracking == null) return false;

    try {
      _setLoading(true);
      _clearError();

      debugPrint('Sending notification: ${trigger.name}');

      final notifications = await _repository.sendNotification(
        orderTracking!.orderId,
        trigger,
        channels: channels,
        customMessage: customMessage,
        customSubject: customSubject,
        immediate: immediate,
      );

      // Update local state with new notifications
      final updatedTracking = orderTracking!.copyWith(
        notificationsSent: [...orderTracking!.notificationsSent, ...notifications],
        lastUpdated: DateTime.now(),
      );

      _orderTracking.value = updatedTracking;
      _lastUpdateTime.value = DateTime.now();

      debugPrint('Successfully sent ${notifications.length} notifications');
      return true;
    } catch (e) {
      debugPrint('Error sending notification: $e');
      _setError('Failed to send notification: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Fetch notification preferences.
  /// 
  /// Args:
  ///   restaurantId: Restaurant identifier
  ///   customerIdentifier: Customer phone or email
  Future<void> fetchNotificationPreferences(
    String restaurantId,
    String customerIdentifier,
  ) async {
    try {
      debugPrint('Fetching notification preferences');

      final preferences = await _repository.getNotificationPreferences(
        restaurantId,
        customerIdentifier,
      );

      _notificationPreferences.value = preferences;
      debugPrint('Successfully fetched notification preferences');
    } catch (e) {
      debugPrint('Error fetching notification preferences: $e');
      // Don't set error for preferences as it's not critical
    }
  }

  /// Update notification preferences.
  /// 
  /// Args:
  ///   preferences: Updated notification preferences
  Future<bool> updateNotificationPreferences(
    NotificationPreference preferences,
  ) async {
    try {
      _setLoading(true);
      _clearError();

      debugPrint('Updating notification preferences');

      final updatedPreferences = await _repository.updateNotificationPreferences(preferences);
      _notificationPreferences.value = updatedPreferences;

      debugPrint('Successfully updated notification preferences');
      return true;
    } catch (e) {
      debugPrint('Error updating notification preferences: $e');
      _setError('Failed to update preferences: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Start periodic refresh of order data.
  /// 
  /// Args:
  ///   intervalSeconds: Refresh interval in seconds
  void startPeriodicRefresh({int intervalSeconds = 30}) {
    _refreshTimer?.cancel();
    _refreshTimer = Timer.periodic(
      Duration(seconds: intervalSeconds),
      (_) => refreshOrderTracking(),
    );
    debugPrint('Started periodic refresh every ${intervalSeconds}s');
  }

  /// Stop periodic refresh.
  void stopPeriodicRefresh() {
    _refreshTimer?.cancel();
    _refreshTimer = null;
    debugPrint('Stopped periodic refresh');
  }

  /// Clear all data and reset state.
  void clearData() {
    _orderTracking.value = null;
    _timeline.value = null;
    _notificationPreferences.value = null;
    _lastUpdateTime.value = null;
    _clearError();
    _cleanup();
    debugPrint('Cleared all order tracking data');
  }

  // Private methods

  Future<void> _fetchTimeline(String orderId) async {
    try {
      final timeline = await _repository.getOrderTimeline(orderId);
      _timeline.value = timeline;
    } catch (e) {
      debugPrint('Error fetching timeline: $e');
      // Don't fail the entire operation if timeline fails
    }
  }

  Future<void> _subscribeToUpdates(String orderId) async {
    try {
      // Cancel existing subscription
      await _realtimeSubscription?.cancel();

      // Subscribe to real-time updates
      final stream = await _subscribeOrderUpdatesUseCase.execute(orderId);
      _realtimeSubscription = stream.listen(
        _handleRealtimeUpdate,
        onError: _handleRealtimeError,
        onDone: _handleRealtimeDisconnect,
      );

      _isConnected.value = true;
      debugPrint('Subscribed to real-time updates for order: $orderId');
    } catch (e) {
      debugPrint('Error subscribing to updates: $e');
      _isConnected.value = false;
    }
  }

  void _handleRealtimeUpdate(RealtimeStatusUpdate update) {
    debugPrint('Received real-time update: ${update.newStatus}');

    if (orderTracking?.orderId != update.orderId) return;

    // Update order status
    final updatedStatus = OrderStatus.values.firstWhere(
      (status) => status.name == update.newStatus,
      orElse: () => orderTracking!.currentStatus,
    );

    final updatedTracking = orderTracking!.copyWith(
      currentStatus: updatedStatus,
      estimatedCompletionTime: update.estimatedCompletionTime,
      lastUpdated: update.timestamp,
    );

    _orderTracking.value = updatedTracking;
    _lastUpdateTime.value = update.timestamp;
    _isConnected.value = true;

    // Show notification if appropriate
    if (update.shouldNotify) {
      Get.snackbar(
        'Order Update',
        update.updateMessage,
        snackPosition: SnackPosition.TOP,
        duration: const Duration(seconds: 3),
      );
    }
  }

  void _handleRealtimeError(dynamic error) {
    debugPrint('Real-time connection error: $error');
    _isConnected.value = false;
    
    // Attempt to reconnect after a delay
    Timer(const Duration(seconds: 5), () {
      if (orderTracking != null) {
        _subscribeToUpdates(orderTracking!.orderId);
      }
    });
  }

  void _handleRealtimeDisconnect() {
    debugPrint('Real-time connection disconnected');
    _isConnected.value = false;
  }

  void _setLoading(bool loading) {
    _isLoading.value = loading;
  }

  void _setRefreshing(bool refreshing) {
    _isRefreshing.value = refreshing;
  }

  void _setError(String? error) {
    _error.value = error;
  }

  void _clearError() {
    _error.value = null;
  }

  void _cleanup() {
    _realtimeSubscription?.cancel();
    _realtimeSubscription = null;
    _refreshTimer?.cancel();
    _refreshTimer = null;
    _isConnected.value = false;
  }
}
