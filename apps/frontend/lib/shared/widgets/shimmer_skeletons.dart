import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';

import '../../core/theme/app_animations.dart';
import '../../core/theme/app_spacing.dart';
import '../responsive/screen_size.dart';

/// Professional shimmer skeleton components for loading states.
///
/// Provides realistic loading placeholders that match content structure
/// and improve perceived performance during data loading.
class ShimmerSkeletons {
  /// Private constructor to prevent instantiation
  ShimmerSkeletons._();

  /// Creates a shimmer skeleton for menu item cards.
  ///
  /// Displays a realistic placeholder for menu items with image,
  /// title, description, and price sections.
  static Widget menuItem({
    double? height,
    bool showImage = true,
    bool showPrice = true,
  }) {
    return Builder(
      builder: (context) {
        final screenSize = ScreenSize.of(context);
        final effectiveHeight = height ??
            screenSize.responsiveValue(
              mobile: 120.0,
              tablet: 140.0,
              desktop: 160.0,
            )!;

        return _ShimmerWrapper(
          child: Container(
            height: effectiveHeight,
            margin: EdgeInsets.symmetric(
              vertical: AppSpacing.sm * screenSize.spacingMultiplier,
              horizontal: AppSpacing.md * screenSize.spacingMultiplier,
            ),
            child: Row(
              children: [
                // Image placeholder
                if (showImage) ...[
                  _ShimmerBox(
                    width: effectiveHeight * 0.7,
                    height: effectiveHeight * 0.7,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  SizedBox(width: AppSpacing.md * screenSize.spacingMultiplier),
                ],

                // Content placeholder
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Title
                      _ShimmerBox(
                        width: double.infinity,
                        height: 18,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      SizedBox(
                          height: AppSpacing.xs * screenSize.spacingMultiplier),

                      // Description lines
                      _ShimmerBox(
                        width: screenSize.responsiveValue(
                          mobile: 200.0,
                          tablet: 250.0,
                          desktop: 300.0,
                        ),
                        height: 14,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      SizedBox(
                          height: AppSpacing.xs * screenSize.spacingMultiplier),

                      _ShimmerBox(
                        width: screenSize.responsiveValue(
                          mobile: 150.0,
                          tablet: 180.0,
                          desktop: 220.0,
                        ),
                        height: 14,
                        borderRadius: BorderRadius.circular(4),
                      ),

                      const Spacer(),

                      // Price placeholder
                      if (showPrice)
                        _ShimmerBox(
                          width: 80,
                          height: 20,
                          borderRadius: BorderRadius.circular(4),
                        ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  /// Creates a shimmer skeleton for restaurant cards.
  ///
  /// Displays a placeholder for restaurant information cards
  /// with header image, title, subtitle, and stats.
  static Widget restaurantCard() {
    return Builder(
      builder: (context) {
        final screenSize = ScreenSize.of(context);

        return _ShimmerWrapper(
          child: Container(
            margin:
                EdgeInsets.all(AppSpacing.md * screenSize.spacingMultiplier),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header image placeholder
                _ShimmerBox(
                  width: double.infinity,
                  height: screenSize.responsiveValue(
                    mobile: 180.0,
                    tablet: 220.0,
                    desktop: 260.0,
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                SizedBox(height: AppSpacing.md * screenSize.spacingMultiplier),

                // Title placeholder
                _ShimmerBox(
                  width: screenSize.responsiveValue(
                    mobile: 200.0,
                    tablet: 250.0,
                    desktop: 300.0,
                  ),
                  height: 22,
                  borderRadius: BorderRadius.circular(4),
                ),
                SizedBox(height: AppSpacing.sm * screenSize.spacingMultiplier),

                // Subtitle placeholder
                _ShimmerBox(
                  width: screenSize.responsiveValue(
                    mobile: 150.0,
                    tablet: 180.0,
                    desktop: 220.0,
                  ),
                  height: 16,
                  borderRadius: BorderRadius.circular(4),
                ),
                SizedBox(height: AppSpacing.md * screenSize.spacingMultiplier),

                // Stats row placeholder
                Row(
                  children: [
                    _ShimmerBox(
                      width: 60,
                      height: 14,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    SizedBox(
                        width: AppSpacing.md * screenSize.spacingMultiplier),
                    _ShimmerBox(
                      width: 80,
                      height: 14,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    SizedBox(
                        width: AppSpacing.md * screenSize.spacingMultiplier),
                    _ShimmerBox(
                      width: 70,
                      height: 14,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  /// Creates a shimmer skeleton for a list of items.
  ///
  /// Generates multiple skeleton items for list views.
  static Widget list({
    int itemCount = 5,
    double? itemHeight,
    bool showAvatar = true,
  }) {
    return Builder(
      builder: (context) {
        final screenSize = ScreenSize.of(context);
        final effectiveItemHeight = itemHeight ??
            screenSize.responsiveValue(
              mobile: 80.0,
              tablet: 90.0,
              desktop: 100.0,
            )!;

        return Column(
          children: List.generate(
            itemCount,
            (index) => _ShimmerWrapper(
              child: Container(
                height: effectiveItemHeight,
                margin: EdgeInsets.symmetric(
                  vertical: AppSpacing.sm * screenSize.spacingMultiplier,
                  horizontal: AppSpacing.md * screenSize.spacingMultiplier,
                ),
                child: Row(
                  children: [
                    // Avatar/Icon placeholder
                    if (showAvatar) ...[
                      _ShimmerBox(
                        width: effectiveItemHeight * 0.7,
                        height: effectiveItemHeight * 0.7,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      SizedBox(
                          width: AppSpacing.md * screenSize.spacingMultiplier),
                    ],

                    // Content placeholder
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          _ShimmerBox(
                            width: double.infinity,
                            height: 16,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          SizedBox(
                              height:
                                  AppSpacing.xs * screenSize.spacingMultiplier),
                          _ShimmerBox(
                            width: 150,
                            height: 12,
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  /// Creates a shimmer skeleton for dashboard cards.
  ///
  /// Displays placeholders for dashboard statistics and overview cards.
  static Widget dashboardCard() {
    return Builder(
      builder: (context) {
        final screenSize = ScreenSize.of(context);

        return _ShimmerWrapper(
          child: Container(
            padding:
                EdgeInsets.all(AppSpacing.lg * screenSize.spacingMultiplier),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header with icon and title
                Row(
                  children: [
                    _ShimmerBox(
                      width: 24,
                      height: 24,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    SizedBox(
                        width: AppSpacing.sm * screenSize.spacingMultiplier),
                    _ShimmerBox(
                      width: 120,
                      height: 18,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ],
                ),
                SizedBox(height: AppSpacing.md * screenSize.spacingMultiplier),

                // Main value
                _ShimmerBox(
                  width: 80,
                  height: 32,
                  borderRadius: BorderRadius.circular(4),
                ),
                SizedBox(height: AppSpacing.sm * screenSize.spacingMultiplier),

                // Subtitle/description
                _ShimmerBox(
                  width: 100,
                  height: 14,
                  borderRadius: BorderRadius.circular(4),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

/// Wrapper widget that applies shimmer effect to its child.
class _ShimmerWrapper extends StatelessWidget {
  const _ShimmerWrapper({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Shimmer.fromColors(
      baseColor: isDark ? Colors.grey[800]! : Colors.grey[300]!,
      highlightColor: isDark ? Colors.grey[700]! : Colors.grey[100]!,
      period: AppAnimations.shimmerPeriod,
      child: child,
    );
  }
}

/// Basic shimmer box component.
class _ShimmerBox extends StatelessWidget {
  const _ShimmerBox({
    required this.width,
    required this.height,
    this.borderRadius,
  });

  final double width;
  final double height;
  final BorderRadius? borderRadius;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: borderRadius ?? BorderRadius.circular(4),
      ),
    );
  }
}
