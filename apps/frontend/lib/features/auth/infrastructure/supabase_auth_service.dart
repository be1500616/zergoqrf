import 'dart:convert';
import 'dart:developer' as developer;

import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';

import '../domain/auth_entity.dart';

/// Service for communicating with the new Supabase-based backend authentication API.
/// 
/// This service integrates with the improved backend authentication system
/// that properly uses Supabase patterns and eliminates redundant session management.
class SupabaseAuthService {
  final String baseUrl;
  final http.Client httpClient;

  SupabaseAuthService({
    String? baseUrl,
    http.Client? httpClient,
  }) : baseUrl = baseUrl ?? dotenv.env['API_BASE_URL'] ?? 'http://localhost:8000',
       httpClient = httpClient ?? http.Client();

  /// Sign in with email and password using the new backend endpoint.
  Future<AuthResponse> signInWithEmail({
    required String email,
    required String password,
  }) async {
    try {
      final response = await httpClient.post(
        Uri.parse('$baseUrl/auth/signin/email'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return AuthResponse.fromJson(data);
      } else {
        final error = json.decode(response.body);
        throw AuthException(error['error']['message'] ?? 'Sign in failed');
      }
    } catch (e) {
      developer.log('Email sign in error: $e', name: 'SupabaseAuthService');
      if (e is AuthException) rethrow;
      throw AuthException('Network error during sign in');
    }
  }

  /// Sign up with email and password using the new backend endpoint.
  Future<AuthResponse> signUpWithEmail({
    required String email,
    required String password,
    String? name,
    String? role,
    String? restaurantId,
  }) async {
    try {
      final response = await httpClient.post(
        Uri.parse('$baseUrl/auth/signup/email'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'email': email,
          'password': password,
          'name': name,
          'role': role ?? 'customer',
          'restaurant_id': restaurantId,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return AuthResponse.fromJson(data);
      } else {
        final error = json.decode(response.body);
        throw AuthException(error['error']['message'] ?? 'Sign up failed');
      }
    } catch (e) {
      developer.log('Email sign up error: $e', name: 'SupabaseAuthService');
      if (e is AuthException) rethrow;
      throw AuthException('Network error during sign up');
    }
  }

  /// Initiate phone authentication using the new backend endpoint.
  Future<void> signInWithPhone({required String phone}) async {
    try {
      final response = await httpClient.post(
        Uri.parse('$baseUrl/auth/signin/phone'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'phone': phone,
        }),
      );

      if (response.statusCode != 200) {
        final error = json.decode(response.body);
        throw AuthException(error['error']['message'] ?? 'Failed to send OTP');
      }
    } catch (e) {
      developer.log('Phone sign in error: $e', name: 'SupabaseAuthService');
      if (e is AuthException) rethrow;
      throw AuthException('Network error during phone sign in');
    }
  }

  /// Verify phone OTP using the new backend endpoint.
  Future<AuthResponse> verifyPhoneOtp({
    required String phone,
    required String token,
    String? name,
  }) async {
    try {
      final response = await httpClient.post(
        Uri.parse('$baseUrl/auth/verify/phone'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'phone': phone,
          'token': token,
          'name': name,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return AuthResponse.fromJson(data);
      } else {
        final error = json.decode(response.body);
        throw AuthException(error['error']['message'] ?? 'OTP verification failed');
      }
    } catch (e) {
      developer.log('Phone OTP verification error: $e', name: 'SupabaseAuthService');
      if (e is AuthException) rethrow;
      throw AuthException('Network error during OTP verification');
    }
  }

  /// Create anonymous session using the new backend endpoint.
  Future<AnonymousSession> createAnonymousSession({
    required String restaurantId,
    String? tableId,
  }) async {
    try {
      final response = await httpClient.post(
        Uri.parse('$baseUrl/auth/anonymous-session'),
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
        final error = json.decode(response.body);
        throw AuthException(error['error']['message'] ?? 'Failed to create anonymous session');
      }
    } catch (e) {
      developer.log('Anonymous session creation error: $e', name: 'SupabaseAuthService');
      if (e is AuthException) rethrow;
      throw AuthException('Network error during anonymous session creation');
    }
  }

  /// Get current user profile using the new backend endpoint.
  Future<AuthUser> getCurrentUserProfile(String accessToken) async {
    try {
      final response = await httpClient.get(
        Uri.parse('$baseUrl/auth/me'),
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return AuthUser.fromJson(data);
      } else {
        final error = json.decode(response.body);
        throw AuthException(error['error']['message'] ?? 'Failed to get user profile');
      }
    } catch (e) {
      developer.log('Get user profile error: $e', name: 'SupabaseAuthService');
      if (e is AuthException) rethrow;
      throw AuthException('Network error during profile fetch');
    }
  }

  /// Refresh access token using the new backend endpoint.
  Future<AuthResponse> refreshToken(String refreshToken) async {
    try {
      final response = await httpClient.post(
        Uri.parse('$baseUrl/auth/refresh'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'refresh_token': refreshToken,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return AuthResponse.fromJson(data);
      } else {
        final error = json.decode(response.body);
        throw AuthException(error['error']['message'] ?? 'Token refresh failed');
      }
    } catch (e) {
      developer.log('Token refresh error: $e', name: 'SupabaseAuthService');
      if (e is AuthException) rethrow;
      throw AuthException('Network error during token refresh');
    }
  }

  /// Sign out using the new backend endpoint.
  Future<void> signOut(String? accessToken) async {
    try {
      final headers = <String, String>{
        'Content-Type': 'application/json',
      };
      
      if (accessToken != null) {
        headers['Authorization'] = 'Bearer $accessToken';
      }

      final response = await httpClient.post(
        Uri.parse('$baseUrl/auth/signout'),
        headers: headers,
      );

      // Sign out should always succeed, even if there's an error
      if (response.statusCode != 200) {
        developer.log('Sign out warning: ${response.body}', name: 'SupabaseAuthService');
      }
    } catch (e) {
      developer.log('Sign out error: $e', name: 'SupabaseAuthService');
      // Don't throw error for sign out - it should always succeed
    }
  }
}

/// Authentication response model.
class AuthResponse {
  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final int expiresIn;
  final AuthUser user;

  AuthResponse({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.expiresIn,
    required this.user,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
      tokenType: json['token_type'] as String,
      expiresIn: json['expires_in'] as int,
      user: AuthUser.fromJson(json['user'] as Map<String, dynamic>),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'refresh_token': refreshToken,
      'token_type': tokenType,
      'expires_in': expiresIn,
      'user': user.toJson(),
    };
  }
}

/// Authentication exception.
class AuthException implements Exception {
  final String message;

  AuthException(this.message);

  @override
  String toString() => 'AuthException: $message';
}
