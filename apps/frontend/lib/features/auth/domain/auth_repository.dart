import 'auth_entity.dart';

abstract class AuthRepository {
  Future<AuthUser> getUserProfile(String accessToken);
  Future<void> createCustomer(String userId, String phone, String name);
  Future<AnonymousSession> createAnonymousSession(String restaurantId, String tableId);
  Future<bool> validateAnonymousSession(String sessionToken);
}