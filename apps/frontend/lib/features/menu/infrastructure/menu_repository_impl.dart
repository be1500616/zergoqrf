/// Menu repository implementation.
/// 
/// This file contains the concrete implementation of the menu repository
/// that communicates with the backend API.

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/config/api_config.dart';
import '../../../core/services/auth_service.dart';
import '../domain/entities/menu_entities.dart';
import '../domain/repositories/menu_repository.dart';

class MenuRepositoryImpl implements MenuRepository {
  MenuRepositoryImpl({
    required this.apiConfig,
    required this.authService,
  });

  final ApiConfig apiConfig;
  final AuthService authService;

  // Helper method to get headers with authentication
  Future<Map<String, String>> _getHeaders() async {
    final token = await authService.getAccessToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  // Helper method to handle API responses
  T _handleResponse<T>(http.Response response, T Function(Map<String, dynamic>) fromJson) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      final data = json.decode(response.body) as Map<String, dynamic>;
      return fromJson(data);
    } else {
      throw Exception('API Error: ${response.statusCode} - ${response.body}');
    }
  }

  List<T> _handleListResponse<T>(http.Response response, T Function(Map<String, dynamic>) fromJson) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      final data = json.decode(response.body) as List<dynamic>;
      return data.map((item) => fromJson(item as Map<String, dynamic>)).toList();
    } else {
      throw Exception('API Error: ${response.statusCode} - ${response.body}');
    }
  }

  // Category operations
  @override
  Future<MenuCategory> createCategory({
    required String name,
    String? description,
    String? parentCategoryId,
    int sortOrder = 0,
    Map<String, dynamic>? availabilitySchedule,
  }) async {
    final headers = await _getHeaders();
    final body = json.encode({
      'name': name,
      'description': description,
      'parent_category_id': parentCategoryId,
      'sort_order': sortOrder,
      'availability_schedule': availabilitySchedule ?? {},
    });

    final response = await http.post(
      Uri.parse('${apiConfig.baseUrl}/menu/categories'),
      headers: headers,
      body: body,
    );

    return _handleResponse(response, (data) => _menuCategoryFromJson(data));
  }

  @override
  Future<List<MenuCategory>> getCategories({bool includeInactive = false}) async {
    final headers = await _getHeaders();
    final uri = Uri.parse('${apiConfig.baseUrl}/menu/categories').replace(
      queryParameters: {'include_inactive': includeInactive.toString()},
    );

    final response = await http.get(uri, headers: headers);
    return _handleListResponse(response, (data) => _menuCategoryFromJson(data));
  }

  @override
  Future<List<MenuCategory>> getCategoryHierarchy() async {
    final headers = await _getHeaders();
    final response = await http.get(
      Uri.parse('${apiConfig.baseUrl}/menu/categories/hierarchy'),
      headers: headers,
    );

    return _handleListResponse(response, (data) => _menuCategoryFromJson(data));
  }

  @override
  Future<MenuCategory> updateCategory(
    String categoryId,
    Map<String, dynamic> updateData,
  ) async {
    final headers = await _getHeaders();
    final body = json.encode(updateData);

    final response = await http.put(
      Uri.parse('${apiConfig.baseUrl}/menu/categories/$categoryId'),
      headers: headers,
      body: body,
    );

    return _handleResponse(response, (data) => _menuCategoryFromJson(data));
  }

  @override
  Future<void> deleteCategory(String categoryId) async {
    final headers = await _getHeaders();
    final response = await http.delete(
      Uri.parse('${apiConfig.baseUrl}/menu/categories/$categoryId'),
      headers: headers,
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('Failed to delete category: ${response.statusCode} - ${response.body}');
    }
  }

  @override
  Future<void> reorderCategories(List<Map<String, dynamic>> categoryOrders) async {
    final headers = await _getHeaders();
    final body = json.encode({'category_orders': categoryOrders});

    final response = await http.post(
      Uri.parse('${apiConfig.baseUrl}/menu/categories/reorder'),
      headers: headers,
      body: body,
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('Failed to reorder categories: ${response.statusCode} - ${response.body}');
    }
  }

  // Menu item operations
  @override
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
  }) async {
    final headers = await _getHeaders();
    final body = json.encode({
      'category_id': categoryId,
      'name': name,
      'description': description,
      'base_price': basePrice,
      'image_url': imageUrl,
      'gallery_images': galleryImages,
      'status': status.name,
      'dietary_indicators': dietaryIndicators.map((e) => e.name).toList(),
      'allergen_info': allergenInfo,
      'nutritional_info': nutritionalInfo ?? {},
      'preparation_time': preparationTime,
      'sort_order': sortOrder,
      'availability_schedule': availabilitySchedule ?? {},
      'daily_limit': dailyLimit,
      'variants': variants.map((v) => _menuItemVariantToJson(v)).toList(),
      'modifier_groups': modifierGroups.map((g) => _menuItemModifierGroupToJson(g)).toList(),
    });

    final response = await http.post(
      Uri.parse('${apiConfig.baseUrl}/menu/items'),
      headers: headers,
      body: body,
    );

    return _handleResponse(response, (data) => _menuItemFromJson(data));
  }

  @override
  Future<List<MenuItem>> getMenuItems({
    String? categoryId,
    bool includeInactive = false,
  }) async {
    final headers = await _getHeaders();
    final queryParams = <String, String>{
      'include_inactive': includeInactive.toString(),
    };
    if (categoryId != null) {
      queryParams['category_id'] = categoryId;
    }

    final uri = Uri.parse('${apiConfig.baseUrl}/menu/items').replace(
      queryParameters: queryParams,
    );

    final response = await http.get(uri, headers: headers);
    return _handleListResponse(response, (data) => _menuItemFromJson(data));
  }

  @override
  Future<MenuItem?> getMenuItem(String itemId) async {
    final headers = await _getHeaders();
    final response = await http.get(
      Uri.parse('${apiConfig.baseUrl}/menu/items/$itemId'),
      headers: headers,
    );

    if (response.statusCode == 404) {
      return null;
    }

    return _handleResponse(response, (data) => _menuItemFromJson(data));
  }

  @override
  Future<MenuItem> updateMenuItem(
    String itemId,
    Map<String, dynamic> updateData,
  ) async {
    final headers = await _getHeaders();
    final body = json.encode(updateData);

    final response = await http.put(
      Uri.parse('${apiConfig.baseUrl}/menu/items/$itemId'),
      headers: headers,
      body: body,
    );

    return _handleResponse(response, (data) => _menuItemFromJson(data));
  }

  @override
  Future<void> deleteMenuItem(String itemId) async {
    final headers = await _getHeaders();
    final response = await http.delete(
      Uri.parse('${apiConfig.baseUrl}/menu/items/$itemId'),
      headers: headers,
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('Failed to delete menu item: ${response.statusCode} - ${response.body}');
    }
  }

  @override
  Future<List<MenuItem>> searchMenuItems({
    String? query,
    String? categoryId,
    ItemStatus? status,
    List<DietaryIndicator>? dietaryIndicators,
    double? priceMin,
    double? priceMax,
    bool includeInactive = false,
  }) async {
    final headers = await _getHeaders();
    final body = json.encode({
      'query': query,
      'category_id': categoryId,
      'status': status?.name,
      'dietary_indicators': dietaryIndicators?.map((e) => e.name).toList(),
      'price_min': priceMin,
      'price_max': priceMax,
      'include_inactive': includeInactive,
    });

    final response = await http.post(
      Uri.parse('${apiConfig.baseUrl}/menu/items/search'),
      headers: headers,
      body: body,
    );

    return _handleListResponse(response, (data) => _menuItemFromJson(data));
  }

  // Menu versioning operations
  @override
  Future<MenuVersion> createMenuVersion({
    required String versionName,
    String? description,
  }) async {
    final headers = await _getHeaders();
    final body = json.encode({
      'version_name': versionName,
      'description': description,
    });

    final response = await http.post(
      Uri.parse('${apiConfig.baseUrl}/menu/versions'),
      headers: headers,
      body: body,
    );

    return _handleResponse(response, (data) => _menuVersionFromJson(data));
  }

  @override
  Future<List<MenuVersion>> getMenuVersions() async {
    final headers = await _getHeaders();
    final response = await http.get(
      Uri.parse('${apiConfig.baseUrl}/menu/versions'),
      headers: headers,
    );

    return _handleListResponse(response, (data) => _menuVersionFromJson(data));
  }

  @override
  Future<MenuVersion?> getCurrentMenuVersion() async {
    final headers = await _getHeaders();
    final response = await http.get(
      Uri.parse('${apiConfig.baseUrl}/menu/versions/current'),
      headers: headers,
    );

    if (response.statusCode == 404) {
      return null;
    }

    return _handleResponse(response, (data) => _menuVersionFromJson(data));
  }

  @override
  Future<MenuVersion> publishMenuVersion(
    String versionId, {
    bool publishImmediately = true,
    DateTime? scheduledPublishAt,
    String? publishNotes,
  }) async {
    final headers = await _getHeaders();
    final body = json.encode({
      'publish_immediately': publishImmediately,
      'scheduled_publish_at': scheduledPublishAt?.toIso8601String(),
      'publish_notes': publishNotes,
    });

    final response = await http.post(
      Uri.parse('${apiConfig.baseUrl}/menu/versions/$versionId/publish'),
      headers: headers,
      body: body,
    );

    return _handleResponse(response, (data) => _menuVersionFromJson(data));
  }

  @override
  Future<MenuVersion> rollbackToVersion(String versionId) async {
    final headers = await _getHeaders();
    final response = await http.post(
      Uri.parse('${apiConfig.baseUrl}/menu/versions/$versionId/rollback'),
      headers: headers,
    );

    return _handleResponse(response, (data) => _menuVersionFromJson(data));
  }

  // Menu structure operations
  @override
  Future<Map<String, dynamic>> getMenuStructure({String? versionId}) async {
    final headers = await _getHeaders();
    final queryParams = <String, String>{};
    if (versionId != null) {
      queryParams['version_id'] = versionId;
    }

    final uri = Uri.parse('${apiConfig.baseUrl}/menu/structure').replace(
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
    );

    final response = await http.get(uri, headers: headers);
    
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return json.decode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('API Error: ${response.statusCode} - ${response.body}');
    }
  }

  @override
  Future<Map<String, dynamic>> getMenuAnalytics() async {
    final headers = await _getHeaders();
    final response = await http.get(
      Uri.parse('${apiConfig.baseUrl}/menu/analytics'),
      headers: headers,
    );

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return json.decode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('API Error: ${response.statusCode} - ${response.body}');
    }
  }

  @override
  Future<Map<String, dynamic>> getMenuPreview({String? versionId}) async {
    // For now, use the same endpoint as getMenuStructure
    // In a real implementation, this might be a different endpoint
    return getMenuStructure(versionId: versionId);
  }

  // JSON conversion methods
  MenuCategory _menuCategoryFromJson(Map<String, dynamic> json) {
    return MenuCategory(
      id: json['id'] as String,
      restaurantId: json['restaurant_id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      parentCategoryId: json['parent_category_id'] as String?,
      sortOrder: json['sort_order'] as int,
      isActive: json['is_active'] as bool,
      availabilitySchedule: json['availability_schedule'] as Map<String, dynamic>,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      subcategories: (json['subcategories'] as List<dynamic>?)
          ?.map((e) => _menuCategoryFromJson(e as Map<String, dynamic>))
          .toList() ?? [],
      itemCount: json['item_count'] as int?,
    );
  }

  MenuItem _menuItemFromJson(Map<String, dynamic> json) {
    return MenuItem(
      id: json['id'] as String,
      restaurantId: json['restaurant_id'] as String,
      categoryId: json['category_id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      basePrice: (json['base_price'] as num).toDouble(),
      imageUrl: json['image_url'] as String?,
      galleryImages: (json['gallery_images'] as List<dynamic>).cast<String>(),
      status: ItemStatus.values.firstWhere((e) => e.name == json['status']),
      dietaryIndicators: (json['dietary_indicators'] as List<dynamic>)
          .map((e) => DietaryIndicator.values.firstWhere((d) => d.name == e))
          .toList(),
      allergenInfo: (json['allergen_info'] as List<dynamic>).cast<String>(),
      nutritionalInfo: json['nutritional_info'] as Map<String, dynamic>,
      preparationTime: json['preparation_time'] as int?,
      sortOrder: json['sort_order'] as int,
      isActive: json['is_active'] as bool,
      availabilitySchedule: json['availability_schedule'] as Map<String, dynamic>,
      dailyLimit: json['daily_limit'] as int?,
      soldCount: json['sold_count'] as int,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      categoryName: json['category_name'] as String?,
      variants: (json['variants'] as List<dynamic>?)
          ?.map((e) => _menuItemVariantFromJson(e as Map<String, dynamic>))
          .toList() ?? [],
      modifierGroups: (json['modifier_groups'] as List<dynamic>?)
          ?.map((e) => _menuItemModifierGroupFromJson(e as Map<String, dynamic>))
          .toList() ?? [],
    );
  }

  MenuItemVariant _menuItemVariantFromJson(Map<String, dynamic> json) {
    return MenuItemVariant(
      id: json['id'] as String?,
      name: json['name'] as String,
      description: json['description'] as String?,
      priceAdjustment: (json['price_adjustment'] as num).toDouble(),
      sortOrder: json['sort_order'] as int,
      isActive: json['is_active'] as bool,
    );
  }

  MenuItemModifierGroup _menuItemModifierGroupFromJson(Map<String, dynamic> json) {
    return MenuItemModifierGroup(
      id: json['id'] as String?,
      name: json['name'] as String,
      description: json['description'] as String?,
      modifierType: ModifierType.values.firstWhere((e) => e.name == json['modifier_type']),
      isRequired: json['is_required'] as bool,
      minSelections: json['min_selections'] as int,
      maxSelections: json['max_selections'] as int?,
      sortOrder: json['sort_order'] as int,
      isActive: json['is_active'] as bool,
      modifiers: (json['modifiers'] as List<dynamic>?)
          ?.map((e) => _menuItemModifierFromJson(e as Map<String, dynamic>))
          .toList() ?? [],
    );
  }

  MenuItemModifier _menuItemModifierFromJson(Map<String, dynamic> json) {
    return MenuItemModifier(
      id: json['id'] as String?,
      name: json['name'] as String,
      description: json['description'] as String?,
      price: (json['price'] as num).toDouble(),
      sortOrder: json['sort_order'] as int,
      isActive: json['is_active'] as bool,
    );
  }

  MenuVersion _menuVersionFromJson(Map<String, dynamic> json) {
    return MenuVersion(
      id: json['id'] as String,
      restaurantId: json['restaurant_id'] as String,
      versionName: json['version_name'] as String,
      description: json['description'] as String?,
      status: MenuStatus.values.firstWhere((e) => e.name == json['status']),
      isCurrentLive: json['is_current_live'] as bool,
      scheduledPublishAt: json['scheduled_publish_at'] != null
          ? DateTime.parse(json['scheduled_publish_at'] as String)
          : null,
      publishedAt: json['published_at'] != null
          ? DateTime.parse(json['published_at'] as String)
          : null,
      createdBy: json['created_by'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      categoryCount: json['category_count'] as int?,
      itemCount: json['item_count'] as int?,
    );
  }

  // JSON serialization methods
  Map<String, dynamic> _menuItemVariantToJson(MenuItemVariant variant) {
    return {
      'id': variant.id,
      'name': variant.name,
      'description': variant.description,
      'price_adjustment': variant.priceAdjustment,
      'sort_order': variant.sortOrder,
      'is_active': variant.isActive,
    };
  }

  Map<String, dynamic> _menuItemModifierGroupToJson(MenuItemModifierGroup group) {
    return {
      'id': group.id,
      'name': group.name,
      'description': group.description,
      'modifier_type': group.modifierType.name,
      'is_required': group.isRequired,
      'min_selections': group.minSelections,
      'max_selections': group.maxSelections,
      'sort_order': group.sortOrder,
      'is_active': group.isActive,
      'modifiers': group.modifiers.map((m) => _menuItemModifierToJson(m)).toList(),
    };
  }

  Map<String, dynamic> _menuItemModifierToJson(MenuItemModifier modifier) {
    return {
      'id': modifier.id,
      'name': modifier.name,
      'description': modifier.description,
      'price': modifier.price,
      'sort_order': modifier.sortOrder,
      'is_active': modifier.isActive,
    };
  }
}
