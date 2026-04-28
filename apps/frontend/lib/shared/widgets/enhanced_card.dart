import 'package:flutter/material.dart';
import '../responsive/index.dart';
import '../../core/theme/app_spacing.dart';

/// An enhanced card widget with modern design principles.
/// 
/// This card provides smooth animations, proper elevation, hover effects,
/// and responsive behavior following Material Design 3 principles.
/// 
/// Example usage:
/// ```dart
/// EnhancedCard(
///   child: MenuItemContent(),
///   onTap: () => handleMenuItemTap(),
/// )
/// ```
class EnhancedCard extends StatefulWidget {
  /// Creates an enhanced card widget.
  /// 
  /// Args:
  ///   child: The widget to display inside the card.
  ///   onTap: Callback when the card is tapped (optional).
  ///   elevation: Custom elevation (optional, uses responsive defaults).
  ///   borderRadius: Custom border radius (optional, uses responsive defaults).
  ///   padding: Custom padding (optional, uses responsive defaults).
  ///   margin: Custom margin (optional, uses responsive defaults).
  ///   color: Custom background color (optional).
  ///   shadowColor: Custom shadow color (optional).
  ///   animationDuration: Duration for hover/tap animations.
  ///   key: Optional widget key for identification.
  const EnhancedCard({
    super.key,
    required this.child,
    this.onTap,
    this.elevation,
    this.borderRadius,
    this.padding,
    this.margin,
    this.color,
    this.shadowColor,
    this.animationDuration = const Duration(milliseconds: 200),
  });

  /// The child widget to display inside the card.
  final Widget child;

  /// Callback when the card is tapped.
  final VoidCallback? onTap;

  /// Custom elevation for the card.
  final double? elevation;

  /// Custom border radius for the card.
  final BorderRadius? borderRadius;

  /// Custom padding inside the card.
  final EdgeInsetsGeometry? padding;

  /// Custom margin around the card.
  final EdgeInsetsGeometry? margin;

  /// Custom background color for the card.
  final Color? color;

  /// Custom shadow color for the card.
  final Color? shadowColor;

  /// Duration for hover/tap animations.
  final Duration animationDuration;

  @override
  State<EnhancedCard> createState() => _EnhancedCardState();
}

class _EnhancedCardState extends State<EnhancedCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _elevationAnimation;
  
  bool _isHovered = false;
  bool _isPressed = false;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );
    
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.98,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
    
    _elevationAnimation = Tween<double>(
      begin: 0.0,
      end: 2.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _handleHoverEnter() {
    if (!_isPressed) {
      setState(() => _isHovered = true);
      _animationController.forward();
    }
  }

  void _handleHoverExit() {
    setState(() => _isHovered = false);
    if (!_isPressed) {
      _animationController.reverse();
    }
  }

  void _handleTapDown() {
    setState(() => _isPressed = true);
    _animationController.forward();
  }

  void _handleTapUp() {
    setState(() => _isPressed = false);
    if (!_isHovered) {
      _animationController.reverse();
    }
  }

  void _handleTapCancel() {
    setState(() => _isPressed = false);
    if (!_isHovered) {
      _animationController.reverse();
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = ScreenSize.of(context);
    final theme = Theme.of(context);
    
    // Calculate responsive properties
    final effectiveElevation = widget.elevation ?? _getResponsiveElevation(screenSize);
    final effectiveBorderRadius = widget.borderRadius ?? _getResponsiveBorderRadius(screenSize);
    final effectivePadding = widget.padding ?? _getResponsivePadding(screenSize);
    final effectiveMargin = widget.margin ?? _getResponsiveMargin(screenSize);
    
    return AnimatedBuilder(
      animation: _animationController,
      builder: (context, child) {
        return Container(
          margin: effectiveMargin,
          child: Transform.scale(
            scale: _scaleAnimation.value,
            child: Material(
              elevation: effectiveElevation + _elevationAnimation.value,
              borderRadius: effectiveBorderRadius,
              color: widget.color ?? theme.cardColor,
              shadowColor: widget.shadowColor ?? theme.shadowColor.withOpacity(0.1),
              child: InkWell(
                onTap: widget.onTap,
                onTapDown: widget.onTap != null ? (_) => _handleTapDown() : null,
                onTapUp: widget.onTap != null ? (_) => _handleTapUp() : null,
                onTapCancel: widget.onTap != null ? _handleTapCancel : null,
                onHover: widget.onTap != null ? (hovering) {
                  if (hovering) {
                    _handleHoverEnter();
                  } else {
                    _handleHoverExit();
                  }
                } : null,
                borderRadius: effectiveBorderRadius,
                splashColor: theme.primaryColor.withOpacity(0.1),
                highlightColor: theme.primaryColor.withOpacity(0.05),
                child: Padding(
                  padding: effectivePadding,
                  child: widget.child,
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  /// Gets responsive elevation based on screen size.
  double _getResponsiveElevation(ScreenSize screenSize) {
    return screenSize.responsiveValue(
      mobile: 2.0,
      tablet: 4.0,
      desktop: 6.0,
    );
  }

  /// Gets responsive border radius based on screen size.
  BorderRadius _getResponsiveBorderRadius(ScreenSize screenSize) {
    final radius = screenSize.responsiveValue(
      mobile: 12.0,
      tablet: 16.0,
      desktop: 20.0,
    );
    return BorderRadius.circular(radius);
  }

  /// Gets responsive padding based on screen size.
  EdgeInsetsGeometry _getResponsivePadding(ScreenSize screenSize) {
    final padding = screenSize.responsiveValue(
      mobile: AppPadding.card,
      tablet: AppPadding.section,
      desktop: AppPadding.section * 1.25,
    );
    return EdgeInsets.all(padding);
  }

  /// Gets responsive margin based on screen size.
  EdgeInsetsGeometry _getResponsiveMargin(ScreenSize screenSize) {
    final margin = screenSize.responsiveValue(
      mobile: AppMargin.component,
      tablet: AppMargin.section,
      desktop: AppMargin.page,
    );
    return EdgeInsets.all(margin);
  }
}

/// A specialized enhanced card for menu items.
/// 
/// This card is optimized for displaying menu items with proper
/// image handling, typography, and interactive states.
class EnhancedMenuItemCard extends StatelessWidget {
  /// Creates an enhanced menu item card.
  /// 
  /// Args:
  ///   title: The menu item title.
  ///   description: The menu item description (optional).
  ///   price: The menu item price.
  ///   imageUrl: URL for the menu item image (optional).
  ///   onTap: Callback when the card is tapped.
  ///   onAddToCart: Callback when add to cart is pressed (optional).
  ///   isAvailable: Whether the item is available.
  ///   key: Optional widget key for identification.
  const EnhancedMenuItemCard({
    super.key,
    required this.title,
    this.description,
    required this.price,
    this.imageUrl,
    this.onTap,
    this.onAddToCart,
    this.isAvailable = true,
  });

  /// The menu item title.
  final String title;

  /// The menu item description.
  final String? description;

  /// The menu item price.
  final String price;

  /// URL for the menu item image.
  final String? imageUrl;

  /// Callback when the card is tapped.
  final VoidCallback? onTap;

  /// Callback when add to cart is pressed.
  final VoidCallback? onAddToCart;

  /// Whether the item is available.
  final bool isAvailable;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final screenSize = ScreenSize.of(context);
    
    return EnhancedCard(
      onTap: isAvailable ? onTap : null,
      child: screenSize.responsiveValue(
        mobile: _buildMobileLayout(theme, screenSize),
        tablet: _buildTabletLayout(theme, screenSize),
        desktop: _buildDesktopLayout(theme, screenSize),
      ),
    );
  }

  /// Builds the mobile layout (vertical stack).
  Widget _buildMobileLayout(ThemeData theme, ScreenSize screenSize) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (imageUrl != null) _buildImage(screenSize, aspectRatio: 16 / 9),
        if (imageUrl != null) SizedBox(height: AppSpacing.sm * screenSize.spacingMultiplier),
        _buildContent(theme, screenSize),
        SizedBox(height: AppSpacing.sm * screenSize.spacingMultiplier),
        _buildActions(theme, screenSize),
      ],
    );
  }

  /// Builds the tablet layout (horizontal with image).
  Widget _buildTabletLayout(ThemeData theme, ScreenSize screenSize) {
    return Row(
      children: [
        if (imageUrl != null) ...[
          _buildImage(screenSize, width: 120, height: 120),
          SizedBox(width: AppSpacing.md * screenSize.spacingMultiplier),
        ],
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildContent(theme, screenSize),
              SizedBox(height: AppSpacing.sm * screenSize.spacingMultiplier),
              _buildActions(theme, screenSize),
            ],
          ),
        ),
      ],
    );
  }

  /// Builds the desktop layout (enhanced horizontal).
  Widget _buildDesktopLayout(ThemeData theme, ScreenSize screenSize) {
    return Row(
      children: [
        if (imageUrl != null) ...[
          _buildImage(screenSize, width: 140, height: 140),
          SizedBox(width: AppSpacing.lg * screenSize.spacingMultiplier),
        ],
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildContent(theme, screenSize),
              SizedBox(height: AppSpacing.md * screenSize.spacingMultiplier),
              _buildActions(theme, screenSize),
            ],
          ),
        ),
      ],
    );
  }

  /// Builds the image widget.
  Widget _buildImage(ScreenSize screenSize, {double? width, double? height, double? aspectRatio}) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(8.0),
      child: Container(
        width: width,
        height: height,
        decoration: BoxDecoration(
          color: Colors.grey[200],
          borderRadius: BorderRadius.circular(8.0),
        ),
        child: aspectRatio != null
            ? AspectRatio(
                aspectRatio: aspectRatio,
                child: _buildImageContent(),
              )
            : _buildImageContent(),
      ),
    );
  }

  /// Builds the image content.
  Widget _buildImageContent() {
    if (imageUrl != null) {
      return Image.network(
        imageUrl!,
        fit: BoxFit.cover,
        errorBuilder: (context, error, stackTrace) => _buildImagePlaceholder(),
      );
    }
    return _buildImagePlaceholder();
  }

  /// Builds the image placeholder.
  Widget _buildImagePlaceholder() {
    return Container(
      color: Colors.grey[200],
      child: const Icon(
        Icons.restaurant,
        color: Colors.grey,
        size: 32,
      ),
    );
  }

  /// Builds the content section.
  Widget _buildContent(ThemeData theme, ScreenSize screenSize) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w600,
            color: isAvailable ? null : Colors.grey,
          ),
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        if (description != null) ...[
          SizedBox(height: AppSpacing.xs * screenSize.spacingMultiplier),
          Text(
            description!,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: isAvailable ? Colors.grey[600] : Colors.grey[400],
            ),
            maxLines: 3,
            overflow: TextOverflow.ellipsis,
          ),
        ],
        SizedBox(height: AppSpacing.xs * screenSize.spacingMultiplier),
        Text(
          price,
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: isAvailable ? theme.primaryColor : Colors.grey,
          ),
        ),
      ],
    );
  }

  /// Builds the actions section.
  Widget _buildActions(ThemeData theme, ScreenSize screenSize) {
    if (!isAvailable) {
      return Container(
        padding: EdgeInsets.symmetric(
          horizontal: AppSpacing.sm * screenSize.spacingMultiplier,
          vertical: AppSpacing.xs * screenSize.spacingMultiplier,
        ),
        decoration: BoxDecoration(
          color: Colors.grey[200],
          borderRadius: BorderRadius.circular(4),
        ),
        child: Text(
          'Unavailable',
          style: theme.textTheme.bodySmall?.copyWith(
            color: Colors.grey[600],
            fontWeight: FontWeight.w500,
          ),
        ),
      );
    }

    if (onAddToCart == null) return const SizedBox.shrink();

    return Align(
      alignment: Alignment.centerRight,
      child: ElevatedButton.icon(
        onPressed: onAddToCart,
        icon: const Icon(Icons.add_shopping_cart, size: 18),
        label: const Text('Add'),
        style: ElevatedButton.styleFrom(
          padding: EdgeInsets.symmetric(
            horizontal: AppSpacing.md * screenSize.spacingMultiplier,
            vertical: AppSpacing.xs * screenSize.spacingMultiplier,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
    );
  }
}
