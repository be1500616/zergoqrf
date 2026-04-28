import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:get/get.dart';

import '../../../../core/theme/app_animations.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/index.dart';
import '../../application/controllers/cart_controller.dart';
import '../../application/controllers/menu_controller.dart' as diner;
import '../widgets/category_tabs.dart';
import '../widgets/featured_items_section.dart';
import '../widgets/menu_item_card.dart';
import '../widgets/restaurant_header.dart';

/// Enhanced PWA-optimized diner menu screen.
class EnhancedDinerMenuScreen extends StatelessWidget {
  const EnhancedDinerMenuScreen({
    super.key,
    required this.restaurantCode,
  });

  final String restaurantCode;

  @override
  Widget build(BuildContext context) {
    // Get controllers using GetX dependency injection
    final menuController = Get.find<diner.MenuController>();
    final cartController = Get.find<CartController>();
    final scrollController = ScrollController();

    // Load menu data when widget is built
    WidgetsBinding.instance.addPostFrameCallback((_) {
      menuController.loadMenu(restaurantCode);
    });

    return _EnhancedDinerMenuView(
      restaurantCode: restaurantCode,
      menuController: menuController,
      cartController: cartController,
      scrollController: scrollController,
    );
  }
}

/// Internal view widget that handles the UI rendering.
class _EnhancedDinerMenuView extends StatelessWidget {
  const _EnhancedDinerMenuView({
    required this.restaurantCode,
    required this.menuController,
    required this.cartController,
    required this.scrollController,
  });

  final String restaurantCode;
  final diner.MenuController menuController;
  final CartController cartController;
  final ScrollController scrollController;

  @override
  Widget build(BuildContext context) {
    return ResponsiveBuilder(
      builder: (context, breakpoint) {
        return Scaffold(
          body: Obx(() {
            if (menuController.isLoading) {
              return const _LoadingView();
            }

            if (menuController.error != null) {
              return _ErrorView(
                error: menuController.error!,
                onRetry: () => menuController.loadMenu(restaurantCode),
              );
            }

            if (menuController.menuStructure == null) {
              return const _NotFoundView();
            }

            return _ResponsiveMenuView(
              menuController: menuController,
              cartController: cartController,
              scrollController: scrollController,
              breakpoint: breakpoint,
            );
          }),
          bottomNavigationBar: Obx(() {
            final itemCount = cartController.totalItems;
            if (itemCount == 0) return const SizedBox.shrink();

            return _ResponsiveCartBottomBar(
              cartController: cartController,
              itemCount: itemCount,
              breakpoint: breakpoint,
            );
          }),
        );
      },
    );
  }
}

/// Enhanced loading view with modern animations and responsive design.
class _LoadingView extends StatelessWidget {
  const _LoadingView();

  @override
  Widget build(BuildContext context) {
    final screenSize = ScreenSize.of(context);

    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Theme.of(context).colorScheme.surface,
            Theme.of(context).colorScheme.surface.withValues(alpha: 0.8),
          ],
        ),
      ),
      child: screenSize.responsiveValue(
        mobile: const EnhancedLoading(
          message: 'Loading delicious menu...',
          type: LoadingType.pulse,
          size: LoadingSize.medium,
        ),
        tablet: const EnhancedLoading(
          message: 'Preparing your dining experience...',
          type: LoadingType.dots,
          size: LoadingSize.large,
        ),
        desktop: const EnhancedMenuItemLoading(itemCount: 4),
      ),
    );
  }
}

/// Enhanced error view with modern design and animations.
class _ErrorView extends StatelessWidget {
  const _ErrorView({
    required this.error,
    required this.onRetry,
  });

  final String error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final screenSize = ScreenSize.of(context);

    return Center(
      child: AdaptiveContainer(
        child: EnhancedCard(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: EdgeInsets.all(
                    AppSpacing.lg * screenSize.spacingMultiplier),
                decoration: BoxDecoration(
                  color:
                      theme.colorScheme.errorContainer.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.restaurant_menu,
                  size: screenSize.responsiveValue(
                    mobile: 48.0,
                    tablet: 56.0,
                    desktop: 64.0,
                  ),
                  color: theme.colorScheme.error,
                ),
              ),
              SizedBox(height: AppSpacing.lg * screenSize.spacingMultiplier),
              Text(
                'Oops! Something went wrong',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: theme.colorScheme.onSurface,
                ),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: AppSpacing.sm * screenSize.spacingMultiplier),
              Text(
                error,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
                ),
                textAlign: TextAlign.center,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
              SizedBox(height: AppSpacing.xl * screenSize.spacingMultiplier),
              EnhancedButton(
                text: 'Try Again',
                icon: Icons.refresh,
                onPressed: onRetry,
                style: EnhancedButtonStyle.primary,
                width: double.infinity,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Enhanced not found view with modern design.
class _NotFoundView extends StatelessWidget {
  const _NotFoundView();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final screenSize = ScreenSize.of(context);

    return Center(
      child: AdaptiveContainer(
        child: EnhancedCard(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: EdgeInsets.all(
                    AppSpacing.xl * screenSize.spacingMultiplier),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceContainerHighest
                      .withValues(alpha: 0.3),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.search_off,
                  size: screenSize.responsiveValue(
                    mobile: 56.0,
                    tablet: 64.0,
                    desktop: 72.0,
                  ),
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              SizedBox(height: AppSpacing.lg * screenSize.spacingMultiplier),
              Text(
                'Restaurant not found',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: theme.colorScheme.onSurface,
                ),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: AppSpacing.sm * screenSize.spacingMultiplier),
              Text(
                'Please check the QR code and try again.',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
                ),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: AppSpacing.lg * screenSize.spacingMultiplier),
              EnhancedButton(
                text: 'Go Back',
                icon: Icons.arrow_back,
                onPressed: () => Get.back(),
                style: EnhancedButtonStyle.outlined,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Responsive menu view that adapts layout based on screen size.
class _ResponsiveMenuView extends StatelessWidget {
  const _ResponsiveMenuView({
    required this.menuController,
    required this.cartController,
    required this.scrollController,
    required this.breakpoint,
  });

  final diner.MenuController menuController;
  final CartController cartController;
  final ScrollController scrollController;
  final Breakpoint breakpoint;

  @override
  Widget build(BuildContext context) {
    final restaurant = menuController.restaurant!;
    final screenSize = ScreenSize.of(context);

    return ResponsiveLayout(
      mobile: _buildMobileLayout(context, restaurant, screenSize),
      tablet: _buildTabletLayout(context, restaurant, screenSize),
      desktop: _buildDesktopLayout(context, restaurant, screenSize),
    );
  }

  /// Builds the mobile layout with single-column design.
  Widget _buildMobileLayout(
      BuildContext context, dynamic restaurant, ScreenSize screenSize) {
    return CustomScrollView(
      controller: scrollController,
      slivers: [
        // Restaurant header with branding and entrance animation
        RestaurantHeader(restaurant: restaurant)
            .animate()
            .fadeIn(duration: AppAnimations.normal)
            .slideY(begin: -0.3, end: 0),

        // Enhanced search bar with mobile-optimized padding and animation
        SliverToBoxAdapter(
          child: AdaptiveContainer(
            child: EnhancedSearchBar(
              hintText: 'Search delicious items...',
              onSearch: menuController.searchItems,
              onClear: menuController.clearSearch,
            )
                .animate(delay: 200.ms)
                .fadeIn(duration: AppAnimations.normal)
                .slideY(begin: 0.3, end: 0),
          ),
        ),

        // Featured items section with animation (only show when not searching)
        if (!menuController.isSearchMode &&
            menuController.featuredItems.isNotEmpty)
          FeaturedItemsSection(
            items: menuController.featuredItems,
            cartController: cartController,
          )
              .animate(delay: 300.ms)
              .fadeIn(duration: AppAnimations.normal)
              .slideY(begin: 0.3, end: 0),

        // Category tabs with animation (only show when not searching)
        if (!menuController.isSearchMode)
          CategoryTabs(
            categories: menuController.categories,
            selectedCategory: menuController.selectedCategory,
            onCategorySelected: menuController.selectCategory,
          )
              .animate(delay: 400.ms)
              .fadeIn(duration: AppAnimations.normal)
              .slideY(begin: 0.3, end: 0),

        // Menu items list - single column on mobile
        _buildMenuItemsList(context, screenSize, isMobile: true),

        // Bottom padding for cart bar
        SliverToBoxAdapter(
          child: SizedBox(
              height: screenSize.responsiveValue(
                  mobile: 100, tablet: 120, desktop: 140)),
        ),
      ],
    );
  }

  /// Builds the tablet layout with optimized two-column design.
  Widget _buildTabletLayout(
      BuildContext context, dynamic restaurant, ScreenSize screenSize) {
    return CustomScrollView(
      controller: scrollController,
      slivers: [
        // Restaurant header with branding
        RestaurantHeader(restaurant: restaurant),

        // Enhanced search bar and category tabs in a row for tablet
        SliverToBoxAdapter(
          child: AdaptiveContainer(
            child: Row(
              children: [
                Expanded(
                  flex: 2,
                  child: EnhancedSearchBar(
                    hintText: 'Search menu items...',
                    onSearch: menuController.searchItems,
                    onClear: menuController.clearSearch,
                  ),
                ),
                if (!menuController.isSearchMode) ...[
                  SizedBox(width: AppSpacing.md * screenSize.spacingMultiplier),
                  Expanded(
                    flex: 3,
                    child: CategoryTabs(
                      categories: menuController.categories,
                      selectedCategory: menuController.selectedCategory,
                      onCategorySelected: menuController.selectCategory,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),

        // Featured items section (only show when not searching)
        if (!menuController.isSearchMode &&
            menuController.featuredItems.isNotEmpty)
          FeaturedItemsSection(
            items: menuController.featuredItems,
            cartController: cartController,
          ),

        // Menu items grid - responsive columns on tablet
        _buildMenuItemsList(context, screenSize, isMobile: false),

        // Bottom padding for cart bar
        SliverToBoxAdapter(
          child: SizedBox(
              height: screenSize.responsiveValue(
                  mobile: 100, tablet: 120, desktop: 140)),
        ),
      ],
    );
  }

  /// Builds the desktop layout with enhanced multi-column design.
  Widget _buildDesktopLayout(
      BuildContext context, dynamic restaurant, ScreenSize screenSize) {
    return Row(
      children: [
        // Sidebar with categories and search (desktop only)
        if (!menuController.isSearchMode)
          SizedBox(
            width: 280,
            child: AdaptiveContainer(
              child: Column(
                children: [
                  EnhancedSearchBar(
                    hintText: 'Search menu...',
                    onSearch: menuController.searchItems,
                    onClear: menuController.clearSearch,
                  ),
                  SizedBox(
                      height: AppSpacing.md * screenSize.spacingMultiplier),
                  Expanded(
                    child: CategoryTabs(
                      categories: menuController.categories,
                      selectedCategory: menuController.selectedCategory,
                      onCategorySelected: menuController.selectCategory,
                    ),
                  ),
                ],
              ),
            ),
          ),

        // Main content area
        Expanded(
          child: CustomScrollView(
            controller: scrollController,
            slivers: [
              // Restaurant header with branding
              RestaurantHeader(restaurant: restaurant),

              // Enhanced search bar for desktop when in search mode
              if (menuController.isSearchMode)
                SliverToBoxAdapter(
                  child: AdaptiveContainer(
                    child: EnhancedSearchBar(
                      hintText: 'Search menu items...',
                      onSearch: menuController.searchItems,
                      onClear: menuController.clearSearch,
                    ),
                  ),
                ),

              // Featured items section (only show when not searching)
              if (!menuController.isSearchMode &&
                  menuController.featuredItems.isNotEmpty)
                FeaturedItemsSection(
                  items: menuController.featuredItems,
                  cartController: cartController,
                ),

              // Menu items grid - multi-column on desktop
              _buildMenuItemsList(context, screenSize, isMobile: false),

              // Bottom padding
              SliverToBoxAdapter(
                child: SizedBox(
                    height: screenSize.responsiveValue(
                        mobile: 100, tablet: 120, desktop: 140)),
              ),
            ],
          ),
        ),
      ],
    );
  }

  /// Builds the responsive menu items list.
  Widget _buildMenuItemsList(BuildContext context, ScreenSize screenSize,
      {required bool isMobile}) {
    return SliverToBoxAdapter(
      child: AdaptiveContainer(
        child: Obx(() {
          final items = menuController.displayedItems;

          if (items.isEmpty) {
            return _EmptyStateView(
              isSearchMode: menuController.isSearchMode,
              searchQuery: menuController.searchQuery,
            );
          }

          if (isMobile || screenSize.isMobileSize) {
            // Single column layout for mobile
            return Column(
              children: items.map((item) {
                return Padding(
                  padding: EdgeInsets.only(
                      bottom: screenSize.spacingMultiplier * 12),
                  child: MenuItemCard(
                    item: item,
                    cartController: cartController,
                  ),
                );
              }).toList(),
            );
          } else {
            // Grid layout for tablet and desktop
            return ResponsiveGrid(
              children: items.map((item) {
                return MenuItemCard(
                  item: item,
                  cartController: cartController,
                );
              }).toList(),
            );
          }
        }),
      ),
    );
  }
}

/// Enhanced empty state view with modern design and animations.
class _EmptyStateView extends StatelessWidget {
  const _EmptyStateView({
    required this.isSearchMode,
    required this.searchQuery,
  });

  final bool isSearchMode;
  final String searchQuery;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final screenSize = ScreenSize.of(context);

    return Center(
      child: AdaptiveContainer(
        child: EnhancedCard(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: EdgeInsets.all(
                    AppSpacing.xl * screenSize.spacingMultiplier),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceContainerHighest
                      .withValues(alpha: 0.3),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  isSearchMode ? Icons.search_off : Icons.restaurant_menu,
                  size: screenSize.responsiveValue(
                    mobile: 48.0,
                    tablet: 56.0,
                    desktop: 64.0,
                  ),
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              SizedBox(height: AppSpacing.lg * screenSize.spacingMultiplier),
              Text(
                isSearchMode ? 'No results found' : 'No items available',
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: theme.colorScheme.onSurface,
                ),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: AppSpacing.sm * screenSize.spacingMultiplier),
              Text(
                isSearchMode
                    ? 'Try searching for "$searchQuery" with different keywords.'
                    : 'This category is currently empty. Check back later for new items!',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
                ),
                textAlign: TextAlign.center,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
              if (isSearchMode) ...[
                SizedBox(height: AppSpacing.lg * screenSize.spacingMultiplier),
                EnhancedButton(
                  text: 'Clear Search',
                  icon: Icons.clear,
                  onPressed: () {
                    // Clear search and show all items
                    Get.find<diner.MenuController>().clearSearch();
                  },
                  style: EnhancedButtonStyle.outlined,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

/// Responsive cart bottom bar that adapts to different screen sizes.
class _ResponsiveCartBottomBar extends StatelessWidget {
  const _ResponsiveCartBottomBar({
    required this.cartController,
    required this.itemCount,
    required this.breakpoint,
  });

  final CartController cartController;
  final int itemCount;
  final Breakpoint breakpoint;

  @override
  Widget build(BuildContext context) {
    final screenSize = ScreenSize.of(context);

    return SafeArea(
      child: AdaptiveContainer(
        child: screenSize.responsiveValue(
          mobile: _buildMobileCartBar(context, screenSize),
          tablet: _buildTabletCartBar(context, screenSize),
          desktop: _buildDesktopCartBar(context, screenSize),
        ),
      ),
    );
  }

  /// Builds mobile cart bar with enhanced button.
  Widget _buildMobileCartBar(BuildContext context, ScreenSize screenSize) {
    return EnhancedButton(
      text: 'View Cart ($itemCount)',
      icon: Icons.shopping_cart,
      onPressed: _onCartPressed,
      style: EnhancedButtonStyle.primary,
      width: double.infinity,
    );
  }

  /// Builds tablet cart bar with enhanced styling.
  Widget _buildTabletCartBar(BuildContext context, ScreenSize screenSize) {
    return Container(
      constraints: const BoxConstraints(maxWidth: 400),
      child: EnhancedButton(
        text: 'View Cart ($itemCount)',
        icon: Icons.shopping_cart,
        onPressed: _onCartPressed,
        style: EnhancedButtonStyle.primary,
        width: double.infinity,
      ),
    );
  }

  /// Builds desktop cart bar with enhanced FAB.
  Widget _buildDesktopCartBar(BuildContext context, ScreenSize screenSize) {
    return Align(
      alignment: Alignment.centerRight,
      child: EnhancedFAB(
        icon: Icons.shopping_cart,
        label: 'View Cart ($itemCount)',
        onPressed: _onCartPressed,
        isExtended: true,
        badgeCount: itemCount > 0 ? itemCount : null,
      ),
    );
  }

  /// Handles cart button press.
  void _onCartPressed() {
    // Navigate to cart screen
    Get.toNamed('/cart');
  }
}
