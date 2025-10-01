/// Restaurant info card widget.
///
/// This widget displays restaurant information in a card format.

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../domain/restaurant_entity.dart';

class RestaurantInfoCard extends StatelessWidget {
  final Restaurant restaurant;

  const RestaurantInfoCard({
    super.key,
    required this.restaurant,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Restaurant Information',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                TextButton.icon(
                  onPressed: () => Get.toNamed('/restaurant/settings'),
                  icon: const Icon(Icons.edit, size: 16),
                  label: const Text('Edit'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // Restaurant Code
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue[50],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blue[200]!),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.qr_code,
                    color: Colors.blue[600],
                  ),
                  const SizedBox(width: 12),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Restaurant Code',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.blue[700],
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      Text(
                        restaurant.code,
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.blue[800],
                          letterSpacing: 2,
                        ),
                      ),
                    ],
                  ),
                  const Spacer(),
                  IconButton(
                    onPressed: () {
                      // TODO: Implement copy to clipboard
                      Get.snackbar('Copied', 'Restaurant code copied to clipboard');
                    },
                    icon: Icon(
                      Icons.copy,
                      color: Colors.blue[600],
                    ),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Basic Info
            _buildInfoRow('Name', restaurant.name),
            if (restaurant.description != null && restaurant.description!.isNotEmpty)
              _buildInfoRow('Description', restaurant.description!),
            if (restaurant.address != null && restaurant.address!.isNotEmpty)
              _buildInfoRow('Address', restaurant.address!),
            if (restaurant.phone != null && restaurant.phone!.isNotEmpty)
              _buildInfoRow('Phone', restaurant.phone!),
            if (restaurant.email != null && restaurant.email!.isNotEmpty)
              _buildInfoRow('Email', restaurant.email!),
            if (restaurant.website != null && restaurant.website!.isNotEmpty)
              _buildInfoRow('Website', restaurant.website!),
            if (restaurant.cuisineType != null)
              _buildInfoRow('Cuisine Type', restaurant.cuisineType!),
            if (restaurant.diningStyle != null)
              _buildInfoRow('Dining Style', restaurant.diningStyle!),
            
            const SizedBox(height: 16),
            
            // Status
            Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: restaurant.isActive ? Colors.green : Colors.red,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  restaurant.isActive ? 'Active' : 'Inactive',
                  style: TextStyle(
                    color: restaurant.isActive ? Colors.green : Colors.red,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                Text(
                  'Created: ${_formatDate(restaurant.createdAt)}',
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              label,
              style: TextStyle(
                fontWeight: FontWeight.w500,
                color: Colors.grey[600],
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontWeight: FontWeight.w400,
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}
