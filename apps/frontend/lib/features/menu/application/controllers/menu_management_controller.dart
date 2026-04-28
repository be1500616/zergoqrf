/// Menu management controller.
///
/// This controller manages the state and business logic for menu management.
library;

import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:go_router/go_router.dart';

import '../../domain/entities/menu_entities.dart';
import '../../domain/repositories/menu_repository.dart';

/// Controller for menu management operations
class MenuManagementController extends GetxController {
  MenuManagementController({required this.menuRepository});

  final MenuRepository menuRepository;

  // Observable state
  final _categories = <MenuCategory>[].obs;
  final _menuItems = <MenuItem>[].obs;
  final _menuVersions = <MenuVersion>[].obs;
  final _currentVersion = Rxn<MenuVersion>();
  final _isLoading = false.obs;
  final _error = Rxn<String>();

  // Getters
  List<MenuCategory> get categories => _categories;
  List<MenuItem> get menuItems => _menuItems;
  List<MenuVersion> get menuVersions => _menuVersions;
  MenuVersion? get currentVersion => _currentVersion.value;
  bool get isLoading => _isLoading.value;
  String? get error => _error.value;

  // Filtered getters
  List<MenuCategory> get rootCategories =>
      _categories.where((cat) => cat.parentCategoryId == null).toList();

  List<MenuCategory> getSubcategories(String parentId) =>
      _categories.where((cat) => cat.parentCategoryId == parentId).toList();

  List<MenuItem> getCategoryItems(String categoryId) =>
      _menuItems.where((item) => item.categoryId == categoryId).toList();

  @override
  void onInit() {
    super.onInit();
    loadMenuData();
  }

  /// Load all menu data
  Future<void> loadMenuData() async {
    try {
      _isLoading.value = true;
      _error.value = null;

      await Future.wait([
        loadCategories(),
        loadMenuItems(),
        loadMenuVersions(),
      ]);
    } catch (e) {
      _error.value = e.toString();
    } finally {
      _isLoading.value = false;
    }
  }

  /// Load menu categories
  Future<void> loadCategories() async {
    try {
      final categories = await menuRepository.getCategoryHierarchy();
      _categories.assignAll(categories);
    } catch (e) {
      _error.value = 'Failed to load categories: $e';
      rethrow;
    }
  }

  /// Load menu items
  Future<void> loadMenuItems() async {
    try {
      final items = await menuRepository.getMenuItems();
      _menuItems.assignAll(items);
    } catch (e) {
      _error.value = 'Failed to load menu items: $e';
      rethrow;
    }
  }

  /// Load menu versions
  Future<void> loadMenuVersions() async {
    try {
      final versions = await menuRepository.getMenuVersions();
      _menuVersions.assignAll(versions);

      // Set current version
      final current = versions.firstWhereOrNull((v) => v.isCurrentLive);
      _currentVersion.value = current;
    } catch (e) {
      _error.value = 'Failed to load menu versions: $e';
      rethrow;
    }
  }

  // Category Management

  /// Create a new category
  Future<void> createCategory({
    required String name,
    String? description,
    String? parentCategoryId,
    int sortOrder = 0,
    Map<String, dynamic>? availabilitySchedule,
  }) async {
    try {
      _isLoading.value = true;
      _error.value = null;

      final category = await menuRepository.createCategory(
        name: name,
        description: description,
        parentCategoryId: parentCategoryId,
        sortOrder: sortOrder,
        availabilitySchedule: availabilitySchedule,
      );

      _categories.add(category);
      Get.snackbar('Success', 'Category created successfully');
    } catch (e) {
      _error.value = 'Failed to create category: $e';
      Get.snackbar('Error', 'Failed to create category');
      rethrow;
    } finally {
      _isLoading.value = false;
    }
  }

  /// Update a category
  Future<void> updateCategory(
    String categoryId,
    Map<String, dynamic> updateData,
  ) async {
    try {
      _isLoading.value = true;
      _error.value = null;

      final updatedCategory = await menuRepository.updateCategory(
        categoryId,
        updateData,
      );

      final index = _categories.indexWhere((cat) => cat.id == categoryId);
      if (index != -1) {
        _categories[index] = updatedCategory;
      }

      Get.snackbar('Success', 'Category updated successfully');
    } catch (e) {
      _error.value = 'Failed to update category: $e';
      Get.snackbar('Error', 'Failed to update category');
      rethrow;
    } finally {
      _isLoading.value = false;
    }
  }

  /// Delete a category
  Future<void> deleteCategory(String categoryId) async {
    try {
      _isLoading.value = true;
      _error.value = null;

      await menuRepository.deleteCategory(categoryId);
      _categories.removeWhere((cat) => cat.id == categoryId);

      Get.snackbar('Success', 'Category deleted successfully');
    } catch (e) {
      _error.value = 'Failed to delete category: $e';
      Get.snackbar('Error', 'Failed to delete category');
      rethrow;
    } finally {
      _isLoading.value = false;
    }
  }

  /// Reorder categories
  Future<void> reorderCategories(
      List<Map<String, dynamic>> categoryOrders) async {
    try {
      await menuRepository.reorderCategories(categoryOrders);
      await loadCategories(); // Reload to get updated order
    } catch (e) {
      _error.value = 'Failed to reorder categories: $e';
      Get.snackbar('Error', 'Failed to reorder categories');
      rethrow;
    }
  }

  // Menu Item Management

  /// Create a new menu item
  Future<void> createMenuItem({
    required String categoryId,
    required String name,
    String? description,
    required double basePrice,
    String? imageUrl,
    List<String> galleryImages = const [],
    ItemStatus status = ItemStatus.available,
    List<DietaryIndicator> dietaryIndicators = const [],
    List<String> allergenInfo = const [],
    Map<String, dynamic>? nutritionalInfo,
    int? preparationTime,
    int sortOrder = 0,
    Map<String, dynamic>? availabilitySchedule,
    int? dailyLimit,
    List<MenuItemVariant> variants = const [],
    List<MenuItemModifierGroup> modifierGroups = const [],
  }) async {
    try {
      _isLoading.value = true;
      _error.value = null;

      final item = await menuRepository.createMenuItem(
        categoryId: categoryId,
        name: name,
        description: description,
        basePrice: basePrice,
        imageUrl: imageUrl,
        galleryImages: galleryImages,
        status: status,
        dietaryIndicators: dietaryIndicators,
        allergenInfo: allergenInfo,
        nutritionalInfo: nutritionalInfo,
        preparationTime: preparationTime,
        sortOrder: sortOrder,
        availabilitySchedule: availabilitySchedule,
        dailyLimit: dailyLimit,
        variants: variants,
        modifierGroups: modifierGroups,
      );

      _menuItems.add(item);
      Get.snackbar('Success', 'Menu item created successfully');
    } catch (e) {
      _error.value = 'Failed to create menu item: $e';
      Get.snackbar('Error', 'Failed to create menu item');
      rethrow;
    } finally {
      _isLoading.value = false;
    }
  }

  /// Update a menu item
  Future<void> updateMenuItem(
    String itemId,
    Map<String, dynamic> updateData,
  ) async {
    try {
      _isLoading.value = true;
      _error.value = null;

      final updatedItem =
          await menuRepository.updateMenuItem(itemId, updateData);

      final index = _menuItems.indexWhere((item) => item.id == itemId);
      if (index != -1) {
        _menuItems[index] = updatedItem;
      }

      Get.snackbar('Success', 'Menu item updated successfully');
    } catch (e) {
      _error.value = 'Failed to update menu item: $e';
      Get.snackbar('Error', 'Failed to update menu item');
      rethrow;
    } finally {
      _isLoading.value = false;
    }
  }

  /// Delete a menu item
  Future<void> deleteMenuItem(String itemId) async {
    try {
      _isLoading.value = true;
      _error.value = null;

      await menuRepository.deleteMenuItem(itemId);
      _menuItems.removeWhere((item) => item.id == itemId);

      Get.snackbar('Success', 'Menu item deleted successfully');
    } catch (e) {
      _error.value = 'Failed to delete menu item: $e';
      Get.snackbar('Error', 'Failed to delete menu item');
      rethrow;
    } finally {
      _isLoading.value = false;
    }
  }

  /// Duplicate a menu item
  Future<void> duplicateMenuItem(String itemId) async {
    try {
      _isLoading.value = true;
      _error.value = null;

      final originalItem = _menuItems.firstWhere((item) => item.id == itemId);
      final duplicatedItem = await menuRepository.createMenuItem(
        categoryId: originalItem.categoryId,
        name: '${originalItem.name} (Copy)',
        description: originalItem.description,
        basePrice: originalItem.basePrice,
        imageUrl: originalItem.imageUrl,
        galleryImages: originalItem.galleryImages,
        status: originalItem.status,
        dietaryIndicators: originalItem.dietaryIndicators,
        allergenInfo: originalItem.allergenInfo,
        nutritionalInfo: originalItem.nutritionalInfo,
        preparationTime: originalItem.preparationTime,
        sortOrder: originalItem.sortOrder,
        availabilitySchedule: originalItem.availabilitySchedule,
        dailyLimit: originalItem.dailyLimit,
        variants: originalItem.variants,
        modifierGroups: originalItem.modifierGroups,
      );

      _menuItems.add(duplicatedItem);
      Get.snackbar('Success', 'Menu item duplicated successfully');
    } catch (e) {
      _error.value = 'Failed to duplicate menu item: $e';
      Get.snackbar('Error', 'Failed to duplicate menu item');
      rethrow;
    } finally {
      _isLoading.value = false;
    }
  }

  /// Search menu items
  Future<List<MenuItem>> searchMenuItems({
    String? query,
    String? categoryId,
    ItemStatus? status,
    List<DietaryIndicator>? dietaryIndicators,
    double? priceMin,
    double? priceMax,
    bool includeInactive = false,
  }) async {
    try {
      return await menuRepository.searchMenuItems(
        query: query,
        categoryId: categoryId,
        status: status,
        dietaryIndicators: dietaryIndicators,
        priceMin: priceMin,
        priceMax: priceMax,
        includeInactive: includeInactive,
      );
    } catch (e) {
      _error.value = 'Failed to search menu items: $e';
      rethrow;
    }
  }

  // Menu Versioning

  /// Create a new menu version
  Future<void> createMenuVersion({
    required String versionName,
    String? description,
  }) async {
    try {
      _isLoading.value = true;
      _error.value = null;

      final version = await menuRepository.createMenuVersion(
        versionName: versionName,
        description: description,
      );

      _menuVersions.add(version);
      Get.snackbar('Success', 'Menu version created successfully');
    } catch (e) {
      _error.value = 'Failed to create menu version: $e';
      Get.snackbar('Error', 'Failed to create menu version');
      rethrow;
    } finally {
      _isLoading.value = false;
    }
  }

  /// Publish a menu version
  Future<void> publishMenuVersion(
    String versionId, {
    bool publishImmediately = true,
    DateTime? scheduledPublishAt,
    String? publishNotes,
  }) async {
    try {
      _isLoading.value = true;
      _error.value = null;

      final publishedVersion = await menuRepository.publishMenuVersion(
        versionId,
        publishImmediately: publishImmediately,
        scheduledPublishAt: scheduledPublishAt,
        publishNotes: publishNotes,
      );

      // Update versions list
      final index = _menuVersions.indexWhere((v) => v.id == versionId);
      if (index != -1) {
        _menuVersions[index] = publishedVersion;
      }

      // Update current version if published immediately
      if (publishImmediately) {
        _currentVersion.value = publishedVersion;
      }

      Get.snackbar('Success', 'Menu version published successfully');
    } catch (e) {
      _error.value = 'Failed to publish menu version: $e';
      Get.snackbar('Error', 'Failed to publish menu version');
      rethrow;
    } finally {
      _isLoading.value = false;
    }
  }

  /// Rollback to a previous version
  Future<void> rollbackToVersion(String versionId) async {
    try {
      _isLoading.value = true;
      _error.value = null;

      final rolledBackVersion =
          await menuRepository.rollbackToVersion(versionId);
      _currentVersion.value = rolledBackVersion;

      await loadMenuVersions(); // Reload to update states
      Get.snackbar('Success', 'Menu rolled back successfully');
    } catch (e) {
      _error.value = 'Failed to rollback menu: $e';
      Get.snackbar('Error', 'Failed to rollback menu');
      rethrow;
    } finally {
      _isLoading.value = false;
    }
  }

  /// Get menu analytics
  Future<Map<String, dynamic>> getMenuAnalytics() async {
    try {
      return await menuRepository.getMenuAnalytics();
    } catch (e) {
      _error.value = 'Failed to load menu analytics: $e';
      rethrow;
    }
  }

  /// Get menu preview
  Future<Map<String, dynamic>> getMenuPreview({String? versionId}) async {
    try {
      return await menuRepository.getMenuPreview(versionId: versionId);
    } catch (e) {
      _error.value = 'Failed to load menu preview: $e';
      rethrow;
    }
  }

  /// Clear error
  void clearError() {
    _error.value = null;
  }

  /// Refresh all data
  @override
  Future<void> refresh() async {
    await loadMenuData();
  }

  // Dialog management methods for integration with MenuTabController

  /// Show create category dialog
  void showCreateCategoryDialog() {
    Get.dialog(_CreateCategoryDialog());
  }

  /// Show create item dialog
  void showCreateItemDialog() {
    if (categories.isEmpty) {
      Get.snackbar(
        'No Categories',
        'Please create at least one category before adding items',
        snackPosition: SnackPosition.BOTTOM,
      );
      return;
    }

    // Navigate to item creation screen using GoRouter
    Get.context?.go('/menu/item');
  }

  /// Show create version dialog
  void showCreateVersionDialog() {
    Get.dialog(_CreateVersionDialog());
  }

  /// Show analytics screen
  void showAnalytics() {
    // Navigate to analytics screen using GoRouter
    // This will be updated when we fix navigation patterns
    Get.toNamed('/menu/analytics');
  }

  /// Show settings screen
  void showSettings() {
    // Navigate to settings screen using GoRouter
    // This will be updated when we fix navigation patterns
    Get.toNamed('/menu/settings');
  }
}

// Temporary dialog widgets - these will be migrated to GetView pattern later
class _CreateCategoryDialog extends StatefulWidget {
  @override
  State<_CreateCategoryDialog> createState() => _CreateCategoryDialogState();
}

class _CreateCategoryDialogState extends State<_CreateCategoryDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  String? _selectedParentId;
  final MenuManagementController _controller =
      Get.find<MenuManagementController>();

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Create Category'),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'Category Name',
                hintText: 'e.g., Appetizers, Main Course',
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter a category name';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _descriptionController,
              decoration: const InputDecoration(
                labelText: 'Description (Optional)',
                hintText: 'Brief description of the category',
              ),
              maxLines: 2,
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _selectedParentId,
              decoration: const InputDecoration(
                labelText: 'Parent Category (Optional)',
                hintText: 'Select parent for subcategory',
              ),
              items: [
                const DropdownMenuItem<String>(
                  value: null,
                  child: Text('None (Root Category)'),
                ),
                ..._controller.rootCategories.map((category) {
                  return DropdownMenuItem<String>(
                    value: category.id,
                    child: Text(category.name),
                  );
                }),
              ],
              onChanged: (value) {
                setState(() {
                  _selectedParentId = value;
                });
              },
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _createCategory,
          child: const Text('Create'),
        ),
      ],
    );
  }

  void _createCategory() async {
    if (!_formKey.currentState!.validate()) return;

    try {
      await _controller.createCategory(
        name: _nameController.text.trim(),
        description: _descriptionController.text.trim().isEmpty
            ? null
            : _descriptionController.text.trim(),
        parentCategoryId: _selectedParentId,
      );
      if (mounted) Navigator.of(context).pop();
    } catch (e) {
      // Error is handled by controller
    }
  }
}

class _CreateVersionDialog extends StatefulWidget {
  @override
  State<_CreateVersionDialog> createState() => _CreateVersionDialogState();
}

class _CreateVersionDialogState extends State<_CreateVersionDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final MenuManagementController _controller =
      Get.find<MenuManagementController>();

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Create Menu Version'),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'Version Name',
                hintText: 'e.g., Summer Menu 2024',
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter a version name';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _descriptionController,
              decoration: const InputDecoration(
                labelText: 'Description (Optional)',
                hintText: 'Brief description of this version',
              ),
              maxLines: 3,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _createVersion,
          child: const Text('Create'),
        ),
      ],
    );
  }

  void _createVersion() async {
    if (!_formKey.currentState!.validate()) return;

    try {
      await _controller.createMenuVersion(
        versionName: _nameController.text.trim(),
        description: _descriptionController.text.trim().isEmpty
            ? null
            : _descriptionController.text.trim(),
      );
      if (mounted) Navigator.of(context).pop();
    } catch (e) {
      // Error is handled by controller
    }
  }
}
