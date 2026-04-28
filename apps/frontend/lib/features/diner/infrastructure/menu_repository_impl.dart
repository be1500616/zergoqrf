import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:zergo_frontend/core/config/api_config.dart';
import 'package:zergo_frontend/features/diner/domain/entities/menu_category.dart';
import 'package:zergo_frontend/features/diner/domain/entities/menu_item.dart';
import 'package:zergo_frontend/features/diner/domain/entities/menu_structure.dart';
import 'package:zergo_frontend/features/diner/domain/entities/restaurant_branding.dart';
import 'package:zergo_frontend/features/diner/domain/entities/search_result.dart';
import 'package:zergo_frontend/features/diner/domain/repositories/menu_repository.dart';

/// Enhanced HTTP-backed repository with caching and offline support.
class MenuRepositoryImpl implements MenuRepository {
  MenuRepositoryImpl(this._apiConfig);

  final ApiConfig _apiConfig;
  static const String _cacheKeyPrefix = 'menu_cache_';
  static const Duration _cacheExpiry = Duration(minutes: 30);

  @override
  Future<RestaurantBranding?> getRestaurantBranding(
      String restaurantCode) async {
    final cacheKey = '${_cacheKeyPrefix}branding_$restaurantCode';

    // Try cache first
    final cached = await _getCachedData(cacheKey);
    if (cached != null) {
      try {
        return RestaurantBranding.fromJson(cached);
      } catch (e) {
        // Invalid cache, continue to fetch
      }
    }

    try {
      final uri = Uri.parse(
          '${_apiConfig.baseUrl}/api/v1/public/menu/restaurant/$restaurantCode');
      final resp = await http.get(uri);

      if (resp.statusCode == 404) {
        return null;
      }

      if (resp.statusCode != 200) {
        throw Exception('Failed to load restaurant branding');
      }

      final json = jsonDecode(resp.body) as Map<String, dynamic>;
      final branding = RestaurantBranding.fromJson(json);

      // Cache the result
      await _setCachedData(cacheKey, json);

      return branding;
    } catch (e) {
      // Return cached data if available, even if expired
      if (cached != null) {
        try {
          return RestaurantBranding.fromJson(cached);
        } catch (_) {}
      }
      rethrow;
    }
  }

  @override
  Future<MenuStructure?> getMenuStructure(String restaurantCode) async {
    final cacheKey = '${_cacheKeyPrefix}structure_$restaurantCode';

    // Try cache first
    final cached = await _getCachedData(cacheKey);
    if (cached != null) {
      try {
        return MenuStructure.fromJson(cached);
      } catch (e) {
        // Invalid cache, continue to fetch
      }
    }

    try {
      final uri =
          Uri.parse('${_apiConfig.baseUrl}/api/v1/public/menu/$restaurantCode');
      final resp = await http.get(uri);

      if (resp.statusCode == 404) {
        return null;
      }

      if (resp.statusCode != 200) {
        throw Exception('Failed to load menu structure');
      }

      final json = jsonDecode(resp.body) as Map<String, dynamic>;
      final structure = MenuStructure.fromJson(json);

      // Cache the result
      await _setCachedData(cacheKey, json);

      return structure;
    } catch (e) {
      // Return cached data if available, even if expired
      if (cached != null) {
        try {
          return MenuStructure.fromJson(cached);
        } catch (_) {}
      }
      rethrow;
    }
  }

  @override
  Future<List<MenuCategory>> getMenuCategories(String restaurantCode) async {
    final cacheKey = '${_cacheKeyPrefix}categories_$restaurantCode';

    // Try cache first
    final cached = await _getCachedData(cacheKey);
    if (cached != null) {
      try {
        final List<dynamic> jsonList = cached as List<dynamic>;
        return jsonList
            .map((e) => MenuCategory.fromJson(e as Map<String, dynamic>))
            .toList();
      } catch (e) {
        // Invalid cache, continue to fetch
      }
    }

    try {
      final uri = Uri.parse(
          '${_apiConfig.baseUrl}/api/v1/public/menu/$restaurantCode/categories');
      final resp = await http.get(uri);

      if (resp.statusCode != 200) {
        throw Exception('Failed to load categories');
      }

      final List<dynamic> json = jsonDecode(resp.body) as List<dynamic>;
      final categories = json
          .map((e) => MenuCategory.fromJson(e as Map<String, dynamic>))
          .toList();

      // Cache the result
      await _setCachedData(cacheKey, json);

      return categories;
    } catch (e) {
      // Return cached data if available, even if expired
      if (cached != null) {
        try {
          final List<dynamic> jsonList = cached as List<dynamic>;
          return jsonList
              .map((e) => MenuCategory.fromJson(e as Map<String, dynamic>))
              .toList();
        } catch (_) {}
      }
      rethrow;
    }
  }

  @override
  Future<List<DinerMenuItem>> getCategoryItems(
      String restaurantCode, String categoryId) async {
    final cacheKey =
        '${_cacheKeyPrefix}category_items_${restaurantCode}_$categoryId';

    // Try cache first
    final cached = await _getCachedData(cacheKey);
    if (cached != null) {
      try {
        final jsonMap = cached;
        final itemsJson = jsonMap['items'] as List<dynamic>;
        return itemsJson
            .map((e) => DinerMenuItem.fromJson(e as Map<String, dynamic>))
            .toList();
      } catch (e) {
        // Invalid cache, continue to fetch
      }
    }

    try {
      final uri = Uri.parse(
          '${_apiConfig.baseUrl}/api/v1/public/menu/$restaurantCode/categories/$categoryId/items');
      final resp = await http.get(uri);

      if (resp.statusCode != 200) {
        throw Exception('Failed to load category items');
      }

      final json = jsonDecode(resp.body) as Map<String, dynamic>;
      final List<dynamic> itemsJson = json['items'] as List<dynamic>;
      final items = itemsJson
          .map((e) => DinerMenuItem.fromJson(e as Map<String, dynamic>))
          .toList();

      // Cache the result
      await _setCachedData(cacheKey, json);

      return items;
    } catch (e) {
      // Return cached data if available, even if expired
      if (cached != null) {
        try {
          final jsonMap = cached;
          final List<dynamic> itemsJson = jsonMap['items'] as List<dynamic>;
          return itemsJson
              .map((e) => DinerMenuItem.fromJson(e as Map<String, dynamic>))
              .toList();
        } catch (_) {}
      }
      rethrow;
    }
  }

  @override
  Future<MenuSearchResult> searchMenuItems(String restaurantCode, String query,
      {int limit = 50}) async {
    // Don't cache search results as they are dynamic
    try {
      final uri = Uri.parse(
          '${_apiConfig.baseUrl}/api/v1/public/menu/$restaurantCode/search?query=${Uri.encodeComponent(query)}&limit=$limit');
      final resp = await http.get(uri);

      if (resp.statusCode != 200) {
        throw Exception('Failed to search menu items');
      }

      final json = jsonDecode(resp.body) as Map<String, dynamic>;
      return MenuSearchResult.fromJson(json);
    } catch (e) {
      // Return empty result on error
      return MenuSearchResult(
        items: const [],
        totalCount: 0,
        searchQuery: query,
        categoriesFound: const [],
      );
    }
  }

  @override
  Future<List<DinerMenuItem>> getFeaturedItems(String restaurantCode,
      {int limit = 10}) async {
    final cacheKey = '${_cacheKeyPrefix}featured_$restaurantCode';

    // Try cache first
    final cached = await _getCachedData(cacheKey);
    if (cached != null) {
      try {
        final List<dynamic> jsonList = cached as List<dynamic>;
        return jsonList
            .map((e) => DinerMenuItem.fromJson(e as Map<String, dynamic>))
            .toList();
      } catch (e) {
        // Invalid cache, continue to fetch
      }
    }

    try {
      final uri = Uri.parse(
          '${_apiConfig.baseUrl}/api/v1/public/menu/$restaurantCode/featured?limit=$limit');
      final resp = await http.get(uri);

      if (resp.statusCode != 200) {
        throw Exception('Failed to load featured items');
      }

      final List<dynamic> json = jsonDecode(resp.body) as List<dynamic>;
      final items = json
          .map((e) => DinerMenuItem.fromJson(e as Map<String, dynamic>))
          .toList();

      // Cache the result
      await _setCachedData(cacheKey, json);

      return items;
    } catch (e) {
      // Return cached data if available, even if expired
      if (cached != null) {
        try {
          final List<dynamic> jsonList = cached as List<dynamic>;
          return jsonList
              .map((e) => DinerMenuItem.fromJson(e as Map<String, dynamic>))
              .toList();
        } catch (_) {}
      }
      rethrow;
    }
  }

  // Legacy methods for backward compatibility
  @override
  @Deprecated('Use getRestaurantBranding instead')
  Future<String> resolveRestaurantIdByCode(String restaurantCode) async {
    final branding = await getRestaurantBranding(restaurantCode);
    if (branding == null) {
      throw Exception('Restaurant not found');
    }
    return branding.id;
  }

  @override
  @Deprecated('Use getMenuStructure instead')
  Future<List<DinerMenuItem>> fetchPublicMenuItems(String restaurantId) async {
    // This is a legacy method, we can't easily convert restaurant ID back to code
    // For now, throw an exception suggesting to use the new method
    throw Exception(
        'This method is deprecated. Use getMenuStructure with restaurant code instead.');
  }

  // Cache management methods
  Future<Map<String, dynamic>?> _getCachedData(String key) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cachedJson = prefs.getString(key);
      if (cachedJson == null) return null;

      final cacheData = jsonDecode(cachedJson) as Map<String, dynamic>;
      final timestamp = DateTime.parse(cacheData['timestamp'] as String);

      // Check if cache is expired
      if (DateTime.now().difference(timestamp) > _cacheExpiry) {
        return null;
      }

      return cacheData['data'] as Map<String, dynamic>;
    } catch (e) {
      return null;
    }
  }

  Future<void> _setCachedData(String key, dynamic data) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cacheData = {
        'timestamp': DateTime.now().toIso8601String(),
        'data': data,
      };
      await prefs.setString(key, jsonEncode(cacheData));
    } catch (e) {
      // Ignore cache errors
    }
  }

  /// Clear all cached menu data
  Future<void> clearCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final keys =
          prefs.getKeys().where((key) => key.startsWith(_cacheKeyPrefix));
      for (final key in keys) {
        await prefs.remove(key);
      }
    } catch (e) {
      // Ignore cache errors
    }
  }
}
