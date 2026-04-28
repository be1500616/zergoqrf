/// Menu preview tab widget.
///
/// This widget provides a real-time preview of how the menu will appear
/// to customers accessing via QR code.
library;

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../application/controllers/menu_management_controller.dart';
import '../../application/controllers/menu_preview_controller.dart';
import '../../domain/entities/menu_entities.dart';

class MenuPreviewTab extends GetView<MenuManagementController> {
  const MenuPreviewTab({super.key});

  MenuPreviewController get _previewController =>
      Get.find<MenuPreviewController>();

  @override
  Widget build(BuildContext context) {
    return Obx(() => Column(
          children: [
            // Preview controls
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surface,
                border: Border(
                  bottom: BorderSide(
                    color:
                        Theme.of(context).colorScheme.outline.withOpacity(0.2),
                  ),
                ),
              ),
              child: Column(
                children: [
                  // Device selector
                  Row(
                    children: [
                      Text(
                        'Preview Device:',
                        style: Theme.of(context).textTheme.labelLarge,
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: SegmentedButton<String>(
                          segments: const [
                            ButtonSegment(
                              value: 'mobile',
                              label: Text('Mobile'),
                              icon: Icon(Icons.phone_android),
                            ),
                            ButtonSegment(
                              value: 'tablet',
                              label: Text('Tablet'),
                              icon: Icon(Icons.tablet),
                            ),
                          ],
                          selected: {_previewController.selectedDevice},
                          onSelectionChanged: (Set<String> selection) {
                            _previewController
                                .updateSelectedDevice(selection.first);
                          },
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  // Display options
                  Row(
                    children: [
                      Expanded(
                        child: CheckboxListTile(
                          title: const Text('Show Prices'),
                          value: _previewController.showPrices,
                          onChanged: (value) {
                            _previewController.togglePrices(value ?? true);
                          },
                          dense: true,
                          contentPadding: EdgeInsets.zero,
                        ),
                      ),
                      Expanded(
                        child: CheckboxListTile(
                          title: const Text('Show Descriptions'),
                          value: _previewController.showDescriptions,
                          onChanged: (value) {
                            _previewController
                                .toggleDescriptions(value ?? true);
                          },
                          dense: true,
                          contentPadding: EdgeInsets.zero,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // Preview area
            Expanded(
              child: Container(
                color: Theme.of(context)
                    .colorScheme
                    .surfaceContainerHighest
                    .withOpacity(0.3),
                child: Center(
                  child: Container(
                    width: _previewController.getDeviceWidth(),
                    height: double.infinity,
                    margin: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.surface,
                      borderRadius: BorderRadius.circular(12),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 10,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: _buildMenuPreview(context),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ));
  }

  Widget _buildMenuPreview(BuildContext context) {
    return Obx(() {
      if (controller.categories.isEmpty) {
        return _EmptyMenuPreview();
      }

      return Column(
        children: [
          // Preview header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primaryContainer,
              border: Border(
                bottom: BorderSide(
                  color: Theme.of(context).colorScheme.outline.withOpacity(0.2),
                ),
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.qr_code,
                  color: Theme.of(context).colorScheme.onPrimaryContainer,
                ),
                const SizedBox(width: 8),
                Text(
                  'Customer Menu View',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: Theme.of(context).colorScheme.onPrimaryContainer,
                        fontWeight: FontWeight.w600,
                      ),
                ),
                const Spacer(),
                if (controller.currentVersion != null)
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.primary,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      'LIVE',
                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                            color: Theme.of(context).colorScheme.onPrimary,
                            fontWeight: FontWeight.w600,
                          ),
                    ),
                  ),
              ],
            ),
          ),

          // Menu content
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: controller.rootCategories.length,
              itemBuilder: (context, index) {
                final category = controller.rootCategories[index];
                return _PreviewCategorySection(
                  category: category,
                  controller: controller,
                  showPrices: _previewController.showPrices,
                  showDescriptions: _previewController.showDescriptions,
                );
              },
            ),
          ),
        ],
      );
    });
  }
}

class _EmptyMenuPreview extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.preview_outlined,
            size: 64,
            color: Theme.of(context).colorScheme.outline,
          ),
          const SizedBox(height: 16),
          Text(
            'No Menu to Preview',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  color: Theme.of(context).colorScheme.outline,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Create categories and items to see the preview',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.outline,
                ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class _PreviewCategorySection extends StatelessWidget {
  const _PreviewCategorySection({
    required this.category,
    required this.controller,
    required this.showPrices,
    required this.showDescriptions,
  });

  final MenuCategory category;
  final MenuManagementController controller;
  final bool showPrices;
  final bool showDescriptions;

  @override
  Widget build(BuildContext context) {
    final items = controller.getCategoryItems(category.id);

    if (items.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Category header
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                category.name,
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: Theme.of(context).colorScheme.primary,
                    ),
              ),
              if (category.description != null && showDescriptions) ...[
                const SizedBox(height: 4),
                Text(
                  category.description!,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Theme.of(context)
                            .colorScheme
                            .onSurface
                            .withOpacity(0.7),
                      ),
                ),
              ],
            ],
          ),
        ),

        // Category items
        ...items.map((item) => _PreviewMenuItem(
              item: item,
              showPrices: showPrices,
              showDescriptions: showDescriptions,
            )),

        const SizedBox(height: 24),
      ],
    );
  }
}

class _PreviewMenuItem extends StatelessWidget {
  const _PreviewMenuItem({
    required this.item,
    required this.showPrices,
    required this.showDescriptions,
  });

  final MenuItem item;
  final bool showPrices;
  final bool showDescriptions;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Theme.of(context).colorScheme.outline.withOpacity(0.2),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Item image
          if (item.imageUrl != null) ...[
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(8),
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.network(
                  item.imageUrl!,
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) => Icon(
                    Icons.restaurant,
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 16),
          ],

          // Item details
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Name and dietary indicators
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        item.name,
                        style:
                            Theme.of(context).textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.w600,
                                ),
                      ),
                    ),
                    if (item.dietaryIndicators.isNotEmpty) ...[
                      const SizedBox(width: 8),
                      Wrap(
                        spacing: 4,
                        children:
                            item.dietaryIndicators.take(3).map((indicator) {
                          return Container(
                            width: 16,
                            height: 16,
                            decoration: BoxDecoration(
                              color: _getDietaryColor(indicator),
                              shape: BoxShape.circle,
                            ),
                            child: Center(
                              child: Text(
                                _getDietaryEmoji(indicator),
                                style: const TextStyle(fontSize: 8),
                              ),
                            ),
                          );
                        }).toList(),
                      ),
                    ],
                  ],
                ),

                // Description
                if (item.description != null && showDescriptions) ...[
                  const SizedBox(height: 8),
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

                // Price and variants
                if (showPrices) ...[
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Text(
                        '₹${item.basePrice.toStringAsFixed(2)}',
                        style:
                            Theme.of(context).textTheme.titleMedium?.copyWith(
                                  color: Theme.of(context).colorScheme.primary,
                                  fontWeight: FontWeight.w700,
                                ),
                      ),
                      if (item.variants.isNotEmpty) ...[
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: Theme.of(context)
                                .colorScheme
                                .secondaryContainer,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            '${item.variants.length} sizes',
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
                    ],
                  ),
                ],

                // Preparation time
                if (item.preparationTime != null) ...[
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(
                        Icons.access_time,
                        size: 16,
                        color: Theme.of(context).colorScheme.outline,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '${item.preparationTime} min',
                        style:
                            Theme.of(context).textTheme.labelMedium?.copyWith(
                                  color: Theme.of(context).colorScheme.outline,
                                ),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Color _getDietaryColor(DietaryIndicator indicator) {
    switch (indicator) {
      case DietaryIndicator.vegetarian:
        return Colors.green;
      case DietaryIndicator.vegan:
        return Colors.lightGreen;
      case DietaryIndicator.glutenFree:
        return Colors.orange;
      case DietaryIndicator.keto:
        return Colors.purple;
      case DietaryIndicator.spicy:
        return Colors.red;
      case DietaryIndicator.halal:
        return Colors.blue;
      case DietaryIndicator.kosher:
        return Colors.indigo;
    }
  }

  String _getDietaryEmoji(DietaryIndicator indicator) {
    switch (indicator) {
      case DietaryIndicator.vegetarian:
        return '🥗';
      case DietaryIndicator.vegan:
        return '🌱';
      case DietaryIndicator.glutenFree:
        return '🌾';
      case DietaryIndicator.keto:
        return '🥑';
      case DietaryIndicator.spicy:
        return '🌶️';
      case DietaryIndicator.halal:
        return '☪️';
      case DietaryIndicator.kosher:
        return '✡️';
    }
  }
}
