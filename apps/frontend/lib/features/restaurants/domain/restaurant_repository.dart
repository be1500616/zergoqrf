/// Restaurant repository interface.
///
/// This module defines the abstract repository interface for restaurant data access.

import 'restaurant_entity.dart';

abstract class RestaurantRepository {
  /// Register a new restaurant with owner account.
  Future<RestaurantRegistrationResponse> registerRestaurant(
    RestaurantRegistrationRequest request,
  );

  /// Get current user's restaurant information.
  Future<Restaurant> getMyRestaurant();

  /// Update current user's restaurant information.
  Future<Restaurant> updateMyRestaurant(Map<String, dynamic> updateData);

  /// Update restaurant business hours.
  Future<Restaurant> updateBusinessHours(Map<String, dynamic> businessHours);

  /// Update restaurant settings.
  Future<Restaurant> updateRestaurantSettings(Map<String, dynamic> settings);

  /// Get restaurant by code (public endpoint for QR codes).
  Future<Restaurant> getRestaurantByCode(String code);

  /// Create a new staff member.
  Future<RestaurantStaff> createStaffMember(Map<String, dynamic> staffData);

  /// Get all staff members for the restaurant.
  Future<List<RestaurantStaff>> getRestaurantStaff();

  /// Update a staff member.
  Future<RestaurantStaff> updateStaffMember(
    String staffId,
    Map<String, dynamic> updateData,
  );

  /// Delete a staff member.
  Future<void> deleteStaffMember(String staffId);
}
