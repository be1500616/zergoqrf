/// Restaurant registration screen.
///
/// This module contains the multi-step restaurant registration UI.

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../application/restaurant_controller.dart';
import '../domain/restaurant_entity.dart';
import 'widgets/registration_step_indicator.dart';
import 'widgets/restaurant_info_step.dart';
import 'widgets/owner_info_step.dart';
import 'widgets/business_details_step.dart';
import 'widgets/review_step.dart';

class RestaurantRegistrationScreen extends StatelessWidget {
  const RestaurantRegistrationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.find<RestaurantController>();

    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Restaurant Registration'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 0,
        centerTitle: true,
      ),
      body: Column(
        children: [
          // Progress indicator
          Container(
            color: Colors.white,
            padding: const EdgeInsets.all(16),
            child: Obx(() => RegistrationStepIndicator(
              currentStep: controller.currentStep.value,
              totalSteps: 4,
            )),
          ),
          
          // Step content
          Expanded(
            child: Obx(() {
              switch (controller.currentStep.value) {
                case 0:
                  return const RestaurantInfoStep();
                case 1:
                  return const OwnerInfoStep();
                case 2:
                  return const BusinessDetailsStep();
                case 3:
                  return const ReviewStep();
                default:
                  return const RestaurantInfoStep();
              }
            }),
          ),
          
          // Navigation buttons
          Container(
            color: Colors.white,
            padding: const EdgeInsets.all(16),
            child: Obx(() => Row(
              children: [
                if (controller.currentStep.value > 0)
                  Expanded(
                    child: OutlinedButton(
                      onPressed: controller.previousStep,
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        side: BorderSide(color: Colors.blue[600]!),
                      ),
                      child: const Text('Previous'),
                    ),
                  ),
                
                if (controller.currentStep.value > 0)
                  const SizedBox(width: 16),
                
                Expanded(
                  child: ElevatedButton(
                    onPressed: controller.isRegistering.value
                        ? null
                        : () => _handleNext(controller),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue[600],
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: controller.isRegistering.value
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          )
                        : Text(
                            controller.currentStep.value == 3 ? 'Register' : 'Next',
                          ),
                  ),
                ),
              ],
            )),
          ),
        ],
      ),
    );
  }

  void _handleNext(RestaurantController controller) {
    if (controller.currentStep.value == 3) {
      // Final step - submit registration
      _submitRegistration(controller);
    } else {
      // Validate current step and move to next
      if (_validateCurrentStep(controller)) {
        controller.nextStep();
      }
    }
  }

  bool _validateCurrentStep(RestaurantController controller) {
    switch (controller.currentStep.value) {
      case 0:
        // Validate restaurant info
        final name = controller.registrationData['name'] as String?;
        if (name == null || name.trim().isEmpty) {
          Get.snackbar('Error', 'Restaurant name is required');
          return false;
        }
        return true;
        
      case 1:
        // Validate owner info
        final email = controller.registrationData['owner_email'] as String?;
        final password = controller.registrationData['owner_password'] as String?;
        
        if (email == null || email.trim().isEmpty) {
          Get.snackbar('Error', 'Owner email is required');
          return false;
        }
        
        if (password == null || password.length < 8) {
          Get.snackbar('Error', 'Password must be at least 8 characters');
          return false;
        }
        
        return true;
        
      case 2:
        // Business details are optional
        return true;
        
      default:
        return true;
    }
  }

  void _submitRegistration(RestaurantController controller) {
    final data = controller.registrationData;
    
    final request = RestaurantRegistrationRequest(
      name: data['name'] as String,
      description: data['description'] as String?,
      address: data['address'] as String?,
      phone: data['phone'] as String?,
      email: data['email'] as String?,
      website: data['website'] as String?,
      cuisineType: data['cuisine_type'] as String?,
      diningStyle: data['dining_style'] as String?,
      ownerEmail: data['owner_email'] as String,
      ownerPassword: data['owner_password'] as String,
      ownerName: data['owner_name'] as String?,
    );
    
    controller.registerRestaurant(request);
  }
}
