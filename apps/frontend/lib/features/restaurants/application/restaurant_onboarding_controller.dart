/// RestaurantOnboardingController bridges the shared onboarding flow
/// with the restaurant feature domain logic.
///
/// - Extends shared OnboardingController for step management
/// - Delegates persistence, API calls, and data to RestaurantController
/// - Applies validation using existing shared validators
library;

import 'package:get/get.dart';

import '../../../shared/onboarding/controllers/onboarding_controller.dart';
import '../../../shared/utils/validation_utils.dart';
import './restaurant_controller.dart' as legacy;

/// Controller for restaurant onboarding that coordinates shared onboarding
/// flow mechanics with restaurant-specific domain logic.
class RestaurantOnboardingController extends OnboardingController {
  /// Underlying legacy controller that handles repository/API and data map.
  final legacy.RestaurantController baseController;

  /// Titles for each step.
  final List<String> stepTitles = const [
    'Restaurant Info',
    'Owner Info',
    'Business Details',
    'Review & Submit',
  ];

  RestaurantOnboardingController({required this.baseController});

  @override
  int get totalSteps => stepTitles.length;

  @override
  void initializeOnboarding() {
    // Ensure we start aligned with existing registration state if any.
    currentStep.value = baseController.currentStep.value;
    ever<int>(baseController.currentStep, (v) => currentStep.value = v);
    ever<int>(currentStep, (v) => baseController.currentStep.value = v);
  }

  @override
  String getStepTitle() => stepTitles[currentStep.value];

  @override
  Future<bool> performCustomValidation() async {
    // Step-specific validations leveraging shared validators
    final data = baseController.registrationData;
    switch (currentStep.value) {
      case 0: // Restaurant Info
        final name = (data['name'] as String?)?.trim();
        final nameError = RestaurantNameValidator.validate(name);
        if (nameError != null) {
          setError(nameError);
          return false;
        }
        // Optional fields use existing validators if present
        final website = (data['website'] as String?)?.trim();
        if (website != null && website.isNotEmpty) {
          final urlError = UrlValidator.validate(website);
          if (urlError != null) {
            setError(urlError);
            return false;
          }
        }
        return true;

      case 1: // Owner Info
        final email = (data['owner_email'] as String?)?.trim();
        final password = data['owner_password'] as String?;
        final emailErr = EmailValidator.validate(email);
        if (emailErr != null) {
          setError(emailErr);
          return false;
        }
        final pwdErr = PasswordValidator.validate(password);
        if (pwdErr != null) {
          setError(pwdErr);
          return false;
        }
        return true;

      case 2: // Business Details (optional)
        return true;

      case 3: // Review
        return true;

      default:
        return true;
    }
  }

  @override
  Future<void> completeOnboarding() async {
    // Submission is handled by the base controller; no-op here.
  }

  /// Convenience passthroughs to legacy controller
  bool get isRegistering => baseController.isRegistering.value;
  Map<String, dynamic> get registrationData => baseController.registrationData;

  void updateRegistrationData(String key, dynamic value) {
    baseController.updateRegistrationData(key, value);
  }

  Future<void> submit() async {
    // Submission is orchestrated from the screen using baseController
  }
}
