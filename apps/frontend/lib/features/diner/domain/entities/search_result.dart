import 'menu_item.dart';
import 'menu_category.dart';

/// Search result for menu items.
class MenuSearchResult {
  const MenuSearchResult({
    required this.items,
    required this.totalCount,
    required this.searchQuery,
    this.categoriesFound = const [],
  });

  final List<DinerMenuItem> items;
  final int totalCount;
  final String searchQuery;
  final List<MenuCategory> categoriesFound;

  /// Factory constructor from JSON
  factory MenuSearchResult.fromJson(Map<String, dynamic> json) {
    return MenuSearchResult(
      items: (json['items'] as List<dynamic>)
          .map((e) => DinerMenuItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      totalCount: json['total_count'] as int,
      searchQuery: json['search_query'] as String,
      categoriesFound: (json['categories_found'] as List<dynamic>?)
          ?.map((e) => MenuCategory.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'items': items.map((e) => e.toJson()).toList(),
      'total_count': totalCount,
      'search_query': searchQuery,
      'categories_found': categoriesFound.map((e) => e.toJson()).toList(),
    };
  }

  /// Check if search has results
  bool get hasResults => items.isNotEmpty;

  /// Check if search found multiple categories
  bool get hasMultipleCategories => categoriesFound.length > 1;
}
