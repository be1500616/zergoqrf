/// Operational settings widget.
///
/// This widget allows configuration of operational settings.

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../application/restaurant_controller.dart';
import 'settings_section.dart';

class OperationalSettings extends StatefulWidget {
  const OperationalSettings({super.key});

  @override
  State<OperationalSettings> createState() => _OperationalSettingsState();
}

class _OperationalSettingsState extends State<OperationalSettings> {
  String _serviceModel = 'self_service';
  bool _autoAcceptOrders = true;
  int _estimatedPrepTime = 30;
  bool _emailNotifications = true;
  bool _smsNotifications = false;
  bool _whatsappNotifications = false;

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
      _serviceModel = settings['service_model'] ?? 'self_service';
      _autoAcceptOrders = settings['auto_accept_orders'] ?? true;
      _estimatedPrepTime = settings['estimated_prep_time'] ?? 30;
      _emailNotifications = settings['email_notifications'] ?? true;
      _smsNotifications = settings['sms_notifications'] ?? false;
      _whatsappNotifications = settings['whatsapp_notifications'] ?? false;
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          SettingsSection(
            title: 'Service Model',
            subtitle: 'Choose how customers interact with your restaurant',
            children: [
              _buildServiceModelOption(
                'self_service',
                'Self Service',
                'Customers order and pay themselves using QR codes',
                Icons.qr_code_scanner,
              ),
              const SizedBox(height: 12),
              _buildServiceModelOption(
                'staff_assisted',
                'Staff Assisted',
                'Staff takes orders and processes payments',
                Icons.person,
              ),
            ],
          ),
          const SizedBox(height: 24),
          SettingsSection(
            title: 'Order Management',
            subtitle: 'Configure how orders are handled',
            children: [
              SwitchListTile(
                title: const Text('Auto-accept Orders'),
                subtitle: const Text('Automatically accept incoming orders'),
                value: _autoAcceptOrders,
                onChanged: (value) {
                  setState(() {
                    _autoAcceptOrders = value;
                  });
                },
                contentPadding: EdgeInsets.zero,
              ),
              const SizedBox(height: 16),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Estimated Preparation Time: $_estimatedPrepTime minutes',
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(height: 8),
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
                    },
                  ),
                  Text(
                    'Average time to prepare orders',
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 24),
          SettingsSection(
            title: 'Notifications',
            subtitle: 'Configure notification preferences',
            children: [
              SwitchListTile(
                title: const Text('Email Notifications'),
                subtitle: const Text('Receive order updates via email'),
                value: _emailNotifications,
                onChanged: (value) {
                  setState(() {
                    _emailNotifications = value;
                  });
                },
                contentPadding: EdgeInsets.zero,
              ),
              SwitchListTile(
                title: const Text('SMS Notifications'),
                subtitle: const Text('Receive order updates via SMS'),
                value: _smsNotifications,
                onChanged: (value) {
                  setState(() {
                    _smsNotifications = value;
                  });
                },
                contentPadding: EdgeInsets.zero,
              ),
              SwitchListTile(
                title: const Text('WhatsApp Notifications'),
                subtitle: const Text('Receive order updates via WhatsApp'),
                value: _whatsappNotifications,
                onChanged: (value) {
                  setState(() {
                    _whatsappNotifications = value;
                  });
                },
                contentPadding: EdgeInsets.zero,
              ),
            ],
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _saveOperationalSettings,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue[600],
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: const Text('Save Operational Settings'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildServiceModelOption(
    String value,
    String title,
    String description,
    IconData icon,
  ) {
    final isSelected = _serviceModel == value;
    
    return InkWell(
      onTap: () {
        setState(() {
          _serviceModel = value;
        });
      },
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border.all(
            color: isSelected ? Colors.blue[600]! : Colors.grey[300]!,
            width: 2,
          ),
          borderRadius: BorderRadius.circular(8),
          color: isSelected ? Colors.blue[50] : Colors.white,
        ),
        child: Row(
          children: [
            Radio<String>(
              value: value,
              groupValue: _serviceModel,
              onChanged: (newValue) {
                setState(() {
                  _serviceModel = newValue!;
                });
              },
            ),
            const SizedBox(width: 12),
            Icon(
              icon,
              color: isSelected ? Colors.blue[600] : Colors.grey[600],
              size: 32,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 16,
                      color: isSelected ? Colors.blue[800] : Colors.black87,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    description,
                    style: TextStyle(
                      color: isSelected ? Colors.blue[700] : Colors.grey[600],
                      fontSize: 14,
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

  void _saveOperationalSettings() {
    final controller = Get.find<RestaurantController>();
    
    final settingsData = {
      'service_model': _serviceModel,
      'auto_accept_orders': _autoAcceptOrders,
      'estimated_prep_time': _estimatedPrepTime,
      'email_notifications': _emailNotifications,
      'sms_notifications': _smsNotifications,
      'whatsapp_notifications': _whatsappNotifications,
    };
    
    controller.updateSettings(settingsData);
  }
}
