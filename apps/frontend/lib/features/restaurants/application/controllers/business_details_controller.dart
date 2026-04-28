/// Business details controller for managing restaurant business configuration.
///
/// This controller replaces the StatefulWidget pattern in BusinessDetailsStep
/// with GetX reactive state management.

import 'package:get/get.dart';
import '../restaurant_controller.dart';

class BusinessDetailsController extends GetxController {
  // Observable state
  final _selectedServiceModel = 'self_service'.obs;
  final _autoAcceptOrders = true.obs;
  final _taxRate = 18.0.obs;
  final _serviceChargeRate = 0.0.obs;
  final _estimatedPrepTime = 30.obs;
  
  // Service model options
  final List<Map<String, String>> serviceModels = [
    {
      'value': 'self_service',
      'title': 'Self Service',
      'description': 'Customers order and pay themselves using QR codes',
    },
    {
      'value': 'staff_assisted',
      'title': 'Staff Assisted',
      'description': 'Staff takes orders and processes payments',
    },
  ];
  
  // Getters
  String get selectedServiceModel => _selectedServiceModel.value;
  bool get autoAcceptOrders => _autoAcceptOrders.value;
  double get taxRate => _taxRate.value;
  double get serviceChargeRate => _serviceChargeRate.value;
  int get estimatedPrepTime => _estimatedPrepTime.value;
  
  @override
  void onInit() {
    super.onInit();
    _loadExistingData();
  }
  
  /// Load existing data from restaurant controller
  void _loadExistingData() {
    final controller = Get.find<RestaurantController>();
    final data = controller.registrationData;
    
    _selectedServiceModel.value = data['service_model'] ?? 'self_service';
    _autoAcceptOrders.value = data['auto_accept_orders'] ?? true;
    _taxRate.value = (data['tax_rate'] ?? 18.0).toDouble();
    _serviceChargeRate.value = (data['service_charge_rate'] ?? 0.0).toDouble();
    _estimatedPrepTime.value = (data['estimated_prep_time'] ?? 30).toInt();
  }
  
  /// Update service model
  void updateServiceModel(String model) {
    _selectedServiceModel.value = model;
    _updateRegistrationData('service_model', model);
  }
  
  /// Update auto accept orders setting
  void updateAutoAcceptOrders(bool value) {
    _autoAcceptOrders.value = value;
    _updateRegistrationData('auto_accept_orders', value);
  }
  
  /// Update tax rate
  void updateTaxRate(double rate) {
    _taxRate.value = rate;
    _updateRegistrationData('tax_rate', rate);
  }
  
  /// Update service charge rate
  void updateServiceChargeRate(double rate) {
    _serviceChargeRate.value = rate;
    _updateRegistrationData('service_charge_rate', rate);
  }
  
  /// Update estimated preparation time
  void updateEstimatedPrepTime(int minutes) {
    _estimatedPrepTime.value = minutes;
    _updateRegistrationData('estimated_prep_time', minutes);
  }
  
  /// Helper method to update registration data
  void _updateRegistrationData(String key, dynamic value) {
    final controller = Get.find<RestaurantController>();
    controller.updateRegistrationData(key, value);
  }
  
  /// Get service model by value
  Map<String, String>? getServiceModelByValue(String value) {
    try {
      return serviceModels.firstWhere((model) => model['value'] == value);
    } catch (e) {
      return null;
    }
  }
  
  /// Validate all business details
  bool validateBusinessDetails() {
    if (_selectedServiceModel.value.isEmpty) {
      Get.snackbar('Error', 'Please select a service model');
      return false;
    }
    
    if (_taxRate.value < 0 || _taxRate.value > 100) {
      Get.snackbar('Error', 'Tax rate must be between 0% and 100%');
      return false;
    }
    
    if (_serviceChargeRate.value < 0 || _serviceChargeRate.value > 100) {
      Get.snackbar('Error', 'Service charge rate must be between 0% and 100%');
      return false;
    }
    
    if (_estimatedPrepTime.value < 1 || _estimatedPrepTime.value > 300) {
      Get.snackbar('Error', 'Estimated preparation time must be between 1 and 300 minutes');
      return false;
    }
    
    return true;
  }
  
  /// Reset to default values
  void resetToDefaults() {
    _selectedServiceModel.value = 'self_service';
    _autoAcceptOrders.value = true;
    _taxRate.value = 18.0;
    _serviceChargeRate.value = 0.0;
    _estimatedPrepTime.value = 30;
    
    // Update registration data
    final controller = Get.find<RestaurantController>();
    controller.updateRegistrationData('service_model', 'self_service');
    controller.updateRegistrationData('auto_accept_orders', true);
    controller.updateRegistrationData('tax_rate', 18.0);
    controller.updateRegistrationData('service_charge_rate', 0.0);
    controller.updateRegistrationData('estimated_prep_time', 30);
  }
}
