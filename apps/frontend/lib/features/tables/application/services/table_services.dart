/// Low-level Table HTTP service (kept simple; repository uses similar logic).
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:zergo_frontend/core/config/api_config.dart';
import 'package:zergo_frontend/core/services/auth_service.dart';

class TableService {
  TableService({required this.apiConfig, required this.authService});
  final ApiConfig apiConfig;
  final AuthService authService;

  String get _base => '${apiConfig.baseUrl}/api/v1/tables';

  Future<Map<String, String>> _headers() async => {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${await authService.getAccessToken()}',
      };

  Future<http.Response> list({Map<String, String>? query}) async {
    final headers = await _headers();
    final uri = Uri.parse(_base).replace(queryParameters: query);
    return http.get(uri, headers: headers);
  }

  Future<http.Response> create(Map<String, dynamic> body) async {
    final headers = await _headers();
    return http.post(Uri.parse(_base), headers: headers, body: jsonEncode(body));
  }

  Future<http.Response> update(String id, Map<String, dynamic> body) async {
    final headers = await _headers();
    return http.put(Uri.parse('$_base/$id'), headers: headers, body: jsonEncode(body));
  }

  Future<http.Response> changeStatus(String id, String status) async {
    final headers = await _headers();
    return http.patch(Uri.parse('$_base/$id/status'), headers: headers, body: jsonEncode({'status': status}));
  }

  Future<http.Response> remove(String id) async {
    final headers = await _headers();
    return http.delete(Uri.parse('$_base/$id'), headers: headers);
  }
}

