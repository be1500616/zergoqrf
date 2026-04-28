/// Menu management main screen.
///
/// This screen provides the main interface for menu management with tabs
/// for structure, items, preview, and publishing.
library;

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:get/get.dart';

import '../../../../core/theme/app_animations.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/responsive/index.dart';
import '../../../../shared/widgets/enhanced_button.dart';
import '../../../../shared/widgets/shimmer_skeletons.dart';
import '../../application/controllers/menu_management_controller.dart';
import '../../application/controllers/menu_tab_controller.dart';
import '../widgets/menu_items_tab.dart';
import '../widgets/menu_preview_tab.dart';
import '../widgets/menu_publishing_tab.dart';
import '../widgets/menu_structure_tab.dart';

class MenuManagementScreen extends GetView<MenuManagementController> {
  const MenuManagementScreen({super.key});

  MenuTabController get _tabController => Get.find<MenuTabController>();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final screenSize = ScreenSize.of(context);

    return Scaffold(
      backgroundColor: theme.colorScheme.surface,
      appBar: AppBar(
        title: Text(
          'Menu Management',
          style: theme.textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.w600,
            color: theme.colorScheme.onSurface,
          ),
        ),
        elevation: 0,
        backgroundColor: Colors.transparent,
        foregroundColor: theme.colorScheme.onSurface,
        actions: [
          // Refresh button with enhanced styling
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => controller.refresh(),
            tooltip: 'Refresh',
            style: IconButton.styleFrom(
              backgroundColor: theme.colorScheme.surfaceContainerHighest,
              foregroundColor: theme.colorScheme.onSurface,
            ),
          ).animate().scale(
                duration: AppAnimations.fast,
                curve: AppAnimations.bounce,
              ),
          SizedBox(width: AppSpacing.sm * screenSize.spacingMultiplier),

          // Menu analytics button
          IconButton(
            icon: const Icon(Icons.analytics_outlined),
            onPressed: () => controller.showAnalytics(),
            tooltip: 'Analytics',
            style: IconButton.styleFrom(
              backgroundColor: theme.colorScheme.surfaceContainerHighest,
              foregroundColor: theme.colorScheme.onSurface,
            ),
          ).animate(delay: 100.ms).scale(
                duration: AppAnimations.fast,
                curve: AppAnimations.bounce,
              ),
          SizedBox(width: AppSpacing.sm * screenSize.spacingMultiplier),

          // Settings button
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            onPressed: () => controller.showSettings(),
            tooltip: 'Settings',
            style: IconButton.styleFrom(
              backgroundColor: theme.colorScheme.surfaceContainerHighest,
              foregroundColor: theme.colorScheme.onSurface,
            ),
          ).animate(delay: 200.ms).scale(
                duration: AppAnimations.fast,
                curve: AppAnimations.bounce,
              ),
          SizedBox(width: AppSpacing.md * screenSize.spacingMultiplier),
        ],
        bottom: TabBar(
          controller: _tabController.tabController,
          labelColor: theme.colorScheme.primary,
          unselectedLabelColor:
              theme.colorScheme.onSurface.withValues(alpha: 0.6),
          indicatorColor: theme.colorScheme.primary,
          indicatorWeight: 3.0,
          labelStyle: theme.textTheme.labelLarge?.copyWith(
            fontWeight: FontWeight.w600,
          ),
          unselectedLabelStyle: theme.textTheme.labelLarge?.copyWith(
            fontWeight: FontWeight.w500,
          ),
          tabs: [
            const Tab(
              icon: Icon(Icons.account_tree_outlined),
              text: 'Structure',
            ).animate().fadeIn(delay: 300.ms, duration: AppAnimations.normal),
            const Tab(
              icon: Icon(Icons.restaurant_menu_outlined),
              text: 'Items',
            ).animate().fadeIn(delay: 400.ms, duration: AppAnimations.normal),
            const Tab(
              icon: Icon(Icons.preview_outlined),
              text: 'Preview',
            ).animate().fadeIn(delay: 500.ms, duration: AppAnimations.normal),
            const Tab(
              icon: Icon(Icons.publish_outlined),
              text: 'Publish',
            ).animate().fadeIn(delay: 600.ms, duration: AppAnimations.normal),
          ],
        ),
      ),
      body: Obx(() {
        if (controller.isLoading) {
          return _buildLoadingState(context, theme, screenSize);
        }

        if (controller.error != null) {
          return _buildErrorState(
              context, theme, screenSize, controller.error!);
        }

        return TabBarView(
          controller: _tabController.tabController,
          children: const [
            MenuStructureTab(),
            MenuItemsTab(),
            MenuPreviewTab(),
            MenuPublishingTab(),
          ],
        );
      }),
      floatingActionButton: Obx(() {
        return _tabController.getFabForCurrentTab(context) ??
            const SizedBox.shrink();
      }),
    );
  }

  /// Builds the loading state with shimmer skeletons
  Widget _buildLoadingState(
      BuildContext context, ThemeData theme, ScreenSize screenSize) {
    return Container(
      padding: EdgeInsets.all(AppSpacing.lg * screenSize.spacingMultiplier),
      child: Column(
        children: [
          // Tab content shimmer
          Expanded(
            child: ShimmerSkeletons.list(
              itemCount: 6,
              itemHeight: 80,
              showAvatar: false,
            ),
          ),
        ],
      ),
    ).animate().fadeIn(duration: AppAnimations.fast);
  }

  /// Builds the error state with enhanced styling and animations
  Widget _buildErrorState(BuildContext context, ThemeData theme,
      ScreenSize screenSize, String error) {
    return Container(
      padding: EdgeInsets.all(AppSpacing.xl * screenSize.spacingMultiplier),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Error icon with animation
            Container(
              padding:
                  EdgeInsets.all(AppSpacing.lg * screenSize.spacingMultiplier),
              decoration: BoxDecoration(
                color: theme.colorScheme.errorContainer,
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.error_outline_rounded,
                size: 64 * screenSize.spacingMultiplier,
                color: theme.colorScheme.onErrorContainer,
              ),
            )
                .animate()
                .scale(
                  duration: AppAnimations.slow,
                  curve: AppAnimations.bounce,
                )
                .then()
                .shake(
                  duration: AppAnimations.errorShake,
                  hz: 2,
                ),

            SizedBox(height: AppSpacing.lg * screenSize.spacingMultiplier),

            // Error title
            Text(
              'Unable to Load Menu Data',
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w600,
                color: theme.colorScheme.onSurface,
              ),
              textAlign: TextAlign.center,
            )
                .animate(delay: 200.ms)
                .fadeIn(duration: AppAnimations.normal)
                .slideY(begin: 0.3, end: 0),

            SizedBox(height: AppSpacing.sm * screenSize.spacingMultiplier),

            // Error message
            Text(
              _getErrorMessage(error),
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
              ),
              textAlign: TextAlign.center,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            )
                .animate(delay: 300.ms)
                .fadeIn(duration: AppAnimations.normal)
                .slideY(begin: 0.3, end: 0),

            SizedBox(height: AppSpacing.xl * screenSize.spacingMultiplier),

            // Retry button
            EnhancedButton(
              text: 'Try Again',
              icon: Icons.refresh_rounded,
              onPressed: () => controller.refresh(),
              style: EnhancedButtonStyle.primary,
            )
                .animate(delay: 400.ms)
                .fadeIn(duration: AppAnimations.normal)
                .slideY(begin: 0.5, end: 0),
          ],
        ),
      ),
    );
  }

  /// Gets a user-friendly error message
  String _getErrorMessage(String error) {
    if (error.contains('Not authenticated')) {
      return 'Please sign in to access menu management features.';
    } else if (error.contains('Failed to fetch')) {
      return 'Unable to connect to the server. Please check your internet connection.';
    } else if (error.contains('timeout')) {
      return 'The request timed out. Please try again.';
    } else {
      return 'An unexpected error occurred. Please try again.';
    }
  }
}
