import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:zergo_frontend/features/menu/application/controllers/menu_management_controller.dart';
import 'package:zergo_frontend/features/menu/domain/entities/menu_entities.dart';

class EditCategoryDialog extends StatefulWidget {
  final MenuCategory category;

  const EditCategoryDialog({super.key, required this.category});

  @override
  State<EditCategoryDialog> createState() => _EditCategoryDialogState();
}

class _EditCategoryDialogState extends State<EditCategoryDialog> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameController;
  late TextEditingController _descriptionController;
  String? _selectedParentId;
  final MenuManagementController _controller = Get.find<MenuManagementController>();

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.category.name);
    _descriptionController = TextEditingController(text: widget.category.description);
    _selectedParentId = widget.category.parentCategoryId;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Edit Category'),
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
                ..._controller.rootCategories
                    .where((category) => category.id != widget.category.id)
                    .map((category) {
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
          onPressed: _updateCategory,
          child: const Text('Update'),
        ),
      ],
    );
  }

  void _updateCategory() async {
    if (!_formKey.currentState!.validate()) return;

    try {
      await _controller.updateCategory(
        widget.category.id,
        {
          'name': _nameController.text.trim(),
          'description': _descriptionController.text.trim().isEmpty
              ? null
              : _descriptionController.text.trim(),
          'parent_category_id': _selectedParentId,
        },
      );
      Navigator.of(context).pop();
    } catch (e) {
      // Error is handled by controller
    }
  }
}