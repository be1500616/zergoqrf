/// Menu tab controller for managing tab state in MenuManagementScreen.
///
/// This controller replaces the TabController from StatefulWidget pattern
/// with GetX reactive state management.
library;

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import 'menu_management_controller.dart';

class MenuTabController extends GetxController
    with GetSingleTickerProviderStateMixin {
  late TabController tabController;

  // Observable state
  final _currentTabIndex = 0.obs;

  // Getters
  int get currentTabIndex => _currentTabIndex.value;

  @override
  void onInit() {
    super.onInit();
    tabController = TabController(length: 4, vsync: this);

    // Listen to tab changes
    tabController.addListener(() {
      if (!tabController.indexIsChanging) {
        _currentTabIndex.value = tabController.index;
      }
    });
  }

  @override
  void onClose() {
    tabController.dispose();
    super.onClose();
  }

  /// Navigate to specific tab
  void goToTab(int index) {
    if (index >= 0 && index < 4) {
      tabController.animateTo(index);
      _currentTabIndex.value = index;
    }
  }

  /// Get the appropriate FAB for current tab
  Widget? getFabForCurrentTab(BuildContext context) {
    switch (currentTabIndex) {
      case 0: // Structure tab
        return FloatingActionButton.extended(
          onPressed: () => _showCreateCategoryDialog(context),
          icon: const Icon(Icons.add),
          label: const Text('Add Category'),
        );
      case 1: // Items tab
        return FloatingActionButton.extended(
          onPressed: _showCreateItemDialog,
          icon: const Icon(Icons.add),
          label: const Text('Add Item'),
        );
      case 2: // Preview tab
        return FloatingActionButton.extended(
          onPressed: _refreshPreview,
          icon: const Icon(Icons.refresh),
          label: const Text('Refresh Preview'),
        );
      case 3: // Publish tab
        return FloatingActionButton.extended(
          onPressed: () => _showCreateVersionDialog(context),
          icon: const Icon(Icons.add),
          label: const Text('New Version'),
        );
      default:
        return null;
    }
  }

  void _showCreateCategoryDialog(BuildContext context) {
    // This will be handled by the MenuManagementController
    Get.find<MenuManagementController>().showCreateCategoryDialog();
  }

  void _showCreateItemDialog() {
    // This will be handled by the MenuManagementController
    Get.find<MenuManagementController>().showCreateItemDialog();
  }

  void _refreshPreview() {
    // This will be handled by the MenuManagementController
    Get.find<MenuManagementController>().refresh();
  }

  void _showCreateVersionDialog(BuildContext context) {
    // This will be handled by the MenuManagementController
    Get.find<MenuManagementController>().showCreateVersionDialog();
  }
}
