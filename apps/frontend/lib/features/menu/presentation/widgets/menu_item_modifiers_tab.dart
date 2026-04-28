/// Menu item modifiers tab widget.
/// 
/// This widget provides interface for managing menu item modifiers and add-ons.

import 'package:flutter/material.dart';
import '../../domain/entities/menu_entities.dart';

class MenuItemModifiersTab extends StatelessWidget {
  const MenuItemModifiersTab({
    super.key,
    required this.modifierGroups,
    required this.onModifierGroupsChanged,
  });

  final List<MenuItemModifierGroup> modifierGroups;
  final Function(List<MenuItemModifierGroup>) onModifierGroupsChanged;

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
                'Add-ons & Modifiers',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                      color: Theme.of(context).colorScheme.primary,
                    ),
              ),
              const Spacer(),
              OutlinedButton.icon(
                onPressed: () => _addModifierGroup(context),
                icon: const Icon(Icons.add),
                label: const Text('Add Group'),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Create groups of add-ons like toppings, sides, or customizations',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                ),
          ),
          const SizedBox(height: 24),
          
          // Modifier groups list
          if (modifierGroups.isEmpty)
            _EmptyModifiersState(onAddGroup: () => _addModifierGroup(context))
          else
            ...modifierGroups.asMap().entries.map((entry) {
              final index = entry.key;
              final group = entry.value;
              return _ModifierGroupCard(
                group: group,
                index: index,
                onEdit: () => _editModifierGroup(context, index, group),
                onDelete: () => _deleteModifierGroup(index),
              );
            }),
        ],
      ),
    );
  }

  void _addModifierGroup(BuildContext context) {
    _showModifierGroupDialog(context, null, null);
  }

  void _editModifierGroup(BuildContext context, int index, MenuItemModifierGroup group) {
    _showModifierGroupDialog(context, index, group);
  }

  void _deleteModifierGroup(int index) {
    final newGroups = List<MenuItemModifierGroup>.from(modifierGroups)..removeAt(index);
    onModifierGroupsChanged(newGroups);
  }

  void _showModifierGroupDialog(BuildContext context, int? index, MenuItemModifierGroup? group) {
    showDialog(
      context: context,
      builder: (context) => _ModifierGroupDialog(
        group: group,
        onSave: (newGroup) {
          final newGroups = List<MenuItemModifierGroup>.from(modifierGroups);
          if (index != null) {
            newGroups[index] = newGroup;
          } else {
            newGroups.add(newGroup.copyWith(sortOrder: newGroups.length));
          }
          onModifierGroupsChanged(newGroups);
        },
      ),
    );
  }
}

class _EmptyModifiersState extends StatelessWidget {
  const _EmptyModifiersState({required this.onAddGroup});

  final VoidCallback onAddGroup;

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
            Icons.add_circle_outline,
            size: 48,
            color: Theme.of(context).colorScheme.outline,
          ),
          const SizedBox(height: 16),
          Text(
            'No Add-ons Yet',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Theme.of(context).colorScheme.outline,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Create groups of add-ons like toppings, extras, or customizations',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.outline,
                ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: onAddGroup,
            icon: const Icon(Icons.add),
            label: const Text('Add First Group'),
          ),
        ],
      ),
    );
  }
}

class _ModifierGroupCard extends StatefulWidget {
  const _ModifierGroupCard({
    required this.group,
    required this.index,
    required this.onEdit,
    required this.onDelete,
  });

  final MenuItemModifierGroup group;
  final int index;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  @override
  State<_ModifierGroupCard> createState() => _ModifierGroupCardState();
}

class _ModifierGroupCardState extends State<_ModifierGroupCard> {
  bool _isExpanded = false;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Column(
        children: [
          // Group header
          ListTile(
            leading: Icon(
              _isExpanded ? Icons.expand_less : Icons.expand_more,
              color: Theme.of(context).colorScheme.primary,
            ),
            title: Text(
              widget.group.name,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (widget.group.description != null) ...[
                  Text(widget.group.description!),
                  const SizedBox(height: 4),
                ],
                Row(
                  children: [
                    _TypeChip(type: widget.group.modifierType),
                    const SizedBox(width: 8),
                    if (widget.group.isRequired)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.orange.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(4),
                          border: Border.all(color: Colors.orange.withOpacity(0.3)),
                        ),
                        child: Text(
                          'Required',
                          style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                color: Colors.orange,
                                fontWeight: FontWeight.w500,
                              ),
                        ),
                      ),
                    const SizedBox(width: 8),
                    Text(
                      '${widget.group.modifiers.length} options',
                      style: Theme.of(context).textTheme.labelMedium?.copyWith(
                            color: Theme.of(context).colorScheme.outline,
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
                    color: widget.group.isActive ? Colors.green : Colors.red,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 8),
                // More options
                PopupMenuButton<String>(
                  onSelected: (value) => _handleAction(value),
                  itemBuilder: (context) => [
                    const PopupMenuItem(
                      value: 'edit',
                      child: ListTile(
                        leading: Icon(Icons.edit_outlined),
                        title: Text('Edit Group'),
                        contentPadding: EdgeInsets.zero,
                      ),
                    ),
                    const PopupMenuDivider(),
                    const PopupMenuItem(
                      value: 'delete',
                      child: ListTile(
                        leading: Icon(Icons.delete_outline, color: Colors.red),
                        title: Text('Delete Group', style: TextStyle(color: Colors.red)),
                        contentPadding: EdgeInsets.zero,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            onTap: () {
              setState(() {
                _isExpanded = !_isExpanded;
              });
            },
          ),
          
          // Expandable modifiers list
          if (_isExpanded) ...[
            const Divider(height: 1),
            if (widget.group.modifiers.isEmpty)
              Padding(
                padding: const EdgeInsets.all(16),
                child: Text(
                  'No modifiers in this group',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Theme.of(context).colorScheme.outline,
                      ),
                ),
              )
            else
              ...widget.group.modifiers.map((modifier) => ListTile(
                    leading: const Icon(Icons.circle, size: 8),
                    title: Text(modifier.name),
                    subtitle: modifier.description != null ? Text(modifier.description!) : null,
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        if (modifier.price > 0)
                          Text(
                            '+₹${modifier.price.toStringAsFixed(2)}',
                            style: Theme.of(context).textTheme.labelMedium?.copyWith(
                                  color: Theme.of(context).colorScheme.primary,
                                  fontWeight: FontWeight.w600,
                                ),
                          ),
                        const SizedBox(width: 8),
                        Container(
                          width: 6,
                          height: 6,
                          decoration: BoxDecoration(
                            color: modifier.isActive ? Colors.green : Colors.red,
                            shape: BoxShape.circle,
                          ),
                        ),
                      ],
                    ),
                  )),
          ],
        ],
      ),
    );
  }

  void _handleAction(String action) {
    switch (action) {
      case 'edit':
        widget.onEdit();
        break;
      case 'delete':
        widget.onDelete();
        break;
    }
  }
}

class _TypeChip extends StatelessWidget {
  const _TypeChip({required this.type});

  final ModifierType type;

  @override
  Widget build(BuildContext context) {
    String label;
    Color color;

    switch (type) {
      case ModifierType.singleSelect:
        label = 'Single Select';
        color = Colors.blue;
        break;
      case ModifierType.multiSelect:
        label = 'Multi Select';
        color = Colors.green;
        break;
      case ModifierType.quantity:
        label = 'Quantity';
        color = Colors.purple;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
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

class _ModifierGroupDialog extends StatefulWidget {
  const _ModifierGroupDialog({
    required this.group,
    required this.onSave,
  });

  final MenuItemModifierGroup? group;
  final Function(MenuItemModifierGroup) onSave;

  @override
  State<_ModifierGroupDialog> createState() => _ModifierGroupDialogState();
}

class _ModifierGroupDialogState extends State<_ModifierGroupDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _minSelectionsController = TextEditingController();
  final _maxSelectionsController = TextEditingController();
  
  ModifierType _modifierType = ModifierType.singleSelect;
  bool _isRequired = false;
  bool _isActive = true;
  List<MenuItemModifier> _modifiers = [];

  @override
  void initState() {
    super.initState();
    if (widget.group != null) {
      _nameController.text = widget.group!.name;
      _descriptionController.text = widget.group!.description ?? '';
      _minSelectionsController.text = widget.group!.minSelections.toString();
      _maxSelectionsController.text = widget.group!.maxSelections?.toString() ?? '';
      _modifierType = widget.group!.modifierType;
      _isRequired = widget.group!.isRequired;
      _isActive = widget.group!.isActive;
      _modifiers = List.from(widget.group!.modifiers);
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _minSelectionsController.dispose();
    _maxSelectionsController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Container(
        width: MediaQuery.of(context).size.width * 0.9,
        height: MediaQuery.of(context).size.height * 0.8,
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Text(
              widget.group == null ? 'Add Modifier Group' : 'Edit Modifier Group',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
            ),
            const SizedBox(height: 24),
            
            // Form
            Expanded(
              child: Form(
                key: _formKey,
                child: SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Group name
                      TextFormField(
                        controller: _nameController,
                        decoration: const InputDecoration(
                          labelText: 'Group Name *',
                          hintText: 'e.g., Toppings, Sides, Extras',
                        ),
                        validator: (value) {
                          if (value == null || value.trim().isEmpty) {
                            return 'Please enter a group name';
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
                          hintText: 'Brief description of this group',
                        ),
                        maxLines: 2,
                      ),
                      const SizedBox(height: 16),
                      
                      // Modifier type
                      DropdownButtonFormField<ModifierType>(
                        value: _modifierType,
                        decoration: const InputDecoration(
                          labelText: 'Selection Type',
                        ),
                        items: ModifierType.values.map((type) {
                          String label;
                          String description;
                          
                          switch (type) {
                            case ModifierType.singleSelect:
                              label = 'Single Select';
                              description = 'Customer can select only one option';
                              break;
                            case ModifierType.multiSelect:
                              label = 'Multi Select';
                              description = 'Customer can select multiple options';
                              break;
                            case ModifierType.quantity:
                              label = 'Quantity';
                              description = 'Customer can specify quantity for each option';
                              break;
                          }
                          
                          return DropdownMenuItem<ModifierType>(
                            value: type,
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(label),
                                Text(
                                  description,
                                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                        color: Theme.of(context).colorScheme.outline,
                                      ),
                                ),
                              ],
                            ),
                          );
                        }).toList(),
                        onChanged: (value) {
                          setState(() {
                            _modifierType = value ?? ModifierType.singleSelect;
                          });
                        },
                      ),
                      const SizedBox(height: 16),
                      
                      // Selection constraints
                      if (_modifierType == ModifierType.multiSelect) ...[
                        Row(
                          children: [
                            Expanded(
                              child: TextFormField(
                                controller: _minSelectionsController,
                                decoration: const InputDecoration(
                                  labelText: 'Min Selections',
                                  hintText: '0',
                                ),
                                keyboardType: TextInputType.number,
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: TextFormField(
                                controller: _maxSelectionsController,
                                decoration: const InputDecoration(
                                  labelText: 'Max Selections',
                                  hintText: 'Optional',
                                ),
                                keyboardType: TextInputType.number,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                      ],
                      
                      // Toggles
                      SwitchListTile(
                        title: const Text('Required'),
                        subtitle: const Text('Customer must make a selection'),
                        value: _isRequired,
                        onChanged: (value) {
                          setState(() {
                            _isRequired = value;
                          });
                        },
                      ),
                      SwitchListTile(
                        title: const Text('Active'),
                        subtitle: const Text('Available for customers'),
                        value: _isActive,
                        onChanged: (value) {
                          setState(() {
                            _isActive = value;
                          });
                        },
                      ),
                      const SizedBox(height: 24),
                      
                      // Modifiers section
                      Row(
                        children: [
                          Text(
                            'Options',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.w600,
                                ),
                          ),
                          const Spacer(),
                          OutlinedButton.icon(
                            onPressed: _addModifier,
                            icon: const Icon(Icons.add),
                            label: const Text('Add Option'),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      
                      // Modifiers list
                      if (_modifiers.isEmpty)
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            border: Border.all(
                              color: Theme.of(context).colorScheme.outline.withOpacity(0.3),
                            ),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            'No options added yet',
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                  color: Theme.of(context).colorScheme.outline,
                                ),
                            textAlign: TextAlign.center,
                          ),
                        )
                      else
                        ..._modifiers.asMap().entries.map((entry) {
                          final index = entry.key;
                          final modifier = entry.value;
                          return Card(
                            child: ListTile(
                              title: Text(modifier.name),
                              subtitle: modifier.description != null ? Text(modifier.description!) : null,
                              trailing: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  if (modifier.price > 0)
                                    Text(
                                      '+₹${modifier.price.toStringAsFixed(2)}',
                                      style: Theme.of(context).textTheme.labelMedium?.copyWith(
                                            color: Theme.of(context).colorScheme.primary,
                                            fontWeight: FontWeight.w600,
                                          ),
                                    ),
                                  IconButton(
                                    onPressed: () => _editModifier(index),
                                    icon: const Icon(Icons.edit_outlined),
                                  ),
                                  IconButton(
                                    onPressed: () => _deleteModifier(index),
                                    icon: const Icon(Icons.delete_outline),
                                    color: Theme.of(context).colorScheme.error,
                                  ),
                                ],
                              ),
                            ),
                          );
                        }),
                    ],
                  ),
                ),
              ),
            ),
            
            // Actions
            const SizedBox(height: 24),
            Row(
              children: [
                const Spacer(),
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Cancel'),
                ),
                const SizedBox(width: 16),
                ElevatedButton(
                  onPressed: _saveGroup,
                  child: const Text('Save'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _addModifier() {
    _showModifierDialog(null, null);
  }

  void _editModifier(int index) {
    _showModifierDialog(index, _modifiers[index]);
  }

  void _deleteModifier(int index) {
    setState(() {
      _modifiers.removeAt(index);
    });
  }

  void _showModifierDialog(int? index, MenuItemModifier? modifier) {
    final nameController = TextEditingController(text: modifier?.name ?? '');
    final descriptionController = TextEditingController(text: modifier?.description ?? '');
    final priceController = TextEditingController(text: modifier?.price.toString() ?? '0');
    bool isActive = modifier?.isActive ?? true;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: Text(modifier == null ? 'Add Option' : 'Edit Option'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: const InputDecoration(
                  labelText: 'Option Name *',
                  hintText: 'e.g., Extra Cheese, Large Fries',
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Description (Optional)',
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: priceController,
                decoration: const InputDecoration(
                  labelText: 'Additional Price',
                  prefixText: '₹ ',
                  hintText: '0.00',
                ),
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 16),
              SwitchListTile(
                title: const Text('Active'),
                value: isActive,
                onChanged: (value) {
                  setState(() {
                    isActive = value;
                  });
                },
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                if (nameController.text.trim().isEmpty) return;
                
                final newModifier = MenuItemModifier(
                  id: modifier?.id,
                  name: nameController.text.trim(),
                  description: descriptionController.text.trim().isEmpty
                      ? null
                      : descriptionController.text.trim(),
                  price: double.tryParse(priceController.text) ?? 0,
                  sortOrder: modifier?.sortOrder ?? _modifiers.length,
                  isActive: isActive,
                );

                this.setState(() {
                  if (index != null) {
                    _modifiers[index] = newModifier;
                  } else {
                    _modifiers.add(newModifier);
                  }
                });

                Navigator.of(context).pop();
              },
              child: const Text('Save'),
            ),
          ],
        ),
      ),
    );
  }

  void _saveGroup() {
    if (!_formKey.currentState!.validate()) return;
    if (_modifiers.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please add at least one option')),
      );
      return;
    }

    final group = MenuItemModifierGroup(
      id: widget.group?.id,
      name: _nameController.text.trim(),
      description: _descriptionController.text.trim().isEmpty
          ? null
          : _descriptionController.text.trim(),
      modifierType: _modifierType,
      isRequired: _isRequired,
      minSelections: int.tryParse(_minSelectionsController.text) ?? 0,
      maxSelections: _maxSelectionsController.text.trim().isEmpty
          ? null
          : int.tryParse(_maxSelectionsController.text),
      sortOrder: widget.group?.sortOrder ?? 0,
      isActive: _isActive,
      modifiers: _modifiers,
    );

    widget.onSave(group);
    Navigator.of(context).pop();
  }
}
