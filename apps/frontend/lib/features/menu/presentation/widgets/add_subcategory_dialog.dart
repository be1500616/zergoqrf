import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:zergo_frontend/features/menu/application/controllers/menu_management_controller.dart';
import 'package:zergo_frontend/features/menu/domain/entities/menu_entities.dart';

class AddSubcategoryDialog extends StatefulWidget {
  final MenuCategory parentCategory;

  const AddSubcategoryDialog({super.key, required this.parentCategory});

  @override
  State<AddSubcategoryDialog> createState() => _AddSubcategoryDialogState();
}

class _AddSubcategoryDialogState extends State<AddSubcategoryDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final MenuManagementController _controller = Get.find<MenuManagementController>();

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Add Subcategory to ${widget.parentCategory.name}'),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'Subcategory Name',
                hintText: 'e.g., Soups, Salads',
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter a subcategory name';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _descriptionController,
              decoration: const InputDecoration(
                labelText: 'Description (Optional)',
                hintText: 'Brief description of the subcategory',
              ),
              maxLines: 2,
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
          onPressed: _createSubcategory,
          child: const Text('Create'),
        ),
      ],
    );
  }

  void _createSubcategory() async {
    if (!_formKey.currentState!.validate()) return;

    try {
      await _controller.createCategory(
        name: _nameController.text.trim(),
        description: _descriptionController.text.trim().isEmpty
            ? null
            : _descriptionController.text.trim(),
        parentCategoryId: widget.parentCategory.id,
      );
      Navigator.of(context).pop();
    } catch (e) {
      // Error is handled by controller
    }
  }
}