/// Menu category entity for public menu display.
class MenuCategory {
  const MenuCategory({
    required this.id,
    required this.name,
    this.description,
    this.sortOrder = 0,
    this.itemCount = 0,
  });

  final String id;
  final String name;
  final String? description;
  final int sortOrder;
  final int itemCount;

  /// Factory constructor from JSON
  factory MenuCategory.fromJson(Map<String, dynamic> json) {
    return MenuCategory(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      sortOrder: json['sort_order'] as int? ?? 0,
      itemCount: json['item_count'] as int? ?? 0,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'sort_order': sortOrder,
      'item_count': itemCount,
    };
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is MenuCategory && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}
