/// Menu structure tab widget.
///
/// This widget displays the hierarchical menu structure with drag-and-drop
/// functionality for organizing categories and items.
library;

import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:go_router/go_router.dart';
import 'package:zergo_frontend/features/menu/presentation/widgets/add_subcategory_dialog.dart';
import 'package:zergo_frontend/features/menu/presentation/widgets/edit_category_dialog.dart';

import '../../application/controllers/menu_management_controller.dart';
import '../../domain/entities/menu_entities.dart';

class MenuStructureTab extends StatelessWidget {
  const MenuStructureTab({super.key});

  @override
  Widget build(BuildContext context) {
    final MenuManagementController controller =
        Get.find<MenuManagementController>();

    return Obx(() {
      if (controller.categories.isEmpty) {
        return _EmptyState();
      }

      return RefreshIndicator(
        onRefresh: () => controller.loadCategories(),
        child: CustomScrollView(
          slivers: [
            SliverPadding(
              padding: const EdgeInsets.all(16),
              sliver: SliverList(
                delegate: SliverChildBuilderDelegate(
                  (context, index) {
                    final category = controller.rootCategories[index];
                    return _CategoryCard(
                      category: category,
                      controller: controller,
                    );
                  },
                  childCount: controller.rootCategories.length,
                ),
              ),
            ),
          ],
        ),
      );
    });
  }
}

class _EmptyState extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.account_tree_outlined,
            size: 64,
            color: Theme.of(context).colorScheme.outline,
          ),
          const SizedBox(height: 16),
          Text(
            'No Categories Yet',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  color: Theme.of(context).colorScheme.outline,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Create your first category to start organizing your menu',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.outline,
                ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () {
              // Trigger the FAB action
              Get.find<MenuManagementController>();
            },
            icon: const Icon(Icons.add),
            label: const Text('Create Category'),
          ),
        ],
      ),
    );
  }
}

class _CategoryCard extends StatelessWidget {
  _CategoryCard({
    required this.category,
    required this.controller,
  });

  final MenuCategory category;
  final MenuManagementController controller;

  final RxBool _isExpanded = true.obs;

  @override
  Widget build(BuildContext context) {
    final subcategories = controller.getSubcategories(category.id);
    final items = controller.getCategoryItems(category.id);

    return Obx(() => Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: Column(
            children: [
              // Category header
              ListTile(
                leading: Icon(
                  _isExpanded.value ? Icons.folder_open : Icons.folder,
                  color: Theme.of(context).colorScheme.primary,
                ),
                title: Text(
                  category.name,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                ),
                subtitle: category.description != null
                    ? Text(category.description!)
                    : null,
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Item count badge
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.primaryContainer,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        '${items.length} items',
                        style: Theme.of(context).textTheme.labelSmall?.copyWith(
                              color: Theme.of(context)
                                  .colorScheme
                                  .onPrimaryContainer,
                            ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    // Expand/collapse button
                    IconButton(
                      icon: Icon(_isExpanded.value
                          ? Icons.expand_less
                          : Icons.expand_more),
                      onPressed: () {
                        _isExpanded.value = !_isExpanded.value;
                      },
                    ),
                    // More options menu
                    PopupMenuButton<String>(
                      onSelected: (value) => _handleMenuAction(value),
                      itemBuilder: (context) => [
                        const PopupMenuItem(
                          value: 'edit',
                          child: ListTile(
                            leading: Icon(Icons.edit_outlined),
                            title: Text('Edit Category'),
                            contentPadding: EdgeInsets.zero,
                          ),
                        ),
                        const PopupMenuItem(
                          value: 'add_subcategory',
                          child: ListTile(
                            leading: Icon(Icons.create_new_folder_outlined),
                            title: Text('Add Subcategory'),
                            contentPadding: EdgeInsets.zero,
                          ),
                        ),
                        const PopupMenuItem(
                          value: 'add_item',
                          child: ListTile(
                            leading: Icon(Icons.add_circle_outline),
                            title: Text('Add Item'),
                            contentPadding: EdgeInsets.zero,
                          ),
                        ),
                        const PopupMenuDivider(),
                        const PopupMenuItem(
                          value: 'delete',
                          child: ListTile(
                            leading:
                                Icon(Icons.delete_outline, color: Colors.red),
                            title: Text('Delete Category',
                                style: TextStyle(color: Colors.red)),
                            contentPadding: EdgeInsets.zero,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                onTap: () {
                  _isExpanded.value = !_isExpanded.value;
                },
              ),

              // Expandable content
              if (_isExpanded.value) ...[
                const Divider(height: 1),

                // Subcategories
                if (subcategories.isNotEmpty) ...[
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
                    child: Row(
                      children: [
                        Icon(
                          Icons.subdirectory_arrow_right,
                          size: 16,
                          color: Theme.of(context).colorScheme.outline,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Subcategories',
                          style: Theme.of(context)
                              .textTheme
                              .labelMedium
                              ?.copyWith(
                                color: Theme.of(context).colorScheme.outline,
                                fontWeight: FontWeight.w500,
                              ),
                        ),
                      ],
                    ),
                  ),
                  ...subcategories.map((subcat) => _SubcategoryTile(
                        subcategory: subcat,
                        controller: controller,
                      )),
                ],

                // Items
                if (items.isNotEmpty) ...[
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
                    child: Row(
                      children: [
                        Icon(
                          Icons.restaurant_menu,
                          size: 16,
                          color: Theme.of(context).colorScheme.outline,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Menu Items',
                          style: Theme.of(context)
                              .textTheme
                              .labelMedium
                              ?.copyWith(
                                color: Theme.of(context).colorScheme.outline,
                                fontWeight: FontWeight.w500,
                              ),
                        ),
                      ],
                    ),
                  ),
                  ...items.map((item) => _MenuItemTile(
                        item: item,
                        controller: controller,
                      )),
                ],

                // Empty state for category
                if (subcategories.isEmpty && items.isEmpty)
                  Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      children: [
                        Icon(
                          Icons.inbox_outlined,
                          size: 32,
                          color: Theme.of(context).colorScheme.outline,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'No items in this category',
                          style: Theme.of(context)
                              .textTheme
                              .bodyMedium
                              ?.copyWith(
                                color: Theme.of(context).colorScheme.outline,
                              ),
                        ),
                        const SizedBox(height: 12),
                        OutlinedButton.icon(
                          onPressed: () => _handleMenuAction('add_item'),
                          icon: const Icon(Icons.add),
                          label: const Text('Add First Item'),
                        ),
                      ],
                    ),
                  ),
              ],
            ],
          ),
        ));
  }

  void _handleMenuAction(String action) {
    switch (action) {
      case 'edit':
        _showEditCategoryDialog();
        break;
      case 'add_subcategory':
        _showAddSubcategoryDialog();
        break;
      case 'add_item':
        _navigateToAddItem();
        break;
      case 'delete':
        _showDeleteConfirmation();
        break;
    }
  }

  void _showEditCategoryDialog() {
    Get.dialog(EditCategoryDialog(category: category));
  }

  void _showAddSubcategoryDialog() {
    Get.dialog(AddSubcategoryDialog(parentCategory: category));
  }

  void _navigateToAddItem() {
    Get.context?.go('/menu/item?categoryId=${category.id}');
  }

  void _showDeleteConfirmation() {
    Get.dialog(
      AlertDialog(
        title: const Text('Delete Category'),
        content: Text(
          'Are you sure you want to delete "${category.name}"? This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              Get.back();
              try {
                await controller.deleteCategory(category.id);
              } catch (e) {
                // Error handled by controller
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Theme.of(Get.context!).colorScheme.error,
              foregroundColor: Theme.of(Get.context!).colorScheme.onError,
            ),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
}

class _SubcategoryTile extends StatelessWidget {
  const _SubcategoryTile({
    required this.subcategory,
    required this.controller,
  });

  final MenuCategory subcategory;
  final MenuManagementController controller;

  @override
  Widget build(BuildContext context) {
    final items = controller.getCategoryItems(subcategory.id);

    return Padding(
      padding: const EdgeInsets.only(left: 32),
      child: ListTile(
        leading: Icon(
          Icons.folder_outlined,
          color: Theme.of(context).colorScheme.secondary,
        ),
        title: Text(subcategory.name),
        subtitle: subcategory.description != null
            ? Text(subcategory.description!)
            : null,
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.secondaryContainer,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            '${items.length}',
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSecondaryContainer,
                ),
          ),
        ),
        onTap: () {
          // Navigate to subcategory items
          Get.context?.go('/menu?categoryId=${subcategory.id}');
        },
      ),
    );
  }
}

class _MenuItemTile extends StatelessWidget {
  const _MenuItemTile({
    required this.item,
    required this.controller,
  });

  final MenuItem item;
  final MenuManagementController controller;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: 32),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Theme.of(context).colorScheme.primaryContainer,
          child: item.imageUrl != null
              ? ClipOval(
                  child: Image.network(
                    item.imageUrl!,
                    width: 40,
                    height: 40,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) => Icon(
                      Icons.restaurant,
                      color: Theme.of(context).colorScheme.onPrimaryContainer,
                    ),
                  ),
                )
              : Icon(
                  Icons.restaurant,
                  color: Theme.of(context).colorScheme.onPrimaryContainer,
                ),
        ),
        title: Text(item.name),
        subtitle: Text('₹${item.basePrice.toStringAsFixed(2)}'),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Status indicator
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                color: _getStatusColor(context, item.status),
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 8),
            // More options
            PopupMenuButton<String>(
              onSelected: (value) => _handleItemAction(value),
              itemBuilder: (context) => [
                const PopupMenuItem(
                  value: 'edit',
                  child: ListTile(
                    leading: Icon(Icons.edit_outlined),
                    title: Text('Edit Item'),
                    contentPadding: EdgeInsets.zero,
                  ),
                ),
                const PopupMenuItem(
                  value: 'duplicate',
                  child: ListTile(
                    leading: Icon(Icons.copy_outlined),
                    title: Text('Duplicate'),
                    contentPadding: EdgeInsets.zero,
                  ),
                ),
                const PopupMenuDivider(),
                const PopupMenuItem(
                  value: 'delete',
                  child: ListTile(
                    leading: Icon(Icons.delete_outline, color: Colors.red),
                    title: Text('Delete Item',
                        style: TextStyle(color: Colors.red)),
                    contentPadding: EdgeInsets.zero,
                  ),
                ),
              ],
            ),
          ],
        ),
        onTap: () {
          Get.toNamed('/menu/item/${item.id}');
        },
      ),
    );
  }

  Color _getStatusColor(BuildContext context, ItemStatus status) {
    switch (status) {
      case ItemStatus.available:
        return Colors.green;
      case ItemStatus.unavailable:
        return Colors.red;
      case ItemStatus.seasonal:
        return Colors.orange;
      case ItemStatus.featured:
        return Colors.blue;
    }
  }

  void _handleItemAction(String action) {
    switch (action) {
      case 'edit':
        Get.context?.go('/menu/item?itemId=${item.id}');
        break;
      case 'duplicate':
        // TODO: Implement duplicate functionality
        Get.snackbar('Coming Soon',
            'Duplicate item functionality will be available soon');
        break;
      case 'delete':
        _showDeleteConfirmation();
        break;
    }
  }

  void _showDeleteConfirmation() {
    Get.dialog(
      AlertDialog(
        title: const Text('Delete Menu Item'),
        content: Text(
          'Are you sure you want to delete "${item.name}"? This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              Get.back();
              try {
                await controller.deleteMenuItem(item.id);
              } catch (e) {
                // Error handled by controller
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Theme.of(Get.context!).colorScheme.error,
              foregroundColor: Theme.of(Get.context!).colorScheme.onError,
            ),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
}
