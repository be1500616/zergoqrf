/// Kitchen order management GetX controller.
/// 
/// This controller manages the state and business logic for kitchen order
/// management, including bulk operations, real-time updates, and staff workflow.
import 'dart:async';
import 'package:get/get.dart';
import 'package:flutter/foundation.dart';

import '../../domain/entities/order_tracking.dart';
import '../../domain/entities/order_status_update.dart';
import '../../domain/repositories/order_tracking_repository.dart';

/// GetX controller for kitchen order management functionality.
class KitchenOrderController extends GetxController {
  /// Creates a kitchen order controller.
  KitchenOrderController({
    required OrderTrackingRepository repository,
  }) : _repository = repository;

  final OrderTrackingRepository _repository;

  // Reactive state variables
  final _orders = <OrderTracking>[].obs;
  final _selectedOrders = <String>{}.obs;
  final _isLoading = false.obs;
  final _isRefreshing = false.obs;
  final _error = Rxn<String>();
  final _isConnected = false.obs;
  final _lastUpdateTime = Rxn<DateTime>();
  final _filterStatus = Rxn<OrderStatus>();
  final _sortBy = KitchenSortBy.priority.obs;

  // Real-time subscription
  StreamSubscription<RealtimeStatusUpdate>? _realtimeSubscription;
  Timer? _refreshTimer;

  // Current restaurant context
  String? _currentRestaurantId;

  // Getters for reactive state
  List<OrderTracking> get orders => _orders;
  Set<String> get selectedOrders => _selectedOrders;
  bool get isLoading => _isLoading.value;
  bool get isRefreshing => _isRefreshing.value;
  String? get error => _error.value;
  bool get isConnected => _isConnected.value;
  DateTime? get lastUpdateTime => _lastUpdateTime.value;
  OrderStatus? get filterStatus => _filterStatus.value;
  KitchenSortBy get sortBy => _sortBy.value;

  // Computed properties
  bool get hasData => orders.isNotEmpty;
  bool get hasError => error != null;
  bool get hasSelectedOrders => selectedOrders.isNotEmpty;
  int get selectedOrdersCount => selectedOrders.length;
  int get totalOrders => orders.length;
  int get activeOrdersCount => orders.where((o) => !o.currentStatus.isTerminal).length;
  int get overdueOrdersCount => orders.where((o) => o.isOverdue).length;

  // Filtered and sorted orders
  List<OrderTracking> get filteredOrders {
    var filtered = orders.where((order) {
      if (filterStatus != null && order.currentStatus != filterStatus) {
        return false;
      }
      return true;
    }).toList();

    // Sort orders
    switch (sortBy) {
      case KitchenSortBy.priority:
        filtered.sort((a, b) {
          // Overdue orders first
          if (a.isOverdue && !b.isOverdue) return -1;
          if (!a.isOverdue && b.isOverdue) return 1;
          
          // Then by status priority
          final aStatusPriority = _getStatusPriority(a.currentStatus);
          final bStatusPriority = _getStatusPriority(b.currentStatus);
          if (aStatusPriority != bStatusPriority) {
            return aStatusPriority.compareTo(bStatusPriority);
          }
          
          // Finally by order time (oldest first)
          return a.lastUpdated.compareTo(b.lastUpdated);
        });
        break;
      case KitchenSortBy.timeAsc:
        filtered.sort((a, b) => a.lastUpdated.compareTo(b.lastUpdated));
        break;
      case KitchenSortBy.timeDesc:
        filtered.sort((a, b) => b.lastUpdated.compareTo(a.lastUpdated));
        break;
      case KitchenSortBy.status:
        filtered.sort((a, b) => a.currentStatus.name.compareTo(b.currentStatus.name));
        break;
    }

    return filtered;
  }

  @override
  void onInit() {
    super.onInit();
    debugPrint('KitchenOrderController initialized');
  }

  @override
  void onClose() {
    _cleanup();
    super.onClose();
  }

  /// Initialize kitchen orders for a restaurant.
  /// 
  /// Args:
  ///   restaurantId: Restaurant identifier
  ///   activeOnly: Whether to only include active orders
  ///   autoRefresh: Whether to start auto-refresh
  Future<void> initializeKitchenOrders(
    String restaurantId, {
    bool activeOnly = true,
    bool autoRefresh = true,
  }) async {
    _currentRestaurantId = restaurantId;
    
    await fetchKitchenOrders(
      restaurantId,
      activeOnly: activeOnly,
    );

    if (autoRefresh) {
      startPeriodicRefresh();
    }

    // Subscribe to real-time updates
    await _subscribeToKitchenUpdates(restaurantId);
  }

  /// Fetch kitchen orders for a restaurant.
  /// 
  /// Args:
  ///   restaurantId: Restaurant identifier
  ///   activeOnly: Whether to only include active orders
  ///   limit: Maximum number of orders to return
  Future<void> fetchKitchenOrders(
    String restaurantId, {
    bool activeOnly = true,
    int limit = 50,
  }) async {
    try {
      _setLoading(true);
      _clearError();

      debugPrint('Fetching kitchen orders for restaurant: $restaurantId');

      final orders = await _repository.getKitchenOrders(
        restaurantId,
        activeOnly: activeOnly,
        limit: limit,
      );

      _orders.value = orders;
      _lastUpdateTime.value = DateTime.now();

      debugPrint('Successfully fetched ${orders.length} kitchen orders');
    } catch (e) {
      debugPrint('Error fetching kitchen orders: $e');
      _setError('Failed to load kitchen orders: ${e.toString()}');
    } finally {
      _setLoading(false);
    }
  }

  /// Refresh kitchen orders.
  Future<void> refreshKitchenOrders() async {
    if (_currentRestaurantId == null) return;

    try {
      _setRefreshing(true);
      await fetchKitchenOrders(_currentRestaurantId!);
    } finally {
      _setRefreshing(false);
    }
  }

  /// Update status for a single order.
  /// 
  /// Args:
  ///   orderId: Order identifier
  ///   newStatus: New order status
  ///   preparationNotes: Optional preparation notes
  ///   notifyCustomer: Whether to notify customer
  Future<bool> updateOrderStatus(
    String orderId,
    String newStatus, {
    String? preparationNotes,
    bool notifyCustomer = true,
  }) async {
    try {
      _setLoading(true);
      _clearError();

      debugPrint('Updating order $orderId status to: $newStatus');

      final statusUpdate = await _repository.updateOrderStatus(
        orderId,
        newStatus,
        preparationNotes: preparationNotes,
        changeReason: 'Kitchen staff update',
        notifyCustomer: notifyCustomer,
      );

      // Update local state
      final orderIndex = _orders.indexWhere((o) => o.orderId == orderId);
      if (orderIndex != -1) {
        final updatedOrder = _orders[orderIndex].copyWith(
          currentStatus: OrderStatus.values.firstWhere(
            (status) => status.name == newStatus,
            orElse: () => _orders[orderIndex].currentStatus,
          ),
          statusHistory: [..._orders[orderIndex].statusHistory, statusUpdate],
          lastUpdated: DateTime.now(),
        );

        _orders[orderIndex] = updatedOrder;
        _orders.refresh();
      }

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

  /// Bulk update status for selected orders.
  /// 
  /// Args:
  ///   newStatus: New status for all selected orders
  ///   preparationNotes: Optional preparation notes
  ///   notifyCustomers: Whether to notify customers
  Future<bool> bulkUpdateOrderStatus(
    String newStatus, {
    String? preparationNotes,
    bool notifyCustomers = true,
  }) async {
    if (selectedOrders.isEmpty) return false;

    try {
      _setLoading(true);
      _clearError();

      debugPrint('Bulk updating ${selectedOrders.length} orders to: $newStatus');

      final statusUpdates = await _repository.bulkUpdateOrderStatus(
        selectedOrders.toList(),
        newStatus,
        preparationNotes: preparationNotes,
        notifyCustomers: notifyCustomers,
      );

      // Update local state for successful updates
      for (final statusUpdate in statusUpdates) {
        final orderIndex = _orders.indexWhere((o) => o.orderId == statusUpdate.orderId);
        if (orderIndex != -1) {
          final updatedOrder = _orders[orderIndex].copyWith(
            currentStatus: OrderStatus.values.firstWhere(
              (status) => status.name == newStatus,
              orElse: () => _orders[orderIndex].currentStatus,
            ),
            statusHistory: [..._orders[orderIndex].statusHistory, statusUpdate],
            lastUpdated: DateTime.now(),
          );

          _orders[orderIndex] = updatedOrder;
        }
      }

      _orders.refresh();
      clearSelection();

      debugPrint('Successfully bulk updated ${statusUpdates.length} orders');
      
      Get.snackbar(
        'Bulk Update Complete',
        'Updated ${statusUpdates.length} orders to $newStatus',
        snackPosition: SnackPosition.TOP,
        duration: const Duration(seconds: 3),
      );

      return true;
    } catch (e) {
      debugPrint('Error bulk updating orders: $e');
      _setError('Failed to bulk update: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Update item status for a specific order item.
  /// 
  /// Args:
  ///   orderId: Order identifier
  ///   itemId: Order item identifier
  ///   newStatus: New item status
  ///   preparationNotes: Optional preparation notes
  Future<bool> updateOrderItemStatus(
    String orderId,
    String itemId,
    OrderItemStatus newStatus, {
    String? preparationNotes,
  }) async {
    try {
      debugPrint('Updating item $itemId status to: ${newStatus.name}');

      final itemTracking = await _repository.updateOrderItemStatus(
        orderId,
        itemId,
        newStatus,
        preparationNotes: preparationNotes,
      );

      // Update local state
      final orderIndex = _orders.indexWhere((o) => o.orderId == orderId);
      if (orderIndex != -1) {
        final updatedItemTracking = _orders[orderIndex].itemTracking.map((item) {
          return item.orderItemId == itemId ? itemTracking : item;
        }).toList();

        final updatedOrder = _orders[orderIndex].copyWith(
          itemTracking: updatedItemTracking,
          lastUpdated: DateTime.now(),
        );

        _orders[orderIndex] = updatedOrder;
        _orders.refresh();
      }

      debugPrint('Successfully updated item status');
      return true;
    } catch (e) {
      debugPrint('Error updating item status: $e');
      _setError('Failed to update item status: ${e.toString()}');
      return false;
    }
  }

  /// Toggle order selection.
  /// 
  /// Args:
  ///   orderId: Order identifier
  void toggleOrderSelection(String orderId) {
    if (_selectedOrders.contains(orderId)) {
      _selectedOrders.remove(orderId);
    } else {
      _selectedOrders.add(orderId);
    }
    debugPrint('Selected orders: ${_selectedOrders.length}');
  }

  /// Select all visible orders.
  void selectAllOrders() {
    _selectedOrders.clear();
    _selectedOrders.addAll(filteredOrders.map((o) => o.orderId));
    debugPrint('Selected all ${_selectedOrders.length} orders');
  }

  /// Clear order selection.
  void clearSelection() {
    _selectedOrders.clear();
    debugPrint('Cleared order selection');
  }

  /// Set status filter.
  /// 
  /// Args:
  ///   status: Status to filter by (null for all)
  void setStatusFilter(OrderStatus? status) {
    _filterStatus.value = status;
    debugPrint('Set status filter: ${status?.name ?? 'all'}');
  }

  /// Set sort order.
  /// 
  /// Args:
  ///   sortBy: Sort criteria
  void setSortBy(KitchenSortBy sortBy) {
    _sortBy.value = sortBy;
    debugPrint('Set sort by: ${sortBy.name}');
  }

  /// Start periodic refresh of kitchen orders.
  /// 
  /// Args:
  ///   intervalSeconds: Refresh interval in seconds
  void startPeriodicRefresh({int intervalSeconds = 15}) {
    _refreshTimer?.cancel();
    _refreshTimer = Timer.periodic(
      Duration(seconds: intervalSeconds),
      (_) => refreshKitchenOrders(),
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
    _orders.clear();
    _selectedOrders.clear();
    _lastUpdateTime.value = null;
    _filterStatus.value = null;
    _clearError();
    _cleanup();
    debugPrint('Cleared all kitchen order data');
  }

  // Private methods

  Future<void> _subscribeToKitchenUpdates(String restaurantId) async {
    try {
      // Cancel existing subscription
      await _realtimeSubscription?.cancel();

      // Subscribe to real-time updates for the restaurant
      final stream = _repository.subscribeToKitchenUpdates(restaurantId);
      _realtimeSubscription = stream.listen(
        _handleRealtimeUpdate,
        onError: _handleRealtimeError,
        onDone: _handleRealtimeDisconnect,
      );

      _isConnected.value = true;
      debugPrint('Subscribed to kitchen updates for restaurant: $restaurantId');
    } catch (e) {
      debugPrint('Error subscribing to kitchen updates: $e');
      _isConnected.value = false;
    }
  }

  void _handleRealtimeUpdate(RealtimeStatusUpdate update) {
    debugPrint('Received kitchen real-time update: ${update.newStatus}');

    final orderIndex = _orders.indexWhere((o) => o.orderId == update.orderId);
    if (orderIndex == -1) return;

    // Update order status
    final updatedStatus = OrderStatus.values.firstWhere(
      (status) => status.name == update.newStatus,
      orElse: () => _orders[orderIndex].currentStatus,
    );

    final updatedOrder = _orders[orderIndex].copyWith(
      currentStatus: updatedStatus,
      estimatedCompletionTime: update.estimatedCompletionTime,
      lastUpdated: update.timestamp,
    );

    _orders[orderIndex] = updatedOrder;
    _orders.refresh();
    _lastUpdateTime.value = update.timestamp;
    _isConnected.value = true;
  }

  void _handleRealtimeError(dynamic error) {
    debugPrint('Kitchen real-time connection error: $error');
    _isConnected.value = false;
    
    // Attempt to reconnect after a delay
    Timer(const Duration(seconds: 5), () {
      if (_currentRestaurantId != null) {
        _subscribeToKitchenUpdates(_currentRestaurantId!);
      }
    });
  }

  void _handleRealtimeDisconnect() {
    debugPrint('Kitchen real-time connection disconnected');
    _isConnected.value = false;
  }

  int _getStatusPriority(OrderStatus status) {
    switch (status) {
      case OrderStatus.placed:
        return 1;
      case OrderStatus.confirmed:
        return 2;
      case OrderStatus.preparing:
        return 3;
      case OrderStatus.ready:
        return 4;
      case OrderStatus.completed:
        return 6;
      case OrderStatus.cancelled:
        return 7;
    }
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

/// Kitchen sort criteria enumeration
enum KitchenSortBy {
  priority,
  timeAsc,
  timeDesc,
  status;

  /// Get human-readable display name
  String get displayName {
    switch (this) {
      case KitchenSortBy.priority:
        return 'Priority';
      case KitchenSortBy.timeAsc:
        return 'Oldest First';
      case KitchenSortBy.timeDesc:
        return 'Newest First';
      case KitchenSortBy.status:
        return 'Status';
    }
  }

  /// Get icon identifier
  String get icon {
    switch (this) {
      case KitchenSortBy.priority:
        return 'priority_high';
      case KitchenSortBy.timeAsc:
        return 'schedule';
      case KitchenSortBy.timeDesc:
        return 'schedule';
      case KitchenSortBy.status:
        return 'sort';
    }
  }
}
