/// Cart service for API integration.
///
/// Handles all cart-related API calls to the backend.
library;

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../../../../core/config/api_config.dart';
import '../../domain/entities/menu_item.dart';

/// Cart service for managing cart operations with backend API.
class CartService {
  CartService(this._apiConfig);

  final ApiConfig _apiConfig;
  static const String _sessionTokenKey = 'cart_session_token';
  static const String _restaurantIdKey = 'cart_restaurant_id';

  /// Get the current cart session token from storage.
  Future<String?> getSessionToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_sessionTokenKey);
  }

  /// Save cart session token to storage.
  Future<void> saveSessionToken(String token, String restaurantId) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_sessionTokenKey, token);
    await prefs.setString(_restaurantIdKey, restaurantId);
  }

  /// Clear cart session from storage.
  Future<void> clearSession() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_sessionTokenKey);
    await prefs.remove(_restaurantIdKey);
  }

  /// Create an anonymous cart session.
  Future<Map<String, dynamic>> createAnonymousSession({
    required String restaurantId,
    String? tableId,
  }) async {
    final url = Uri.parse('${_apiConfig.baseUrl}/api/v1/cart/sessions/anonymous');

    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'restaurant_id': restaurantId,
        if (tableId != null) 'table_id': tableId,
      }),
    );

    if (response.statusCode == 200 || response.statusCode == 201) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      final sessionToken = data['session_token'] as String;
      await saveSessionToken(sessionToken, restaurantId);
      return data;
    } else {
      throw Exception(
        'Failed to create cart session: ${response.statusCode} - ${response.body}',
      );
    }
  }

  /// Get or create cart session for a restaurant.
  Future<String> getOrCreateSession(String restaurantId) async {
    String? token = await getSessionToken();

    // If we have a token, verify it's still valid
    if (token != null) {
      try {
        final summary = await getCartSummary(token);
        // Check if session is for the same restaurant
        if (summary['session']['restaurant_id'] == restaurantId) {
          return token;
        }
      } catch (e) {
        // Session invalid or expired, create new one
        print('Existing session invalid: $e');
      }
    }

    // Create new session
    final session = await createAnonymousSession(restaurantId: restaurantId);
    return session['session_token'] as String;
  }

  /// Add item to cart.
  Future<Map<String, dynamic>> addItemToCart({
    required String sessionToken,
    required String menuItemId,
    required int quantity,
    Map<String, dynamic>? customizations,
    String? specialInstructions,
  }) async {
    final url = Uri.parse(
      '${_apiConfig.baseUrl}/api/v1/cart/sessions/$sessionToken/items',
    );

    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'menu_item_id': menuItemId,
        'quantity': quantity,
        if (customizations != null) 'customizations': customizations,
        if (specialInstructions != null)
          'special_instructions': specialInstructions,
      }),
    );

    if (response.statusCode == 200 || response.statusCode == 201) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception(
        'Failed to add item to cart: ${response.statusCode} - ${response.body}',
      );
    }
  }

  /// Update cart item quantity.
  Future<Map<String, dynamic>> updateCartItem({
    required String itemId,
    required int quantity,
  }) async {
    final url = Uri.parse('${_apiConfig.baseUrl}/api/v1/cart/items/$itemId');

    final response = await http.put(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'quantity': quantity}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception(
        'Failed to update cart item: ${response.statusCode} - ${response.body}',
      );
    }
  }

  /// Remove item from cart.
  Future<bool> removeCartItem(String itemId) async {
    final url = Uri.parse('${_apiConfig.baseUrl}/api/v1/cart/items/$itemId');

    final response = await http.delete(url);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return data['success'] as bool? ?? false;
    } else {
      throw Exception(
        'Failed to remove cart item: ${response.statusCode} - ${response.body}',
      );
    }
  }

  /// Get cart summary.
  Future<Map<String, dynamic>> getCartSummary(String sessionToken) async {
    final url = Uri.parse(
      '${_apiConfig.baseUrl}/api/v1/cart/sessions/$sessionToken/summary',
    );

    final response = await http.get(url);

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception(
        'Failed to get cart summary: ${response.statusCode} - ${response.body}',
      );
    }
  }

  /// Get all cart items.
  Future<List<Map<String, dynamic>>> getCartItems(String sessionToken) async {
    final url = Uri.parse(
      '${_apiConfig.baseUrl}/api/v1/cart/sessions/$sessionToken/items',
    );

    final response = await http.get(url);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as List<dynamic>;
      return data.cast<Map<String, dynamic>>();
    } else {
      throw Exception(
        'Failed to get cart items: ${response.statusCode} - ${response.body}',
      );
    }
  }

  /// Clear all items from cart.
  Future<bool> clearCart(String sessionToken) async {
    final url = Uri.parse(
      '${_apiConfig.baseUrl}/api/v1/cart/sessions/$sessionToken/items',
    );

    final response = await http.delete(url);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return data['success'] as bool? ?? false;
    } else {
      throw Exception(
        'Failed to clear cart: ${response.statusCode} - ${response.body}',
      );
    }
  }
}

