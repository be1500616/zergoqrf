/// Menu repository interface.
/// 
/// This file defines the abstract repository interface for menu data access.

import '../entities/menu_entities.dart';

/// Abstract repository interface for menu data access
abstract class MenuRepository {
  // Category operations
  Future<MenuCategory> createCategory({
    required String name,
    String? description,
    String? parentCategoryId,
    int sortOrder = 0,
    Map<String, dynamic>? availabilitySchedule,
  });

  Future<List<MenuCategory>> getCategories({bool includeInactive = false});

  Future<List<MenuCategory>> getCategoryHierarchy();

  Future<MenuCategory> updateCategory(
    String categoryId,
    Map<String, dynamic> updateData,
  );

  Future<void> deleteCategory(String categoryId);

  Future<void> reorderCategories(List<Map<String, dynamic>> categoryOrders);

  // Menu item operations
  Future<MenuItem> createMenuItem({
    required String categoryId,
    required String name,
    String? description,
    required double basePrice,
    String? imageUrl,
    List<String> galleryImages = const [],
    ItemStatus status = ItemStatus.available,
    List<DietaryIndicator> dietaryIndicators = const [],
    List<String> allergenInfo = const [],
    Map<String, dynamic>? nutritionalInfo,
    int? preparationTime,
    int sortOrder = 0,
    Map<String, dynamic>? availabilitySchedule,
    int? dailyLimit,
    List<MenuItemVariant> variants = const [],
    List<MenuItemModifierGroup> modifierGroups = const [],
  });

  Future<List<MenuItem>> getMenuItems({
    String? categoryId,
    bool includeInactive = false,
  });

  Future<MenuItem?> getMenuItem(String itemId);

  Future<MenuItem> updateMenuItem(
    String itemId,
    Map<String, dynamic> updateData,
  );

  Future<void> deleteMenuItem(String itemId);

  Future<List<MenuItem>> searchMenuItems({
    String? query,
    String? categoryId,
    ItemStatus? status,
    List<DietaryIndicator>? dietaryIndicators,
    double? priceMin,
    double? priceMax,
    bool includeInactive = false,
  });

  // Menu versioning operations
  Future<MenuVersion> createMenuVersion({
    required String versionName,
    String? description,
  });

  Future<List<MenuVersion>> getMenuVersions();

  Future<MenuVersion?> getCurrentMenuVersion();

  Future<MenuVersion> publishMenuVersion(
    String versionId, {
    bool publishImmediately = true,
    DateTime? scheduledPublishAt,
    String? publishNotes,
  });

  Future<MenuVersion> rollbackToVersion(String versionId);

  // Menu structure operations
  Future<Map<String, dynamic>> getMenuStructure({String? versionId});

  Future<Map<String, dynamic>> getMenuAnalytics();

  Future<Map<String, dynamic>> getMenuPreview({String? versionId});
}
