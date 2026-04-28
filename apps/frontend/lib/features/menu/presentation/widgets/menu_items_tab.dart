/// Menu items tab widget.
///
/// This widget displays all menu items with filtering and search capabilities.
library;

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../application/controllers/menu_items_controller.dart';
import '../../application/controllers/menu_management_controller.dart';
import '../../domain/entities/menu_entities.dart';

class MenuItemsTab extends GetView<MenuItemsController> {
  const MenuItemsTab({super.key});

  @override
  Widget build(BuildContext context) {
    final menuController = Get.find<MenuManagementController>();

    return Column(
      children: [
        // Search and filter bar
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            border: Border(
              bottom: BorderSide(
                color: Theme.of(context).colorScheme.outline.withOpacity(0.2),
              ),
            ),
          ),
          child: Column(
            children: [
              // Search bar
              TextField(
                controller: controller.searchController,
                decoration: InputDecoration(
                  hintText: 'Search menu items...',
                  prefixIcon: const Icon(Icons.search),
                  suffixIcon: Obx(() => controller.searchQuery.value.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.clear),
                          onPressed: () {
                            controller.clearSearch();
                          },
                        )
                      : const SizedBox.shrink()),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                onChanged: (value) {
                  // Search is handled by controller listener
                },
              ),
              const SizedBox(height: 12),
              // Filter chips
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    // Category filter
                    Obx(() => FilterChip(
                          label: Text(controller.selectedCategoryId.value ==
                                  null
                              ? 'All Categories'
                              : menuController.categories
                                      .firstWhereOrNull((c) =>
                                          c.id ==
                                          controller.selectedCategoryId.value)
                                      ?.name ??
                                  'Unknown'),
                          selected: controller.selectedCategoryId.value != null,
                          onSelected: (selected) =>
                              _showCategoryFilter(context),
                        )),
                    const SizedBox(width: 8),
                    // Status filter
                    Obx(() => FilterChip(
                          label: Text(controller
                                  .selectedStatus.value?.name.capitalize ??
                              'All Status'),
                          selected: controller.selectedStatus.value != null,
                          onSelected: (selected) => _showStatusFilter(context),
                        )),
                    const SizedBox(width: 8),
                    // Clear filters
                    Obx(() => (controller.selectedCategoryId.value != null ||
                            controller.selectedStatus.value != null)
                        ? ActionChip(
                            label: const Text('Clear Filters'),
                            onPressed: () {
                              controller.clearFilters();
                            },
                          )
                        : const SizedBox.shrink()),
                  ],
                ),
              ),
            ],
          ),
        ),

        // Items list
        Expanded(
          child: Obx(() {
            final allItems = menuController.menuItems;
            final filteredItems = controller.getFilteredItems(allItems);

            if (filteredItems.isEmpty) {
              return _EmptyState(
                hasFilters: controller.searchQuery.value.isNotEmpty ||
                    controller.selectedCategoryId.value != null ||
                    controller.selectedStatus.value != null,
              );
            }

            return RefreshIndicator(
              onRefresh: () => menuController.loadMenuItems(),
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: filteredItems.length,
                itemBuilder: (context, index) {
                  final item = filteredItems[index];
                  return _MenuItemCard(
                    item: item,
                    controller: menuController,
                  );
                },
              ),
            );
          }),
        ),
      ],
    );
  }

  void _showCategoryFilter(BuildContext context) {
    final menuController = Get.find<MenuManagementController>();
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Filter by Category',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            ListTile(
              title: const Text('All Categories'),
              leading: Radio<String?>(
                value: null,
                groupValue: controller.selectedCategoryId.value,
                onChanged: (value) {
                  controller.setCategoryFilter(value);
                  Navigator.pop(context);
                },
              ),
            ),
            ...menuController.categories.map((category) => ListTile(
                  title: Text(category.name),
                  leading: Radio<String?>(
                    value: category.id,
                    groupValue: controller.selectedCategoryId.value,
                    onChanged: (value) {
                      controller.setCategoryFilter(value);
                      Navigator.pop(context);
                    },
                  ),
                )),
          ],
        ),
      ),
    );
  }

  void _showStatusFilter(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Filter by Status',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            ListTile(
              title: const Text('All Status'),
              leading: Radio<ItemStatus?>(
                value: null,
                groupValue: controller.selectedStatus.value,
                onChanged: (value) {
                  controller.setStatusFilter(value);
                  Navigator.pop(context);
                },
              ),
            ),
            ...ItemStatus.values.map((status) => ListTile(
                  title: Text(status.name.capitalize ?? ''),
                  leading: Radio<ItemStatus?>(
                    value: status,
                    groupValue: controller.selectedStatus.value,
                    onChanged: (value) {
                      controller.setStatusFilter(value);
                      Navigator.pop(context);
                    },
                  ),
                )),
          ],
        ),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState({required this.hasFilters});

  final bool hasFilters;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            hasFilters ? Icons.search_off : Icons.restaurant_menu_outlined,
            size: 64,
            color: Theme.of(context).colorScheme.outline,
          ),
          const SizedBox(height: 16),
          Text(
            hasFilters ? 'No items found' : 'No Menu Items Yet',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  color: Theme.of(context).colorScheme.outline,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            hasFilters
                ? 'Try adjusting your search or filters'
                : 'Create your first menu item to get started',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.outline,
                ),
            textAlign: TextAlign.center,
          ),
          if (!hasFilters) ...[
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => Get.toNamed('/menu/item/create'),
              icon: const Icon(Icons.add),
              label: const Text('Create Menu Item'),
            ),
          ],
        ],
      ),
    );
  }
}

class _MenuItemCard extends StatelessWidget {
  const _MenuItemCard({
    required this.item,
    required this.controller,
  });

  final MenuItem item;
  final MenuManagementController controller;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => Get.toNamed('/menu/item/${item.id}'),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // Item image
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(8),
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                ),
                child: item.imageUrl != null
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.network(
                          item.imageUrl!,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) => Icon(
                            Icons.restaurant,
                            color:
                                Theme.of(context).colorScheme.onSurfaceVariant,
                          ),
                        ),
                      )
                    : Icon(
                        Icons.restaurant,
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
              ),
              const SizedBox(width: 16),

              // Item details
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Name and status
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            item.name,
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(
                                  fontWeight: FontWeight.w600,
                                ),
                          ),
                        ),
                        _StatusChip(status: item.status),
                      ],
                    ),

                    // Description
                    if (item.description != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        item.description!,
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: Theme.of(context)
                                  .colorScheme
                                  .onSurface
                                  .withOpacity(0.7),
                            ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],

                    const SizedBox(height: 8),

                    // Price and category
                    Row(
                      children: [
                        Text(
                          '₹${item.basePrice.toStringAsFixed(2)}',
                          style: Theme.of(context)
                              .textTheme
                              .titleMedium
                              ?.copyWith(
                                color: Theme.of(context).colorScheme.primary,
                                fontWeight: FontWeight.w600,
                              ),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: Theme.of(context)
                                .colorScheme
                                .secondaryContainer,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            item.categoryName ?? 'Unknown Category',
                            style: Theme.of(context)
                                .textTheme
                                .labelSmall
                                ?.copyWith(
                                  color: Theme.of(context)
                                      .colorScheme
                                      .onSecondaryContainer,
                                ),
                          ),
                        ),
                      ],
                    ),

                    // Dietary indicators
                    if (item.dietaryIndicators.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 4,
                        children: item.dietaryIndicators
                            .map((indicator) =>
                                _DietaryChip(indicator: indicator))
                            .toList(),
                      ),
                    ],
                  ],
                ),
              ),

              // Actions
              PopupMenuButton<String>(
                onSelected: (value) => _handleAction(value),
                itemBuilder: (context) => [
                  const PopupMenuItem(
                    value: 'edit',
                    child: ListTile(
                      leading: Icon(Icons.edit_outlined),
                      title: Text('Edit'),
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
                      title:
                          Text('Delete', style: TextStyle(color: Colors.red)),
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _handleAction(String action) {
    switch (action) {
      case 'edit':
        Get.toNamed('/menu/item', arguments: {'itemId': item.id});
        break;
      case 'duplicate':
        controller.duplicateMenuItem(item.id);
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
        content: Text('Are you sure you want to delete "${item.name}"?'),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              Get.back();
              await controller.deleteMenuItem(item.id);
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

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.status});

  final ItemStatus status;

  @override
  Widget build(BuildContext context) {
    Color color;
    String label;

    switch (status) {
      case ItemStatus.available:
        color = Colors.green;
        label = 'Available';
        break;
      case ItemStatus.unavailable:
        color = Colors.red;
        label = 'Unavailable';
        break;
      case ItemStatus.seasonal:
        color = Colors.orange;
        label = 'Seasonal';
        break;
      case ItemStatus.featured:
        color = Colors.blue;
        label = 'Featured';
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w500,
            ),
      ),
    );
  }
}

class _DietaryChip extends StatelessWidget {
  const _DietaryChip({required this.indicator});

  final DietaryIndicator indicator;

  @override
  Widget build(BuildContext context) {
    String emoji;
    String label;

    switch (indicator) {
      case DietaryIndicator.vegetarian:
        emoji = '🥗';
        label = 'Veg';
        break;
      case DietaryIndicator.vegan:
        emoji = '🌱';
        label = 'Vegan';
        break;
      case DietaryIndicator.glutenFree:
        emoji = '🌾';
        label = 'GF';
        break;
      case DietaryIndicator.keto:
        emoji = '🥑';
        label = 'Keto';
        break;
      case DietaryIndicator.spicy:
        emoji = '🌶️';
        label = 'Spicy';
        break;
      case DietaryIndicator.halal:
        emoji = '☪️';
        label = 'Halal';
        break;
      case DietaryIndicator.kosher:
        emoji = '✡️';
        label = 'Kosher';
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.primaryContainer,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(emoji, style: const TextStyle(fontSize: 10)),
          const SizedBox(width: 2),
          Text(
            label,
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  color: Theme.of(context).colorScheme.onPrimaryContainer,
                ),
          ),
        ],
      ),
    );
  }
}
