/// Staff card widget.
///
/// This widget displays staff member information in a card format.
library;

import 'package:flutter/material.dart';

import '../../domain/restaurant_entity.dart';

class StaffCard extends StatelessWidget {
  final RestaurantStaff staff;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  const StaffCard({
    super.key,
    required this.staff,
    this.onEdit,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: _getRoleColor(staff.role),
                  child: Icon(
                    _getRoleIcon(staff.role),
                    color: Colors.white,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        staff.name ?? 'Unknown',
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 16,
                        ),
                      ),
                      if (staff.email != null)
                        Text(
                          staff.email!,
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 14,
                          ),
                        ),
                    ],
                  ),
                ),
                PopupMenuButton<String>(
                  onSelected: (value) {
                    switch (value) {
                      case 'edit':
                        onEdit?.call();
                        break;
                      case 'delete':
                        onDelete?.call();
                        break;
                    }
                  },
                  itemBuilder: (context) => [
                    const PopupMenuItem(
                      value: 'edit',
                      child: Row(
                        children: [
                          Icon(Icons.edit, size: 16),
                          SizedBox(width: 8),
                          Text('Edit'),
                        ],
                      ),
                    ),
                    if (staff.role != 'owner')
                      const PopupMenuItem(
                        value: 'delete',
                        child: Row(
                          children: [
                            Icon(Icons.delete, size: 16, color: Colors.red),
                            SizedBox(width: 8),
                            Text('Delete', style: TextStyle(color: Colors.red)),
                          ],
                        ),
                      ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Role badge
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: _getRoleColor(staff.role).withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: _getRoleColor(staff.role).withOpacity(0.3),
                ),
              ),
              child: Text(
                _getRoleDisplayName(staff.role),
                style: TextStyle(
                  color: _getRoleColor(staff.role),
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),

            const SizedBox(height: 12),

            // Status and dates
            Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: staff.isActive ? Colors.green : Colors.red,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  staff.isActive ? 'Active' : 'Inactive',
                  style: TextStyle(
                    color: staff.isActive ? Colors.green : Colors.red,
                    fontWeight: FontWeight.w600,
                    fontSize: 12,
                  ),
                ),
                const Spacer(),
                Text(
                  'Added: ${_formatDate(staff.createdAt)}',
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 12,
                  ),
                ),
              ],
            ),

            // Permissions preview
            if (staff.permissions.isNotEmpty) ...[
              const SizedBox(height: 12),
              const Divider(),
              const SizedBox(height: 8),
              Text(
                'Permissions',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: Colors.grey[700],
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: _getPermissionChips(),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color _getRoleColor(String role) {
    switch (role.toLowerCase()) {
      case 'owner':
        return Colors.purple;
      case 'manager':
        return Colors.blue;
      case 'kitchen':
        return Colors.orange;
      case 'service':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  IconData _getRoleIcon(String role) {
    switch (role.toLowerCase()) {
      case 'owner':
        return Icons.business;
      case 'manager':
        return Icons.manage_accounts;
      case 'kitchen':
        return Icons.restaurant;
      case 'service':
        return Icons.room_service;
      default:
        return Icons.person;
    }
  }

  String _getRoleDisplayName(String role) {
    switch (role.toLowerCase()) {
      case 'owner':
        return 'Owner';
      case 'manager':
        return 'Manager';
      case 'kitchen':
        return 'Kitchen Staff';
      case 'service':
        return 'Service Staff';
      default:
        return role.capitalize ?? role;
    }
  }

  List<Widget> _getPermissionChips() {
    final permissions = <String>[];

    staff.permissions.forEach((key, value) {
      if (value == true) {
        permissions.add(_getPermissionDisplayName(key));
      }
    });

    final List<Widget> chips = permissions.take(3).map<Widget>((permission) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
        decoration: BoxDecoration(
          color: Colors.grey[100],
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.grey[300]!),
        ),
        child: Text(
          permission,
          style: TextStyle(
            fontSize: 10,
            color: Colors.grey[700],
          ),
        ),
      );
    }).toList();

    if (permissions.length > 3) {
      chips.add(
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
          decoration: BoxDecoration(
            color: Colors.grey[200],
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            '+${permissions.length - 3} more',
            style: TextStyle(
              fontSize: 10,
              color: Colors.grey[600],
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      );
    }

    return chips;
  }

  String _getPermissionDisplayName(String permission) {
    switch (permission) {
      case 'manage_restaurant':
        return 'Restaurant';
      case 'manage_menu':
        return 'Menu';
      case 'manage_orders':
        return 'Orders';
      case 'manage_tables':
        return 'Tables';
      case 'manage_staff':
        return 'Staff';
      case 'view_analytics':
        return 'Analytics';
      case 'manage_payments':
        return 'Payments';
      default:
        return StaffCardStringExtension(permission.replaceAll('_', ' '))
                .capitalize ??
            permission;
    }
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}

extension StaffCardStringExtension on String {
  String? get capitalize {
    if (isEmpty) return null;
    return '${this[0].toUpperCase()}${substring(1)}';
  }
}
