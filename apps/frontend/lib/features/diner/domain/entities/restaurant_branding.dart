/// Restaurant branding entity for public menu display.
class RestaurantBranding {
  const RestaurantBranding({
    required this.id,
    required this.name,
    required this.code,
    this.logoUrl,
    this.primaryColor = '#FF6B35',
    this.secondaryColor = '#2C3E50',
    this.accentColor = '#F39C12',
    this.description,
    this.cuisineType,
    this.phone,
    this.address,
  });

  final String id;
  final String name;
  final String code;
  final String? logoUrl;
  final String primaryColor;
  final String secondaryColor;
  final String accentColor;
  final String? description;
  final String? cuisineType;
  final String? phone;
  final String? address;

  /// Factory constructor from JSON
  factory RestaurantBranding.fromJson(Map<String, dynamic> json) {
    return RestaurantBranding(
      id: json['id'] as String,
      name: json['name'] as String,
      code: json['code'] as String,
      logoUrl: json['logo_url'] as String?,
      primaryColor: json['primary_color'] as String? ?? '#FF6B35',
      secondaryColor: json['secondary_color'] as String? ?? '#2C3E50',
      accentColor: json['accent_color'] as String? ?? '#F39C12',
      description: json['description'] as String?,
      cuisineType: json['cuisine_type'] as String?,
      phone: json['phone'] as String?,
      address: json['address'] as String?,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'code': code,
      'logo_url': logoUrl,
      'primary_color': primaryColor,
      'secondary_color': secondaryColor,
      'accent_color': accentColor,
      'description': description,
      'cuisine_type': cuisineType,
      'phone': phone,
      'address': address,
    };
  }
}
