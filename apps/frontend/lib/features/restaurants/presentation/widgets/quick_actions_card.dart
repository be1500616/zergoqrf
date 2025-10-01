/// Quick actions card widget.
///
/// This widget provides quick access to common restaurant management actions.

import 'package:flutter/material.dart';
import 'package:get/get.dart';

class QuickActionsCard extends StatelessWidget {
  const QuickActionsCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Quick Actions',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 16),
            GridView.count(
              crossAxisCount: 2,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: 2.5,
              children: [
                _buildActionButton(
                  'Manage Menu',
                  Icons.restaurant_menu,
                  Colors.orange,
                  () {
                    Get.snackbar('Coming Soon', 'Menu management feature coming soon!');
                  },
                ),
                _buildActionButton(
                  'View Orders',
                  Icons.receipt_long,
                  Colors.blue,
                  () {
                    Get.snackbar('Coming Soon', 'Order management feature coming soon!');
                  },
                ),
                _buildActionButton(
                  'Manage Tables',
                  Icons.table_restaurant,
                  Colors.green,
                  () {
                    Get.snackbar('Coming Soon', 'Table management feature coming soon!');
                  },
                ),
                _buildActionButton(
                  'Staff Management',
                  Icons.people,
                  Colors.purple,
                  () => Get.toNamed('/restaurant/staff'),
                ),
                _buildActionButton(
                  'QR Codes',
                  Icons.qr_code,
                  Colors.teal,
                  () {
                    Get.snackbar('Coming Soon', 'QR code generation feature coming soon!');
                  },
                ),
                _buildActionButton(
                  'Analytics',
                  Icons.analytics,
                  Colors.indigo,
                  () {
                    Get.snackbar('Coming Soon', 'Analytics feature coming soon!');
                  },
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButton(
    String title,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Row(
          children: [
            Icon(
              icon,
              color: color,
              size: 24,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                title,
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: color,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
