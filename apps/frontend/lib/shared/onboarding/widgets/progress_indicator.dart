/// Enhanced progress indicator for onboarding flows.
///
/// This widget provides visual progress tracking with completion percentage,
/// clickable steps for navigation, animated transitions, and achievement
/// celebrations using the existing AppAnimations system.
library;

import 'package:flutter/material.dart';

import '../../../core/theme/app_animations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/responsive/breakpoints.dart';

/// Enhanced onboarding progress indicator.
///
/// Displays progress through the onboarding flow with visual feedback,
/// step navigation, and responsive design that adapts to screen size.
class OnboardingProgressIndicator extends StatelessWidget {
  /// Creates an onboarding progress indicator.
  const OnboardingProgressIndicator({
    super.key,
    required this.steps,
    required this.currentStep,
    this.stepCompletion = const {},
    this.onStepTapped,
    this.showPercentage = true,
    this.showLabels = true,
  });

  /// List of step titles.
  final List<String> steps;

  /// Current active step index (0-based).
  final int currentStep;

  /// Map of step completion status.
  final Map<int, bool> stepCompletion;

  /// Callback when a step is tapped.
  final Function(int)? onStepTapped;

  /// Whether to show completion percentage.
  final bool showPercentage;

  /// Whether to show step labels.
  final bool showLabels;

  /// Calculate completion percentage.
  double get completionPercentage {
    if (steps.isEmpty) return 0.0;
    return (currentStep + 1) / steps.length;
  }

  @override
  Widget build(BuildContext context) {
    final breakpoint = BreakpointConfig.getCurrentBreakpoint(context);
    final isMobile = breakpoint == Breakpoint.mobile;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Progress bar
        _buildProgressBar(context),

        const SizedBox(height: AppSpacing.md),

        // Step indicators
        if (isMobile)
          _buildMobileStepIndicators(context)
        else
          _buildDesktopStepIndicators(context),

        // Completion percentage
        if (showPercentage) ...[
          const SizedBox(height: AppSpacing.sm),
          _buildCompletionPercentage(context),
        ],
      ],
    );
  }

  /// Build the progress bar.
  Widget _buildProgressBar(BuildContext context) {
    return TweenAnimationBuilder<double>(
      duration: AppAnimations.normal,
      curve: AppAnimations.emphasize,
      tween: Tween<double>(
        begin: 0.0,
        end: completionPercentage,
      ),
      builder: (context, value, child) {
        return Container(
          height: 8,
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surfaceContainerHighest,
            borderRadius: BorderRadius.circular(4),
          ),
          child: FractionallySizedBox(
            alignment: Alignment.centerLeft,
            widthFactor: value,
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    AppColors.primary,
                    AppColors.primary.withValues(alpha: 0.8),
                  ],
                ),
                borderRadius: BorderRadius.circular(4),
              ),
            ),
          ),
        );
      },
    );
  }

  /// Build mobile step indicators (dots).
  Widget _buildMobileStepIndicators(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(
        steps.length,
        (index) => Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4),
          child: _buildDotIndicator(context, index),
        ),
      ),
    );
  }

  /// Build desktop step indicators (numbered with labels).
  Widget _buildDesktopStepIndicators(BuildContext context) {
    return Row(
      children: List.generate(
        steps.length,
        (index) {
          final isLast = index == steps.length - 1;
          return Expanded(
            child: Row(
              children: [
                Expanded(
                  child: _buildNumberedIndicator(context, index),
                ),
                if (!isLast)
                  Expanded(
                    child: _buildConnectorLine(context, index),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }

  /// Build dot indicator for mobile.
  Widget _buildDotIndicator(BuildContext context, int index) {
    final isActive = index == currentStep;
    final isCompleted = stepCompletion[index] == true || index < currentStep;
    final canTap = onStepTapped != null && index <= currentStep;

    return GestureDetector(
      onTap: canTap ? () => onStepTapped!(index) : null,
      child: TweenAnimationBuilder<double>(
        duration: AppAnimations.fast,
        curve: AppAnimations.standard,
        tween: Tween<double>(
          begin: 0.0,
          end: isActive ? 1.0 : 0.0,
        ),
        builder: (context, value, child) {
          final size = isActive ? 12.0 : 8.0;
          return Container(
            width: size,
            height: size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isCompleted
                  ? AppColors.success
                  : isActive
                      ? AppColors.primary
                      : Theme.of(context).colorScheme.surfaceContainerHighest,
              border: Border.all(
                color: isActive
                    ? AppColors.primary
                    : Theme.of(context).colorScheme.outline,
                width: isActive ? 2 : 1,
              ),
            ),
          );
        },
      ),
    );
  }

  /// Build numbered indicator for desktop.
  Widget _buildNumberedIndicator(BuildContext context, int index) {
    final isActive = index == currentStep;
    final isCompleted = stepCompletion[index] == true || index < currentStep;
    final canTap = onStepTapped != null && index <= currentStep;

    return GestureDetector(
      onTap: canTap ? () => onStepTapped!(index) : null,
      child: Column(
        children: [
          // Number circle
          TweenAnimationBuilder<double>(
            duration: AppAnimations.fast,
            curve: AppAnimations.bounce,
            tween: Tween<double>(
              begin: 0.0,
              end: isActive ? 1.0 : 0.0,
            ),
            builder: (context, value, child) {
              final scale = 1.0 + (value * 0.1);
              return Transform.scale(
                scale: scale,
                child: Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isCompleted
                        ? AppColors.success
                        : isActive
                            ? AppColors.primary
                            : Theme.of(context)
                                .colorScheme
                                .surfaceContainerHighest,
                    border: Border.all(
                      color: isActive
                          ? AppColors.primary
                          : Theme.of(context).colorScheme.outline,
                      width: isActive ? 2 : 1,
                    ),
                  ),
                  child: Center(
                    child: isCompleted
                        ? const Icon(
                            Icons.check,
                            color: Colors.white,
                            size: 20,
                          )
                        : Text(
                            '${index + 1}',
                            style: TextStyle(
                              color: isActive
                                  ? Colors.white
                                  : Theme.of(context)
                                      .colorScheme
                                      .onSurfaceVariant,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                  ),
                ),
              );
            },
          ),

          // Label
          if (showLabels) ...[
            const SizedBox(height: AppSpacing.xs),
            Text(
              steps[index],
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: isActive
                        ? Theme.of(context).colorScheme.primary
                        : Theme.of(context).colorScheme.onSurfaceVariant,
                    fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
                  ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ],
      ),
    );
  }

  /// Build connector line between steps.
  Widget _buildConnectorLine(BuildContext context, int index) {
    final isCompleted = stepCompletion[index] == true || index < currentStep;

    return Container(
      height: 2,
      margin: const EdgeInsets.only(bottom: 40),
      color: isCompleted
          ? AppColors.success
          : Theme.of(context).colorScheme.surfaceContainerHighest,
    );
  }

  /// Build completion percentage text.
  Widget _buildCompletionPercentage(BuildContext context) {
    return TweenAnimationBuilder<double>(
      duration: AppAnimations.normal,
      curve: AppAnimations.standard,
      tween: Tween<double>(
        begin: 0.0,
        end: completionPercentage,
      ),
      builder: (context, value, child) {
        return Text(
          '${(value * 100).toInt()}% Complete',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
                fontWeight: FontWeight.w500,
              ),
        );
      },
    );
  }
}
