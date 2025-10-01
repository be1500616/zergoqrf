/// Add staff dialog widget.
///
/// This widget provides a dialog for adding or editing staff members.
library;

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../application/restaurant_controller.dart';
import '../../domain/restaurant_entity.dart';

class AddStaffDialog extends StatefulWidget {
  final RestaurantStaff? staff;

  const AddStaffDialog({super.key, this.staff});

  @override
  State<AddStaffDialog> createState() => _AddStaffDialogState();
}

class _AddStaffDialogState extends State<AddStaffDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  String _selectedRole = 'service';
  final Map<String, bool> _permissions = {
    'manage_restaurant': false,
    'manage_menu': false,
    'manage_orders': false,
    'manage_tables': false,
    'manage_staff': false,
    'view_analytics': false,
    'manage_payments': false,
  };

  bool _isEditing = false;
  bool _obscurePassword = true;

  @override
  void initState() {
    super.initState();
    _isEditing = widget.staff != null;

    if (_isEditing) {
      _loadStaffData();
    } else {
      _setDefaultPermissions();
    }
  }

  void _loadStaffData() {
    final staff = widget.staff!;
    _nameController.text = staff.name ?? '';
    _emailController.text = staff.email ?? '';
    _selectedRole = staff.role;

    // Load permissions
    staff.permissions.forEach((key, value) {
      if (_permissions.containsKey(key)) {
        _permissions[key] = value == true;
      }
    });
  }

  void _setDefaultPermissions() {
    switch (_selectedRole) {
      case 'manager':
        _permissions['manage_menu'] = true;
        _permissions['manage_orders'] = true;
        _permissions['manage_tables'] = true;
        _permissions['view_analytics'] = true;
        break;
      case 'kitchen':
        _permissions['manage_orders'] = true;
        break;
      case 'service':
        _permissions['manage_orders'] = true;
        _permissions['manage_tables'] = true;
        break;
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Container(
        width: MediaQuery.of(context).size.width * 0.9,
        constraints: const BoxConstraints(maxWidth: 500, maxHeight: 600),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Header
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.blue[600],
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(8),
                  topRight: Radius.circular(8),
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    _isEditing ? Icons.edit : Icons.person_add,
                    color: Colors.white,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      _isEditing ? 'Edit Staff Member' : 'Add Staff Member',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: () => Navigator.of(context).pop(),
                    icon: const Icon(Icons.close, color: Colors.white),
                  ),
                ],
              ),
            ),

            // Content
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Basic Information
                      const Text(
                        'Basic Information',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 12),

                      TextFormField(
                        controller: _nameController,
                        decoration: const InputDecoration(
                          labelText: 'Full Name',
                          border: OutlineInputBorder(),
                          prefixIcon: Icon(Icons.person),
                        ),
                        validator: (value) {
                          if (value == null || value.trim().isEmpty) {
                            return 'Name is required';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),

                      TextFormField(
                        controller: _emailController,
                        decoration: const InputDecoration(
                          labelText: 'Email Address',
                          border: OutlineInputBorder(),
                          prefixIcon: Icon(Icons.email),
                        ),
                        keyboardType: TextInputType.emailAddress,
                        enabled: !_isEditing, // Can't change email when editing
                        validator: (value) {
                          if (value == null || value.trim().isEmpty) {
                            return 'Email is required';
                          }
                          if (!GetUtils.isEmail(value)) {
                            return 'Please enter a valid email';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),

                      if (!_isEditing)
                        TextFormField(
                          controller: _passwordController,
                          decoration: InputDecoration(
                            labelText: 'Password',
                            border: const OutlineInputBorder(),
                            prefixIcon: const Icon(Icons.lock),
                            suffixIcon: IconButton(
                              icon: Icon(
                                _obscurePassword
                                    ? Icons.visibility
                                    : Icons.visibility_off,
                              ),
                              onPressed: () {
                                setState(() {
                                  _obscurePassword = !_obscurePassword;
                                });
                              },
                            ),
                          ),
                          obscureText: _obscurePassword,
                          validator: (value) {
                            if (!_isEditing &&
                                (value == null || value.length < 8)) {
                              return 'Password must be at least 8 characters';
                            }
                            return null;
                          },
                        ),

                      if (!_isEditing) const SizedBox(height: 24),

                      // Role Selection
                      const Text(
                        'Role',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 12),

                      DropdownButtonFormField<String>(
                        value: _selectedRole,
                        decoration: const InputDecoration(
                          border: OutlineInputBorder(),
                          prefixIcon: Icon(Icons.work),
                        ),
                        items: const [
                          DropdownMenuItem(
                              value: 'manager', child: Text('Manager')),
                          DropdownMenuItem(
                              value: 'kitchen', child: Text('Kitchen Staff')),
                          DropdownMenuItem(
                              value: 'service', child: Text('Service Staff')),
                        ],
                        onChanged: _isEditing && widget.staff?.role == 'owner'
                            ? null // Can't change owner role
                            : (value) {
                                setState(() {
                                  _selectedRole = value!;
                                  _setDefaultPermissions();
                                });
                              },
                      ),
                      const SizedBox(height: 24),

                      // Permissions
                      const Text(
                        'Permissions',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 12),

                      ..._permissions.entries.map((entry) {
                        return CheckboxListTile(
                          title: Text(_getPermissionDisplayName(entry.key)),
                          subtitle: Text(_getPermissionDescription(entry.key)),
                          value: entry.value,
                          onChanged: (value) {
                            setState(() {
                              _permissions[entry.key] = value ?? false;
                            });
                          },
                          contentPadding: EdgeInsets.zero,
                        );
                      }),
                    ],
                  ),
                ),
              ),
            ),

            // Actions
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey[50],
                borderRadius: const BorderRadius.only(
                  bottomLeft: Radius.circular(8),
                  bottomRight: Radius.circular(8),
                ),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.of(context).pop(),
                      child: const Text('Cancel'),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: _saveStaff,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue[600],
                        foregroundColor: Colors.white,
                      ),
                      child: Text(_isEditing ? 'Update' : 'Add Staff'),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getPermissionDisplayName(String permission) {
    switch (permission) {
      case 'manage_restaurant':
        return 'Manage Restaurant';
      case 'manage_menu':
        return 'Manage Menu';
      case 'manage_orders':
        return 'Manage Orders';
      case 'manage_tables':
        return 'Manage Tables';
      case 'manage_staff':
        return 'Manage Staff';
      case 'view_analytics':
        return 'View Analytics';
      case 'manage_payments':
        return 'Manage Payments';
      default:
        return StringExtension(permission.replaceAll('_', ' ')).capitalize ??
            permission;
    }
  }

  String _getPermissionDescription(String permission) {
    switch (permission) {
      case 'manage_restaurant':
        return 'Edit restaurant information and settings';
      case 'manage_menu':
        return 'Add, edit, and remove menu items';
      case 'manage_orders':
        return 'View and process customer orders';
      case 'manage_tables':
        return 'Manage table assignments and status';
      case 'manage_staff':
        return 'Add, edit, and remove staff members';
      case 'view_analytics':
        return 'Access sales and performance reports';
      case 'manage_payments':
        return 'Handle payment processing and refunds';
      default:
        return '';
    }
  }

  void _saveStaff() {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    final controller = Get.find<RestaurantController>();

    final staffData = {
      'name': _nameController.text.trim(),
      'role': _selectedRole,
      'permissions': _permissions,
    };

    if (_isEditing) {
      // Update existing staff
      controller.updateStaffMember(widget.staff!.id, staffData);
    } else {
      // Add new staff
      staffData['email'] = _emailController.text.trim();
      staffData['password'] = _passwordController.text;
      controller.createStaffMember(staffData);
    }

    Navigator.of(context).pop();
  }
}

extension StringExtension on String {
  String? get capitalize {
    if (isEmpty) return null;
    return '${this[0].toUpperCase()}${substring(1)}';
  }
}
