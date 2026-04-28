import '../entities/menu_item.dart';
import '../entities/menu_category.dart';
import '../entities/menu_structure.dart';
import '../entities/restaurant_branding.dart';
import '../entities/search_result.dart';

/// Enhanced repository interface for public menu data.
abstract class MenuRepository {
  /// Get restaurant branding information by code.
  Future<RestaurantBranding?> getRestaurantBranding(String restaurantCode);

  /// Get complete menu structure by restaurant code.
  Future<MenuStructure?> getMenuStructure(String restaurantCode);

  /// Get menu categories for a restaurant.
  Future<List<MenuCategory>> getMenuCategories(String restaurantCode);

  /// Get menu items for a specific category.
  Future<List<DinerMenuItem>> getCategoryItems(String restaurantCode, String categoryId);

  /// Search menu items by query.
  Future<MenuSearchResult> searchMenuItems(String restaurantCode, String query, {int limit = 50});

  /// Get featured menu items.
  Future<List<DinerMenuItem>> getFeaturedItems(String restaurantCode, {int limit = 10});

  /// Legacy methods for backward compatibility
  @Deprecated('Use getRestaurantBranding instead')
  Future<String> resolveRestaurantIdByCode(String restaurantCode);

  @Deprecated('Use getMenuStructure instead')
  Future<List<DinerMenuItem>> fetchPublicMenuItems(String restaurantId);
}

