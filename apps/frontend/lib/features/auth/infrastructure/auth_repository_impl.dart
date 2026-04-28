import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';

import '../domain/auth_repository.dart';
import '../domain/auth_entity.dart';

class AuthRepositoryImpl implements AuthRepository {
  final String baseUrl;
  final http.Client httpClient;

  AuthRepositoryImpl({
    String? baseUrl,
    http.Client? httpClient,
  }) : baseUrl = baseUrl ?? dotenv.env['API_BASE_URL'] ?? 'http://localhost:8000',
       httpClient = httpClient ?? http.Client();

  @override
  Future<AuthUser> getUserProfile(String accessToken) async {
    final response = await httpClient.get(
      Uri.parse('$baseUrl/auth/profile'),
      headers: {
        'Authorization': 'Bearer $accessToken',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return AuthUser.fromJson(data);
    } else {
      throw Exception('Failed to get user profile: ${response.body}');
    }
  }

  @override
  Future<void> createCustomer(String userId, String phone, String name) async {
    final response = await httpClient.post(
      Uri.parse('$baseUrl/customers'),
      headers: {
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'id': userId,
        'phone': phone,
        'name': name,
      }),
    );

    if (response.statusCode != 200 && response.statusCode != 201) {
      throw Exception('Failed to create customer: ${response.body}');
    }
  }

  @override
  Future<AnonymousSession> createAnonymousSession(String restaurantId, String tableId) async {
    final response = await httpClient.post(
      Uri.parse('$baseUrl/auth/anonymous'),
      headers: {
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'restaurant_id': restaurantId,
        'table_id': tableId,
      }),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return AnonymousSession.fromJson(data);
    } else {
      throw Exception('Failed to create anonymous session: ${response.body}');
    }
  }

  @override
  Future<bool> validateAnonymousSession(String sessionToken) async {
    final response = await httpClient.post(
      Uri.parse('$baseUrl/auth/validate-anonymous'),
      headers: {
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'session_token': sessionToken,
      }),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['valid'] == true;
    } else {
      return false;
    }
  }
}