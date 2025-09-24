/// Financial settings widget.
///
/// This widget allows configuration of financial settings like taxes and charges.

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../application/restaurant_controller.dart';
import 'settings_section.dart';

class FinancialSettings extends StatefulWidget {
  const FinancialSettings({super.key});

  @override
  State<FinancialSettings> createState() => _FinancialSettingsState();
}

class _FinancialSettingsState extends State<FinancialSettings> {
  final _formKey = GlobalKey<FormState>();
  
  String _currency = 'INR';
  double _taxRate = 18.0;
  double _serviceChargeRate = 0.0;
  
  final List<String> _currencies = [
    'INR',
    'USD',
    'EUR',
    'GBP',
    'AUD',
    'CAD',
  ];

  @override
  void initState() {
    super.initState();
    _loadExistingSettings();
  }

  void _loadExistingSettings() {
    final controller = Get.find<RestaurantController>();
    final restaurant = controller.currentRestaurant.value;
    
    if (restaurant != null && restaurant.settings.isNotEmpty) {
      final settings = restaurant.settings;
      _currency = settings['currency'] ?? 'INR';
      _taxRate = ((settings['tax_rate'] ?? 0.18) * 100).toDouble();
      _serviceChargeRate = ((settings['service_charge_rate'] ?? 0.0) * 100).toDouble();
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Form(
        key: _formKey,
        child: Column(
          children: [
            SettingsSection(
              title: 'Currency & Pricing',
              subtitle: 'Configure your restaurant\'s currency and pricing settings',
              children: [
                DropdownButtonFormField<String>(
                  value: _currency,
                  decoration: const InputDecoration(
                    labelText: 'Currency',
                    border: OutlineInputBorder(),
                    filled: true,
                    fillColor: Colors.white,
                  ),
                  items: _currencies.map((currency) {
                    return DropdownMenuItem(
                      value: currency,
                      child: Text(currency),
                    );
                  }).toList(),
                  onChanged: (value) {
                    setState(() {
                      _currency = value!;
                    });
                  },
                ),
              ],
            ),
            const SizedBox(height: 24),
            SettingsSection(
              title: 'Taxes & Charges',
              subtitle: 'Set up tax rates and service charges',
              children: [
                // Tax Rate
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Tax Rate: ${_taxRate.toStringAsFixed(1)}%',
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 8),
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
                      },
                    ),
                    Text(
                      'Applied to all menu items',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                
                // Service Charge Rate
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Service Charge: ${_serviceChargeRate.toStringAsFixed(1)}%',
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 8),
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
                      },
                    ),
                    Text(
                      'Additional charge for service',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                
                // Preview
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.grey[50],
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.grey[300]!),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Pricing Preview',
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          color: Colors.grey[700],
                        ),
                      ),
                      const SizedBox(height: 12),
                      _buildPreviewRow('Item Price', '₹100.00'),
                      _buildPreviewRow('Tax (${_taxRate.toStringAsFixed(1)}%)', '₹${(_taxRate).toStringAsFixed(2)}'),
                      _buildPreviewRow('Service Charge (${_serviceChargeRate.toStringAsFixed(1)}%)', '₹${(_serviceChargeRate).toStringAsFixed(2)}'),
                      const Divider(),
                      _buildPreviewRow(
                        'Total',
                        '₹${(100 + _taxRate + _serviceChargeRate).toStringAsFixed(2)}',
                        isTotal: true,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _saveFinancialSettings,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue[600],
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: const Text('Save Financial Settings'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            SettingsSection(
              title: 'Payment Methods',
              subtitle: 'Configure accepted payment methods',
              children: [
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(32),
                    child: Column(
                      children: [
                        Icon(
                          Icons.payment,
                          size: 48,
                          color: Colors.grey,
                        ),
                        SizedBox(height: 16),
                        Text(
                          'Payment method configuration coming soon',
                          style: TextStyle(
                            color: Colors.grey,
                            fontSize: 16,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPreviewRow(String label, String value, {bool isTotal = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
              fontSize: isTotal ? 16 : 14,
            ),
          ),
          Text(
            value,
            style: TextStyle(
              fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
              fontSize: isTotal ? 16 : 14,
            ),
          ),
        ],
      ),
    );
  }

  void _saveFinancialSettings() {
    final controller = Get.find<RestaurantController>();
    
    final settingsData = {
      'currency': _currency,
      'tax_rate': _taxRate / 100,
      'service_charge_rate': _serviceChargeRate / 100,
    };
    
    controller.updateSettings(settingsData);
  }
}
