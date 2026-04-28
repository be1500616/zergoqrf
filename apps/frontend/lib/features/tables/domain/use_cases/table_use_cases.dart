/// Table management use cases.
library;

import '../entities/table_entities.dart';
import '../repositories/table_repositories.dart';

class GetTablesUseCase {
  final TableRepository repo;
  GetTablesUseCase(this.repo);
  Future<List<Table>> call({String? floorId, TableStatus? status, int? partySize}) {
    return repo.getTables(floorId: floorId, status: status, partySize: partySize);
  }
}

class GetTableUseCase {
  final TableRepository repo;
  GetTableUseCase(this.repo);
  Future<Table> call(String id) => repo.getTable(id);
}

class CreateTableUseCase {
  final TableRepository repo;
  CreateTableUseCase(this.repo);
  Future<Table> call({
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
  }) {
    return repo.createTable(
      floorId: floorId,
      tableNumber: tableNumber,
      capacity: capacity,
      shape: shape,
      category: category,
      position: position,
      dimensions: dimensions,
      rotation: rotation,
      specialRequirements: specialRequirements,
      isAccessible: isAccessible,
      hasPowerOutlet: hasPowerOutlet,
      hasWindowView: hasWindowView,
      minPartySize: minPartySize,
      maxPartySize: maxPartySize,
      notes: notes,
    );
  }
}

class UpdateTableUseCase {
  final TableRepository repo;
  UpdateTableUseCase(this.repo);
  Future<Table> call({
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
  }) {
    return repo.updateTable(
      tableId: tableId,
      floorId: floorId,
      tableNumber: tableNumber,
      capacity: capacity,
      shape: shape,
      category: category,
      position: position,
      dimensions: dimensions,
      rotation: rotation,
      specialRequirements: specialRequirements,
      isAccessible: isAccessible,
      hasPowerOutlet: hasPowerOutlet,
      hasWindowView: hasWindowView,
      minPartySize: minPartySize,
      maxPartySize: maxPartySize,
      notes: notes,
      isActive: isActive,
    );
  }
}

class DeleteTableUseCase {
  final TableRepository repo;
  DeleteTableUseCase(this.repo);
  Future<void> call(String id) => repo.deleteTable(id);
}

class UpdateTableStatusUseCase {
  final TableRepository repo;
  UpdateTableStatusUseCase(this.repo);
  Future<void> call({required String tableId, required TableStatus status}) {
    return repo.updateTableStatus(tableId: tableId, status: status);
  }
}

