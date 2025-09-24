/// Restaurant settings screen.
///
/// This module contains the comprehensive restaurant settings interface.

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../application/restaurant_controller.dart';
import 'widgets/settings_section.dart';
import 'widgets/business_hours_settings.dart';
import 'widgets/financial_settings.dart';
import 'widgets/operational_settings.dart';
import 'widgets/branding_settings.dart';

class RestaurantSettingsScreen extends StatefulWidget {
  const RestaurantSettingsScreen({super.key});

  @override
  State<RestaurantSettingsScreen> createState() => _RestaurantSettingsScreenState();
}

class _RestaurantSettingsScreenState extends State<RestaurantSettingsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final controller = Get.find<RestaurantController>();

    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Restaurant Settings'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          labelColor: Colors.blue[600],
          unselectedLabelColor: Colors.grey[600],
          indicatorColor: Colors.blue[600],
          tabs: const [
            Tab(text: 'General'),
            Tab(text: 'Hours'),
            Tab(text: 'Financial'),
            Tab(text: 'Operations'),
            Tab(text: 'Branding'),
          ],
        ),
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(
            child: CircularProgressIndicator(),
          );
        }

        final restaurant = controller.currentRestaurant.value;
        if (restaurant == null) {
          return const Center(
            child: Text('No restaurant data available'),
          );
        }

        return TabBarView(
          controller: _tabController,
          children: [
            // General Settings
            SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  SettingsSection(
                    title: 'Basic Information',
                    children: [
                      _buildTextField(
                        'Restaurant Name',
                        restaurant.name,
                        (value) => controller.updateRestaurant({'name': value}),
                      ),
                      const SizedBox(height: 16),
                      _buildTextField(
                        'Description',
                        restaurant.description ?? '',
                        (value) => controller.updateRestaurant({'description': value}),
                        maxLines: 3,
                      ),
                      const SizedBox(height: 16),
                      _buildTextField(
                        'Address',
                        restaurant.address ?? '',
                        (value) => controller.updateRestaurant({'address': value}),
                        maxLines: 2,
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(
                            child: _buildTextField(
                              'Phone',
                              restaurant.phone ?? '',
                              (value) => controller.updateRestaurant({'phone': value}),
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: _buildTextField(
                              'Email',
                              restaurant.email ?? '',
                              (value) => controller.updateRestaurant({'email': value}),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      _buildTextField(
                        'Website',
                        restaurant.website ?? '',
                        (value) => controller.updateRestaurant({'website': value}),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  SettingsSection(
                    title: 'Restaurant Details',
                    children: [
                      _buildDropdownField(
                        'Cuisine Type',
                        restaurant.cuisineType,
                        [
                          'Indian',
                          'Chinese',
                          'Italian',
                          'Mexican',
                          'Thai',
                          'Japanese',
                          'American',
                          'Mediterranean',
                          'Continental',
                          'Multi-Cuisine',
                        ],
                        (value) => controller.updateRestaurant({'cuisine_type': value}),
                      ),
                      const SizedBox(height: 16),
                      _buildDropdownField(
                        'Dining Style',
                        restaurant.diningStyle,
                        [
                          'Casual Dining',
                          'Fine Dining',
                          'Fast Food',
                          'Cafe',
                          'Bar & Grill',
                          'Food Truck',
                          'Buffet',
                          'Family Restaurant',
                        ],
                        (value) => controller.updateRestaurant({'dining_style': value}),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // Business Hours
            const BusinessHoursSettings(),

            // Financial Settings
            const FinancialSettings(),

            // Operational Settings
            const OperationalSettings(),

            // Branding Settings
            const BrandingSettings(),
          ],
        );
      }),
    );
  }

  Widget _buildTextField(
    String label,
    String initialValue,
    Function(String) onChanged, {
    int maxLines = 1,
  }) {
    return TextFormField(
      initialValue: initialValue,
      decoration: InputDecoration(
        labelText: label,
        border: const OutlineInputBorder(),
        filled: true,
        fillColor: Colors.white,
      ),
      maxLines: maxLines,
      onChanged: onChanged,
    );
  }

  Widget _buildDropdownField(
    String label,
    String? currentValue,
    List<String> options,
    Function(String?) onChanged,
  ) {
    return DropdownButtonFormField<String>(
      value: currentValue,
      decoration: InputDecoration(
        labelText: label,
        border: const OutlineInputBorder(),
        filled: true,
        fillColor: Colors.white,
      ),
      items: options.map((option) {
        return DropdownMenuItem(
          value: option,
          child: Text(option),
        );
      }).toList(),
      onChanged: onChanged,
    );
  }
}
