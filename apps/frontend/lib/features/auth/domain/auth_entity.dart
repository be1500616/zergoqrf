import 'package:equatable/equatable.dart';

class AuthUser extends Equatable {
  final String id;
  final String? email;
  final String? phone;
  final String? name;
  final String role;
  final String? restaurantId;
  final Map<String, dynamic> permissions;
  final bool isActive;
  final bool isAnonymous;
  final DateTime? createdAt;

  const AuthUser({
    required this.id,
    this.email,
    this.phone,
    this.name,
    required this.role,
    this.restaurantId,
    this.permissions = const {},
    this.isActive = true,
    this.isAnonymous = false,
    this.createdAt,
  });

  factory AuthUser.fromJson(Map<String, dynamic> json) {
    return AuthUser(
      id: json['id'] as String,
      email: json['email'] as String?,
      phone: json['phone'] as String?,
      name: json['name'] as String?,
      role: json['role'] as String,
      restaurantId: json['restaurant_id'] as String?,
      permissions: json['permissions'] as Map<String, dynamic>? ?? {},
      isActive: json['is_active'] as bool? ?? true,
      isAnonymous: json['is_anonymous'] as bool? ?? false,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'phone': phone,
      'name': name,
      'role': role,
      'restaurant_id': restaurantId,
      'permissions': permissions,
      'is_active': isActive,
      'is_anonymous': isAnonymous,
      'created_at': createdAt?.toIso8601String(),
    };
  }

  AuthUser copyWith({
    String? id,
    String? email,
    String? phone,
    String? name,
    String? role,
    String? restaurantId,
    Map<String, dynamic>? permissions,
    bool? isActive,
    bool? isAnonymous,
    DateTime? createdAt,
  }) {
    return AuthUser(
      id: id ?? this.id,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      name: name ?? this.name,
      role: role ?? this.role,
      restaurantId: restaurantId ?? this.restaurantId,
      permissions: permissions ?? this.permissions,
      isActive: isActive ?? this.isActive,
      isAnonymous: isAnonymous ?? this.isAnonymous,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  bool hasRole(String targetRole) => role == targetRole;

  bool hasAnyRole(List<String> roles) => roles.contains(role);

  bool hasPermission(String permission) {
    if (role == 'owner') return true;
    return permissions[permission] == true;
  }

  bool canAccessRestaurant(String? targetRestaurantId) {
    if (targetRestaurantId == null) return true;
    return restaurantId == targetRestaurantId;
  }

  @override
  List<Object?> get props => [
        id,
        email,
        phone,
        name,
        role,
        restaurantId,
        permissions,
        isActive,
        isAnonymous,
        createdAt,
      ];
}

class AnonymousSession extends Equatable {
  final String sessionId;
  final String sessionToken;
  final String restaurantId;
  final String tableId;
  final DateTime expiresAt;

  const AnonymousSession({
    required this.sessionId,
    required this.sessionToken,
    required this.restaurantId,
    required this.tableId,
    required this.expiresAt,
  });

  factory AnonymousSession.fromJson(Map<String, dynamic> json) {
    return AnonymousSession(
      sessionId: json['session_id'] as String,
      sessionToken: json['session_token'] as String,
      restaurantId: json['restaurant_id'] as String,
      tableId: json['table_id'] as String,
      expiresAt: DateTime.parse(json['expires_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'session_id': sessionId,
      'session_token': sessionToken,
      'restaurant_id': restaurantId,
      'table_id': tableId,
      'expires_at': expiresAt.toIso8601String(),
    };
  }

  bool get isExpired => DateTime.now().isAfter(expiresAt);

  @override
  List<Object?> get props => [
        sessionId,
        sessionToken,
        restaurantId,
        tableId,
        expiresAt,
      ];
}