/// ZERGO QR Shared Onboarding System
///
/// A comprehensive, reusable onboarding framework that can be adapted for
/// different user types (restaurants, staff, customers). This system eliminates
/// code duplication through a well-architected component system following
/// Clean Architecture principles.
///
/// Features:
/// - Component-based architecture with reusable widgets
/// - GetX controllers for state management (not mixins)
/// - Responsive design using existing BreakpointConfig
/// - Progressive profiling with auto-save capabilities
/// - Professional trust-building elements
/// - Comprehensive validation using existing validation_utils.dart
///
/// Leverages Existing Infrastructure:
/// - Validation: shared/utils/validation_utils.dart
/// - Animations: core/theme/app_animations.dart + shared/performance/animation_optimizer.dart
/// - Theme: core/theme/ (AppColors, AppSpacing, AppTypography)
/// - Responsive: shared/responsive/breakpoints.dart
/// - State: GetX pattern with .obs reactive variables
library;

// Reusable components
export 'components/index.dart';
// Controllers
export 'controllers/onboarding_controller.dart';
// Core widgets
export 'widgets/index.dart';
