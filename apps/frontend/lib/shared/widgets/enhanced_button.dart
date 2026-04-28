import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../core/theme/app_spacing.dart';
import '../../core/theme/app_animations.dart';
import '../responsive/index.dart';

/// An enhanced button with smooth animations and micro-interactions.
///
/// This button provides smooth hover effects, press animations, loading states,
/// and follows Material Design 3 principles with proper responsive behavior.
///
/// Example usage:
/// ```dart
/// EnhancedButton(
///   text: 'Add to Cart',
///   onPressed: () => handleAddToCart(),
///   icon: Icons.add_shopping_cart,
///   style: EnhancedButtonStyle.primary,
/// )
/// ```
class EnhancedButton extends StatefulWidget {
  /// Creates an enhanced button widget.
  ///
  /// Args:
  ///   text: The button text.
  ///   onPressed: Callback when the button is pressed.
  ///   icon: Optional icon to display (optional).
  ///   style: Button style variant.
  ///   isLoading: Whether to show loading state.
  ///   isEnabled: Whether the button is enabled.
  ///   width: Custom width (optional, defaults to fit content).
  ///   height: Custom height (optional, uses responsive defaults).
  ///   key: Optional widget key for identification.
  const EnhancedButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.icon,
    this.style = EnhancedButtonStyle.primary,
    this.isLoading = false,
    this.isEnabled = true,
    this.width,
    this.height,
  });

  /// The button text.
  final String text;

  /// Callback when the button is pressed.
  final VoidCallback? onPressed;

  /// Optional icon to display.
  final IconData? icon;

  /// Button style variant.
  final EnhancedButtonStyle style;

  /// Whether to show loading state.
  final bool isLoading;

  /// Whether the button is enabled.
  final bool isEnabled;

  /// Custom width.
  final double? width;

  /// Custom height.
  final double? height;

  @override
  State<EnhancedButton> createState() => _EnhancedButtonState();
}

class _EnhancedButtonState extends State<EnhancedButton>
    with TickerProviderStateMixin {
  late AnimationController _scaleController;
  late AnimationController _shimmerController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _shimmerAnimation;

  bool _isHovered = false;
  bool _isPressed = false;

  @override
  void initState() {
    super.initState();

    _scaleController = AnimationController(
      duration: const Duration(milliseconds: 150),
      vsync: this,
    );

    _shimmerController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.95,
    ).animate(CurvedAnimation(
      parent: _scaleController,
      curve: Curves.easeInOut,
    ));

    _shimmerAnimation = Tween<double>(
      begin: -1.0,
      end: 2.0,
    ).animate(CurvedAnimation(
      parent: _shimmerController,
      curve: Curves.easeInOut,
    ));

    if (widget.isLoading) {
      _shimmerController.repeat();
    }
  }

  @override
  void didUpdateWidget(EnhancedButton oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isLoading != oldWidget.isLoading) {
      if (widget.isLoading) {
        _shimmerController.repeat();
      } else {
        _shimmerController.stop();
      }
    }
  }

  @override
  void dispose() {
    _scaleController.dispose();
    _shimmerController.dispose();
    super.dispose();
  }

  void _handleTapDown() {
    if (_isEnabled) {
      setState(() => _isPressed = true);
      _scaleController.forward();
    }
  }

  void _handleTapUp() {
    setState(() => _isPressed = false);
    _scaleController.reverse();
  }

  void _handleTapCancel() {
    setState(() => _isPressed = false);
    _scaleController.reverse();
  }

  void _handleHoverEnter() {
    if (_isEnabled) {
      setState(() => _isHovered = true);
    }
  }

  void _handleHoverExit() {
    setState(() => _isHovered = false);
  }

  bool get _isEnabled =>
      widget.isEnabled && !widget.isLoading && widget.onPressed != null;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final screenSize = ScreenSize.of(context);

    final buttonHeight = widget.height ?? _getResponsiveHeight(screenSize);
    final buttonWidth = widget.width;

    return AnimatedBuilder(
      animation: Listenable.merge([_scaleController, _shimmerController]),
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: Container(
            width: buttonWidth,
            height: buttonHeight,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(_getBorderRadius(screenSize)),
              boxShadow: _isEnabled && (_isHovered || _isPressed)
                  ? [
                      BoxShadow(
                        color: _getButtonColor(theme).withOpacity(0.3),
                        blurRadius: 8,
                        offset: const Offset(0, 4),
                      ),
                    ]
                  : null,
            ),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: _isEnabled ? widget.onPressed : null,
                onTapDown: (_) => _handleTapDown(),
                onTapUp: (_) => _handleTapUp(),
                onTapCancel: _handleTapCancel,
                onHover: (hovering) {
                  if (hovering) {
                    _handleHoverEnter();
                  } else {
                    _handleHoverExit();
                  }
                },
                borderRadius:
                    BorderRadius.circular(_getBorderRadius(screenSize)),
                child: Container(
                  decoration: BoxDecoration(
                    color: _getButtonColor(theme),
                    borderRadius:
                        BorderRadius.circular(_getBorderRadius(screenSize)),
                    border: widget.style == EnhancedButtonStyle.outlined
                        ? Border.all(
                            color: _getBorderColor(theme),
                            width: 1.5,
                          )
                        : null,
                  ),
                  child: Stack(
                    children: [
                      if (widget.isLoading)
                        _buildShimmerOverlay(theme, screenSize),
                      _buildButtonContent(theme, screenSize),
                    ],
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  /// Builds the shimmer overlay for loading state.
  Widget _buildShimmerOverlay(ThemeData theme, ScreenSize screenSize) {
    return Positioned.fill(
      child: ClipRRect(
        borderRadius: BorderRadius.circular(_getBorderRadius(screenSize)),
        child: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              stops: [
                (_shimmerAnimation.value - 0.3).clamp(0.0, 1.0),
                _shimmerAnimation.value.clamp(0.0, 1.0),
                (_shimmerAnimation.value + 0.3).clamp(0.0, 1.0),
              ],
              colors: [
                Colors.transparent,
                Colors.white.withOpacity(0.2),
                Colors.transparent,
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// Builds the button content (text and icon).
  Widget _buildButtonContent(ThemeData theme, ScreenSize screenSize) {
    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: _getHorizontalPadding(screenSize),
        vertical: _getVerticalPadding(screenSize),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        mainAxisSize: MainAxisSize.min,
        children: [
          if (widget.isLoading) ...[
            SizedBox(
              width: _getIconSize(screenSize),
              height: _getIconSize(screenSize),
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(_getTextColor(theme)),
              ),
            ),
            SizedBox(width: AppSpacing.xs * screenSize.spacingMultiplier),
          ] else if (widget.icon != null) ...[
            Icon(
              widget.icon,
              size: _getIconSize(screenSize),
              color: _getTextColor(theme),
            ),
            SizedBox(width: AppSpacing.xs * screenSize.spacingMultiplier),
          ],
          Text(
            widget.isLoading ? 'Loading...' : widget.text,
            style: _getTextStyle(theme, screenSize),
          ),
        ],
      ),
    );
  }

  /// Gets the button background color based on style and state.
  Color _getButtonColor(ThemeData theme) {
    if (!_isEnabled) {
      return theme.colorScheme.onSurface.withOpacity(0.12);
    }

    switch (widget.style) {
      case EnhancedButtonStyle.primary:
        return _isHovered
            ? theme.primaryColor.withOpacity(0.9)
            : theme.primaryColor;
      case EnhancedButtonStyle.secondary:
        return _isHovered
            ? theme.colorScheme.secondary.withOpacity(0.9)
            : theme.colorScheme.secondary;
      case EnhancedButtonStyle.outlined:
        return _isHovered
            ? theme.primaryColor.withOpacity(0.1)
            : Colors.transparent;
      case EnhancedButtonStyle.text:
        return _isHovered
            ? theme.primaryColor.withOpacity(0.1)
            : Colors.transparent;
    }
  }

  /// Gets the border color for outlined buttons.
  Color _getBorderColor(ThemeData theme) {
    if (!_isEnabled) {
      return theme.colorScheme.onSurface.withOpacity(0.12);
    }
    return theme.primaryColor;
  }

  /// Gets the text color based on style and state.
  Color _getTextColor(ThemeData theme) {
    if (!_isEnabled) {
      return theme.colorScheme.onSurface.withOpacity(0.38);
    }

    switch (widget.style) {
      case EnhancedButtonStyle.primary:
        return theme.colorScheme.onPrimary;
      case EnhancedButtonStyle.secondary:
        return theme.colorScheme.onSecondary;
      case EnhancedButtonStyle.outlined:
      case EnhancedButtonStyle.text:
        return theme.primaryColor;
    }
  }

  /// Gets the text style based on screen size.
  TextStyle _getTextStyle(ThemeData theme, ScreenSize screenSize) {
    final baseStyle = theme.textTheme.labelLarge ?? const TextStyle();
    final fontSize = screenSize.responsiveValue(
      mobile: 14.0,
      tablet: 16.0,
      desktop: 16.0,
    );

    return baseStyle.copyWith(
      fontSize: fontSize,
      fontWeight: FontWeight.w600,
      color: _getTextColor(theme),
    );
  }

  /// Gets responsive height based on screen size.
  double _getResponsiveHeight(ScreenSize screenSize) {
    return screenSize.responsiveValue(
      mobile: 44.0, // Minimum touch target
      tablet: 48.0,
      desktop: 52.0,
    );
  }

  /// Gets responsive border radius.
  double _getBorderRadius(ScreenSize screenSize) {
    return screenSize.responsiveValue(
      mobile: 8.0,
      tablet: 12.0,
      desktop: 12.0,
    );
  }

  /// Gets responsive horizontal padding.
  double _getHorizontalPadding(ScreenSize screenSize) {
    return screenSize.responsiveValue(
      mobile: AppSpacing.md,
      tablet: AppSpacing.lg,
      desktop: AppSpacing.xl,
    );
  }

  /// Gets responsive vertical padding.
  double _getVerticalPadding(ScreenSize screenSize) {
    return screenSize.responsiveValue(
      mobile: AppSpacing.sm,
      tablet: AppSpacing.md,
      desktop: AppSpacing.md,
    );
  }

  /// Gets responsive icon size.
  double _getIconSize(ScreenSize screenSize) {
    return screenSize.responsiveValue(
      mobile: 18.0,
      tablet: 20.0,
      desktop: 22.0,
    );
  }
}

/// Button style variants.
enum EnhancedButtonStyle {
  /// Primary filled button.
  primary,

  /// Secondary filled button.
  secondary,

  /// Outlined button.
  outlined,

  /// Text button.
  text,
}
