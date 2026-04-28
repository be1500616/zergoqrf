/// Menu item pricing tab widget.
/// 
/// This widget provides interface for managing menu item variants and pricing.

import 'package:flutter/material.dart';
import '../../domain/entities/menu_entities.dart';

class MenuItemPricingTab extends StatelessWidget {
  const MenuItemPricingTab({
    super.key,
    required this.variants,
    required this.onVariantsChanged,
  });

  final List<MenuItemVariant> variants;
  final Function(List<MenuItemVariant>) onVariantsChanged;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Text(
                'Size Variants',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                      color: Theme.of(context).colorScheme.primary,
                    ),
              ),
              const Spacer(),
              OutlinedButton.icon(
                onPressed: () => _addVariant(context),
                icon: const Icon(Icons.add),
                label: const Text('Add Variant'),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Create different sizes or options for this item with price adjustments',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                ),
          ),
          const SizedBox(height: 24),
          
          // Variants list
          if (variants.isEmpty)
            _EmptyVariantsState(onAddVariant: () => _addVariant(context))
          else
            ...variants.asMap().entries.map((entry) {
              final index = entry.key;
              final variant = entry.value;
              return _VariantCard(
                variant: variant,
                index: index,
                onEdit: () => _editVariant(context, index, variant),
                onDelete: () => _deleteVariant(index),
                onReorder: (oldIndex, newIndex) => _reorderVariants(oldIndex, newIndex),
              );
            }),
        ],
      ),
    );
  }

  void _addVariant(BuildContext context) {
    _showVariantDialog(context, null, null);
  }

  void _editVariant(BuildContext context, int index, MenuItemVariant variant) {
    _showVariantDialog(context, index, variant);
  }

  void _deleteVariant(int index) {
    final newVariants = List<MenuItemVariant>.from(variants)..removeAt(index);
    onVariantsChanged(newVariants);
  }

  void _reorderVariants(int oldIndex, int newIndex) {
    final newVariants = List<MenuItemVariant>.from(variants);
    final variant = newVariants.removeAt(oldIndex);
    newVariants.insert(newIndex, variant);
    
    // Update sort orders
    for (int i = 0; i < newVariants.length; i++) {
      newVariants[i] = newVariants[i].copyWith(sortOrder: i);
    }
    
    onVariantsChanged(newVariants);
  }

  void _showVariantDialog(BuildContext context, int? index, MenuItemVariant? variant) {
    showDialog(
      context: context,
      builder: (context) => _VariantDialog(
        variant: variant,
        onSave: (newVariant) {
          final newVariants = List<MenuItemVariant>.from(variants);
          if (index != null) {
            newVariants[index] = newVariant;
          } else {
            newVariants.add(newVariant.copyWith(sortOrder: newVariants.length));
          }
          onVariantsChanged(newVariants);
        },
      ),
    );
  }
}

class _EmptyVariantsState extends StatelessWidget {
  const _EmptyVariantsState({required this.onAddVariant});

  final VoidCallback onAddVariant;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        border: Border.all(
          color: Theme.of(context).colorScheme.outline.withOpacity(0.3),
        ),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(
            Icons.straighten_outlined,
            size: 48,
            color: Theme.of(context).colorScheme.outline,
          ),
          const SizedBox(height: 16),
          Text(
            'No Size Variants',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Theme.of(context).colorScheme.outline,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Add different sizes like Small, Medium, Large with price adjustments',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.outline,
                ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: onAddVariant,
            icon: const Icon(Icons.add),
            label: const Text('Add First Variant'),
          ),
        ],
      ),
    );
  }
}

class _VariantCard extends StatelessWidget {
  const _VariantCard({
    required this.variant,
    required this.index,
    required this.onEdit,
    required this.onDelete,
    required this.onReorder,
  });

  final MenuItemVariant variant;
  final int index;
  final VoidCallback onEdit;
  final VoidCallback onDelete;
  final Function(int, int) onReorder;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: ReorderableDragStartListener(
          index: index,
          child: Icon(
            Icons.drag_handle,
            color: Theme.of(context).colorScheme.outline,
          ),
        ),
        title: Text(
          variant.name,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (variant.description != null) ...[
              Text(variant.description!),
              const SizedBox(height: 4),
            ],
            Row(
              children: [
                Text(
                  'Price Adjustment: ',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                Text(
                  variant.priceAdjustment >= 0
                      ? '+₹${variant.priceAdjustment.toStringAsFixed(2)}'
                      : '-₹${(-variant.priceAdjustment).toStringAsFixed(2)}',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: variant.priceAdjustment >= 0
                            ? Colors.green
                            : Colors.red,
                        fontWeight: FontWeight.w600,
                      ),
                ),
              ],
            ),
          ],
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Active/Inactive indicator
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                color: variant.isActive ? Colors.green : Colors.red,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 8),
            // Edit button
            IconButton(
              onPressed: onEdit,
              icon: const Icon(Icons.edit_outlined),
            ),
            // Delete button
            IconButton(
              onPressed: onDelete,
              icon: const Icon(Icons.delete_outline),
              color: Theme.of(context).colorScheme.error,
            ),
          ],
        ),
      ),
    );
  }
}

class _VariantDialog extends StatefulWidget {
  const _VariantDialog({
    required this.variant,
    required this.onSave,
  });

  final MenuItemVariant? variant;
  final Function(MenuItemVariant) onSave;

  @override
  State<_VariantDialog> createState() => _VariantDialogState();
}

class _VariantDialogState extends State<_VariantDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _priceAdjustmentController = TextEditingController();
  bool _isActive = true;

  @override
  void initState() {
    super.initState();
    if (widget.variant != null) {
      _nameController.text = widget.variant!.name;
      _descriptionController.text = widget.variant!.description ?? '';
      _priceAdjustmentController.text = widget.variant!.priceAdjustment.toString();
      _isActive = widget.variant!.isActive;
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _priceAdjustmentController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.variant == null ? 'Add Variant' : 'Edit Variant'),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Variant name
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'Variant Name *',
                hintText: 'e.g., Small, Medium, Large',
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter a variant name';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            
            // Description
            TextFormField(
              controller: _descriptionController,
              decoration: const InputDecoration(
                labelText: 'Description (Optional)',
                hintText: 'e.g., Serves 1-2 people',
              ),
              maxLines: 2,
            ),
            const SizedBox(height: 16),
            
            // Price adjustment
            TextFormField(
              controller: _priceAdjustmentController,
              decoration: const InputDecoration(
                labelText: 'Price Adjustment *',
                hintText: '0.00',
                prefixText: '₹ ',
                helperText: 'Use negative values for discounts',
              ),
              keyboardType: const TextInputType.numberWithOptions(
                decimal: true,
                signed: true,
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter a price adjustment';
                }
                if (double.tryParse(value) == null) {
                  return 'Please enter a valid number';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            
            // Active toggle
            SwitchListTile(
              title: const Text('Active'),
              subtitle: const Text('Available for customers to select'),
              value: _isActive,
              onChanged: (value) {
                setState(() {
                  _isActive = value;
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
          onPressed: _saveVariant,
          child: const Text('Save'),
        ),
      ],
    );
  }

  void _saveVariant() {
    if (!_formKey.currentState!.validate()) return;

    final variant = MenuItemVariant(
      id: widget.variant?.id,
      name: _nameController.text.trim(),
      description: _descriptionController.text.trim().isEmpty
          ? null
          : _descriptionController.text.trim(),
      priceAdjustment: double.parse(_priceAdjustmentController.text),
      sortOrder: widget.variant?.sortOrder ?? 0,
      isActive: _isActive,
    );

    widget.onSave(variant);
    Navigator.of(context).pop();
  }
}
