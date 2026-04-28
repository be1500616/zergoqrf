/// Menu domain entities for the Flutter frontend.
///
/// This file contains the core business entities for menu management.
library;

import 'package:equatable/equatable.dart';

/// Menu status enumeration
enum MenuStatus {
  draft,
  live,
  scheduled,
  archived,
}

/// Menu item status enumeration
enum ItemStatus {
  available,
  unavailable,
  seasonal,
  featured,
}

/// Dietary indicator enumeration
enum DietaryIndicator {
  vegetarian,
  vegan,
  glutenFree,
  keto,
  spicy,
  halal,
  kosher,
}

/// Modifier type enumeration
enum ModifierType {
  singleSelect,
  multiSelect,
  quantity,
}

/// Menu category entity
class MenuCategory extends Equatable {
  const MenuCategory({
    required this.id,
    required this.restaurantId,
    required this.name,
    this.description,
    this.parentCategoryId,
    required this.sortOrder,
    required this.isActive,
    required this.availabilitySchedule,
    required this.createdAt,
    required this.updatedAt,
    this.subcategories = const [],
    this.itemCount,
  });

  final String id;
  final String restaurantId;
  final String name;
  final String? description;
  final String? parentCategoryId;
  final int sortOrder;
  final bool isActive;
  final Map<String, dynamic> availabilitySchedule;
  final DateTime createdAt;
  final DateTime updatedAt;
  final List<MenuCategory> subcategories;
  final int? itemCount;

  @override
  List<Object?> get props => [
        id,
        restaurantId,
        name,
        description,
        parentCategoryId,
        sortOrder,
        isActive,
        availabilitySchedule,
        createdAt,
        updatedAt,
        subcategories,
        itemCount,
      ];

  MenuCategory copyWith({
    String? id,
    String? restaurantId,
    String? name,
    String? description,
    String? parentCategoryId,
    int? sortOrder,
    bool? isActive,
    Map<String, dynamic>? availabilitySchedule,
    DateTime? createdAt,
    DateTime? updatedAt,
    List<MenuCategory>? subcategories,
    int? itemCount,
  }) {
    return MenuCategory(
      id: id ?? this.id,
      restaurantId: restaurantId ?? this.restaurantId,
      name: name ?? this.name,
      description: description ?? this.description,
      parentCategoryId: parentCategoryId ?? this.parentCategoryId,
      sortOrder: sortOrder ?? this.sortOrder,
      isActive: isActive ?? this.isActive,
      availabilitySchedule: availabilitySchedule ?? this.availabilitySchedule,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      subcategories: subcategories ?? this.subcategories,
      itemCount: itemCount ?? this.itemCount,
    );
  }
}

/// Menu item variant entity
class MenuItemVariant extends Equatable {
  const MenuItemVariant({
    this.id,
    required this.name,
    this.description,
    required this.priceAdjustment,
    required this.sortOrder,
    required this.isActive,
  });

  final String? id;
  final String name;
  final String? description;
  final double priceAdjustment;
  final int sortOrder;
  final bool isActive;

  @override
  List<Object?> get props => [
        id,
        name,
        description,
        priceAdjustment,
        sortOrder,
        isActive,
      ];

  MenuItemVariant copyWith({
    String? id,
    String? name,
    String? description,
    double? priceAdjustment,
    int? sortOrder,
    bool? isActive,
  }) {
    return MenuItemVariant(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      priceAdjustment: priceAdjustment ?? this.priceAdjustment,
      sortOrder: sortOrder ?? this.sortOrder,
      isActive: isActive ?? this.isActive,
    );
  }
}

/// Menu item modifier entity
class MenuItemModifier extends Equatable {
  const MenuItemModifier({
    this.id,
    required this.name,
    this.description,
    required this.price,
    required this.sortOrder,
    required this.isActive,
  });

  final String? id;
  final String name;
  final String? description;
  final double price;
  final int sortOrder;
  final bool isActive;

  @override
  List<Object?> get props => [
        id,
        name,
        description,
        price,
        sortOrder,
        isActive,
      ];

  MenuItemModifier copyWith({
    String? id,
    String? name,
    String? description,
    double? price,
    int? sortOrder,
    bool? isActive,
  }) {
    return MenuItemModifier(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      price: price ?? this.price,
      sortOrder: sortOrder ?? this.sortOrder,
      isActive: isActive ?? this.isActive,
    );
  }
}

/// Menu item modifier group entity
class MenuItemModifierGroup extends Equatable {
  const MenuItemModifierGroup({
    this.id,
    required this.name,
    this.description,
    required this.modifierType,
    required this.isRequired,
    required this.minSelections,
    this.maxSelections,
    required this.sortOrder,
    required this.isActive,
    required this.modifiers,
  });

  final String? id;
  final String name;
  final String? description;
  final ModifierType modifierType;
  final bool isRequired;
  final int minSelections;
  final int? maxSelections;
  final int sortOrder;
  final bool isActive;
  final List<MenuItemModifier> modifiers;

  @override
  List<Object?> get props => [
        id,
        name,
        description,
        modifierType,
        isRequired,
        minSelections,
        maxSelections,
        sortOrder,
        isActive,
        modifiers,
      ];

  MenuItemModifierGroup copyWith({
    String? id,
    String? name,
    String? description,
    ModifierType? modifierType,
    bool? isRequired,
    int? minSelections,
    int? maxSelections,
    int? sortOrder,
    bool? isActive,
    List<MenuItemModifier>? modifiers,
  }) {
    return MenuItemModifierGroup(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      modifierType: modifierType ?? this.modifierType,
      isRequired: isRequired ?? this.isRequired,
      minSelections: minSelections ?? this.minSelections,
      maxSelections: maxSelections ?? this.maxSelections,
      sortOrder: sortOrder ?? this.sortOrder,
      isActive: isActive ?? this.isActive,
      modifiers: modifiers ?? this.modifiers,
    );
  }
}

/// Menu item entity
class MenuItem extends Equatable {
  const MenuItem({
    required this.id,
    required this.restaurantId,
    required this.categoryId,
    required this.name,
    this.description,
    required this.basePrice,
    this.imageUrl,
    required this.galleryImages,
    required this.status,
    required this.dietaryIndicators,
    required this.allergenInfo,
    required this.nutritionalInfo,
    this.preparationTime,
    required this.sortOrder,
    required this.isActive,
    required this.availabilitySchedule,
    this.dailyLimit,
    required this.soldCount,
    this.isFeatured = false,
    required this.createdAt,
    required this.updatedAt,
    this.categoryName,
    required this.variants,
    required this.modifierGroups,
  });

  final String id;
  final String restaurantId;
  final String categoryId;
  final String name;
  final String? description;
  final double basePrice;
  final String? imageUrl;
  final List<String> galleryImages;
  final ItemStatus status;
  final List<DietaryIndicator> dietaryIndicators;
  final List<String> allergenInfo;
  final Map<String, dynamic> nutritionalInfo;
  final int? preparationTime;
  final int sortOrder;
  final bool isActive;
  final Map<String, dynamic> availabilitySchedule;
  final int? dailyLimit;
  final int soldCount;
  final bool isFeatured;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String? categoryName;
  final List<MenuItemVariant> variants;
  final List<MenuItemModifierGroup> modifierGroups;

  @override
  List<Object?> get props => [
        id,
        restaurantId,
        categoryId,
        name,
        description,
        basePrice,
        imageUrl,
        galleryImages,
        status,
        dietaryIndicators,
        allergenInfo,
        nutritionalInfo,
        preparationTime,
        sortOrder,
        isActive,
        availabilitySchedule,
        dailyLimit,
        soldCount,
        isFeatured,
        createdAt,
        updatedAt,
        categoryName,
        variants,
        modifierGroups,
      ];

  MenuItem copyWith({
    String? id,
    String? restaurantId,
    String? categoryId,
    String? name,
    String? description,
    double? basePrice,
    String? imageUrl,
    List<String>? galleryImages,
    ItemStatus? status,
    List<DietaryIndicator>? dietaryIndicators,
    List<String>? allergenInfo,
    Map<String, dynamic>? nutritionalInfo,
    int? preparationTime,
    int? sortOrder,
    bool? isActive,
    Map<String, dynamic>? availabilitySchedule,
    int? dailyLimit,
    int? soldCount,
    DateTime? createdAt,
    DateTime? updatedAt,
    String? categoryName,
    List<MenuItemVariant>? variants,
    List<MenuItemModifierGroup>? modifierGroups,
  }) {
    return MenuItem(
      id: id ?? this.id,
      restaurantId: restaurantId ?? this.restaurantId,
      categoryId: categoryId ?? this.categoryId,
      name: name ?? this.name,
      description: description ?? this.description,
      basePrice: basePrice ?? this.basePrice,
      imageUrl: imageUrl ?? this.imageUrl,
      galleryImages: galleryImages ?? this.galleryImages,
      status: status ?? this.status,
      dietaryIndicators: dietaryIndicators ?? this.dietaryIndicators,
      allergenInfo: allergenInfo ?? this.allergenInfo,
      nutritionalInfo: nutritionalInfo ?? this.nutritionalInfo,
      preparationTime: preparationTime ?? this.preparationTime,
      sortOrder: sortOrder ?? this.sortOrder,
      isActive: isActive ?? this.isActive,
      availabilitySchedule: availabilitySchedule ?? this.availabilitySchedule,
      dailyLimit: dailyLimit ?? this.dailyLimit,
      soldCount: soldCount ?? this.soldCount,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      categoryName: categoryName ?? this.categoryName,
      variants: variants ?? this.variants,
      modifierGroups: modifierGroups ?? this.modifierGroups,
    );
  }
}

/// Menu version entity
class MenuVersion extends Equatable {
  const MenuVersion({
    required this.id,
    required this.restaurantId,
    required this.versionName,
    this.description,
    required this.status,
    required this.isCurrentLive,
    this.scheduledPublishAt,
    this.publishedAt,
    required this.createdBy,
    required this.createdAt,
    required this.updatedAt,
    this.categoryCount,
    this.itemCount,
  });

  final String id;
  final String restaurantId;
  final String versionName;
  final String? description;
  final MenuStatus status;
  final bool isCurrentLive;
  final DateTime? scheduledPublishAt;
  final DateTime? publishedAt;
  final String createdBy;
  final DateTime createdAt;
  final DateTime updatedAt;
  final int? categoryCount;
  final int? itemCount;

  @override
  List<Object?> get props => [
        id,
        restaurantId,
        versionName,
        description,
        status,
        isCurrentLive,
        scheduledPublishAt,
        publishedAt,
        createdBy,
        createdAt,
        updatedAt,
        categoryCount,
        itemCount,
      ];

  MenuVersion copyWith({
    String? id,
    String? restaurantId,
    String? versionName,
    String? description,
    MenuStatus? status,
    bool? isCurrentLive,
    DateTime? scheduledPublishAt,
    DateTime? publishedAt,
    String? createdBy,
    DateTime? createdAt,
    DateTime? updatedAt,
    int? categoryCount,
    int? itemCount,
  }) {
    return MenuVersion(
      id: id ?? this.id,
      restaurantId: restaurantId ?? this.restaurantId,
      versionName: versionName ?? this.versionName,
      description: description ?? this.description,
      status: status ?? this.status,
      isCurrentLive: isCurrentLive ?? this.isCurrentLive,
      scheduledPublishAt: scheduledPublishAt ?? this.scheduledPublishAt,
      publishedAt: publishedAt ?? this.publishedAt,
      createdBy: createdBy ?? this.createdBy,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      categoryCount: categoryCount ?? this.categoryCount,
      itemCount: itemCount ?? this.itemCount,
    );
  }
}
