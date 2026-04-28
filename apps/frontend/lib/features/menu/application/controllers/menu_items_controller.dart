/// Menu items controller for managing menu items tab functionality.
///
/// This controller manages search, filtering, and display of menu items
/// with reactive state management using GetX patterns.
library;

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../domain/entities/menu_entities.dart';

class MenuItemsController extends GetxController {
  /// Text editing controller for search input
  final TextEditingController searchController = TextEditingController();

  /// Current search query
  final RxString searchQuery = ''.obs;

  /// Selected category filter
  final RxnString selectedCategoryId = RxnString();

  /// Selected status filter
  final Rxn<ItemStatus> selectedStatus = Rxn<ItemStatus>();

  /// Whether to show only featured items
  final RxBool showFeaturedOnly = false.obs;

  /// Sort option
  final RxString sortBy = 'name'.obs; // name, price, created, popularity

  /// Sort direction
  final RxBool sortAscending = true.obs;

  @override
  void onInit() {
    super.onInit();

    // Listen to search text changes
    searchController.addListener(() {
      searchQuery.value = searchController.text;
    });
  }

  @override
  void onClose() {
    searchController.dispose();
    super.onClose();
  }

  /// Clear search input
  void clearSearch() {
    searchController.clear();
    searchQuery.value = '';
  }

  /// Set category filter
  void setCategoryFilter(String? categoryId) {
    selectedCategoryId.value = categoryId;
  }

  /// Set status filter
  void setStatusFilter(ItemStatus? status) {
    selectedStatus.value = status;
  }

  /// Toggle featured items filter
  void toggleFeaturedFilter() {
    showFeaturedOnly.value = !showFeaturedOnly.value;
  }

  /// Set sort option
  void setSortBy(String sortOption) {
    if (sortBy.value == sortOption) {
      // Toggle sort direction if same option
      sortAscending.value = !sortAscending.value;
    } else {
      sortBy.value = sortOption;
      sortAscending.value = true;
    }
  }

  /// Clear all filters
  void clearFilters() {
    selectedCategoryId.value = null;
    selectedStatus.value = null;
    showFeaturedOnly.value = false;
    clearSearch();
  }

  /// Get filtered and sorted menu items
  List<MenuItem> getFilteredItems(List<MenuItem> allItems) {
    var filteredItems = allItems.where((item) {
      // Search filter
      if (searchQuery.value.isNotEmpty) {
        final query = searchQuery.value.toLowerCase();
        if (!item.name.toLowerCase().contains(query) &&
            !(item.description?.toLowerCase().contains(query) ?? false)) {
          return false;
        }
      }

      // Category filter
      if (selectedCategoryId.value != null) {
        if (item.categoryId != selectedCategoryId.value) {
          return false;
        }
      }

      // Status filter
      if (selectedStatus.value != null) {
        if (item.status != selectedStatus.value) {
          return false;
        }
      }

      // Featured filter
      if (showFeaturedOnly.value) {
        if (!item.isFeatured) {
          return false;
        }
      }

      return true;
    }).toList();

    // Sort items
    filteredItems.sort((a, b) {
      int comparison = 0;

      switch (sortBy.value) {
        case 'name':
          comparison = a.name.compareTo(b.name);
          break;
        case 'price':
          comparison = a.basePrice.compareTo(b.basePrice);
          break;
        case 'created':
          comparison = a.createdAt.compareTo(b.createdAt);
          break;
        case 'popularity':
          // Using soldCount as popularity metric
          comparison = a.soldCount.compareTo(b.soldCount);
          break;
      }

      return sortAscending.value ? comparison : -comparison;
    });

    return filteredItems;
  }

  /// Get filter summary text
  String getFilterSummary(int totalItems, int filteredItems) {
    if (totalItems == filteredItems) {
      return 'Showing all $totalItems items';
    }

    List<String> activeFilters = [];

    if (searchQuery.value.isNotEmpty) {
      activeFilters.add('search');
    }

    if (selectedCategoryId.value != null) {
      activeFilters.add('category');
    }

    if (selectedStatus.value != null) {
      activeFilters.add('status');
    }

    if (showFeaturedOnly.value) {
      activeFilters.add('featured');
    }

    String filterText = activeFilters.join(', ');
    return 'Showing $filteredItems of $totalItems items (filtered by $filterText)';
  }
}
