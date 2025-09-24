/// Restaurant controller for state management.
///
/// This module contains the GetX controller for restaurant state management.
library;

import 'package:get/get.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../domain/restaurant_entity.dart';
import '../domain/restaurant_repository.dart';
import '../infrastructure/restaurant_repository_impl.dart';

class RestaurantController extends GetxController {
  final RestaurantRepository _repository;

  // Observable state
  final Rx<Restaurant?> currentRestaurant = Rx<Restaurant?>(null);
  final RxList<RestaurantStaff> staff = <RestaurantStaff>[].obs;
  final RxBool isLoading = false.obs;
  final RxBool isRegistering = false.obs;
  final RxString error = ''.obs;

  // Registration form state
  final RxInt currentStep = 0.obs;
  final RxMap<String, dynamic> registrationData = <String, dynamic>{}.obs;

  RestaurantController({RestaurantRepository? repository})
      : _repository = repository ?? RestaurantRepositoryImpl();

  @override
  void onInit() {
    super.onInit();
    // Load restaurant data if user is authenticated
    if (Supabase.instance.client.auth.currentSession != null) {
      loadRestaurantData();
    }
  }

  /// Register a new restaurant
  Future<void> registerRestaurant(RestaurantRegistrationRequest request) async {
    try {
      isRegistering.value = true;
      error.value = '';

      final response = await _repository.registerRestaurant(request);

      // Update current restaurant
      currentRestaurant.value = response.restaurant;

      // Store session in Supabase auth (use refresh token as per Supabase v2 API)
      await Supabase.instance.client.auth.setSession(
        response.refreshToken,
      );

      Get.snackbar(
        'Success',
        'Restaurant registered successfully!',
        snackPosition: SnackPosition.BOTTOM,
      );

      // Navigate to dashboard
      Get.offAllNamed('/dashboard');
    } catch (e) {
      error.value = e.toString();
      Get.snackbar(
        'Error',
        'Registration failed: ${e.toString()}',
        snackPosition: SnackPosition.BOTTOM,
      );
    } finally {
      isRegistering.value = false;
    }
  }

  /// Load current restaurant data
  Future<void> loadRestaurantData() async {
    try {
      isLoading.value = true;
      error.value = '';

      final restaurant = await _repository.getMyRestaurant();
      currentRestaurant.value = restaurant;

      // Load staff data
      await loadStaffData();
    } catch (e) {
      error.value = e.toString();
      print('Failed to load restaurant data: $e');
    } finally {
      isLoading.value = false;
    }
  }

  /// Update restaurant information
  Future<void> updateRestaurant(Map<String, dynamic> updateData) async {
    try {
      isLoading.value = true;
      error.value = '';

      final restaurant = await _repository.updateMyRestaurant(updateData);
      currentRestaurant.value = restaurant;

      Get.snackbar(
        'Success',
        'Restaurant updated successfully!',
        snackPosition: SnackPosition.BOTTOM,
      );
    } catch (e) {
      error.value = e.toString();
      Get.snackbar(
        'Error',
        'Update failed: ${e.toString()}',
        snackPosition: SnackPosition.BOTTOM,
      );
    } finally {
      isLoading.value = false;
    }
  }

  /// Update business hours
  Future<void> updateBusinessHours(Map<String, dynamic> businessHours) async {
    try {
      isLoading.value = true;
      error.value = '';

      final restaurant = await _repository.updateBusinessHours(businessHours);
      currentRestaurant.value = restaurant;

      Get.snackbar(
        'Success',
        'Business hours updated successfully!',
        snackPosition: SnackPosition.BOTTOM,
      );
    } catch (e) {
      error.value = e.toString();
      Get.snackbar(
        'Error',
        'Update failed: ${e.toString()}',
        snackPosition: SnackPosition.BOTTOM,
      );
    } finally {
      isLoading.value = false;
    }
  }

  /// Update restaurant settings
  Future<void> updateSettings(Map<String, dynamic> settings) async {
    try {
      isLoading.value = true;
      error.value = '';

      final restaurant = await _repository.updateRestaurantSettings(settings);
      currentRestaurant.value = restaurant;

      Get.snackbar(
        'Success',
        'Settings updated successfully!',
        snackPosition: SnackPosition.BOTTOM,
      );
    } catch (e) {
      error.value = e.toString();
      Get.snackbar(
        'Error',
        'Update failed: ${e.toString()}',
        snackPosition: SnackPosition.BOTTOM,
      );
    } finally {
      isLoading.value = false;
    }
  }

  /// Load staff data
  Future<void> loadStaffData() async {
    try {
      final staffList = await _repository.getRestaurantStaff();
      staff.assignAll(staffList);
    } catch (e) {
      print('Failed to load staff data: $e');
    }
  }

  /// Create a new staff member
  Future<void> createStaffMember(Map<String, dynamic> staffData) async {
    try {
      isLoading.value = true;
      error.value = '';

      final newStaff = await _repository.createStaffMember(staffData);
      staff.add(newStaff);

      Get.snackbar(
        'Success',
        'Staff member added successfully!',
        snackPosition: SnackPosition.BOTTOM,
      );
    } catch (e) {
      error.value = e.toString();
      Get.snackbar(
        'Error',
        'Failed to add staff: ${e.toString()}',
        snackPosition: SnackPosition.BOTTOM,
      );
    } finally {
      isLoading.value = false;
    }
  }

  /// Update a staff member
  Future<void> updateStaffMember(
      String staffId, Map<String, dynamic> updateData) async {
    try {
      isLoading.value = true;
      error.value = '';

      final updatedStaff =
          await _repository.updateStaffMember(staffId, updateData);

      final index = staff.indexWhere((s) => s.id == staffId);
      if (index != -1) {
        staff[index] = updatedStaff;
      }

      Get.snackbar(
        'Success',
        'Staff member updated successfully!',
        snackPosition: SnackPosition.BOTTOM,
      );
    } catch (e) {
      error.value = e.toString();
      Get.snackbar(
        'Error',
        'Update failed: ${e.toString()}',
        snackPosition: SnackPosition.BOTTOM,
      );
    } finally {
      isLoading.value = false;
    }
  }

  /// Delete a staff member
  Future<void> deleteStaffMember(String staffId) async {
    try {
      isLoading.value = true;
      error.value = '';

      await _repository.deleteStaffMember(staffId);
      staff.removeWhere((s) => s.id == staffId);

      Get.snackbar(
        'Success',
        'Staff member removed successfully!',
        snackPosition: SnackPosition.BOTTOM,
      );
    } catch (e) {
      error.value = e.toString();
      Get.snackbar(
        'Error',
        'Delete failed: ${e.toString()}',
        snackPosition: SnackPosition.BOTTOM,
      );
    } finally {
      isLoading.value = false;
    }
  }

  /// Registration form helpers
  void nextStep() {
    if (currentStep.value < 3) {
      currentStep.value++;
    }
  }

  void previousStep() {
    if (currentStep.value > 0) {
      currentStep.value--;
    }
  }

  void updateRegistrationData(String key, dynamic value) {
    registrationData[key] = value;
  }

  void resetRegistration() {
    currentStep.value = 0;
    registrationData.clear();
    isRegistering.value = false;
    error.value = '';
  }
}
