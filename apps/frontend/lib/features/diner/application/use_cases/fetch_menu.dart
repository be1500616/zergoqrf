import '../../domain/entities/menu_item.dart';
import '../../domain/entities/menu_structure.dart';
import '../../domain/entities/restaurant_branding.dart';
import '../../domain/entities/search_result.dart';
import '../../domain/repositories/menu_repository.dart';

/// Enhanced use case for fetching restaurant menu data.
class FetchMenuUseCase {
  FetchMenuUseCase(this._repo);
  final MenuRepository _repo;

  /// Get complete menu structure by restaurant code.
  Future<MenuStructure?> getMenuStructure(String restaurantCode) async {
    return _repo.getMenuStructure(restaurantCode);
  }

  /// Get restaurant branding information.
  Future<RestaurantBranding?> getRestaurantBranding(String restaurantCode) async {
    return _repo.getRestaurantBranding(restaurantCode);
  }

  /// Search menu items.
  Future<MenuSearchResult> searchMenuItems(String restaurantCode, String query) async {
    return _repo.searchMenuItems(restaurantCode, query);
  }

  /// Get featured items.
  Future<List<DinerMenuItem>> getFeaturedItems(String restaurantCode) async {
    return _repo.getFeaturedItems(restaurantCode);
  }

  /// Legacy method for backward compatibility.
  @Deprecated('Use getMenuStructure instead')
  Future<List<DinerMenuItem>> call(String restaurantCode) async {
    final structure = await _repo.getMenuStructure(restaurantCode);
    return structure?.items ?? [];
  }
}

