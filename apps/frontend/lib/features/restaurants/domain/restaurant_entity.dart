/// Restaurant domain entities.
///
/// This module contains the core business entities for the restaurant feature.

import 'package:equatable/equatable.dart';

class Restaurant extends Equatable {
  /// Restaurant entity representing a restaurant business.
  
  final String id;
  final String name;
  final String code;
  final String? description;
  final String? address;
  final String? phone;
  final String? email;
  final String? website;
  final String? cuisineType;
  final String? diningStyle;
  final Map<String, dynamic> businessHours;
  final Map<String, dynamic> settings;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;

  const Restaurant({
    required this.id,
    required this.name,
    required this.code,
    this.description,
    this.address,
    this.phone,
    this.email,
    this.website,
    this.cuisineType,
    this.diningStyle,
    this.businessHours = const {},
    this.settings = const {},
    this.isActive = true,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Restaurant.fromJson(Map<String, dynamic> json) {
    return Restaurant(
      id: json['id'] as String,
      name: json['name'] as String,
      code: json['code'] as String,
      description: json['description'] as String?,
      address: json['address'] as String?,
      phone: json['phone'] as String?,
      email: json['email'] as String?,
      website: json['website'] as String?,
      cuisineType: json['cuisine_type'] as String?,
      diningStyle: json['dining_style'] as String?,
      businessHours: json['business_hours'] as Map<String, dynamic>? ?? {},
      settings: json['settings'] as Map<String, dynamic>? ?? {},
      isActive: json['is_active'] as bool? ?? true,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'code': code,
      'description': description,
      'address': address,
      'phone': phone,
      'email': email,
      'website': website,
      'cuisine_type': cuisineType,
      'dining_style': diningStyle,
      'business_hours': businessHours,
      'settings': settings,
      'is_active': isActive,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  Restaurant copyWith({
    String? id,
    String? name,
    String? code,
    String? description,
    String? address,
    String? phone,
    String? email,
    String? website,
    String? cuisineType,
    String? diningStyle,
    Map<String, dynamic>? businessHours,
    Map<String, dynamic>? settings,
    bool? isActive,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Restaurant(
      id: id ?? this.id,
      name: name ?? this.name,
      code: code ?? this.code,
      description: description ?? this.description,
      address: address ?? this.address,
      phone: phone ?? this.phone,
      email: email ?? this.email,
      website: website ?? this.website,
      cuisineType: cuisineType ?? this.cuisineType,
      diningStyle: diningStyle ?? this.diningStyle,
      businessHours: businessHours ?? this.businessHours,
      settings: settings ?? this.settings,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        name,
        code,
        description,
        address,
        phone,
        email,
        website,
        cuisineType,
        diningStyle,
        businessHours,
        settings,
        isActive,
        createdAt,
        updatedAt,
      ];
}

class RestaurantStaff extends Equatable {
  /// Restaurant staff entity.
  
  final String id;
  final String restaurantId;
  final String userId;
  final String role;
  final Map<String, dynamic> permissions;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String? email;
  final String? name;

  const RestaurantStaff({
    required this.id,
    required this.restaurantId,
    required this.userId,
    required this.role,
    this.permissions = const {},
    this.isActive = true,
    required this.createdAt,
    required this.updatedAt,
    this.email,
    this.name,
  });

  factory RestaurantStaff.fromJson(Map<String, dynamic> json) {
    return RestaurantStaff(
      id: json['id'] as String,
      restaurantId: json['restaurant_id'] as String,
      userId: json['user_id'] as String,
      role: json['role'] as String,
      permissions: json['permissions'] as Map<String, dynamic>? ?? {},
      isActive: json['is_active'] as bool? ?? true,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      email: json['email'] as String?,
      name: json['name'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'restaurant_id': restaurantId,
      'user_id': userId,
      'role': role,
      'permissions': permissions,
      'is_active': isActive,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'email': email,
      'name': name,
    };
  }

  @override
  List<Object?> get props => [
        id,
        restaurantId,
        userId,
        role,
        permissions,
        isActive,
        createdAt,
        updatedAt,
        email,
        name,
      ];
}

class RestaurantRegistrationRequest extends Equatable {
  /// Request model for restaurant registration.
  
  final String name;
  final String? description;
  final String? address;
  final String? phone;
  final String? email;
  final String? website;
  final String? cuisineType;
  final String? diningStyle;
  final String ownerEmail;
  final String ownerPassword;
  final String? ownerName;

  const RestaurantRegistrationRequest({
    required this.name,
    this.description,
    this.address,
    this.phone,
    this.email,
    this.website,
    this.cuisineType,
    this.diningStyle,
    required this.ownerEmail,
    required this.ownerPassword,
    this.ownerName,
  });

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'description': description,
      'address': address,
      'phone': phone,
      'email': email,
      'website': website,
      'cuisine_type': cuisineType,
      'dining_style': diningStyle,
      'owner_email': ownerEmail,
      'owner_password': ownerPassword,
      'owner_name': ownerName,
    };
  }

  @override
  List<Object?> get props => [
        name,
        description,
        address,
        phone,
        email,
        website,
        cuisineType,
        diningStyle,
        ownerEmail,
        ownerPassword,
        ownerName,
      ];
}

class RestaurantRegistrationResponse extends Equatable {
  /// Response model for restaurant registration.
  
  final Restaurant restaurant;
  final RestaurantStaff owner;
  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final int expiresIn;

  const RestaurantRegistrationResponse({
    required this.restaurant,
    required this.owner,
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.expiresIn,
  });

  factory RestaurantRegistrationResponse.fromJson(Map<String, dynamic> json) {
    return RestaurantRegistrationResponse(
      restaurant: Restaurant.fromJson(json['restaurant'] as Map<String, dynamic>),
      owner: RestaurantStaff.fromJson(json['owner'] as Map<String, dynamic>),
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
      tokenType: json['token_type'] as String,
      expiresIn: json['expires_in'] as int,
    );
  }

  @override
  List<Object?> get props => [
        restaurant,
        owner,
        accessToken,
        refreshToken,
        tokenType,
        expiresIn,
      ];
}
