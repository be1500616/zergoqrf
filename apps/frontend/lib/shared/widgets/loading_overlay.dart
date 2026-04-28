import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../core/theme/app_animations.dart';
import '../responsive/screen_size.dart';
import 'enhanced_loading.dart';

/// Professional loading overlay that can be displayed over content.
/// 
/// Provides smooth fade-in/out animations and customizable loading indicators
/// for better user experience during async operations.
class LoadingOverlay extends StatelessWidget {
  /// Creates a loading overlay widget.
  /// 
  /// Args:
  ///   isLoading: Whether to show the loading overlay.
  ///   child: The child widget to overlay.
  ///   loadingWidget: Custom loading widget to display.
  ///   backgroundColor: Background color of the overlay.
  ///   opacity: Opacity of the overlay background.
  ///   message: Optional loading message to display.
  ///   dismissible: Whether the overlay can be dismissed by tapping.
  ///   onDismiss: Callback when overlay is dismissed (if dismissible).
  const LoadingOverlay({
    super.key,
    required this.isLoading,
    required this.child,
    this.loadingWidget,
    this.backgroundColor,
    this.opacity = 0.8,
    this.message,
    this.dismissible = false,
    this.onDismiss,
  });

  /// Whether to show the loading overlay.
  final bool isLoading;

  /// The child widget to overlay.
  final Widget child;

  /// Custom loading widget to display.
  final Widget? loadingWidget;

  /// Background color of the overlay.
  final Color? backgroundColor;

  /// Opacity of the overlay background.
  final double opacity;

  /// Optional loading message to display.
  final String? message;

  /// Whether the overlay can be dismissed by tapping.
  final bool dismissible;

  /// Callback when overlay is dismissed.
  final VoidCallback? onDismiss;

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        child,
        if (isLoading)
          _buildOverlay(context),
      ],
    );
  }

  Widget _buildOverlay(BuildContext context) {
    final theme = Theme.of(context);
    final screenSize = ScreenSize.of(context);
    
    final overlay = Container(
      color: (backgroundColor ?? Colors.black).withOpacity(opacity),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Loading indicator
            loadingWidget ?? const EnhancedLoading(
              type: LoadingType.spinner,
              size: LoadingSize.large,
            ),
            
            // Loading message
            if (message != null) ...[
              SizedBox(height: 24 * screenSize.spacingMultiplier),
              Container(
                padding: EdgeInsets.symmetric(
                  horizontal: 24 * screenSize.spacingMultiplier,
                  vertical: 12 * screenSize.spacingMultiplier,
                ),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surface.withOpacity(0.9),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  message!,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurface,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ],
          ],
        ),
      ),
    );

    // Add tap to dismiss functionality if enabled
    final overlayWidget = dismissible && onDismiss != null
        ? GestureDetector(
            onTap: onDismiss,
            child: overlay,
          )
        : overlay;

    // Add smooth fade animation
    return overlayWidget
        .animate()
        .fadeIn(
          duration: AppAnimations.fast,
          curve: AppAnimations.decelerate,
        )
        .scaleXY(
          begin: 0.95,
          end: 1.0,
          duration: AppAnimations.fast,
          curve: AppAnimations.decelerate,
        );
  }
}

/// Specialized loading overlay for full-screen loading states.
/// 
/// Provides a more prominent loading experience for major operations
/// like app initialization or data synchronization.
class FullScreenLoadingOverlay extends StatelessWidget {
  /// Creates a full-screen loading overlay.
  const FullScreenLoadingOverlay({
    super.key,
    required this.isLoading,
    required this.child,
    this.title = 'Loading...',
    this.subtitle,
    this.loadingType = LoadingType.spinner,
    this.showProgress = false,
    this.progress = 0.0,
  });

  /// Whether to show the loading overlay.
  final bool isLoading;

  /// The child widget to overlay.
  final Widget child;

  /// Main loading title.
  final String title;

  /// Optional subtitle for additional context.
  final String? subtitle;

  /// Type of loading animation to display.
  final LoadingType loadingType;

  /// Whether to show a progress indicator.
  final bool showProgress;

  /// Progress value (0.0 to 1.0) if showing progress.
  final double progress;

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        child,
        if (isLoading)
          _buildFullScreenOverlay(context),
      ],
    );
  }

  Widget _buildFullScreenOverlay(BuildContext context) {
    final theme = Theme.of(context);
    final screenSize = ScreenSize.of(context);

    return Container(
      color: theme.colorScheme.surface,
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Loading animation
            EnhancedLoading(
              type: loadingType,
              size: LoadingSize.large,
            ),
            
            SizedBox(height: 32 * screenSize.spacingMultiplier),
            
            // Title
            Text(
              title,
              style: theme.textTheme.headlineSmall?.copyWith(
                color: theme.colorScheme.onSurface,
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
            
            // Subtitle
            if (subtitle != null) ...[
              SizedBox(height: 8 * screenSize.spacingMultiplier),
              Text(
                subtitle!,
                style: theme.textTheme.bodyLarge?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                textAlign: TextAlign.center,
              ),
            ],
            
            // Progress indicator
            if (showProgress) ...[
              SizedBox(height: 24 * screenSize.spacingMultiplier),
              SizedBox(
                width: screenSize.responsiveValue(
                  mobile: 200.0,
                  tablet: 250.0,
                  desktop: 300.0,
                ),
                child: LinearProgressIndicator(
                  value: progress,
                  backgroundColor: theme.colorScheme.surfaceContainerHighest,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    theme.primaryColor,
                  ),
                ),
              ),
              SizedBox(height: 8 * screenSize.spacingMultiplier),
              Text(
                '${(progress * 100).toInt()}%',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ],
        ),
      ),
    )
        .animate()
        .fadeIn(
          duration: AppAnimations.normal,
          curve: AppAnimations.decelerate,
        );
  }
}

/// Inline loading widget for smaller sections.
/// 
/// Provides a compact loading state for individual components
/// or sections within a larger interface.
class InlineLoading extends StatelessWidget {
  /// Creates an inline loading widget.
  const InlineLoading({
    super.key,
    this.message,
    this.type = LoadingType.dots,
    this.size = LoadingSize.small,
    this.color,
    this.alignment = MainAxisAlignment.center,
  });

  /// Optional loading message.
  final String? message;

  /// Type of loading animation.
  final LoadingType type;

  /// Size of the loading indicator.
  final LoadingSize size;

  /// Color of the loading indicator.
  final Color? color;

  /// Alignment of the loading content.
  final MainAxisAlignment alignment;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final screenSize = ScreenSize.of(context);

    return Row(
      mainAxisAlignment: alignment,
      mainAxisSize: MainAxisSize.min,
      children: [
        EnhancedLoading(
          type: type,
          size: size,
          color: color,
        ),
        if (message != null) ...[
          SizedBox(width: 12 * screenSize.spacingMultiplier),
          Text(
            message!,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ],
    )
        .animate()
        .fadeIn(
          duration: AppAnimations.fast,
          curve: AppAnimations.decelerate,
        );
  }
}
