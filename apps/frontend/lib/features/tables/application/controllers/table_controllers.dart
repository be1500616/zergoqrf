/// Table management controller using GetX.
import 'package:get/get.dart';
import '../../domain/entities/table_entities.dart' as domain;
import '../../domain/repositories/table_repositories.dart';

class TableManagementController extends GetxController {
  TableManagementController({required this.repository});

  final TableRepository repository;

  final RxList<domain.Table> _tables = <domain.Table>[].obs;
  final RxBool _loading = false.obs;
  final RxnString _error = RxnString();

  // Filters
  final RxnString _floorId = RxnString();
  final Rxn<domain.TableStatus> _status = Rxn<domain.TableStatus>();
  final RxnInt _partySize = RxnInt();
  final RxString _query = ''.obs;

  List<domain.Table> get tables {
    final q = _query.value.trim().toLowerCase();
    if (q.isEmpty) return _tables;
    return _tables.where((t) =>
      t.tableNumber.toLowerCase().contains(q) ||
      (t.notes ?? '').toLowerCase().contains(q) ||
      t.category.name.toLowerCase().contains(q)
    ).toList();
  }

  bool get isLoading => _loading.value;
  String? get error => _error.value;
  String? get floorId => _floorId.value;
  domain.TableStatus? get status => _status.value;
  int? get partySize => _partySize.value;

  @override
  void onInit() {
    super.onInit();
    loadTables();
  }

  void setQuery(String value) => _query.value = value;
  void setFloor(String? id) => _floorId.value = id;
  void setStatus(domain.TableStatus? s) => _status.value = s;
  void setPartySize(int? n) => _partySize.value = n;

  Future<void> loadTables() async {
    try {
      _loading.value = true;
      _error.value = null;
      final list = await repository.getTables(
        floorId: _floorId.value,
        status: _status.value,
        partySize: _partySize.value,
      );
      _tables.assignAll(list);
    } catch (e) {
      _error.value = e.toString();
    } finally {
      _loading.value = false;
    }
  }

  Future<void> refreshList() => loadTables();

  Future<domain.Table?> createTable({
    String? floorId,
    required String tableNumber,
    required int capacity,
    domain.TableShape shape = domain.TableShape.round,
    domain.TableCategory category = domain.TableCategory.regular,
    domain.Position? position,
    domain.Dimensions? dimensions,
    double rotation = 0,
    List<String> specialRequirements = const [],
    bool isAccessible = false,
    bool hasPowerOutlet = false,
    bool hasWindowView = false,
    int minPartySize = 1,
    int? maxPartySize,
    String? notes,
  }) async {
    try {
      _loading.value = true;
      final created = await repository.createTable(
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
      _tables.add(created);
      return created;
    } catch (e) {
      _error.value = e.toString();
      return null;
    } finally {
      _loading.value = false;
    }
  }

  Future<domain.Table?> updateTable(String id, Map<String, dynamic> updates) async {
    try {
      _loading.value = true;
      final updated = await repository.updateTable(
        tableId: id,
        floorId: updates['floor_id'] as String?,
        tableNumber: updates['table_number'] as String?,
        capacity: updates['capacity'] as int?,
        shape: updates['shape'] as domain.TableShape?,
        category: updates['category'] as domain.TableCategory?,
        position: updates['position'] as domain.Position?,
        dimensions: updates['dimensions'] as domain.Dimensions?,
        rotation: updates['rotation'] as double?,
        specialRequirements: (updates['special_requirements'] as List<String>?),
        isAccessible: updates['is_accessible'] as bool?,
        hasPowerOutlet: updates['has_power_outlet'] as bool?,
        hasWindowView: updates['has_window_view'] as bool?,
        minPartySize: updates['min_party_size'] as int?,
        maxPartySize: updates['max_party_size'] as int?,
        notes: updates['notes'] as String?,
        isActive: updates['is_active'] as bool?,
      );
      final idx = _tables.indexWhere((t) => t.id == id);
      if (idx != -1) _tables[idx] = updated;
      return updated;
    } catch (e) {
      _error.value = e.toString();
      return null;
    } finally {
      _loading.value = false;
    }
  }

  Future<bool> deleteTable(String id) async {
    try {
      _loading.value = true;
      await repository.deleteTable(id);
      _tables.removeWhere((t) => t.id == id);
      return true;
    } catch (e) {
      _error.value = e.toString();
      return false;
    } finally {
      _loading.value = false;
    }
  }

  Future<bool> updateStatus(String id, domain.TableStatus status) async {
    try {
      _loading.value = true;
      await repository.updateTableStatus(tableId: id, status: status);
      final idx = _tables.indexWhere((t) => t.id == id);
      if (idx != -1) _tables[idx] = _tables[idx].copyWith(status: status);
      return true;
    } catch (e) {
      _error.value = e.toString();
      return false;
    } finally {
      _loading.value = false;
    }
  }
}

