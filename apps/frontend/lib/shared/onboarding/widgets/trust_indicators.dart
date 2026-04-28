/// Trust building components for onboarding.
///
/// This widget provides professional trust elements including security badges,
/// testimonials, statistics, and social proof to build credibility during
/// the onboarding process.
library;

import 'package:flutter/material.dart';

import '../../../core/theme/app_animations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';

/// Trust indicators widget for building credibility.
///
/// Displays various trust elements to reassure users during onboarding,
/// including security badges, statistics, and testimonials.
class TrustIndicators extends StatelessWidget {
  /// Creates trust indicators.
  const TrustIndicators({
    super.key,
    this.showSecurityBadge = true,
    this.showStatistics = true,
    this.showTestimonial = false,
    this.customMessage,
  });

  /// Whether to show security badge.
  final bool showSecurityBadge;

  /// Whether to show statistics.
  final bool showStatistics;

  /// Whether to show testimonial.
  final bool showTestimonial;

  /// Custom trust message.
  final String? customMessage;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (showSecurityBadge) ...[
          _buildSecurityBadge(context),
          const SizedBox(height: AppSpacing.md),
        ],
        if (showStatistics) ...[
          _buildStatistics(context),
          const SizedBox(height: AppSpacing.md),
        ],
        if (showTestimonial) ...[
          _buildTestimonial(context),
          const SizedBox(height: AppSpacing.md),
        ],
        if (customMessage != null) ...[
          _buildCustomMessage(context),
        ],
      ],
    );
  }

  /// Build security badge.
  Widget _buildSecurityBadge(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: AppColors.success.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: AppColors.success.withValues(alpha: 0.3),
        ),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.verified_user,
            color: AppColors.success,
            size: 24,
          ),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Secure & Encrypted',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        color: AppColors.success,
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 2),
                Text(
                  'Your data is protected with bank-level encryption',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Build statistics section.
  Widget _buildStatistics(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: Theme.of(context)
            .colorScheme
            .surfaceContainerHighest
            .withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Trusted by Restaurants Worldwide',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: AppSpacing.md),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildStatItem(
                context,
                icon: Icons.restaurant,
                value: '10,000+',
                label: 'Restaurants',
              ),
              _buildStatItem(
                context,
                icon: Icons.shopping_bag,
                value: '1M+',
                label: 'Orders',
              ),
              _buildStatItem(
                context,
                icon: Icons.star,
                value: '4.8',
                label: 'Rating',
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// Build individual stat item.
  Widget _buildStatItem(
    BuildContext context, {
    required IconData icon,
    required String value,
    required String label,
  }) {
    return TweenAnimationBuilder<double>(
      duration: AppAnimations.slow,
      curve: AppAnimations.bounce,
      tween: Tween<double>(begin: 0.0, end: 1.0),
      builder: (context, animValue, child) {
        return Opacity(
          opacity: animValue,
          child: Transform.scale(
            scale: animValue,
            child: Column(
              children: [
                Icon(
                  icon,
                  color: AppColors.primary,
                  size: 32,
                ),
                const SizedBox(height: AppSpacing.xs),
                Text(
                  value,
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: AppColors.primary,
                      ),
                ),
                Text(
                  label,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  /// Build testimonial section.
  Widget _buildTestimonial(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: Theme.of(context)
            .colorScheme
            .primaryContainer
            .withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.2),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: List.generate(
              5,
              (index) => const Icon(
                Icons.star,
                color: Colors.amber,
                size: 16,
              ),
            ),
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            '"ZERGO QR transformed our restaurant operations. Setup was incredibly easy and our customers love the seamless ordering experience."',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontStyle: FontStyle.italic,
                ),
          ),
          const SizedBox(height: AppSpacing.sm),
          Row(
            children: [
              const CircleAvatar(
                radius: 16,
                backgroundColor: AppColors.primary,
                child: Text(
                  'JD',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              const SizedBox(width: AppSpacing.sm),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'John Doe',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  Text(
                    'Owner, The Gourmet Kitchen',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Theme.of(context).colorScheme.onSurfaceVariant,
                        ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// Build custom message.
  Widget _buildCustomMessage(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: Theme.of(context)
            .colorScheme
            .surfaceContainerHighest
            .withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.info_outline,
            color: AppColors.primary,
            size: 20,
          ),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Text(
              customMessage!,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
        ],
      ),
    );
  }
}

/// Feature highlight widget for showcasing key features.
class FeatureHighlight extends StatelessWidget {
  /// Creates a feature highlight.
  const FeatureHighlight({
    super.key,
    required this.icon,
    required this.title,
    required this.description,
  });

  /// Feature icon.
  final IconData icon;

  /// Feature title.
  final String title;

  /// Feature description.
  final String description;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(AppSpacing.sm),
          decoration: BoxDecoration(
            color: AppColors.primary.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            icon,
            color: AppColors.primary,
            size: 24,
          ),
        ),
        const SizedBox(width: AppSpacing.md),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 4),
              Text(
                description,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
