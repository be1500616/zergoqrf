import 'package:get/get.dart';
import 'package:zergo_frontend/features/diner/domain/entities/menu_item.dart';

import '../services/cart_service.dart';

/// Enhanced cart controller with backend API integration.
class CartController extends GetxController {
  CartController(this._cartService);

  final CartService _cartService;

  // Observable state
  final RxMap<String, int> _qtyByItemId = <String, int>{}.obs;
  final RxMap<String, DinerMenuItem> _itemsById = <String, DinerMenuItem>{}.obs;
  final RxMap<String, String> _cartItemIdByMenuItemId = <String, String>{}.obs;
  final RxBool _isLoading = false.obs;
  final RxString _error = ''.obs;
  final RxDouble _subtotal = 0.0.obs;
  final RxDouble _tax = 0.0.obs;
  final RxDouble _total = 0.0.obs;

  String? _sessionToken;
  String? _restaurantId;

  /// Get all items in cart with quantities
  Map<String, int> get items => _qtyByItemId;

  /// Get all menu items in cart
  Map<String, DinerMenuItem> get menuItems => _itemsById;

  /// Get total number of items in cart
  int get totalItems => _qtyByItemId.values.fold(0, (sum, qty) => sum + qty);

  /// Loading state
  bool get isLoading => _isLoading.value;

  /// Error message
  String get error => _error.value;

  /// Cart totals
  double get subtotal => _subtotal.value;
  double get tax => _tax.value;
  double get total => _total.value;

  /// Set restaurant context for cart operations
  void setRestaurantContext(String restaurantId) {
    _restaurantId = restaurantId;
  }

  /// Initialize cart - load from backend if session exists
  @override
  void onInit() {
    super.onInit();
    _loadCartFromBackend();
  }

  /// Load cart from backend
  Future<void> _loadCartFromBackend() async {
    try {
      _sessionToken = await _cartService.getSessionToken();
      if (_sessionToken != null) {
        await loadCart();
      }
    } catch (e) {
      print('Error loading cart from backend: $e');
      // Continue with empty cart
    }
  }

  /// Load cart summary from backend
  Future<void> loadCart() async {
    if (_sessionToken == null) return;

    try {
      _isLoading.value = true;
      _error.value = '';

      final summary = await _cartService.getCartSummary(_sessionToken!);

      // Update state from summary
      _qtyByItemId.clear();
      _itemsById.clear();
      _cartItemIdByMenuItemId.clear();

      final itemsList = summary['items'] as List<dynamic>;
      for (final item in itemsList) {
        final menuItemId = item['menu_item_id'] as String;
        final cartItemId = item['id'] as String;
        final quantity = item['quantity'] as int;

        _qtyByItemId[menuItemId] = quantity;
        _cartItemIdByMenuItemId[menuItemId] = cartItemId;

        // Reconstruct DinerMenuItem from cart item data
        _itemsById[menuItemId] = DinerMenuItem(
          id: menuItemId,
          categoryId: '', // Not needed for cart display
          name: item['item_name'] as String,
          description: item['item_description'] as String?,
          basePrice: (item['base_price'] as num).toDouble(),
          imageUrl: null, // Not stored in cart
        );
      }

      // Update totals
      _subtotal.value = (summary['subtotal'] as num).toDouble();
      _tax.value = (summary['tax_amount'] as num).toDouble();
      _total.value = (summary['total_amount'] as num).toDouble();
    } catch (e) {
      _error.value = 'Failed to load cart: $e';
      print('Error loading cart: $e');
    } finally {
      _isLoading.value = false;
    }
  }

  /// Add an item to the cart
  Future<void> addItem(DinerMenuItem item, {String? restaurantId}) async {
    try {
      _isLoading.value = true;
      _error.value = '';

      // Get or create session
      final effectiveRestaurantId = restaurantId ?? _restaurantId;
      if (effectiveRestaurantId == null) {
        throw Exception('Restaurant ID required for cart operations');
      }

      _sessionToken = await _cartService.getOrCreateSession(
        effectiveRestaurantId,
      );
      _restaurantId = effectiveRestaurantId;

      // Check if item already in cart
      final currentQty = _qtyByItemId[item.id] ?? 0;
      final newQty = currentQty + 1;

      if (currentQty > 0) {
        // Update existing item
        final cartItemId = _cartItemIdByMenuItemId[item.id]!;
        await _cartService.updateCartItem(
          itemId: cartItemId,
          quantity: newQty,
        );
      } else {
        // Add new item
        final result = await _cartService.addItemToCart(
          sessionToken: _sessionToken!,
          menuItemId: item.id,
          quantity: 1,
        );
        _cartItemIdByMenuItemId[item.id] = result['id'] as String;
      }

      // Update local state
      _qtyByItemId[item.id] = newQty;
      _itemsById[item.id] = item;

      // Reload cart to get updated totals
      await loadCart();
    } catch (e) {
      _error.value = 'Failed to add item: $e';
      print('Error adding item to cart: $e');
      rethrow;
    } finally {
      _isLoading.value = false;
    }
  }

  /// Remove one quantity of an item from the cart
  Future<void> removeItem(String itemId) async {
    if (!_qtyByItemId.containsKey(itemId)) return;

    try {
      _isLoading.value = true;
      _error.value = '';

      final currentQty = _qtyByItemId[itemId] ?? 0;
      final newQty = currentQty - 1;

      if (newQty <= 0) {
        // Remove item completely
        final cartItemId = _cartItemIdByMenuItemId[itemId]!;
        await _cartService.removeCartItem(cartItemId);
        _qtyByItemId.remove(itemId);
        _itemsById.remove(itemId);
        _cartItemIdByMenuItemId.remove(itemId);
      } else {
        // Update quantity
        final cartItemId = _cartItemIdByMenuItemId[itemId]!;
        await _cartService.updateCartItem(
          itemId: cartItemId,
          quantity: newQty,
        );
        _qtyByItemId[itemId] = newQty;
      }

      // Reload cart to get updated totals
      await loadCart();
    } catch (e) {
      _error.value = 'Failed to remove item: $e';
      print('Error removing item from cart: $e');
      rethrow;
    } finally {
      _isLoading.value = false;
    }
  }

  /// Get quantity of a specific item
  int getItemQuantity(String itemId) => _qtyByItemId[itemId] ?? 0;

  /// Clear all items from cart
  Future<void> clearCart() async {
    if (_sessionToken == null) return;

    try {
      _isLoading.value = true;
      _error.value = '';

      await _cartService.clearCart(_sessionToken!);

      _qtyByItemId.clear();
      _itemsById.clear();
      _cartItemIdByMenuItemId.clear();
      _subtotal.value = 0.0;
      _tax.value = 0.0;
      _total.value = 0.0;
    } catch (e) {
      _error.value = 'Failed to clear cart: $e';
      print('Error clearing cart: $e');
      rethrow;
    } finally {
      _isLoading.value = false;
    }
  }

  /// Legacy methods for backward compatibility
  Future<void> add(DinerMenuItem item) => addItem(item);
  Future<void> remove(DinerMenuItem item) => removeItem(item.id);
  int quantityOf(String itemId) => getItemQuantity(itemId);

  @override
  void onClose() {
    _qtyByItemId.close();
    _itemsById.close();
    _cartItemIdByMenuItemId.close();
    _isLoading.close();
    _error.close();
    _subtotal.close();
    _tax.close();
    _total.close();
    super.onClose();
  }
}
