/// Staff dialog controller for managing staff creation and editing.
///
/// This controller replaces the StatefulWidget pattern in AddStaffDialog
/// with GetX reactive state management.

import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../restaurant_controller.dart';
import '../../domain/restaurant_entity.dart';

class StaffDialogController extends GetxController {
  // Form controllers
  final nameController = TextEditingController();
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  final formKey = GlobalKey<FormState>();
  
  // Observable state
  final _selectedRole = 'service'.obs;
  final _permissions = <String, bool>{
    'manage_restaurant': false,
    'manage_menu': false,
    'manage_orders': false,
    'manage_tables': false,
    'manage_staff': false,
    'view_analytics': false,
    'manage_payments': false,
  }.obs;
  final _isEditing = false.obs;
  final _obscurePassword = true.obs;
  final _isLoading = false.obs;
  
  // Current staff being edited (if any)
  RestaurantStaff? _currentStaff;
  
  // Getters
  String get selectedRole => _selectedRole.value;
  Map<String, bool> get permissions => _permissions;
  bool get isEditing => _isEditing.value;
  bool get obscurePassword => _obscurePassword.value;
  bool get isLoading => _isLoading.value;
  
  @override
  void onClose() {
    nameController.dispose();
    emailController.dispose();
    passwordController.dispose();
    super.onClose();
  }
  
  /// Initialize for editing existing staff
  void initializeForEdit(RestaurantStaff staff) {
    _currentStaff = staff;
    _isEditing.value = true;
    
    nameController.text = staff.name ?? '';
    emailController.text = staff.email ?? '';
    _selectedRole.value = staff.role;
    
    // Load permissions
    staff.permissions.forEach((key, value) {
      if (_permissions.containsKey(key)) {
        _permissions[key] = value == true;
      }
    });
  }
  
  /// Initialize for creating new staff
  void initializeForCreate() {
    _isEditing.value = false;
    _currentStaff = null;
    
    nameController.clear();
    emailController.clear();
    passwordController.clear();
    _selectedRole.value = 'service';
    _setDefaultPermissions();
  }
  
  /// Update selected role and set default permissions
  void updateRole(String role) {
    _selectedRole.value = role;
    _setDefaultPermissions();
  }
  
  /// Toggle password visibility
  void togglePasswordVisibility() {
    _obscurePassword.value = !_obscurePassword.value;
  }
  
  /// Update permission value
  void updatePermission(String permission, bool value) {
    _permissions[permission] = value;
  }
  
  /// Set default permissions based on role
  void _setDefaultPermissions() {
    // Reset all permissions
    _permissions.updateAll((key, value) => false);
    
    switch (_selectedRole.value) {
      case 'manager':
        _permissions['manage_menu'] = true;
        _permissions['manage_orders'] = true;
        _permissions['manage_tables'] = true;
        _permissions['view_analytics'] = true;
        break;
      case 'kitchen':
        _permissions['manage_orders'] = true;
        break;
      case 'service':
        _permissions['manage_orders'] = true;
        _permissions['manage_tables'] = true;
        break;
    }
  }
  
  /// Save staff member (create or update)
  Future<void> saveStaff() async {
    if (!formKey.currentState!.validate()) {
      return;
    }
    
    _isLoading.value = true;
    
    try {
      final controller = Get.find<RestaurantController>();
      
      final staffData = {
        'name': nameController.text.trim(),
        'role': _selectedRole.value,
        'permissions': Map<String, bool>.from(_permissions),
      };
      
      if (_isEditing.value && _currentStaff != null) {
        // Update existing staff
        await controller.updateStaffMember(_currentStaff!.id, staffData);
      } else {
        // Add new staff
        staffData['email'] = emailController.text.trim();
        staffData['password'] = passwordController.text;
        await controller.createStaffMember(staffData);
      }
      
      Get.back(); // Close dialog
    } catch (e) {
      Get.snackbar(
        'Error',
        'Failed to save staff member: ${e.toString()}',
        snackPosition: SnackPosition.BOTTOM,
      );
    } finally {
      _isLoading.value = false;
    }
  }
  
  /// Get display name for permission
  String getPermissionDisplayName(String permission) {
    switch (permission) {
      case 'manage_restaurant':
        return 'Manage Restaurant';
      case 'manage_menu':
        return 'Manage Menu';
      case 'manage_orders':
        return 'Manage Orders';
      case 'manage_tables':
        return 'Manage Tables';
      case 'manage_staff':
        return 'Manage Staff';
      case 'view_analytics':
        return 'View Analytics';
      case 'manage_payments':
        return 'Manage Payments';
      default:
        return permission.replaceAll('_', ' ').split(' ')
            .map((word) => word.isNotEmpty ? '${word[0].toUpperCase()}${word.substring(1)}' : '')
            .join(' ');
    }
  }
  
  /// Get description for permission
  String getPermissionDescription(String permission) {
    switch (permission) {
      case 'manage_restaurant':
        return 'Edit restaurant information and settings';
      case 'manage_menu':
        return 'Add, edit, and remove menu items';
      case 'manage_orders':
        return 'View and process customer orders';
      case 'manage_tables':
        return 'Manage table assignments and status';
      case 'manage_staff':
        return 'Add, edit, and remove staff members';
      case 'view_analytics':
        return 'Access sales and performance reports';
      case 'manage_payments':
        return 'Handle payment processing and refunds';
      default:
        return '';
    }
  }
}
