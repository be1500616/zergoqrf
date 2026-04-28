/// Table management domain entities.
/// 
/// This module contains the core business entities for table management.

import 'package:equatable/equatable.dart';

/// Table status enumeration.
enum TableStatus {
  available('available'),
  occupied('occupied'),
  reserved('reserved'),
  cleaning('cleaning'),
  maintenance('maintenance'),
  outOfOrder('out_of_order');

  const TableStatus(this.value);
  final String value;

  static TableStatus fromString(String value) {
    return TableStatus.values.firstWhere(
      (status) => status.value == value,
      orElse: () => TableStatus.available,
    );
  }
}

/// Table shape enumeration.
enum TableShape {
  round('round'),
  square('square'),
  rectangular('rectangular'),
  oval('oval');

  const TableShape(this.value);
  final String value;

  static TableShape fromString(String value) {
    return TableShape.values.firstWhere(
      (shape) => shape.value == value,
      orElse: () => TableShape.round,
    );
  }
}

/// Table category enumeration.
enum TableCategory {
  regular('regular'),
  vip('vip'),
  outdoor('outdoor'),
  bar('bar'),
  counter('counter'),
  booth('booth');

  const TableCategory(this.value);
  final String value;

  static TableCategory fromString(String value) {
    return TableCategory.values.firstWhere(
      (category) => category.value == value,
      orElse: () => TableCategory.regular,
    );
  }
}

/// Table position value object.
class Position extends Equatable {
  const Position({
    required this.x,
    required this.y,
  });

  final double x;
  final double y;

  Position copyWith({
    double? x,
    double? y,
  }) {
    return Position(
      x: x ?? this.x,
      y: y ?? this.y,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'x': x,
      'y': y,
    };
  }

  factory Position.fromJson(Map<String, dynamic> json) {
    return Position(
      x: (json['x'] as num).toDouble(),
      y: (json['y'] as num).toDouble(),
    );
  }

  @override
  List<Object?> get props => [x, y];
}

/// Table dimensions value object.
class Dimensions extends Equatable {
  const Dimensions({
    required this.width,
    required this.height,
  });

  final double width;
  final double height;

  Dimensions copyWith({
    double? width,
    double? height,
  }) {
    return Dimensions(
      width: width ?? this.width,
      height: height ?? this.height,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'width': width,
      'height': height,
    };
  }

  factory Dimensions.fromJson(Map<String, dynamic> json) {
    return Dimensions(
      width: (json['width'] as num).toDouble(),
      height: (json['height'] as num).toDouble(),
    );
  }

  @override
  List<Object?> get props => [width, height];
}

/// QR code data value object.
class QRCodeData extends Equatable {
  const QRCodeData({
    required this.token,
    this.url,
    this.data = const {},
  });

  final String token;
  final String? url;
  final Map<String, dynamic> data;

  QRCodeData copyWith({
    String? token,
    String? url,
    Map<String, dynamic>? data,
  }) {
    return QRCodeData(
      token: token ?? this.token,
      url: url ?? this.url,
      data: data ?? this.data,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'token': token,
      'url': url,
      'data': data,
    };
  }

  factory QRCodeData.fromJson(Map<String, dynamic> json) {
    return QRCodeData(
      token: json['token'] as String,
      url: json['url'] as String?,
      data: Map<String, dynamic>.from(json['data'] ?? {}),
    );
  }

  @override
  List<Object?> get props => [token, url, data];
}

/// Floor entity representing a restaurant floor.
class Floor extends Equatable {
  const Floor({
    required this.id,
    required this.restaurantId,
    required this.name,
    this.description,
    required this.floorNumber,
    required this.isActive,
    required this.layoutConfig,
    required this.createdAt,
    required this.updatedAt,
  });

  final String id;
  final String restaurantId;
  final String name;
  final String? description;
  final int floorNumber;
  final bool isActive;
  final Map<String, dynamic> layoutConfig;
  final DateTime createdAt;
  final DateTime updatedAt;

  Floor copyWith({
    String? id,
    String? restaurantId,
    String? name,
    String? description,
    int? floorNumber,
    bool? isActive,
    Map<String, dynamic>? layoutConfig,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Floor(
      id: id ?? this.id,
      restaurantId: restaurantId ?? this.restaurantId,
      name: name ?? this.name,
      description: description ?? this.description,
      floorNumber: floorNumber ?? this.floorNumber,
      isActive: isActive ?? this.isActive,
      layoutConfig: layoutConfig ?? this.layoutConfig,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'restaurant_id': restaurantId,
      'name': name,
      'description': description,
      'floor_number': floorNumber,
      'is_active': isActive,
      'layout_config': layoutConfig,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  factory Floor.fromJson(Map<String, dynamic> json) {
    return Floor(
      id: json['id'] as String,
      restaurantId: json['restaurant_id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      floorNumber: json['floor_number'] as int,
      isActive: json['is_active'] as bool,
      layoutConfig: Map<String, dynamic>.from(json['layout_config'] ?? {}),
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  @override
  List<Object?> get props => [
        id,
        restaurantId,
        name,
        description,
        floorNumber,
        isActive,
        layoutConfig,
        createdAt,
        updatedAt,
      ];
}

/// Table entity representing a restaurant table.
class Table extends Equatable {
  const Table({
    required this.id,
    required this.restaurantId,
    this.floorId,
    required this.tableNumber,
    required this.capacity,
    required this.status,
    required this.shape,
    required this.category,
    this.position,
    this.dimensions,
    required this.rotation,
    required this.specialRequirements,
    required this.isAccessible,
    required this.hasPowerOutlet,
    required this.hasWindowView,
    required this.minPartySize,
    this.maxPartySize,
    this.qrCodeData,
    this.lastCleanedAt,
    this.lastOccupiedAt,
    this.notes,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
  });

  final String id;
  final String restaurantId;
  final String? floorId;
  final String tableNumber;
  final int capacity;
  final TableStatus status;
  final TableShape shape;
  final TableCategory category;
  final Position? position;
  final Dimensions? dimensions;
  final double rotation;
  final List<String> specialRequirements;
  final bool isAccessible;
  final bool hasPowerOutlet;
  final bool hasWindowView;
  final int minPartySize;
  final int? maxPartySize;
  final QRCodeData? qrCodeData;
  final DateTime? lastCleanedAt;
  final DateTime? lastOccupiedAt;
  final String? notes;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;

  /// Check if table can accommodate a party of given size.
  bool canAccommodate(int partySize) {
    return isActive &&
        status == TableStatus.available &&
        minPartySize <= partySize &&
        partySize <= (maxPartySize ?? capacity);
  }

  /// Check if table is available for reservation.
  bool get isAvailableForReservation {
    return isActive &&
        (status == TableStatus.available || status == TableStatus.reserved);
  }

  /// Check if table needs cleaning.
  bool get needsCleaning {
    if (lastCleanedAt == null) return true;
    if (lastOccupiedAt != null && lastOccupiedAt!.isAfter(lastCleanedAt!)) {
      return true;
    }
    return false;
  }

  Table copyWith({
    String? id,
    String? restaurantId,
    String? floorId,
    String? tableNumber,
    int? capacity,
    TableStatus? status,
    TableShape? shape,
    TableCategory? category,
    Position? position,
    Dimensions? dimensions,
    double? rotation,
    List<String>? specialRequirements,
    bool? isAccessible,
    bool? hasPowerOutlet,
    bool? hasWindowView,
    int? minPartySize,
    int? maxPartySize,
    QRCodeData? qrCodeData,
    DateTime? lastCleanedAt,
    DateTime? lastOccupiedAt,
    String? notes,
    bool? isActive,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Table(
      id: id ?? this.id,
      restaurantId: restaurantId ?? this.restaurantId,
      floorId: floorId ?? this.floorId,
      tableNumber: tableNumber ?? this.tableNumber,
      capacity: capacity ?? this.capacity,
      status: status ?? this.status,
      shape: shape ?? this.shape,
      category: category ?? this.category,
      position: position ?? this.position,
      dimensions: dimensions ?? this.dimensions,
      rotation: rotation ?? this.rotation,
      specialRequirements: specialRequirements ?? this.specialRequirements,
      isAccessible: isAccessible ?? this.isAccessible,
      hasPowerOutlet: hasPowerOutlet ?? this.hasPowerOutlet,
      hasWindowView: hasWindowView ?? this.hasWindowView,
      minPartySize: minPartySize ?? this.minPartySize,
      maxPartySize: maxPartySize ?? this.maxPartySize,
      qrCodeData: qrCodeData ?? this.qrCodeData,
      lastCleanedAt: lastCleanedAt ?? this.lastCleanedAt,
      lastOccupiedAt: lastOccupiedAt ?? this.lastOccupiedAt,
      notes: notes ?? this.notes,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'restaurant_id': restaurantId,
      'floor_id': floorId,
      'table_number': tableNumber,
      'capacity': capacity,
      'status': status.value,
      'shape': shape.value,
      'category': category.value,
      'position': position?.toJson(),
      'dimensions': dimensions?.toJson(),
      'rotation': rotation,
      'special_requirements': specialRequirements,
      'is_accessible': isAccessible,
      'has_power_outlet': hasPowerOutlet,
      'has_window_view': hasWindowView,
      'min_party_size': minPartySize,
      'max_party_size': maxPartySize,
      'qr_code_data': qrCodeData?.toJson(),
      'last_cleaned_at': lastCleanedAt?.toIso8601String(),
      'last_occupied_at': lastOccupiedAt?.toIso8601String(),
      'notes': notes,
      'is_active': isActive,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  factory Table.fromJson(Map<String, dynamic> json) {
    return Table(
      id: json['id'] as String,
      restaurantId: json['restaurant_id'] as String,
      floorId: json['floor_id'] as String?,
      tableNumber: json['table_number'] as String,
      capacity: json['capacity'] as int,
      status: TableStatus.fromString(json['status'] as String),
      shape: TableShape.fromString(json['shape'] as String),
      category: TableCategory.fromString(json['category'] as String),
      position: json['position'] != null
          ? Position.fromJson(json['position'] as Map<String, dynamic>)
          : null,
      dimensions: json['dimensions'] != null
          ? Dimensions.fromJson(json['dimensions'] as Map<String, dynamic>)
          : null,
      rotation: (json['rotation'] as num?)?.toDouble() ?? 0.0,
      specialRequirements: List<String>.from(json['special_requirements'] ?? []),
      isAccessible: json['is_accessible'] as bool? ?? false,
      hasPowerOutlet: json['has_power_outlet'] as bool? ?? false,
      hasWindowView: json['has_window_view'] as bool? ?? false,
      minPartySize: json['min_party_size'] as int? ?? 1,
      maxPartySize: json['max_party_size'] as int?,
      qrCodeData: json['qr_code_data'] != null
          ? QRCodeData.fromJson(json['qr_code_data'] as Map<String, dynamic>)
          : null,
      lastCleanedAt: json['last_cleaned_at'] != null
          ? DateTime.parse(json['last_cleaned_at'] as String)
          : null,
      lastOccupiedAt: json['last_occupied_at'] != null
          ? DateTime.parse(json['last_occupied_at'] as String)
          : null,
      notes: json['notes'] as String?,
      isActive: json['is_active'] as bool? ?? true,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  @override
  List<Object?> get props => [
        id,
        restaurantId,
        floorId,
        tableNumber,
        capacity,
        status,
        shape,
        category,
        position,
        dimensions,
        rotation,
        specialRequirements,
        isAccessible,
        hasPowerOutlet,
        hasWindowView,
        minPartySize,
        maxPartySize,
        qrCodeData,
        lastCleanedAt,
        lastOccupiedAt,
        notes,
        isActive,
        createdAt,
        updatedAt,
      ];
}
