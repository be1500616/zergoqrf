import 'package:get/get.dart';

import '../../domain/entities/menu_category.dart';
import '../../domain/entities/menu_item.dart';
import '../../domain/entities/menu_structure.dart';
import '../../domain/entities/restaurant_branding.dart';
import '../../domain/entities/search_result.dart';
import '../use_cases/fetch_menu.dart';

/// Enhanced menu controller for public menu browsing.
class MenuController extends GetxController {
  MenuController(this._fetchMenuUseCase);

  final FetchMenuUseCase _fetchMenuUseCase;

  // Observable state
  final _isLoading = true.obs;
  final _menuStructure = Rxn<MenuStructure>();
  final _selectedCategory = Rxn<MenuCategory>();
  final _searchQuery = ''.obs;
  final _searchResults = Rxn<MenuSearchResult>();
  final _isSearching = false.obs;
  final _error = Rxn<String>();

  // Getters
  bool get isLoading => _isLoading.value;
  MenuStructure? get menuStructure => _menuStructure.value;
  RestaurantBranding? get restaurant => _menuStructure.value?.restaurant;
  List<MenuCategory> get categories => _menuStructure.value?.categories ?? [];
  List<DinerMenuItem> get allItems => _menuStructure.value?.items ?? [];
  MenuCategory? get selectedCategory => _selectedCategory.value;
  String get searchQuery => _searchQuery.value;
  MenuSearchResult? get searchResults => _searchResults.value;
  bool get isSearching => _isSearching.value;
  String? get error => _error.value;

  // Computed properties
  List<DinerMenuItem> get displayedItems {
    if (isSearching && searchResults != null) {
      return searchResults!.items;
    }

    if (selectedCategory != null) {
      return menuStructure?.getItemsForCategory(selectedCategory!.id) ?? [];
    }

    return allItems;
  }

  List<DinerMenuItem> get featuredItems {
    return menuStructure?.featuredItems ?? [];
  }

  bool get hasSearchResults => searchResults?.hasResults ?? false;
  bool get isSearchMode => searchQuery.isNotEmpty;

  /// Load menu structure for a restaurant.
  Future<void> loadMenu(String restaurantCode) async {
    try {
      _isLoading.value = true;
      _error.value = null;

      final structure =
          await _fetchMenuUseCase.getMenuStructure(restaurantCode);

      if (structure == null) {
        _error.value = 'Restaurant not found';
        return;
      }

      _menuStructure.value = structure;

      // Select first category by default
      if (categories.isNotEmpty) {
        _selectedCategory.value = categories.first;
      }
    } catch (e) {
      _error.value = 'Failed to load menu: ${e.toString()}';
    } finally {
      _isLoading.value = false;
    }
  }

  /// Select a category to display its items.
  void selectCategory(MenuCategory? category) {
    _selectedCategory.value = category;
    _clearSearch();
  }

  /// Search menu items.
  Future<void> searchItems(String query) async {
    if (query.trim().isEmpty) {
      _clearSearch();
      return;
    }

    try {
      _isSearching.value = true;
      _searchQuery.value = query;

      if (menuStructure == null) return;

      final results = await _fetchMenuUseCase.searchMenuItems(
        menuStructure!.restaurant.code,
        query,
      );

      _searchResults.value = results;
    } catch (e) {
      // Handle search error silently, show empty results
      _searchResults.value = MenuSearchResult(
        items: const [],
        totalCount: 0,
        searchQuery: query,
      );
    } finally {
      _isSearching.value = false;
    }
  }

  /// Clear search and return to category view.
  void _clearSearch() {
    _searchQuery.value = '';
    _searchResults.value = null;
    _isSearching.value = false;
  }

  /// Clear search from UI.
  void clearSearch() {
    _clearSearch();
  }

  /// Refresh menu data.
  @override
  Future<void> refresh() async {
    if (menuStructure != null) {
      await loadMenu(menuStructure!.restaurant.code);
    }
  }

  /// Get items for a specific category.
  List<DinerMenuItem> getItemsForCategory(String categoryId) {
    return menuStructure?.getItemsForCategory(categoryId) ?? [];
  }

  @override
  void onClose() {
    _isLoading.close();
    _menuStructure.close();
    _selectedCategory.close();
    _searchQuery.close();
    _searchResults.close();
    _isSearching.close();
    _error.close();
    super.onClose();
  }
}
