import 'restaurant_branding.dart';
import 'menu_category.dart';
import 'menu_item.dart';

/// Complete menu structure for public browsing.
class MenuStructure {
  const MenuStructure({
    required this.restaurant,
    required this.categories,
    required this.items,
    required this.lastUpdated,
  });

  final RestaurantBranding restaurant;
  final List<MenuCategory> categories;
  final List<DinerMenuItem> items;
  final DateTime lastUpdated;

  /// Factory constructor from JSON
  factory MenuStructure.fromJson(Map<String, dynamic> json) {
    return MenuStructure(
      restaurant: RestaurantBranding.fromJson(json['restaurant'] as Map<String, dynamic>),
      categories: (json['categories'] as List<dynamic>)
          .map((e) => MenuCategory.fromJson(e as Map<String, dynamic>))
          .toList(),
      items: (json['items'] as List<dynamic>)
          .map((e) => DinerMenuItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      lastUpdated: DateTime.parse(json['last_updated'] as String),
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'restaurant': restaurant.toJson(),
      'categories': categories.map((e) => e.toJson()).toList(),
      'items': items.map((e) => e.toJson()).toList(),
      'last_updated': lastUpdated.toIso8601String(),
    };
  }

  /// Get items for a specific category
  List<DinerMenuItem> getItemsForCategory(String categoryId) {
    return items.where((item) => item.categoryId == categoryId).toList();
  }

  /// Get featured items
  List<DinerMenuItem> get featuredItems {
    return items.where((item) => item.isFeatured).toList();
  }

  /// Get available items only
  List<DinerMenuItem> get availableItems {
    return items.where((item) => item.isAvailable).toList();
  }
}
