import 'dietary_indicator.dart';
import 'item_status.dart';

/// Enhanced diner-facing menu item entity for public menu browsing.
class DinerMenuItem {
  const DinerMenuItem({
    required this.id,
    required this.categoryId,
    required this.name,
    required this.basePrice,
    this.description,
    this.imageUrl,
    this.galleryImages = const [],
    this.status = ItemStatus.available,
    this.dietaryIndicators = const [],
    this.allergenInfo = const [],
    this.preparationTime,
    this.sortOrder = 0,
    this.isFeatured = false,
  });

  final String id;
  final String categoryId;
  final String name;
  final double basePrice;
  final String? description;
  final String? imageUrl;
  final List<String> galleryImages;
  final ItemStatus status;
  final List<DietaryIndicator> dietaryIndicators;
  final List<String> allergenInfo;
  final int? preparationTime; // in minutes
  final int sortOrder;
  final bool isFeatured;

  /// Get price in cents for backward compatibility
  int get priceCents => (basePrice * 100).round();

  /// Check if item is available for ordering
  bool get isAvailable => status.isAvailable;

  /// Factory constructor from JSON
  factory DinerMenuItem.fromJson(Map<String, dynamic> json) {
    return DinerMenuItem(
      id: json['id'] as String,
      categoryId: json['category_id'] as String,
      name: json['name'] as String,
      basePrice: (json['base_price'] as num).toDouble(),
      description: json['description'] as String?,
      imageUrl: json['image_url'] as String?,
      galleryImages: (json['gallery_images'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList() ?? [],
      status: ItemStatus.fromValue(json['status'] as String? ?? 'available'),
      dietaryIndicators: DietaryIndicator.fromValueList(
        (json['dietary_indicators'] as List<dynamic>?)
            ?.map((e) => e as String)
            .toList() ?? [],
      ),
      allergenInfo: (json['allergen_info'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList() ?? [],
      preparationTime: json['preparation_time'] as int?,
      sortOrder: json['sort_order'] as int? ?? 0,
      isFeatured: json['is_featured'] as bool? ?? false,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'category_id': categoryId,
      'name': name,
      'base_price': basePrice,
      'description': description,
      'image_url': imageUrl,
      'gallery_images': galleryImages,
      'status': status.value,
      'dietary_indicators': DietaryIndicator.toValueList(dietaryIndicators),
      'allergen_info': allergenInfo,
      'preparation_time': preparationTime,
      'sort_order': sortOrder,
      'is_featured': isFeatured,
    };
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is DinerMenuItem && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

