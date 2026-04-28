import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../core/theme/app_spacing.dart';
import '../../core/theme/app_animations.dart';
import '../responsive/index.dart';

/// An enhanced floating action button with smooth animations and micro-interactions.
///
/// This FAB provides smooth hover effects, press animations, morphing capabilities,
/// and follows Material Design 3 principles with proper responsive behavior.
///
/// Example usage:
/// ```dart
/// EnhancedFAB(
///   icon: Icons.add_shopping_cart,
///   label: 'Add to Cart',
///   onPressed: () => handleAddToCart(),
///   badgeCount: cartItemCount,
/// )
/// ```
class EnhancedFAB extends StatefulWidget {
  /// Creates an enhanced floating action button.
  ///
  /// Args:
  ///   icon: The icon to display.
  ///   onPressed: Callback when the FAB is pressed.
  ///   label: Optional label text for extended FAB.
  ///   badgeCount: Optional badge count to display.
  ///   isExtended: Whether to show as extended FAB with label.
  ///   backgroundColor: Custom background color (optional).
  ///   foregroundColor: Custom foreground color (optional).
  ///   heroTag: Hero tag for page transitions.
  ///   key: Optional widget key for identification.
  const EnhancedFAB({
    super.key,
    required this.icon,
    required this.onPressed,
    this.label,
    this.badgeCount,
    this.isExtended = false,
    this.backgroundColor,
    this.foregroundColor,
    this.heroTag,
  });

  /// The icon to display.
  final IconData icon;

  /// Callback when the FAB is pressed.
  final VoidCallback? onPressed;

  /// Optional label text for extended FAB.
  final String? label;

  /// Optional badge count to display.
  final int? badgeCount;

  /// Whether to show as extended FAB with label.
  final bool isExtended;

  /// Custom background color.
  final Color? backgroundColor;

  /// Custom foreground color.
  final Color? foregroundColor;

  /// Hero tag for page transitions.
  final Object? heroTag;

  @override
  State<EnhancedFAB> createState() => _EnhancedFABState();
}

class _EnhancedFABState extends State<EnhancedFAB>
    with TickerProviderStateMixin {
  late AnimationController _scaleController;
  late AnimationController _rotationController;
  late AnimationController _pulseController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _rotationAnimation;
  late Animation<double> _pulseAnimation;

  bool _isHovered = false;
  bool _isPressed = false;

  @override
  void initState() {
    super.initState();

    _scaleController = AnimationController(
      duration: const Duration(milliseconds: 150),
      vsync: this,
    );

    _rotationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.9,
    ).animate(CurvedAnimation(
      parent: _scaleController,
      curve: Curves.easeInOut,
    ));

    _rotationAnimation = Tween<double>(
      begin: 0.0,
      end: 0.25,
    ).animate(CurvedAnimation(
      parent: _rotationController,
      curve: Curves.elasticOut,
    ));

    _pulseAnimation = Tween<double>(
      begin: 1.0,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));

    // Start pulse animation if there's a badge
    if (widget.badgeCount != null && widget.badgeCount! > 0) {
      _pulseController.repeat(reverse: true);
    }
  }

  @override
  void didUpdateWidget(EnhancedFAB oldWidget) {
    super.didUpdateWidget(oldWidget);

    // Handle badge count changes
    if (widget.badgeCount != oldWidget.badgeCount) {
      if (widget.badgeCount != null && widget.badgeCount! > 0) {
        _pulseController.repeat(reverse: true);
      } else {
        _pulseController.stop();
        _pulseController.reset();
      }
    }
  }

  @override
  void dispose() {
    _scaleController.dispose();
    _rotationController.dispose();
    _pulseController.dispose();
    super.dispose();
  }

  void _handleTapDown() {
    setState(() => _isPressed = true);
    _scaleController.forward();
    _rotationController.forward();
  }

  void _handleTapUp() {
    setState(() => _isPressed = false);
    _scaleController.reverse();
    _rotationController.reverse();
  }

  void _handleTapCancel() {
    setState(() => _isPressed = false);
    _scaleController.reverse();
    _rotationController.reverse();
  }

  void _handleHoverEnter() {
    setState(() => _isHovered = true);
  }

  void _handleHoverExit() {
    setState(() => _isHovered = false);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final screenSize = ScreenSize.of(context);

    return AnimatedBuilder(
      animation: Listenable.merge([
        _scaleController,
        _rotationController,
        _pulseController,
      ]),
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: Stack(
            clipBehavior: Clip.none,
            children: [
              // Pulse effect for badge
              if (widget.badgeCount != null && widget.badgeCount! > 0)
                Transform.scale(
                  scale: _pulseAnimation.value,
                  child: Container(
                    width: _getFABSize(screenSize),
                    height: _getFABSize(screenSize),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: (widget.backgroundColor ?? theme.primaryColor)
                          .withOpacity(0.3),
                    ),
                  ),
                ),

              // Main FAB
              Transform.rotate(
                angle: _rotationAnimation.value * 2 * 3.14159,
                child: widget.isExtended && widget.label != null
                    ? _buildExtendedFAB(theme, screenSize)
                    : _buildRegularFAB(theme, screenSize),
              ),

              // Badge
              if (widget.badgeCount != null && widget.badgeCount! > 0)
                _buildBadge(theme, screenSize),
            ],
          ),
        );
      },
    );
  }

  /// Builds the regular circular FAB.
  Widget _buildRegularFAB(ThemeData theme, ScreenSize screenSize) {
    return Container(
      width: _getFABSize(screenSize),
      height: _getFABSize(screenSize),
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: widget.backgroundColor ?? theme.primaryColor,
        boxShadow: _isHovered
            ? [
                BoxShadow(
                  color: (widget.backgroundColor ?? theme.primaryColor)
                      .withOpacity(0.4),
                  blurRadius: 12,
                  offset: const Offset(0, 6),
                ),
              ]
            : [
                BoxShadow(
                  color: Colors.black.withOpacity(0.2),
                  blurRadius: 8,
                  offset: const Offset(0, 4),
                ),
              ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: widget.onPressed,
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
          customBorder: const CircleBorder(),
          child: Center(
            child: Icon(
              widget.icon,
              size: _getIconSize(screenSize),
              color: widget.foregroundColor ?? theme.colorScheme.onPrimary,
            ),
          ),
        ),
      ),
    );
  }

  /// Builds the extended FAB with label.
  Widget _buildExtendedFAB(ThemeData theme, ScreenSize screenSize) {
    return Container(
      height: _getFABSize(screenSize),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(_getFABSize(screenSize) / 2),
        color: widget.backgroundColor ?? theme.primaryColor,
        boxShadow: _isHovered
            ? [
                BoxShadow(
                  color: (widget.backgroundColor ?? theme.primaryColor)
                      .withOpacity(0.4),
                  blurRadius: 12,
                  offset: const Offset(0, 6),
                ),
              ]
            : [
                BoxShadow(
                  color: Colors.black.withOpacity(0.2),
                  blurRadius: 8,
                  offset: const Offset(0, 4),
                ),
              ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: widget.onPressed,
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
          borderRadius: BorderRadius.circular(_getFABSize(screenSize) / 2),
          child: Padding(
            padding: EdgeInsets.symmetric(
              horizontal: AppSpacing.lg * screenSize.spacingMultiplier,
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  widget.icon,
                  size: _getIconSize(screenSize),
                  color: widget.foregroundColor ?? theme.colorScheme.onPrimary,
                ),
                SizedBox(width: AppSpacing.sm * screenSize.spacingMultiplier),
                Text(
                  widget.label!,
                  style: theme.textTheme.labelLarge?.copyWith(
                    color:
                        widget.foregroundColor ?? theme.colorScheme.onPrimary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// Builds the badge for displaying count.
  Widget _buildBadge(ThemeData theme, ScreenSize screenSize) {
    final badgeSize = screenSize.responsiveValue(
      mobile: 20.0,
      tablet: 24.0,
      desktop: 24.0,
    );

    return Positioned(
      top: -4,
      right: widget.isExtended ? 8 : -4,
      child: Container(
        width: badgeSize,
        height: badgeSize,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: theme.colorScheme.error,
          border: Border.all(
            color: theme.colorScheme.surface,
            width: 2,
          ),
        ),
        child: Center(
          child: Text(
            widget.badgeCount! > 99 ? '99+' : widget.badgeCount.toString(),
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.onError,
              fontWeight: FontWeight.bold,
              fontSize: screenSize.responsiveValue(
                mobile: 10.0,
                tablet: 11.0,
                desktop: 12.0,
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// Gets responsive FAB size based on screen size.
  double _getFABSize(ScreenSize screenSize) {
    return screenSize.responsiveValue(
      mobile: 56.0,
      tablet: 64.0,
      desktop: 64.0,
    );
  }

  /// Gets responsive icon size based on screen size.
  double _getIconSize(ScreenSize screenSize) {
    return screenSize.responsiveValue(
      mobile: 24.0,
      tablet: 28.0,
      desktop: 28.0,
    );
  }
}
