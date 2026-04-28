import 'package:flutter/material.dart';
import '../../../core/theme/app_spacing.dart';
import '../breakpoints.dart';

/// A responsive grid widget that adapts column count based on screen size.
/// 
/// This widget uses the existing AppGrid tokens and automatically adjusts
/// the number of columns based on the current breakpoint. It provides
/// consistent spacing and responsive behavior across all screen sizes.
/// 
/// Example usage:
/// ```dart
/// ResponsiveGrid(
///   children: [
///     MenuItemCard(item: item1),
///     MenuItemCard(item: item2),
///     MenuItemCard(item: item3),
///   ],
/// )
/// ```
class ResponsiveGrid extends StatelessWidget {
  /// Creates a responsive grid widget.
  /// 
  /// Args:
  ///   children: List of widgets to display in the grid.
  ///   spacing: Custom spacing between grid items (optional).
  ///   runSpacing: Custom spacing between grid rows (optional).
  ///   padding: Custom padding around the grid (optional).
  ///   crossAxisAlignment: How children are aligned cross-axis.
  ///   mainAxisAlignment: How children are aligned main-axis.
  ///   key: Optional widget key for identification.
  const ResponsiveGrid({
    super.key,
    required this.children,
    this.spacing,
    this.runSpacing,
    this.padding,
    this.crossAxisAlignment = WrapCrossAlignment.start,
    this.mainAxisAlignment = WrapAlignment.start,
  });

  /// List of child widgets to display in the grid.
  final List<Widget> children;

  /// Spacing between grid items horizontally.
  final double? spacing;

  /// Spacing between grid rows vertically.
  final double? runSpacing;

  /// Padding around the entire grid.
  final EdgeInsetsGeometry? padding;

  /// How children are aligned along the cross axis.
  final WrapCrossAlignment crossAxisAlignment;

  /// How children are aligned along the main axis.
  final WrapAlignment mainAxisAlignment;

  @override
  Widget build(BuildContext context) {
    final columns = BreakpointConfig.getGridColumns(context);
    final screenWidth = MediaQuery.of(context).size.width;
    
    // Calculate responsive spacing using existing AppSpacing system
    final spacingMultiplier = BreakpointConfig.getSpacingMultiplier(context);
    final effectiveSpacing = spacing ?? (AppGrid.gutter * spacingMultiplier);
    final effectiveRunSpacing = runSpacing ?? (AppGrid.gutter * spacingMultiplier);
    final effectivePadding = padding ?? EdgeInsets.all(AppGrid.margin * spacingMultiplier);
    
    // Calculate item width based on available space and columns
    final availableWidth = screenWidth - effectivePadding.horizontal;
    final totalSpacing = effectiveSpacing * (columns - 1);
    final itemWidth = (availableWidth - totalSpacing) / columns;
    
    return Padding(
      padding: effectivePadding,
      child: Wrap(
        spacing: effectiveSpacing,
        runSpacing: effectiveRunSpacing,
        crossAxisAlignment: crossAxisAlignment,
        alignment: mainAxisAlignment,
        children: children.map((child) {
          return SizedBox(
            width: itemWidth,
            child: child,
          );
        }).toList(),
      ),
    );
  }
}

/// A responsive grid view widget for scrollable grids.
/// 
/// This widget creates a scrollable grid that adapts its column count
/// based on the current breakpoint. It's ideal for displaying large
/// lists of items like menu items or product catalogs.
/// 
/// Example usage:
/// ```dart
/// ResponsiveGridView(
///   itemCount: menuItems.length,
///   itemBuilder: (context, index) => MenuItemCard(
///     item: menuItems[index],
///   ),
/// )
/// ```
class ResponsiveGridView extends StatelessWidget {
  /// Creates a responsive grid view widget.
  /// 
  /// Args:
  ///   itemCount: Number of items in the grid.
  ///   itemBuilder: Builder function for grid items.
  ///   spacing: Custom spacing between grid items (optional).
  ///   runSpacing: Custom spacing between grid rows (optional).
  ///   padding: Custom padding around the grid (optional).
  ///   shrinkWrap: Whether the grid should shrink-wrap its content.
  ///   physics: Scroll physics for the grid view.
  ///   key: Optional widget key for identification.
  const ResponsiveGridView({
    super.key,
    required this.itemCount,
    required this.itemBuilder,
    this.spacing,
    this.runSpacing,
    this.padding,
    this.shrinkWrap = false,
    this.physics,
  });

  /// Number of items in the grid.
  final int itemCount;

  /// Builder function for creating grid items.
  final Widget Function(BuildContext context, int index) itemBuilder;

  /// Spacing between grid items horizontally.
  final double? spacing;

  /// Spacing between grid rows vertically.
  final double? runSpacing;

  /// Padding around the entire grid.
  final EdgeInsetsGeometry? padding;

  /// Whether the grid should shrink-wrap its content.
  final bool shrinkWrap;

  /// Scroll physics for the grid view.
  final ScrollPhysics? physics;

  @override
  Widget build(BuildContext context) {
    final columns = BreakpointConfig.getGridColumns(context);
    final spacingMultiplier = BreakpointConfig.getSpacingMultiplier(context);
    
    // Calculate responsive spacing using existing AppSpacing system
    final effectiveSpacing = spacing ?? (AppGrid.gutter * spacingMultiplier);
    final effectiveRunSpacing = runSpacing ?? (AppGrid.gutter * spacingMultiplier);
    final effectivePadding = padding ?? EdgeInsets.all(AppGrid.margin * spacingMultiplier);
    
    return Padding(
      padding: effectivePadding,
      child: GridView.builder(
        shrinkWrap: shrinkWrap,
        physics: physics,
        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: columns,
          crossAxisSpacing: effectiveSpacing,
          mainAxisSpacing: effectiveRunSpacing,
          childAspectRatio: _getChildAspectRatio(context),
        ),
        itemCount: itemCount,
        itemBuilder: itemBuilder,
      ),
    );
  }

  /// Gets the appropriate child aspect ratio based on breakpoint.
  /// 
  /// Args:
  ///   context: The build context to get breakpoint information.
  /// 
  /// Returns:
  ///   The aspect ratio for grid items.
  double _getChildAspectRatio(BuildContext context) {
    final breakpoint = BreakpointConfig.getCurrentBreakpoint(context);
    
    switch (breakpoint) {
      case Breakpoint.mobile:
        return 1.0; // Square items on mobile
      case Breakpoint.mobileLarge:
        return 1.1; // Slightly wider on large mobile
      case Breakpoint.tablet:
        return 1.2; // Wider on tablet
      case Breakpoint.desktop:
      case Breakpoint.desktopXL:
        return 1.3; // Widest on desktop
    }
  }
}
