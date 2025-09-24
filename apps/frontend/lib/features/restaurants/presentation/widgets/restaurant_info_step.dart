/// Restaurant information step widget.
///
/// This widget contains the form for basic restaurant information.

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../application/restaurant_controller.dart';

class RestaurantInfoStep extends StatefulWidget {
  const RestaurantInfoStep({super.key});

  @override
  State<RestaurantInfoStep> createState() => _RestaurantInfoStepState();
}

class _RestaurantInfoStepState extends State<RestaurantInfoStep> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _addressController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _websiteController = TextEditingController();

  String? _selectedCuisineType;
  String? _selectedDiningStyle;

  final List<String> _cuisineTypes = [
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
  ];

  final List<String> _diningStyles = [
    'Casual Dining',
    'Fine Dining',
    'Fast Food',
    'Cafe',
    'Bar & Grill',
    'Food Truck',
    'Buffet',
    'Family Restaurant',
  ];

  @override
  void initState() {
    super.initState();
    _loadExistingData();
  }

  void _loadExistingData() {
    final controller = Get.find<RestaurantController>();
    final data = controller.registrationData;
    
    _nameController.text = data['name'] ?? '';
    _descriptionController.text = data['description'] ?? '';
    _addressController.text = data['address'] ?? '';
    _phoneController.text = data['phone'] ?? '';
    _emailController.text = data['email'] ?? '';
    _websiteController.text = data['website'] ?? '';
    _selectedCuisineType = data['cuisine_type'];
    _selectedDiningStyle = data['dining_style'];
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _addressController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _websiteController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final controller = Get.find<RestaurantController>();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Restaurant Information',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Tell us about your restaurant',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 24),

            // Restaurant Name
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'Restaurant Name *',
                hintText: 'Enter your restaurant name',
                border: OutlineInputBorder(),
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Restaurant name is required';
                }
                return null;
              },
              onChanged: (value) {
                controller.updateRegistrationData('name', value);
              },
            ),
            const SizedBox(height: 16),

            // Description
            TextFormField(
              controller: _descriptionController,
              decoration: const InputDecoration(
                labelText: 'Description',
                hintText: 'Brief description of your restaurant',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
              onChanged: (value) {
                controller.updateRegistrationData('description', value);
              },
            ),
            const SizedBox(height: 16),

            // Address
            TextFormField(
              controller: _addressController,
              decoration: const InputDecoration(
                labelText: 'Address',
                hintText: 'Restaurant address',
                border: OutlineInputBorder(),
              ),
              maxLines: 2,
              onChanged: (value) {
                controller.updateRegistrationData('address', value);
              },
            ),
            const SizedBox(height: 16),

            // Phone and Email
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _phoneController,
                    decoration: const InputDecoration(
                      labelText: 'Phone',
                      hintText: '+91 9876543210',
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.phone,
                    onChanged: (value) {
                      controller.updateRegistrationData('phone', value);
                    },
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextFormField(
                    controller: _emailController,
                    decoration: const InputDecoration(
                      labelText: 'Email',
                      hintText: 'restaurant@example.com',
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.emailAddress,
                    onChanged: (value) {
                      controller.updateRegistrationData('email', value);
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Website
            TextFormField(
              controller: _websiteController,
              decoration: const InputDecoration(
                labelText: 'Website',
                hintText: 'https://yourrestaurant.com',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.url,
              onChanged: (value) {
                controller.updateRegistrationData('website', value);
              },
            ),
            const SizedBox(height: 16),

            // Cuisine Type
            DropdownButtonFormField<String>(
              value: _selectedCuisineType,
              decoration: const InputDecoration(
                labelText: 'Cuisine Type',
                border: OutlineInputBorder(),
              ),
              items: _cuisineTypes.map((cuisine) {
                return DropdownMenuItem(
                  value: cuisine,
                  child: Text(cuisine),
                );
              }).toList(),
              onChanged: (value) {
                setState(() {
                  _selectedCuisineType = value;
                });
                controller.updateRegistrationData('cuisine_type', value);
              },
            ),
            const SizedBox(height: 16),

            // Dining Style
            DropdownButtonFormField<String>(
              value: _selectedDiningStyle,
              decoration: const InputDecoration(
                labelText: 'Dining Style',
                border: OutlineInputBorder(),
              ),
              items: _diningStyles.map((style) {
                return DropdownMenuItem(
                  value: style,
                  child: Text(style),
                );
              }).toList(),
              onChanged: (value) {
                setState(() {
                  _selectedDiningStyle = value;
                });
                controller.updateRegistrationData('dining_style', value);
              },
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}
