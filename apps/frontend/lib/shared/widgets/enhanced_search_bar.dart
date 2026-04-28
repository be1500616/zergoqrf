import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../core/theme/app_spacing.dart';
import '../../core/theme/app_animations.dart';
import '../responsive/index.dart';

/// An enhanced search bar with modern design and smooth animations.
///
/// This search bar provides smooth focus transitions, proper responsive
/// behavior, and follows Material Design 3 principles.
///
/// Example usage:
/// ```dart
/// EnhancedSearchBar(
///   hintText: 'Search menu items...',
///   onSearch: (query) => handleSearch(query),
///   onClear: () => handleClear(),
/// )
/// ```
class EnhancedSearchBar extends StatefulWidget {
  /// Creates an enhanced search bar widget.
  ///
  /// Args:
  ///   hintText: Placeholder text for the search field.
  ///   onSearch: Callback when search query changes.
  ///   onClear: Callback when clear button is pressed.
  ///   initialValue: Initial value for the search field.
  ///   enabled: Whether the search bar is enabled.
  ///   autofocus: Whether to autofocus the search field.
  ///   key: Optional widget key for identification.
  const EnhancedSearchBar({
    super.key,
    this.hintText = 'Search...',
    this.onSearch,
    this.onClear,
    this.initialValue,
    this.enabled = true,
    this.autofocus = false,
  });

  /// Placeholder text for the search field.
  final String hintText;

  /// Callback when search query changes.
  final ValueChanged<String>? onSearch;

  /// Callback when clear button is pressed.
  final VoidCallback? onClear;

  /// Initial value for the search field.
  final String? initialValue;

  /// Whether the search bar is enabled.
  final bool enabled;

  /// Whether to autofocus the search field.
  final bool autofocus;

  @override
  State<EnhancedSearchBar> createState() => _EnhancedSearchBarState();
}

class _EnhancedSearchBarState extends State<EnhancedSearchBar>
    with SingleTickerProviderStateMixin {
  late TextEditingController _controller;
  late FocusNode _focusNode;
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<Color?> _colorAnimation;

  bool _isFocused = false;
  bool _hasText = false;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.initialValue);
    _focusNode = FocusNode();
    _hasText = _controller.text.isNotEmpty;

    _animationController = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.02,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));

    _focusNode.addListener(_handleFocusChange);
    _controller.addListener(_handleTextChange);
  }

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    _animationController.dispose();
    super.dispose();
  }

  void _handleFocusChange() {
    setState(() {
      _isFocused = _focusNode.hasFocus;
    });

    if (_isFocused) {
      _animationController.forward();
    } else {
      _animationController.reverse();
    }
  }

  void _handleTextChange() {
    final hasText = _controller.text.isNotEmpty;
    if (hasText != _hasText) {
      setState(() {
        _hasText = hasText;
      });
    }

    widget.onSearch?.call(_controller.text);
  }

  void _handleClear() {
    _controller.clear();
    widget.onClear?.call();
    _focusNode.requestFocus();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final screenSize = ScreenSize.of(context);

    _colorAnimation = ColorTween(
      begin: theme.colorScheme.outline.withOpacity(0.3),
      end: theme.primaryColor,
    ).animate(_animationController);

    return AnimatedBuilder(
      animation: _animationController,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: Container(
            decoration: BoxDecoration(
              borderRadius:
                  BorderRadius.circular(_getResponsiveBorderRadius(screenSize)),
              border: Border.all(
                color: _colorAnimation.value ?? theme.colorScheme.outline,
                width: _isFocused ? 2.0 : 1.0,
              ),
              color: theme.colorScheme.surface,
              boxShadow: _isFocused
                  ? [
                      BoxShadow(
                        color: theme.primaryColor.withOpacity(0.1),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ]
                  : null,
            ),
            child: TextField(
              controller: _controller,
              focusNode: _focusNode,
              enabled: widget.enabled,
              autofocus: widget.autofocus,
              style: theme.textTheme.bodyLarge,
              decoration: InputDecoration(
                hintText: widget.hintText,
                hintStyle: theme.textTheme.bodyLarge?.copyWith(
                  color: theme.colorScheme.onSurface.withOpacity(0.6),
                ),
                prefixIcon: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  child: Icon(
                    Icons.search,
                    color: _isFocused
                        ? theme.primaryColor
                        : theme.colorScheme.onSurface.withOpacity(0.6),
                    size: _getResponsiveIconSize(screenSize),
                  ),
                ),
                suffixIcon: _hasText
                    ? AnimatedScale(
                        scale: _hasText ? 1.0 : 0.0,
                        duration: const Duration(milliseconds: 200),
                        child: IconButton(
                          icon: Icon(
                            Icons.clear,
                            color: theme.colorScheme.onSurface.withOpacity(0.6),
                            size: _getResponsiveIconSize(screenSize),
                          ),
                          onPressed: _handleClear,
                          splashRadius: 20,
                        ),
                      )
                    : null,
                border: InputBorder.none,
                contentPadding: EdgeInsets.symmetric(
                  horizontal: _getResponsivePadding(screenSize),
                  vertical: _getResponsivePadding(screenSize),
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  /// Gets responsive border radius based on screen size.
  double _getResponsiveBorderRadius(ScreenSize screenSize) {
    return screenSize.responsiveValue(
      mobile: 12.0,
      tablet: 16.0,
      desktop: 20.0,
    );
  }

  /// Gets responsive icon size based on screen size.
  double _getResponsiveIconSize(ScreenSize screenSize) {
    return screenSize.responsiveValue(
      mobile: 20.0,
      tablet: 22.0,
      desktop: 24.0,
    );
  }

  /// Gets responsive padding based on screen size.
  double _getResponsivePadding(ScreenSize screenSize) {
    return screenSize.responsiveValue(
      mobile: AppSpacing.sm,
      tablet: AppSpacing.md,
      desktop: AppSpacing.lg,
    );
  }
}

/// A specialized search bar for menu items with category filtering.
///
/// This search bar includes category chips and advanced filtering options
/// optimized for restaurant menu interfaces.
class EnhancedMenuSearchBar extends StatefulWidget {
  /// Creates an enhanced menu search bar.
  ///
  /// Args:
  ///   hintText: Placeholder text for the search field.
  ///   onSearch: Callback when search query changes.
  ///   onClear: Callback when clear button is pressed.
  ///   categories: List of available categories for filtering.
  ///   selectedCategories: Currently selected categories.
  ///   onCategoryToggle: Callback when a category is toggled.
  ///   showCategories: Whether to show category chips.
  ///   key: Optional widget key for identification.
  const EnhancedMenuSearchBar({
    super.key,
    this.hintText = 'Search menu items...',
    this.onSearch,
    this.onClear,
    this.categories = const [],
    this.selectedCategories = const [],
    this.onCategoryToggle,
    this.showCategories = true,
  });

  /// Placeholder text for the search field.
  final String hintText;

  /// Callback when search query changes.
  final ValueChanged<String>? onSearch;

  /// Callback when clear button is pressed.
  final VoidCallback? onClear;

  /// List of available categories for filtering.
  final List<String> categories;

  /// Currently selected categories.
  final List<String> selectedCategories;

  /// Callback when a category is toggled.
  final ValueChanged<String>? onCategoryToggle;

  /// Whether to show category chips.
  final bool showCategories;

  @override
  State<EnhancedMenuSearchBar> createState() => _EnhancedMenuSearchBarState();
}

class _EnhancedMenuSearchBarState extends State<EnhancedMenuSearchBar> {
  @override
  Widget build(BuildContext context) {
    final screenSize = ScreenSize.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        EnhancedSearchBar(
          hintText: widget.hintText,
          onSearch: widget.onSearch,
          onClear: widget.onClear,
        ),
        if (widget.showCategories && widget.categories.isNotEmpty) ...[
          SizedBox(height: AppSpacing.sm * screenSize.spacingMultiplier),
          _buildCategoryChips(screenSize),
        ],
      ],
    );
  }

  /// Builds the category filter chips.
  Widget _buildCategoryChips(ScreenSize screenSize) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: widget.categories.map((category) {
          final isSelected = widget.selectedCategories.contains(category);
          return Padding(
            padding: EdgeInsets.only(
              right: AppSpacing.xs * screenSize.spacingMultiplier,
            ),
            child: FilterChip(
              label: Text(category),
              selected: isSelected,
              onSelected: (_) => widget.onCategoryToggle?.call(category),
              backgroundColor: Theme.of(context).colorScheme.surface,
              selectedColor: Theme.of(context).primaryColor.withOpacity(0.2),
              checkmarkColor: Theme.of(context).primaryColor,
              labelStyle: TextStyle(
                color: isSelected
                    ? Theme.of(context).primaryColor
                    : Theme.of(context).colorScheme.onSurface,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
              ),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
                side: BorderSide(
                  color: isSelected
                      ? Theme.of(context).primaryColor
                      : Theme.of(context).colorScheme.outline.withOpacity(0.3),
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}
