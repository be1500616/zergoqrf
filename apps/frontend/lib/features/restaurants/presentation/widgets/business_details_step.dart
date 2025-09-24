/// Business details step widget.
///
/// This widget contains the form for business configuration details.

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../application/restaurant_controller.dart';

class BusinessDetailsStep extends StatefulWidget {
  const BusinessDetailsStep({super.key});

  @override
  State<BusinessDetailsStep> createState() => _BusinessDetailsStepState();
}

class _BusinessDetailsStepState extends State<BusinessDetailsStep> {
  String _selectedServiceModel = 'self_service';
  bool _autoAcceptOrders = true;
  double _taxRate = 18.0;
  double _serviceChargeRate = 0.0;
  int _estimatedPrepTime = 30;

  final List<Map<String, String>> _serviceModels = [
    {
      'value': 'self_service',
      'title': 'Self Service',
      'description': 'Customers order and pay themselves using QR codes',
    },
    {
      'value': 'staff_assisted',
      'title': 'Staff Assisted',
      'description': 'Staff takes orders and processes payments',
    },
  ];

  @override
  void initState() {
    super.initState();
    _loadExistingData();
  }

  void _loadExistingData() {
    final controller = Get.find<RestaurantController>();
    final data = controller.registrationData;
    
    _selectedServiceModel = data['service_model'] ?? 'self_service';
    _autoAcceptOrders = data['auto_accept_orders'] ?? true;
    _taxRate = (data['tax_rate'] ?? 18.0).toDouble();
    _serviceChargeRate = (data['service_charge_rate'] ?? 0.0).toDouble();
    _estimatedPrepTime = (data['estimated_prep_time'] ?? 30).toInt();
  }

  @override
  Widget build(BuildContext context) {
    final controller = Get.find<RestaurantController>();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Business Configuration',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Configure your restaurant operations',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 24),

          // Service Model
          Text(
            'Service Model',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          
          ..._serviceModels.map((model) {
            return Container(
              margin: const EdgeInsets.only(bottom: 12),
              child: InkWell(
                onTap: () {
                  setState(() {
                    _selectedServiceModel = model['value']!;
                  });
                  controller.updateRegistrationData('service_model', model['value']);
                },
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    border: Border.all(
                      color: _selectedServiceModel == model['value']
                          ? Colors.blue[600]!
                          : Colors.grey[300]!,
                      width: 2,
                    ),
                    borderRadius: BorderRadius.circular(8),
                    color: _selectedServiceModel == model['value']
                        ? Colors.blue[50]
                        : Colors.white,
                  ),
                  child: Row(
                    children: [
                      Radio<String>(
                        value: model['value']!,
                        groupValue: _selectedServiceModel,
                        onChanged: (value) {
                          setState(() {
                            _selectedServiceModel = value!;
                          });
                          controller.updateRegistrationData('service_model', value);
                        },
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              model['title']!,
                              style: const TextStyle(
                                fontWeight: FontWeight.w600,
                                fontSize: 16,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              model['description']!,
                              style: TextStyle(
                                color: Colors.grey[600],
                                fontSize: 14,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          }).toList(),
          
          const SizedBox(height: 24),

          // Order Settings
          Text(
            'Order Settings',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),

          SwitchListTile(
            title: const Text('Auto-accept Orders'),
            subtitle: const Text('Automatically accept incoming orders'),
            value: _autoAcceptOrders,
            onChanged: (value) {
              setState(() {
                _autoAcceptOrders = value;
              });
              controller.updateRegistrationData('auto_accept_orders', value);
            },
            contentPadding: EdgeInsets.zero,
          ),
          
          const SizedBox(height: 16),

          // Estimated Prep Time
          Text(
            'Estimated Preparation Time: $_estimatedPrepTime minutes',
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
          Slider(
            value: _estimatedPrepTime.toDouble(),
            min: 10,
            max: 120,
            divisions: 22,
            label: '$_estimatedPrepTime min',
            onChanged: (value) {
              setState(() {
                _estimatedPrepTime = value.round();
              });
              controller.updateRegistrationData('estimated_prep_time', _estimatedPrepTime);
            },
          ),
          
          const SizedBox(height: 24),

          // Financial Settings
          Text(
            'Financial Settings',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),

          // Tax Rate
          Text(
            'Tax Rate: ${_taxRate.toStringAsFixed(1)}%',
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
          Slider(
            value: _taxRate,
            min: 0,
            max: 30,
            divisions: 60,
            label: '${_taxRate.toStringAsFixed(1)}%',
            onChanged: (value) {
              setState(() {
                _taxRate = value;
              });
              controller.updateRegistrationData('tax_rate', _taxRate / 100);
            },
          ),
          
          const SizedBox(height: 16),

          // Service Charge Rate
          Text(
            'Service Charge: ${_serviceChargeRate.toStringAsFixed(1)}%',
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
          Slider(
            value: _serviceChargeRate,
            min: 0,
            max: 20,
            divisions: 40,
            label: '${_serviceChargeRate.toStringAsFixed(1)}%',
            onChanged: (value) {
              setState(() {
                _serviceChargeRate = value;
              });
              controller.updateRegistrationData('service_charge_rate', _serviceChargeRate / 100);
            },
          ),
          
          const SizedBox(height: 24),

          // Info Card
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.amber[50],
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.amber[200]!),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.info_outline,
                  color: Colors.amber[700],
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'These settings can be changed later from your restaurant dashboard.',
                    style: TextStyle(
                      color: Colors.amber[800],
                      fontSize: 14,
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 24),
        ],
      ),
    );
  }
}
