/// Business hours settings widget.
///
/// This widget allows configuration of restaurant business hours.

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../application/restaurant_controller.dart';
import 'settings_section.dart';

class BusinessHoursSettings extends StatefulWidget {
  const BusinessHoursSettings({super.key});

  @override
  State<BusinessHoursSettings> createState() => _BusinessHoursSettingsState();
}

class _BusinessHoursSettingsState extends State<BusinessHoursSettings> {
  final Map<String, Map<String, String?>> _businessHours = {
    'monday': {'open': null, 'close': null, 'closed': 'false'},
    'tuesday': {'open': null, 'close': null, 'closed': 'false'},
    'wednesday': {'open': null, 'close': null, 'closed': 'false'},
    'thursday': {'open': null, 'close': null, 'closed': 'false'},
    'friday': {'open': null, 'close': null, 'closed': 'false'},
    'saturday': {'open': null, 'close': null, 'closed': 'false'},
    'sunday': {'open': null, 'close': null, 'closed': 'false'},
  };

  @override
  void initState() {
    super.initState();
    _loadExistingHours();
  }

  void _loadExistingHours() {
    final controller = Get.find<RestaurantController>();
    final restaurant = controller.currentRestaurant.value;
    
    if (restaurant != null && restaurant.businessHours.isNotEmpty) {
      restaurant.businessHours.forEach((day, hours) {
        if (_businessHours.containsKey(day) && hours is Map) {
          _businessHours[day] = {
            'open': hours['open']?.toString(),
            'close': hours['close']?.toString(),
            'closed': hours['closed']?.toString() ?? 'false',
          };
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          SettingsSection(
            title: 'Business Hours',
            subtitle: 'Set your restaurant operating hours for each day',
            children: [
              ..._businessHours.entries.map((entry) {
                return _buildDayRow(entry.key, entry.value);
              }).toList(),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _saveBusinessHours,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue[600],
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  child: const Text('Save Business Hours'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          SettingsSection(
            title: 'Special Hours',
            subtitle: 'Configure special hours for holidays and events',
            children: [
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: Column(
                    children: [
                      Icon(
                        Icons.event,
                        size: 48,
                        color: Colors.grey,
                      ),
                      SizedBox(height: 16),
                      Text(
                        'Special hours configuration coming soon',
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
    );
  }

  Widget _buildDayRow(String day, Map<String, String?> hours) {
    final isClosed = hours['closed'] == 'true';
    
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        children: [
          SizedBox(
            width: 100,
            child: Text(
              day.capitalize!,
              style: const TextStyle(
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Row(
              children: [
                Checkbox(
                  value: isClosed,
                  onChanged: (value) {
                    setState(() {
                      _businessHours[day]!['closed'] = value.toString();
                    });
                  },
                ),
                const Text('Closed'),
                const SizedBox(width: 16),
                if (!isClosed) ...[
                  Expanded(
                    child: _buildTimeField(
                      'Open',
                      hours['open'],
                      (time) {
                        setState(() {
                          _businessHours[day]!['open'] = time;
                        });
                      },
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildTimeField(
                      'Close',
                      hours['close'],
                      (time) {
                        setState(() {
                          _businessHours[day]!['close'] = time;
                        });
                      },
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTimeField(
    String label,
    String? value,
    Function(String) onChanged,
  ) {
    return TextFormField(
      initialValue: value,
      decoration: InputDecoration(
        labelText: label,
        hintText: 'HH:MM',
        border: const OutlineInputBorder(),
        filled: true,
        fillColor: Colors.white,
        suffixIcon: IconButton(
          icon: const Icon(Icons.access_time),
          onPressed: () => _selectTime(onChanged),
        ),
      ),
      readOnly: true,
      onTap: () => _selectTime(onChanged),
    );
  }

  Future<void> _selectTime(Function(String) onChanged) async {
    final time = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.now(),
    );
    
    if (time != null) {
      final formattedTime = '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
      onChanged(formattedTime);
    }
  }

  void _saveBusinessHours() {
    final controller = Get.find<RestaurantController>();
    
    // Convert to the format expected by the API
    final hoursData = <String, dynamic>{};
    
    _businessHours.forEach((day, hours) {
      if (hours['closed'] == 'true') {
        hoursData[day] = {'closed': true};
      } else {
        hoursData[day] = {
          'open': hours['open'],
          'close': hours['close'],
          'closed': false,
        };
      }
    });
    
    controller.updateBusinessHours(hoursData);
  }
}
