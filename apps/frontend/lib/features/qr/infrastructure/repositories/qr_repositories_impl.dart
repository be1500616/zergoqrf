import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:zergo_frontend/core/config/api_config.dart';
import 'package:zergo_frontend/core/services/auth_service.dart';
import '../../domain/entities/qr_entities.dart';
import '../../domain/repositories/qr_repositories.dart';

class QRRepositoryImpl implements QRRepository {
  QRRepositoryImpl({required this.apiConfig, required this.authService});
  final ApiConfig apiConfig;
  final AuthService authService;

  String get _base => '${apiConfig.baseUrl}/api/v1/qr';

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

  @override
  Future<QRResponse> generate({required String tableId, Map<String, dynamic>? config}) async {
    final res = await http.post(
      Uri.parse('$_base/generate'),
      headers: await _headers(),
      body: jsonEncode({'table_id': tableId, ...(config ?? {})}),
    );
    return _decodeObject(res, (m) => QRResponse.fromJson(m));
  }

  @override
  Future<BulkQRResponse> generateBulk({required List<String> tableIds, Map<String, dynamic>? config}) async {
    final res = await http.post(
      Uri.parse('$_base/generate/bulk'),
      headers: await _headers(),
      body: jsonEncode({'table_ids': tableIds, ...(config ?? {})}),
    );
    return _decodeObject(res, (m) => BulkQRResponse.fromJson(m));
  }

  @override
  Future<QRPreviewData> preview({required Map<String, dynamic> payload}) async {
    final res = await http.post(
      Uri.parse('$_base/preview'),
      headers: await _headers(),
      body: jsonEncode(payload),
    );
    return _decodeObject(res, (m) => QRPreviewData.fromJson(m));
  }

  @override
  Future<QRManagementGrid> managementGrid() async {
    final res = await http.get(Uri.parse('$_base/management'), headers: await _headers());
    return _decodeObject(res, (m) => QRManagementGrid.fromJson(m));
  }
}

