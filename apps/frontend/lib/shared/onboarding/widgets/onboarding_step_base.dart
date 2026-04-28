/// Base class for all onboarding steps.
///
/// This abstract class provides a common interface and shared functionality
/// for all onboarding steps, including validation logic, animation patterns,
/// auto-save functionality, and consistent error handling.
library;

import 'dart:async';

import 'package:flutter/material.dart';
import 'package:get/get.dart';

/// Abstract base class for all onboarding steps.
///
/// Provides common interface, validation logic, animation patterns,
/// and auto-save functionality that all onboarding steps should implement.
///
/// Example usage:
/// ```dart
/// class RestaurantInfoStep extends OnboardingStepBase {
///   @override
///   String get stepTitle => 'Restaurant Information';
///
///   @override
///   String get stepDescription => 'Tell us about your restaurant';
///
///   @override
///   Widget buildStepContent(BuildContext context) {
///     return Column(children: [...]);
///   }
///
///   @override
///   bool validateStep() {
///     return _formKey.currentState?.validate() ?? false;
///   }
/// }
/// ```
abstract class OnboardingStepBase extends StatefulWidget {
  /// Creates an onboarding step.
  ///
  /// Args:
  ///   key: Optional widget key for identification.
  ///   stepIndex: The index of this step in the onboarding flow.
  ///   totalSteps: Total number of steps in the onboarding flow.
  ///   onStepCompleted: Callback when step validation passes.
  ///   onStepChanged: Callback when step data changes.
  ///   autoSaveEnabled: Whether to enable automatic saving of step data.
  const OnboardingStepBase({
    super.key,
    required this.stepIndex,
    required this.totalSteps,
    this.onStepCompleted,
    this.onStepChanged,
    this.autoSaveEnabled = true,
  });

  /// The index of this step in the onboarding flow (0-based).
  final int stepIndex;

  /// Total number of steps in the onboarding flow.
  final int totalSteps;

  /// Callback invoked when step validation passes.
  final VoidCallback? onStepCompleted;

  /// Callback invoked when step data changes.
  final ValueChanged<Map<String, dynamic>>? onStepChanged;

  /// Whether to enable automatic saving of step data.
  final bool autoSaveEnabled;

  /// The title of this onboarding step.
  ///
  /// This will be displayed in the progress indicator and step header.
  String get stepTitle;

  /// The description of this onboarding step.
  ///
  /// This provides additional context about what the user should do.
  String get stepDescription;

  /// The icon representing this step (optional).
  ///
  /// If provided, will be displayed in the progress indicator.
  IconData? get stepIcon => null;

  /// Whether this step is required to complete onboarding.
  ///
  /// Required steps must be completed before proceeding.
  bool get isRequired => true;

  /// The minimum time (in milliseconds) a user should spend on this step.
  ///
  /// Used for analytics and progress tracking.
  int get minimumTimeMs => 5000;

  /// Build the main content for this onboarding step.
  ///
  /// This method must be implemented by concrete step classes to provide
  /// the specific UI content for the step.
  ///
  /// Args:
  ///   context: The build context.
  ///
  /// Returns:
  ///   The widget tree for the step content.
  Widget buildStepContent(BuildContext context);

  /// Validate the current step data.
  ///
  /// This method should return true if all required data for this step
  /// is valid and complete, false otherwise.
  ///
  /// Returns:
  ///   True if step data is valid, false otherwise.
  bool validateStep();

  /// Get the current step data as a map.
  ///
  /// This data will be used for auto-saving and final submission.
  ///
  /// Returns:
  ///   Map containing the current step data.
  Map<String, dynamic> getStepData();

  /// Load existing data into this step.
  ///
  /// Called when resuming onboarding or loading saved data.
  ///
  /// Args:
  ///   data: The data to load into this step.
  void loadStepData(Map<String, dynamic> data);

  /// Reset this step to its initial state.
  ///
  /// Clears all form data and validation errors.
  void resetStep();

  /// Called when the step becomes active.
  ///
  /// Override to perform any initialization when the step is displayed.
  void onStepActivated() {}

  /// Called when the step becomes inactive.
  ///
  /// Override to perform cleanup when leaving the step.
  void onStepDeactivated() {}

  @override
  State<OnboardingStepBase> createState() => _OnboardingStepBaseState();
}

/// State class for OnboardingStepBase.
///
/// Handles the common functionality including auto-save, validation,
/// and lifecycle management.
class _OnboardingStepBaseState extends State<OnboardingStepBase>
    with TickerProviderStateMixin {
  /// Form key for validation.
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();

  /// Whether the step is currently loading.
  final RxBool _isLoading = false.obs;

  /// Current validation errors.
  final RxList<String> _validationErrors = <String>[].obs;

  /// Timer for auto-save functionality.
  Timer? _autoSaveTimer;

  @override
  void initState() {
    super.initState();
    widget.onStepActivated();

    if (widget.autoSaveEnabled) {
      _setupAutoSave();
    }
  }

  @override
  void dispose() {
    _autoSaveTimer?.cancel();
    widget.onStepDeactivated();
    super.dispose();
  }

  /// Set up auto-save functionality.
  void _setupAutoSave() {
    _autoSaveTimer = Timer.periodic(
      const Duration(seconds: 30),
      (_) => _performAutoSave(),
    );
  }

  /// Perform auto-save of current step data.
  void _performAutoSave() {
    if (!mounted) return;

    final stepData = widget.getStepData();
    if (stepData.isNotEmpty) {
      widget.onStepChanged?.call(stepData);
    }
  }

  /// Validate the current step.
  bool _validateCurrentStep() {
    _validationErrors.clear();

    // Validate form if present
    final formValid = _formKey.currentState?.validate() ?? true;

    // Validate step-specific logic
    final stepValid = widget.validateStep();

    if (!formValid || !stepValid) {
      _validationErrors.add('Please correct the errors above');
      return false;
    }

    return true;
  }

  /// Handle step completion.
  void _handleStepCompletion() {
    if (_validateCurrentStep()) {
      _performAutoSave();
      widget.onStepCompleted?.call();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Step header
          _buildStepHeader(context),

          const SizedBox(height: 24),

          // Step content
          Expanded(
            child: widget.buildStepContent(context),
          ),

          const SizedBox(height: 24),

          // Validation errors
          Obx(() => _buildValidationErrors(context)),

          // Step actions
          _buildStepActions(context),
        ],
      ),
    );
  }

  /// Build the step header with title and description.
  Widget _buildStepHeader(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          widget.stepTitle,
          style: theme.textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          widget.stepDescription,
          style: theme.textTheme.bodyLarge?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }

  /// Build validation error messages.
  Widget _buildValidationErrors(BuildContext context) {
    if (_validationErrors.isEmpty) {
      return const SizedBox.shrink();
    }

    final theme = Theme.of(context);

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: theme.colorScheme.errorContainer,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: _validationErrors
            .map((error) => Text(
                  error,
                  style: TextStyle(
                    color: theme.colorScheme.onErrorContainer,
                  ),
                ))
            .toList(),
      ),
    );
  }

  /// Build step action buttons.
  Widget _buildStepActions(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        // Back button (if not first step)
        if (widget.stepIndex > 0)
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('Back'),
          )
        else
          const SizedBox.shrink(),

        // Next/Complete button
        Obx(() => ElevatedButton(
              onPressed: _isLoading.value ? null : _handleStepCompletion,
              child: _isLoading.value
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Text(
                      widget.stepIndex == widget.totalSteps - 1
                          ? 'Complete'
                          : 'Next',
                    ),
            )),
      ],
    );
  }
}
