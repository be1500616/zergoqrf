import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../application/controllers/cart_controller.dart';
import '../../domain/entities/menu_item.dart';

/// Enhanced menu item card with dietary indicators and improved design.
class MenuItemCard extends StatelessWidget {
  const MenuItemCard({
    super.key,
    required this.item,
    required this.cartController,
  });

  final DinerMenuItem item;
  final CartController cartController;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => _showItemDetails(context),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Item image
              _buildItemImage(context),
              const SizedBox(width: 12),

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
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                        if (item.isFeatured)
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 6,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.orange,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              'FEATURED',
                              style: TextStyle(
                                color: colorScheme.onPrimary,
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                      ],
                    ),

                    // Description
                    if (item.description != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        item.description!,
                        style: TextStyle(
                          fontSize: 14,
                          color: colorScheme.onSurfaceVariant,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],

                    const SizedBox(height: 8),

                    // Dietary indicators
                    if (item.dietaryIndicators.isNotEmpty)
                      _buildDietaryIndicators(context),

                    // Allergen info
                    if (item.allergenInfo.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        'Contains: ${item.allergenInfo.join(', ')}',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.red[600],
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ],

                    const SizedBox(height: 8),

                    // Price and preparation time
                    Row(
                      children: [
                        Text(
                          '\$${item.basePrice.toStringAsFixed(2)}',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: colorScheme.primary,
                          ),
                        ),
                        if (item.preparationTime != null) ...[
                          const SizedBox(width: 8),
                          Icon(
                            Icons.access_time,
                            size: 16,
                            color: colorScheme.onSurfaceVariant,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            '${item.preparationTime} min',
                            style: TextStyle(
                              fontSize: 12,
                              color: colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),

              // Add to cart button
              _buildAddButton(context),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildItemImage(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return ClipRRect(
      borderRadius: BorderRadius.circular(8),
      child: SizedBox(
        width: 80,
        height: 80,
        child: item.imageUrl != null
            ? CachedNetworkImage(
                imageUrl: item.imageUrl!,
                fit: BoxFit.cover,
                placeholder: (context, url) {
                  final scheme = Theme.of(context).colorScheme;
                  return Container(
                    color: scheme.surfaceContainerHighest,
                    child: const Center(
                      child: CircularProgressIndicator(),
                    ),
                  );
                },
                errorWidget: (context, url, error) {
                  final scheme = Theme.of(context).colorScheme;
                  return Container(
                    color: scheme.surfaceContainerHighest,
                    child: Icon(
                      Icons.restaurant,
                      color: scheme.onSurfaceVariant,
                    ),
                  );
                },
              )
            : Container(
                color: colorScheme.surfaceContainerHighest,
                child: Icon(
                  Icons.restaurant,
                  color: colorScheme.onSurfaceVariant,
                ),
              ),
      ),
    );
  }

  Widget _buildDietaryIndicators(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Wrap(
      spacing: 4,
      runSpacing: 4,
      children: item.dietaryIndicators.map((indicator) {
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
          decoration: BoxDecoration(
            color: colorScheme.primaryContainer,
            border: Border.all(color: colorScheme.primary),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                indicator.icon,
                style: const TextStyle(fontSize: 12),
              ),
              const SizedBox(width: 2),
              Text(
                indicator.displayName,
                style: TextStyle(
                  fontSize: 10,
                  color: colorScheme.onPrimaryContainer,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildAddButton(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Obx(() {
      final quantity = cartController.getItemQuantity(item.id);

      if (quantity == 0) {
        return ElevatedButton(
          onPressed:
              item.isAvailable ? () => cartController.addItem(item) : null,
          style: ElevatedButton.styleFrom(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          ),
          child: const Text('Add'),
        );
      }

      return Container(
        decoration: BoxDecoration(
          color: colorScheme.primary,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              onPressed: () => cartController.removeItem(item.id),
              icon: Icon(Icons.remove, color: colorScheme.onPrimary, size: 16),
              constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
            ),
            Text(
              quantity.toString(),
              style: TextStyle(
                color: colorScheme.onPrimary,
                fontWeight: FontWeight.bold,
              ),
            ),
            IconButton(
              onPressed: () => cartController.addItem(item),
              icon: Icon(Icons.add, color: colorScheme.onPrimary, size: 16),
              constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
            ),
          ],
        ),
      );
    });
  }

  void _showItemDetails(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _ItemDetailsSheet(
        item: item,
        cartController: cartController,
      ),
    );
  }
}

class _ItemDetailsSheet extends StatelessWidget {
  const _ItemDetailsSheet({
    required this.item,
    required this.cartController,
  });

  final DinerMenuItem item;
  final CartController cartController;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Handle bar
          Container(
            margin: const EdgeInsets.only(top: 12),
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: colorScheme.outlineVariant,
              borderRadius: BorderRadius.circular(2),
            ),
          ),

          // Item image
          if (item.imageUrl != null)
            Container(
              height: 200,
              width: double.infinity,
              margin: const EdgeInsets.all(16),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: CachedNetworkImage(
                  imageUrl: item.imageUrl!,
                  fit: BoxFit.cover,
                  placeholder: (context, url) => Container(
                    color: colorScheme.surfaceContainerHighest,
                    child: const Center(child: CircularProgressIndicator()),
                  ),
                  errorWidget: (context, url, error) => Container(
                    color: colorScheme.surfaceContainerHighest,
                    child: const Icon(Icons.restaurant, size: 48),
                  ),
                ),
              ),
            ),

          // Content
          Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Name and price
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Text(
                        item.name,
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    Text(
                      '\$${item.basePrice.toStringAsFixed(2)}',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: colorScheme.primary,
                      ),
                    ),
                  ],
                ),

                // Description
                if (item.description != null) ...[
                  const SizedBox(height: 12),
                  Text(
                    item.description!,
                    style: const TextStyle(fontSize: 16),
                  ),
                ],

                // Dietary indicators
                if (item.dietaryIndicators.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  const Text(
                    'Dietary Information',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: item.dietaryIndicators.map((indicator) {
                      return Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: colorScheme.primaryContainer,
                          border: Border.all(color: colorScheme.primary),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(indicator.icon,
                                style: const TextStyle(fontSize: 16)),
                            const SizedBox(width: 6),
                            Text(
                              indicator.displayName,
                              style: TextStyle(
                                fontSize: 14,
                                color: colorScheme.onPrimaryContainer,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                      );
                    }).toList(),
                  ),
                ],

                // Allergen info
                if (item.allergenInfo.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  const Text(
                    'Allergen Information',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Contains: ${item.allergenInfo.join(', ')}',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.red[600],
                    ),
                  ),
                ],

                // Preparation time
                if (item.preparationTime != null) ...[
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      const Icon(Icons.access_time, size: 20),
                      const SizedBox(width: 8),
                      Text(
                        'Preparation time: ${item.preparationTime} minutes',
                        style: const TextStyle(fontSize: 14),
                      ),
                    ],
                  ),
                ],

                const SizedBox(height: 24),

                // Add to cart button
                SizedBox(
                  width: double.infinity,
                  child: Obx(() {
                    final quantity = cartController.getItemQuantity(item.id);

                    if (quantity == 0) {
                      return ElevatedButton(
                        onPressed: item.isAvailable
                            ? () {
                                cartController.addItem(item);
                                Navigator.pop(context);
                              }
                            : null,
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: Text(
                          item.isAvailable ? 'Add to Cart' : 'Not Available',
                          style: const TextStyle(fontSize: 16),
                        ),
                      );
                    }

                    return Row(
                      children: [
                        Expanded(
                          child: OutlinedButton(
                            onPressed: () => cartController.removeItem(item.id),
                            style: OutlinedButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 16),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            child: const Text('Remove'),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 20,
                            vertical: 16,
                          ),
                          decoration: BoxDecoration(
                            border: Border.all(color: colorScheme.outline),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            quantity.toString(),
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: ElevatedButton(
                            onPressed: () => cartController.addItem(item),
                            style: ElevatedButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 16),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            child: const Text('Add More'),
                          ),
                        ),
                      ],
                    );
                  }),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
