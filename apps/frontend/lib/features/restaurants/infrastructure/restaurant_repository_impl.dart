/// Restaurant repository implementation.
///
/// This module contains the concrete implementation of restaurant repository using HTTP API.

import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;
import 'package:supabase_flutter/supabase_flutter.dart';

import '../domain/restaurant_entity.dart';
import '../domain/restaurant_repository.dart';

class RestaurantRepositoryImpl implements RestaurantRepository {
  final String baseUrl;
  final http.Client httpClient;

  RestaurantRepositoryImpl({
    String? baseUrl,
    http.Client? httpClient,
  })  : baseUrl = baseUrl ?? dotenv.env['API_BASE_URL'] ?? 'http://localhost:8000',
        httpClient = httpClient ?? http.Client();

  @override
  Future<RestaurantRegistrationResponse> registerRestaurant(
    RestaurantRegistrationRequest request,
  ) async {
    final response = await httpClient.post(
      Uri.parse('$baseUrl/restaurants/register'),
      headers: {
        'Content-Type': 'application/json',
      },
      body: json.encode(request.toJson()),
    );

    if (response.statusCode == 201) {
      final data = json.decode(response.body);
      return RestaurantRegistrationResponse.fromJson(data);
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to register restaurant');
    }
  }

  @override
  Future<Restaurant> getMyRestaurant() async {
    final response = await httpClient.get(
      Uri.parse('$baseUrl/restaurants/me'),
      headers: {
        'Authorization': 'Bearer ${await _getAccessToken()}',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return Restaurant.fromJson(data);
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to get restaurant');
    }
  }

  @override
  Future<Restaurant> updateMyRestaurant(Map<String, dynamic> updateData) async {
    final response = await httpClient.put(
      Uri.parse('$baseUrl/restaurants/me'),
      headers: {
        'Authorization': 'Bearer ${await _getAccessToken()}',
        'Content-Type': 'application/json',
      },
      body: json.encode(updateData),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return Restaurant.fromJson(data);
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to update restaurant');
    }
  }

  @override
  Future<Restaurant> updateBusinessHours(Map<String, dynamic> businessHours) async {
    final response = await httpClient.put(
      Uri.parse('$baseUrl/restaurants/me/business-hours'),
      headers: {
        'Authorization': 'Bearer ${await _getAccessToken()}',
        'Content-Type': 'application/json',
      },
      body: json.encode(businessHours),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return Restaurant.fromJson(data);
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to update business hours');
    }
  }

  @override
  Future<Restaurant> updateRestaurantSettings(Map<String, dynamic> settings) async {
    final response = await httpClient.put(
      Uri.parse('$baseUrl/restaurants/me/settings'),
      headers: {
        'Authorization': 'Bearer ${await _getAccessToken()}',
        'Content-Type': 'application/json',
      },
      body: json.encode(settings),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return Restaurant.fromJson(data);
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to update settings');
    }
  }

  @override
  Future<Restaurant> getRestaurantByCode(String code) async {
    final response = await httpClient.get(
      Uri.parse('$baseUrl/restaurants/$code'),
      headers: {
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return Restaurant.fromJson(data);
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to get restaurant');
    }
  }

  @override
  Future<RestaurantStaff> createStaffMember(Map<String, dynamic> staffData) async {
    final response = await httpClient.post(
      Uri.parse('$baseUrl/restaurants/me/staff'),
      headers: {
        'Authorization': 'Bearer ${await _getAccessToken()}',
        'Content-Type': 'application/json',
      },
      body: json.encode(staffData),
    );

    if (response.statusCode == 201) {
      final data = json.decode(response.body);
      return RestaurantStaff.fromJson(data);
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to create staff member');
    }
  }

  @override
  Future<List<RestaurantStaff>> getRestaurantStaff() async {
    final response = await httpClient.get(
      Uri.parse('$baseUrl/restaurants/me/staff'),
      headers: {
        'Authorization': 'Bearer ${await _getAccessToken()}',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final staffList = data['staff'] as List;
      return staffList.map((staff) => RestaurantStaff.fromJson(staff)).toList();
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to get staff');
    }
  }

  @override
  Future<RestaurantStaff> updateStaffMember(
    String staffId,
    Map<String, dynamic> updateData,
  ) async {
    final response = await httpClient.put(
      Uri.parse('$baseUrl/restaurants/me/staff/$staffId'),
      headers: {
        'Authorization': 'Bearer ${await _getAccessToken()}',
        'Content-Type': 'application/json',
      },
      body: json.encode(updateData),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return RestaurantStaff.fromJson(data);
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to update staff member');
    }
  }

  @override
  Future<void> deleteStaffMember(String staffId) async {
    final response = await httpClient.delete(
      Uri.parse('$baseUrl/restaurants/me/staff/$staffId'),
      headers: {
        'Authorization': 'Bearer ${await _getAccessToken()}',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode != 204) {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to delete staff member');
    }
  }

  Future<String> _getAccessToken() async {
    // Get access token from Supabase auth
    try {
      final session = Supabase.instance.client.auth.currentSession;
      return session?.accessToken ?? '';
    } catch (e) {
      print('Error getting access token: $e');
      return '';
    }
  }
}
