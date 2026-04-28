import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:shimmer/shimmer.dart';
import 'package:lottie/lottie.dart';

import '../../core/theme/app_animations.dart';
import '../../core/theme/app_spacing.dart';
import '../responsive/index.dart';

/// An enhanced loading widget with modern animations and responsive design.
///
/// This loading widget provides smooth animations, proper responsive
/// behavior, and follows Material Design 3 principles.
///
/// Example usage:
/// ```dart
/// EnhancedLoading(
///   message: 'Loading menu items...',
///   type: LoadingType.shimmer,
/// )
/// ```
class EnhancedLoading extends StatefulWidget {
  /// Creates an enhanced loading widget.
  ///
  /// Args:
  ///   message: Loading message to display (optional).
  ///   type: Type of loading animation.
  ///   size: Size of the loading indicator.
  ///   color: Color of the loading indicator (optional).
  ///   key: Optional widget key for identification.
  const EnhancedLoading({
    super.key,
    this.message,
    this.type = LoadingType.circular,
    this.size = LoadingSize.medium,
    this.color,
  });

  /// Loading message to display.
  final String? message;

  /// Type of loading animation.
  final LoadingType type;

  /// Size of the loading indicator.
  final LoadingSize size;

  /// Color of the loading indicator.
  final Color? color;

  @override
  State<EnhancedLoading> createState() => _EnhancedLoadingState();
}

class _EnhancedLoadingState extends State<EnhancedLoading>
    with TickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _animation = CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    );

    _controller.repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final screenSize = ScreenSize.of(context);

    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          _buildLoadingIndicator(theme, screenSize),
          if (widget.message != null) ...[
            SizedBox(height: AppSpacing.md * screenSize.spacingMultiplier),
            Text(
              widget.message!,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurface.withOpacity(0.7),
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ],
      ),
    );
  }

  /// Builds the loading indicator based on type.
  Widget _buildLoadingIndicator(ThemeData theme, ScreenSize screenSize) {
    final size = _getIndicatorSize(screenSize);
    final color = widget.color ?? theme.primaryColor;

    switch (widget.type) {
      case LoadingType.circular:
        return SizedBox(
          width: size,
          height: size,
          child: CircularProgressIndicator(
            strokeWidth: size / 10,
            color: color,
          ),
        );

      case LoadingType.dots:
        return _buildDotsIndicator(color, size);

      case LoadingType.pulse:
        return _buildPulseIndicator(color, size);

      case LoadingType.shimmer:
        return _buildShimmerIndicator(theme, screenSize);

      case LoadingType.spinner:
        return SpinKitFadingCircle(
          color: color,
          size: size,
          duration: AppAnimations.spinnerRotation,
        );

      case LoadingType.wave:
        return SpinKitWave(
          color: color,
          size: size * 0.8,
          duration: AppAnimations.normal,
        );

      case LoadingType.threeBounce:
        return SpinKitThreeBounce(
          color: color,
          size: size * 0.6,
          duration: AppAnimations.normal,
        );

      case LoadingType.lottie:
        // Note: You would need to add actual Lottie files to assets
        return SizedBox(
          width: size,
          height: size,
          child: CircularProgressIndicator(color: color), // Fallback
        );
    }
  }

  /// Builds a dots loading indicator.
  Widget _buildDotsIndicator(Color color, double size) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(3, (index) {
            final delay = index * 0.2;
            final animationValue = (_animation.value + delay) % 1.0;
            final scale = 0.5 + (0.5 * (1 - (animationValue - 0.5).abs() * 2));

            return Container(
              margin: EdgeInsets.symmetric(horizontal: size / 8),
              child: Transform.scale(
                scale: scale,
                child: Container(
                  width: size / 4,
                  height: size / 4,
                  decoration: BoxDecoration(
                    color: color,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            );
          }),
        );
      },
    );
  }

  /// Builds a pulse loading indicator.
  Widget _buildPulseIndicator(Color color, double size) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        final scale = 0.8 + (0.4 * _animation.value);
        final opacity = 1.0 - _animation.value;

        return Transform.scale(
          scale: scale,
          child: Container(
            width: size,
            height: size,
            decoration: BoxDecoration(
              color: color.withOpacity(opacity),
              shape: BoxShape.circle,
            ),
          ),
        );
      },
    );
  }

  /// Builds a shimmer loading indicator.
  Widget _buildShimmerIndicator(ThemeData theme, ScreenSize screenSize) {
    return Column(
      children: List.generate(3, (index) {
        return Container(
          margin: EdgeInsets.only(
            bottom: AppSpacing.sm * screenSize.spacingMultiplier,
          ),
          child: _ShimmerBox(
            width: screenSize.responsiveValue(
              mobile: 200.0,
              tablet: 300.0,
              desktop: 400.0,
            ),
            height: screenSize.responsiveValue(
              mobile: 16.0,
              tablet: 20.0,
              desktop: 24.0,
            ),
          ),
        );
      }),
    );
  }

  /// Gets the indicator size based on loading size and screen size.
  double _getIndicatorSize(ScreenSize screenSize) {
    final baseSize = switch (widget.size) {
      LoadingSize.small => 24.0,
      LoadingSize.medium => 40.0,
      LoadingSize.large => 56.0,
    };

    return baseSize * screenSize.spacingMultiplier;
  }
}

/// A shimmer box widget for skeleton loading.
class _ShimmerBox extends StatefulWidget {
  const _ShimmerBox({
    required this.width,
    required this.height,
  });

  final double width;
  final double height;

  @override
  State<_ShimmerBox> createState() => _ShimmerBoxState();
}

class _ShimmerBoxState extends State<_ShimmerBox>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _animation = Tween<double>(
      begin: -1.0,
      end: 2.0,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));

    _controller.repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Container(
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            gradient: LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              stops: [
                (_animation.value - 0.3).clamp(0.0, 1.0),
                _animation.value.clamp(0.0, 1.0),
                (_animation.value + 0.3).clamp(0.0, 1.0),
              ],
              colors: [
                theme.colorScheme.surfaceContainerHighest,
                theme.colorScheme.surfaceContainerHighest.withOpacity(0.5),
                theme.colorScheme.surfaceContainerHighest,
              ],
            ),
          ),
        );
      },
    );
  }
}

/// Types of loading animations.
enum LoadingType {
  /// Circular progress indicator.
  circular,

  /// Animated dots.
  dots,

  /// Pulsing circle.
  pulse,

  /// Shimmer skeleton.
  shimmer,

  /// SpinKit fading circle.
  spinner,

  /// SpinKit wave animation.
  wave,

  /// SpinKit three bounce.
  threeBounce,

  /// Lottie animation.
  lottie,
}

/// Sizes for loading indicators.
enum LoadingSize {
  /// Small loading indicator.
  small,

  /// Medium loading indicator.
  medium,

  /// Large loading indicator.
  large,
}

/// A specialized loading widget for menu items.
///
/// This widget provides skeleton loading specifically designed
/// for menu item cards with proper responsive behavior.
class EnhancedMenuItemLoading extends StatelessWidget {
  /// Creates an enhanced menu item loading widget.
  ///
  /// Args:
  ///   itemCount: Number of skeleton items to show.
  ///   key: Optional widget key for identification.
  const EnhancedMenuItemLoading({
    super.key,
    this.itemCount = 6,
  });

  /// Number of skeleton items to show.
  final int itemCount;

  @override
  Widget build(BuildContext context) {
    final screenSize = ScreenSize.of(context);

    return Column(
      children: List.generate(itemCount, (index) {
        return Container(
          margin: EdgeInsets.only(
            bottom: AppSpacing.md * screenSize.spacingMultiplier,
          ),
          child: _MenuItemSkeleton(),
        );
      }),
    );
  }
}

/// A skeleton widget for menu items.
class _MenuItemSkeleton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final screenSize = ScreenSize.of(context);

    return Container(
      padding: EdgeInsets.all(AppSpacing.md * screenSize.spacingMultiplier),
      decoration: BoxDecoration(
        color: theme.cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: theme.colorScheme.outline.withOpacity(0.1),
        ),
      ),
      child: screenSize.responsiveValue(
        mobile: _buildMobileSkeleton(screenSize),
        tablet: _buildTabletSkeleton(screenSize),
        desktop: _buildDesktopSkeleton(screenSize),
      ),
    );
  }

  /// Builds mobile skeleton layout.
  Widget _buildMobileSkeleton(ScreenSize screenSize) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _ShimmerBox(width: double.infinity, height: 120),
        SizedBox(height: AppSpacing.sm * screenSize.spacingMultiplier),
        const _ShimmerBox(width: 200, height: 20),
        SizedBox(height: AppSpacing.xs * screenSize.spacingMultiplier),
        const _ShimmerBox(width: 150, height: 16),
        SizedBox(height: AppSpacing.xs * screenSize.spacingMultiplier),
        const _ShimmerBox(width: 80, height: 18),
      ],
    );
  }

  /// Builds tablet skeleton layout.
  Widget _buildTabletSkeleton(ScreenSize screenSize) {
    return Row(
      children: [
        const _ShimmerBox(width: 120, height: 120),
        SizedBox(width: AppSpacing.md * screenSize.spacingMultiplier),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const _ShimmerBox(width: double.infinity, height: 20),
              SizedBox(height: AppSpacing.xs * screenSize.spacingMultiplier),
              const _ShimmerBox(width: 200, height: 16),
              SizedBox(height: AppSpacing.xs * screenSize.spacingMultiplier),
              const _ShimmerBox(width: 80, height: 18),
            ],
          ),
        ),
      ],
    );
  }

  /// Builds desktop skeleton layout.
  Widget _buildDesktopSkeleton(ScreenSize screenSize) {
    return Row(
      children: [
        const _ShimmerBox(width: 140, height: 140),
        SizedBox(width: AppSpacing.lg * screenSize.spacingMultiplier),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const _ShimmerBox(width: double.infinity, height: 24),
              SizedBox(height: AppSpacing.sm * screenSize.spacingMultiplier),
              const _ShimmerBox(width: 250, height: 16),
              SizedBox(height: AppSpacing.sm * screenSize.spacingMultiplier),
              const _ShimmerBox(width: 100, height: 20),
            ],
          ),
        ),
      ],
    );
  }
}
