/// Menu item availability tab widget.
///
/// This widget provides interface for managing menu item availability schedules.
library;

import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../application/controllers/availability_controller.dart';

class MenuItemAvailabilityTab extends GetView<AvailabilityController> {
  const MenuItemAvailabilityTab({
    super.key,
    required this.availabilitySchedule,
    required this.onAvailabilityScheduleChanged,
  });

  final Map<String, dynamic> availabilitySchedule;
  final Function(Map<String, dynamic>) onAvailabilityScheduleChanged;

  @override
  Widget build(BuildContext context) {
    // Initialize controller with current schedule
    controller.initializeSchedule(availabilitySchedule);

    return Obx(() => SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Text(
                'Availability Schedule',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                      color: Theme.of(context).colorScheme.primary,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                'Set specific times when this item is available. Leave empty to use restaurant hours.',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Theme.of(context)
                          .colorScheme
                          .onSurface
                          .withOpacity(0.7),
                    ),
              ),
              const SizedBox(height: 24),

              // Quick actions
              Row(
                children: [
                  OutlinedButton.icon(
                    onPressed: _setAllDaysAvailable,
                    icon: const Icon(Icons.check_circle_outline),
                    label: const Text('All Days Available'),
                  ),
                  const SizedBox(width: 12),
                  OutlinedButton.icon(
                    onPressed: _clearAllSchedules,
                    icon: const Icon(Icons.clear_all),
                    label: const Text('Clear All'),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Weekly schedule
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Weekly Schedule',
                        style: Theme.of(context).textTheme.titleSmall?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                      ),
                      const SizedBox(height: 16),

                      // Days list
                      ...controller.weekdays.asMap().entries.map((entry) {
                        final index = entry.key;
                        final day = entry.value;
                        final dayLabel = controller.weekdayLabels[index];

                        return _DayScheduleRow(
                          day: day,
                          dayLabel: dayLabel,
                          schedule: controller.availabilitySchedule[day]
                              as Map<String, dynamic>?,
                          onScheduleChanged: (schedule) {
                            if (schedule != null) {
                              controller.updateWeekdayAvailability(
                                day,
                                schedule['available'] == true,
                                startTime: schedule['start_time'] != null
                                    ? controller
                                        .parseTimeOfDay(schedule['start_time'])
                                    : null,
                                endTime: schedule['end_time'] != null
                                    ? controller
                                        .parseTimeOfDay(schedule['end_time'])
                                    : null,
                              );
                            }
                            onAvailabilityScheduleChanged(
                                controller.availabilitySchedule);
                          },
                        );
                      }),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Special dates section
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            'Special Dates',
                            style: Theme.of(context)
                                .textTheme
                                .titleSmall
                                ?.copyWith(
                                  fontWeight: FontWeight.w600,
                                ),
                          ),
                          const Spacer(),
                          OutlinedButton.icon(
                            onPressed: _addSpecialDate,
                            icon: const Icon(Icons.add),
                            label: const Text('Add Date'),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Override availability for specific dates (holidays, special events, etc.)',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Theme.of(context)
                                  .colorScheme
                                  .onSurface
                                  .withOpacity(0.7),
                            ),
                      ),
                      const SizedBox(height: 16),

                      // Special dates list
                      _buildSpecialDatesList(context),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ));
  }

  Widget _buildSpecialDatesList(BuildContext context) {
    final specialDates =
        availabilitySchedule['special_dates'] as Map<String, dynamic>? ?? {};

    if (specialDates.isEmpty) {
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border.all(
            color: Theme.of(context).colorScheme.outline.withOpacity(0.3),
          ),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          'No special dates configured',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.outline,
              ),
          textAlign: TextAlign.center,
        ),
      );
    }

    return Column(
      children: specialDates.entries.map((entry) {
        final date = entry.key;
        final schedule = entry.value as Map<String, dynamic>;

        return Card(
          child: ListTile(
            leading: const Icon(Icons.event),
            title: Text(_formatDate(date)),
            subtitle: _buildScheduleSubtitle(schedule),
            trailing: IconButton(
              onPressed: () => _removeSpecialDate(date),
              icon: const Icon(Icons.delete_outline),
              color: Theme.of(context).colorScheme.error,
            ),
            onTap: () => _editSpecialDate(date, schedule),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildScheduleSubtitle(Map<String, dynamic> schedule) {
    if (schedule['closed'] == true) {
      return const Text('Closed');
    }

    final start = schedule['start'] as String?;
    final end = schedule['end'] as String?;

    if (start != null && end != null) {
      return Text('$start - $end');
    }

    return const Text('Available');
  }

  String _formatDate(String dateStr) {
    try {
      final date = DateTime.parse(dateStr);
      return '${date.day}/${date.month}/${date.year}';
    } catch (e) {
      return dateStr;
    }
  }

  void _setAllDaysAvailable() {
    // Use controller methods instead
    for (final day in controller.weekdays) {
      controller.updateWeekdayAvailability(day, true);
    }
    onAvailabilityScheduleChanged(controller.availabilitySchedule);
  }

  void _clearAllSchedules() {
    // Use controller methods instead
    for (final day in controller.weekdays) {
      controller.updateWeekdayAvailability(day, false);
    }
    onAvailabilityScheduleChanged(controller.availabilitySchedule);
  }

  void _addSpecialDate() {
    // TODO: Implement special date functionality with controller
  }

  void _editSpecialDate(String date, Map<String, dynamic> schedule) {
    // TODO: Implement special date editing with controller
  }

  void _removeSpecialDate(String date) {
    // TODO: Implement special date removal with controller
  }
}

class _DayScheduleRow extends StatelessWidget {
  const _DayScheduleRow({
    required this.day,
    required this.dayLabel,
    required this.schedule,
    required this.onScheduleChanged,
  });

  final String day;
  final String dayLabel;
  final Map<String, dynamic>? schedule;
  final Function(Map<String, dynamic>?) onScheduleChanged;

  @override
  Widget build(BuildContext context) {
    final isClosed = schedule?['closed'] == true;
    final hasCustomSchedule = schedule != null && !isClosed;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          // Day label
          SizedBox(
            width: 100,
            child: Text(
              dayLabel,
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
            ),
          ),

          // Schedule status
          Expanded(
            child: Row(
              children: [
                // Status chips
                if (schedule == null)
                  Chip(
                    label: const Text('Use Restaurant Hours'),
                    backgroundColor:
                        Theme.of(context).colorScheme.surfaceContainerHighest,
                  )
                else if (isClosed)
                  Chip(
                    label: const Text('Closed'),
                    backgroundColor: Colors.red.withOpacity(0.1),
                    side: BorderSide(color: Colors.red.withOpacity(0.3)),
                  )
                else
                  Chip(
                    label: Text('${schedule!['start']} - ${schedule!['end']}'),
                    backgroundColor: Colors.green.withOpacity(0.1),
                    side: BorderSide(color: Colors.green.withOpacity(0.3)),
                  ),
              ],
            ),
          ),

          // Actions
          PopupMenuButton<String>(
            onSelected: (value) => _handleAction(value, context),
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'restaurant_hours',
                child: Text('Use Restaurant Hours'),
              ),
              const PopupMenuItem(
                value: 'custom_hours',
                child: Text('Set Custom Hours'),
              ),
              const PopupMenuItem(
                value: 'closed',
                child: Text('Mark as Closed'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  void _handleAction(String action, BuildContext context) {
    switch (action) {
      case 'restaurant_hours':
        onScheduleChanged(null);
        break;
      case 'custom_hours':
        _showTimePickerDialog(context);
        break;
      case 'closed':
        onScheduleChanged({'closed': true});
        break;
    }
  }

  void _showTimePickerDialog(BuildContext context) {
    final startController =
        TextEditingController(text: schedule?['start'] ?? '09:00');
    final endController =
        TextEditingController(text: schedule?['end'] ?? '22:00');

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Set Hours for $dayLabel'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: startController,
                    decoration: const InputDecoration(
                      labelText: 'Start Time',
                      hintText: '09:00',
                    ),
                    onTap: () => _selectTime(context, startController),
                    readOnly: true,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextField(
                    controller: endController,
                    decoration: const InputDecoration(
                      labelText: 'End Time',
                      hintText: '22:00',
                    ),
                    onTap: () => _selectTime(context, endController),
                    readOnly: true,
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              onScheduleChanged({
                'closed': false,
                'start': startController.text,
                'end': endController.text,
              });
              Navigator.of(context).pop();
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _selectTime(
      BuildContext context, TextEditingController controller) async {
    final currentTime = _parseTime(controller.text);
    final time = await showTimePicker(
      context: context,
      initialTime: currentTime,
    );

    if (time != null) {
      controller.text = _formatTime(time);
    }
  }

  TimeOfDay _parseTime(String timeStr) {
    try {
      final parts = timeStr.split(':');
      return TimeOfDay(
        hour: int.parse(parts[0]),
        minute: int.parse(parts[1]),
      );
    } catch (e) {
      return const TimeOfDay(hour: 9, minute: 0);
    }
  }

  String _formatTime(TimeOfDay time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }
}

class _SpecialDateDialog extends StatefulWidget {
  const _SpecialDateDialog({
    required this.existingDate,
    required this.existingSchedule,
    required this.onSave,
  });

  final String? existingDate;
  final Map<String, dynamic>? existingSchedule;
  final Function(String, Map<String, dynamic>) onSave;

  @override
  State<_SpecialDateDialog> createState() => _SpecialDateDialogState();
}

class _SpecialDateDialogState extends State<_SpecialDateDialog> {
  DateTime? _selectedDate;
  bool _isClosed = false;
  final _startTimeController = TextEditingController();
  final _endTimeController = TextEditingController();

  @override
  void initState() {
    super.initState();

    if (widget.existingDate != null) {
      _selectedDate = DateTime.parse(widget.existingDate!);
    }

    if (widget.existingSchedule != null) {
      _isClosed = widget.existingSchedule!['closed'] == true;
      _startTimeController.text = widget.existingSchedule!['start'] ?? '09:00';
      _endTimeController.text = widget.existingSchedule!['end'] ?? '22:00';
    } else {
      _startTimeController.text = '09:00';
      _endTimeController.text = '22:00';
    }
  }

  @override
  void dispose() {
    _startTimeController.dispose();
    _endTimeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.existingDate == null
          ? 'Add Special Date'
          : 'Edit Special Date'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Date picker
          ListTile(
            leading: const Icon(Icons.calendar_today),
            title: Text(_selectedDate == null
                ? 'Select Date'
                : '${_selectedDate!.day}/${_selectedDate!.month}/${_selectedDate!.year}'),
            onTap: _selectDate,
          ),
          const SizedBox(height: 16),

          // Closed toggle
          SwitchListTile(
            title: const Text('Closed'),
            subtitle: const Text('Item is not available on this date'),
            value: _isClosed,
            onChanged: (value) {
              setState(() {
                _isClosed = value;
              });
            },
          ),

          // Time pickers (only if not closed)
          if (!_isClosed) ...[
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _startTimeController,
                    decoration: const InputDecoration(
                      labelText: 'Start Time',
                    ),
                    onTap: () => _selectTime(_startTimeController),
                    readOnly: true,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextField(
                    controller: _endTimeController,
                    decoration: const InputDecoration(
                      labelText: 'End Time',
                    ),
                    onTap: () => _selectTime(_endTimeController),
                    readOnly: true,
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _canSave() ? _save : null,
          child: const Text('Save'),
        ),
      ],
    );
  }

  bool _canSave() {
    return _selectedDate != null;
  }

  void _selectDate() async {
    final date = await showDatePicker(
      context: context,
      initialDate: _selectedDate ?? DateTime.now(),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );

    if (date != null) {
      setState(() {
        _selectedDate = date;
      });
    }
  }

  void _selectTime(TextEditingController controller) async {
    final currentTime = _parseTime(controller.text);
    final time = await showTimePicker(
      context: context,
      initialTime: currentTime,
    );

    if (time != null) {
      controller.text = _formatTime(time);
    }
  }

  TimeOfDay _parseTime(String timeStr) {
    try {
      final parts = timeStr.split(':');
      return TimeOfDay(
        hour: int.parse(parts[0]),
        minute: int.parse(parts[1]),
      );
    } catch (e) {
      return const TimeOfDay(hour: 9, minute: 0);
    }
  }

  String _formatTime(TimeOfDay time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }

  void _save() {
    final dateStr = _selectedDate!.toIso8601String().split('T')[0];
    final schedule = _isClosed
        ? {'closed': true}
        : {
            'closed': false,
            'start': _startTimeController.text,
            'end': _endTimeController.text,
          };

    widget.onSave(dateStr, schedule);
    Navigator.of(context).pop();
  }
}
