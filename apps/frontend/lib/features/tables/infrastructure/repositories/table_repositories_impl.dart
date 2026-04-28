/// Concrete implementation of [TableRepository].
///
/// Communicates with backend FastAPI endpoints under `/api/v1/tables`.
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:get/get.dart';
import '../../../../core/config/api_config.dart';
import '../../../../core/services/auth_service.dart';
import '../../domain/entities/table_entities.dart';
import '../../domain/repositories/table_repositories.dart';

class TableRepositoryImpl implements TableRepository {
  TableRepositoryImpl({
    required this.apiConfig,
    required this.authService,
  });

  final ApiConfig apiConfig;
  final AuthService authService;

  String get _base => '${apiConfig.baseUrl}/api/v1/tables';

  Future<Map<String, String>> _headers() async => {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${await authService.getAccessToken()}',
      };

  T _decodeObject<T>(http.Response res, T Function(Map<String, dynamic>) fromJson) {
    if (res.statusCode >= 200 && res.statusCode < 300) {
      final map = json.decode(res.body) as Map<String, dynamic>;
      return fromJson(map);
    }
    throw Exception('API ${res.statusCode}: ${res.body}');
  }

  List<T> _decodeList<T>(http.Response res, T Function(Map<String, dynamic>) fromJson) {
    if (res.statusCode >= 200 && res.statusCode < 300) {
      final list = json.decode(res.body) as List<dynamic>;
      return list.map((e) => fromJson(e as Map<String, dynamic>)).toList();
    }
    throw Exception('API ${res.statusCode}: ${res.body}');
  }

  @override
  Future<List<Table>> getTables({String? floorId, TableStatus? status, int? partySize}) async {
    final headers = await _headers();
    final uri = Uri.parse(_base).replace(queryParameters: {
      if (floorId != null) 'floor_id': floorId,
      if (status != null) 'status': status.value,
      if (partySize != null) 'party_size': partySize.toString(),
    });
    final res = await http.get(uri, headers: headers);
    return _decodeList(res, (m) => Table.fromJson(m));
  }

  @override
  Future<Table> getTable(String tableId) async {
    final headers = await _headers();
    final res = await http.get(Uri.parse('$_base/$tableId'), headers: headers);
    return _decodeObject(res, (m) => Table.fromJson(m));
  }

  @override
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
  }) async {
    final headers = await _headers();
    final body = json.encode({
      'floor_id': floorId,
      'table_number': tableNumber,
      'capacity': capacity,
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
      'notes': notes,
    });
    final res = await http.post(Uri.parse(_base), headers: headers, body: body);
    return _decodeObject(res, (m) => Table.fromJson(m));
  }

  @override
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
  }) async {
    final headers = await _headers();
    final body = json.encode({
      if (floorId != null) 'floor_id': floorId,
      if (tableNumber != null) 'table_number': tableNumber,
      if (capacity != null) 'capacity': capacity,
      if (shape != null) 'shape': shape.value,
      if (category != null) 'category': category.value,
      if (position != null) 'position': position.toJson(),
      if (dimensions != null) 'dimensions': dimensions.toJson(),
      if (rotation != null) 'rotation': rotation,
      if (specialRequirements != null) 'special_requirements': specialRequirements,
      if (isAccessible != null) 'is_accessible': isAccessible,
      if (hasPowerOutlet != null) 'has_power_outlet': hasPowerOutlet,
      if (hasWindowView != null) 'has_window_view': hasWindowView,
      if (minPartySize != null) 'min_party_size': minPartySize,
      if (maxPartySize != null) 'max_party_size': maxPartySize,
      if (notes != null) 'notes': notes,
      if (isActive != null) 'is_active': isActive,
    });
    final res = await http.put(Uri.parse('$_base/$tableId'), headers: headers, body: body);
    return _decodeObject(res, (m) => Table.fromJson(m));
  }

  @override
  Future<void> deleteTable(String tableId) async {
    final headers = await _headers();
    final res = await http.delete(Uri.parse('$_base/$tableId'), headers: headers);
    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw Exception('Failed to delete: ${res.statusCode}');
    }
  }

  @override
  Future<void> updateTableStatus({required String tableId, required TableStatus status}) async {
    final headers = await _headers();
    final body = json.encode({'status': status.value});
    final res = await http.patch(Uri.parse('$_base/$tableId/status'), headers: headers, body: body);
    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw Exception('Failed to update status: ${res.statusCode}');
    }
  }
}

