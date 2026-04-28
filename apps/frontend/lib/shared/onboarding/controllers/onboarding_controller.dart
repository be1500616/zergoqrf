/// Onboarding controller using GetX for state management.
///
/// This controller manages the onboarding flow state, validation,
/// and navigation between steps. It leverages existing utilities
/// from the shared module for validation, animations, and responsive design.
library;

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

/// Base onboarding controller for managing onboarding flow state.
///
/// This controller provides common functionality for all onboarding flows
/// including step navigation, validation, form state management, and
/// progress tracking. It uses GetX reactive state management with .obs
/// variables for automatic UI updates.
abstract class OnboardingController extends GetxController {
  /// Current step index (0-based).
  final currentStep = 0.obs;

  /// Total number of steps in the onboarding flow.
  int get totalSteps;

  /// Whether the current step is valid and can proceed.
  final isCurrentStepValid = false.obs;

  /// Whether the onboarding flow is currently loading/processing.
  final isLoading = false.obs;

  /// Error message for the current step (null if no error).
  final Rx<String?> errorMessage = Rx<String?>(null);

  /// Form key for the current step.
  final formKey = GlobalKey<FormState>();

  /// Debounce timer for validation.
  Timer? _debounceTimer;

  /// Debounce duration for validation (default 300ms).
  Duration get debounceDuration => const Duration(milliseconds: 300);

  @override
  void onInit() {
    super.onInit();
    initializeOnboarding();
  }

  @override
  void onClose() {
    _debounceTimer?.cancel();
    super.onClose();
  }

  /// Initialize onboarding-specific state.
  ///
  /// Override this method to set up initial state for your onboarding flow.
  void initializeOnboarding() {
    // Override in subclasses
  }

  /// Navigate to the next step.
  ///
  /// Validates the current step before proceeding. If validation fails,
  /// the navigation is blocked and error messages are displayed.
  Future<void> nextStep() async {
    if (!await validateCurrentStep()) {
      return;
    }

    if (currentStep.value < totalSteps - 1) {
      currentStep.value++;
      resetStepState();
    } else {
      await completeOnboarding();
    }
  }

  /// Navigate to the previous step.
  void previousStep() {
    if (currentStep.value > 0) {
      currentStep.value--;
      resetStepState();
    }
  }

  /// Jump to a specific step.
  ///
  /// Args:
  ///   step: The step index to jump to (0-based).
  ///   validateCurrent: Whether to validate the current step before jumping.
  Future<void> goToStep(int step, {bool validateCurrent = true}) async {
    if (validateCurrent && !await validateCurrentStep()) {
      return;
    }

    if (step >= 0 && step < totalSteps) {
      currentStep.value = step;
      resetStepState();
    }
  }

  /// Validate the current step.
  ///
  /// Returns:
  ///   True if the current step is valid, false otherwise.
  Future<bool> validateCurrentStep() async {
    errorMessage.value = null;

    // Validate form if present
    if (formKey.currentState != null && !formKey.currentState!.validate()) {
      isCurrentStepValid.value = false;
      return false;
    }

    // Custom validation logic (override in subclasses)
    final customValidation = await performCustomValidation();
    isCurrentStepValid.value = customValidation;
    return customValidation;
  }

  /// Perform custom validation for the current step.
  ///
  /// Override this method to implement step-specific validation logic.
  ///
  /// Returns:
  ///   True if validation passes, false otherwise.
  Future<bool> performCustomValidation() async {
    return true; // Override in subclasses
  }

  /// Reset state when changing steps.
  void resetStepState() {
    errorMessage.value = null;
    isCurrentStepValid.value = false;
    formKey.currentState?.reset();
  }

  /// Complete the onboarding flow.
  ///
  /// Override this method to implement the final submission logic.
  Future<void> completeOnboarding() async {
    // Override in subclasses
  }

  /// Debounced validation for real-time field validation.
  ///
  /// Args:
  ///   validator: The validation function to execute after debounce.
  void debouncedValidation(Future<void> Function() validator) {
    _debounceTimer?.cancel();
    _debounceTimer = Timer(debounceDuration, () async {
      await validator();
    });
  }

  /// Set loading state.
  ///
  /// Args:
  ///   loading: Whether the controller is in loading state.
  void setLoading(bool loading) {
    isLoading.value = loading;
  }

  /// Set error message.
  ///
  /// Args:
  ///   error: The error message to display (null to clear).
  void setError(String? error) {
    errorMessage.value = error;
  }

  /// Clear error message.
  void clearError() {
    errorMessage.value = null;
  }

  /// Get progress percentage (0.0 to 1.0).
  ///
  /// Returns:
  ///   The progress as a value between 0.0 and 1.0.
  double get progress {
    if (totalSteps == 0) return 0.0;
    return (currentStep.value + 1) / totalSteps;
  }

  /// Check if this is the first step.
  ///
  /// Returns:
  ///   True if on the first step.
  bool get isFirstStep => currentStep.value == 0;

  /// Check if this is the last step.
  ///
  /// Returns:
  ///   True if on the last step.
  bool get isLastStep => currentStep.value == totalSteps - 1;

  /// Get the title for the current step.
  ///
  /// Override this method to provide step-specific titles.
  ///
  /// Returns:
  ///   The title for the current step.
  String getStepTitle() {
    return 'Step ${currentStep.value + 1} of $totalSteps';
  }

  /// Get the description for the current step.
  ///
  /// Override this method to provide step-specific descriptions.
  ///
  /// Returns:
  ///   The description for the current step.
  String? getStepDescription() {
    return null; // Override in subclasses
  }

  /// Check if a specific step can be accessed.
  ///
  /// Args:
  ///   step: The step index to check.
  ///
  /// Returns:
  ///   True if the step can be accessed.
  bool canAccessStep(int step) {
    // By default, only allow access to current and previous steps
    return step <= currentStep.value;
  }

  /// Handle back button press.
  ///
  /// Returns:
  ///   True if the back press was handled, false to allow default behavior.
  Future<bool> onBackPressed() async {
    if (!isFirstStep) {
      previousStep();
      return true;
    }
    return false;
  }

  /// Save current step data.
  ///
  /// Override this method to implement step-specific data persistence.
  Future<void> saveStepData() async {
    // Override in subclasses
  }

  /// Load saved step data.
  ///
  /// Override this method to implement step-specific data loading.
  Future<void> loadStepData() async {
    // Override in subclasses
  }
}

