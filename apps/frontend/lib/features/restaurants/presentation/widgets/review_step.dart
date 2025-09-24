/// Review step widget.
///
/// This widget shows a summary of all registration data for review.

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../application/restaurant_controller.dart';

class ReviewStep extends StatelessWidget {
  const ReviewStep({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.find<RestaurantController>();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Obx(() {
        final data = controller.registrationData;
        
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Review & Submit',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Please review your information before submitting',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 24),

            // Restaurant Information
            _buildSection(
              'Restaurant Information',
              [
                _buildInfoRow('Name', data['name'] ?? 'Not provided'),
                if (data['description'] != null && data['description'].toString().isNotEmpty)
                  _buildInfoRow('Description', data['description']),
                if (data['address'] != null && data['address'].toString().isNotEmpty)
                  _buildInfoRow('Address', data['address']),
                if (data['phone'] != null && data['phone'].toString().isNotEmpty)
                  _buildInfoRow('Phone', data['phone']),
                if (data['email'] != null && data['email'].toString().isNotEmpty)
                  _buildInfoRow('Email', data['email']),
                if (data['website'] != null && data['website'].toString().isNotEmpty)
                  _buildInfoRow('Website', data['website']),
                if (data['cuisine_type'] != null)
                  _buildInfoRow('Cuisine Type', data['cuisine_type']),
                if (data['dining_style'] != null)
                  _buildInfoRow('Dining Style', data['dining_style']),
              ],
            ),

            const SizedBox(height: 24),

            // Owner Information
            _buildSection(
              'Owner Information',
              [
                if (data['owner_name'] != null && data['owner_name'].toString().isNotEmpty)
                  _buildInfoRow('Name', data['owner_name']),
                _buildInfoRow('Email', data['owner_email'] ?? 'Not provided'),
                _buildInfoRow('Password', '••••••••'),
              ],
            ),

            const SizedBox(height: 24),

            // Business Configuration
            _buildSection(
              'Business Configuration',
              [
                _buildInfoRow(
                  'Service Model',
                  _getServiceModelDisplay(data['service_model'] ?? 'self_service'),
                ),
                _buildInfoRow(
                  'Auto-accept Orders',
                  (data['auto_accept_orders'] ?? true) ? 'Yes' : 'No',
                ),
                _buildInfoRow(
                  'Estimated Prep Time',
                  '${data['estimated_prep_time'] ?? 30} minutes',
                ),
                _buildInfoRow(
                  'Tax Rate',
                  '${((data['tax_rate'] ?? 0.18) * 100).toStringAsFixed(1)}%',
                ),
                _buildInfoRow(
                  'Service Charge',
                  '${((data['service_charge_rate'] ?? 0.0) * 100).toStringAsFixed(1)}%',
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Terms and Conditions
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.blue[50],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blue[200]!),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.info_outline,
                        color: Colors.blue[600],
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Terms & Conditions',
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          color: Colors.blue[800],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'By registering your restaurant, you agree to our Terms of Service and Privacy Policy. You confirm that all information provided is accurate and complete.',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.blue[700],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Error display
            if (controller.error.value.isNotEmpty)
              Container(
                padding: const EdgeInsets.all(16),
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: Colors.red[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red[200]!),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.error_outline,
                      color: Colors.red[600],
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        controller.error.value,
                        style: TextStyle(
                          color: Colors.red[800],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
          ],
        );
      }),
    );
  }

  Widget _buildSection(String title, List<Widget> children) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey[300]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 16),
          ...children,
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
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

  String _getServiceModelDisplay(String value) {
    switch (value) {
      case 'self_service':
        return 'Self Service';
      case 'staff_assisted':
        return 'Staff Assisted';
      default:
        return value;
    }
  }
}
