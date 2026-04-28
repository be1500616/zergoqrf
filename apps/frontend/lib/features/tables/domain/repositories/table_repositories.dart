/// Table repository interface.
///
/// Defines operations for table management feature.
library;

import '../entities/table_entities.dart';

/// Contract for table data access.
abstract class TableRepository {
  /// Get list of tables with optional filters.
  Future<List<Table>> getTables({
    String? floorId,
    TableStatus? status,
    int? partySize,
  });

  /// Get a single table by ID.
  Future<Table> getTable(String tableId);

  /// Create a new table.
  Future<Table> createTable({
    String? floorId,
    required String tableNumber,
    required int capacity,
    TableShape shape = TableShape.round,
    TableCategory category = TableCategory.regular,
    Position? position,
    Dimensions? dimensions,
    double rotation = 0,
    List<String> specialRequirements = const [],
    bool isAccessible = false,
    bool hasPowerOutlet = false,
    bool hasWindowView = false,
    int minPartySize = 1,
    int? maxPartySize,
    String? notes,
  });

  /// Update an existing table.
  Future<Table> updateTable({
    required String tableId,
    String? floorId,
    String? tableNumber,
    int? capacity,
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
    String? notes,
    bool? isActive,
  });

  /// Delete a table by ID.
  Future<void> deleteTable(String tableId);

  /// Update table status (available, occupied, reserved, etc.).
  Future<void> updateTableStatus({
    required String tableId,
    required TableStatus status,
  });
}

