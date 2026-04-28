/// Availability controller for managing menu item availability schedules.
///
/// This controller replaces the StatefulWidget pattern in MenuItemAvailabilityTab
/// with GetX reactive state management.
library;

import 'package:flutter/material.dart';
import 'package:get/get.dart';

class AvailabilityController extends GetxController {
  // Observable state
  final _availabilitySchedule = <String, dynamic>{}.obs;
  final _specialDates = <DateTime, Map<String, dynamic>>{}.obs;

  // Weekday constants
  final List<String> weekdays = [
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday',
  ];

  final List<String> weekdayLabels = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday',
  ];

  // Getters
  Map<String, dynamic> get availabilitySchedule => _availabilitySchedule;
  Map<DateTime, Map<String, dynamic>> get specialDates => _specialDates;

  /// Initialize with existing availability schedule
  void initializeSchedule(Map<String, dynamic> schedule) {
    _availabilitySchedule.assignAll(schedule);

    // Load special dates if they exist
    if (schedule.containsKey('special_dates')) {
      final specialDatesData =
          schedule['special_dates'] as Map<String, dynamic>? ?? {};
      _specialDates.clear();
      specialDatesData.forEach((dateStr, data) {
        final date = DateTime.tryParse(dateStr);
        if (date != null) {
          _specialDates[date] = data as Map<String, dynamic>;
        }
      });
    }
  }

  /// Update availability for a specific weekday
  void updateWeekdayAvailability(String weekday, bool isAvailable,
      {TimeOfDay? startTime, TimeOfDay? endTime}) {
    if (!weekdays.contains(weekday)) return;

    if (isAvailable && startTime != null && endTime != null) {
      _availabilitySchedule[weekday] = {
        'available': true,
        'start_time':
            '${startTime.hour.toString().padLeft(2, '0')}:${startTime.minute.toString().padLeft(2, '0')}',
        'end_time':
            '${endTime.hour.toString().padLeft(2, '0')}:${endTime.minute.toString().padLeft(2, '0')}',
      };
    } else if (isAvailable) {
      _availabilitySchedule[weekday] = {
        'available': true,
        'start_time': '00:00',
        'end_time': '23:59',
      };
    } else {
      _availabilitySchedule[weekday] = {
        'available': false,
      };
    }

    _notifyScheduleChanged();
  }

  /// Check if a weekday is available
  bool isWeekdayAvailable(String weekday) {
    if (!weekdays.contains(weekday)) return false;
    final daySchedule = _availabilitySchedule[weekday] as Map<String, dynamic>?;
    return daySchedule?['available'] == true;
  }

  /// Get start time for a weekday
  TimeOfDay? getWeekdayStartTime(String weekday) {
    if (!weekdays.contains(weekday)) return null;
    final daySchedule = _availabilitySchedule[weekday] as Map<String, dynamic>?;
    final startTimeStr = daySchedule?['start_time'] as String?;
    if (startTimeStr == null) return null;

    final parts = startTimeStr.split(':');
    if (parts.length != 2) return null;

    final hour = int.tryParse(parts[0]);
    final minute = int.tryParse(parts[1]);
    if (hour == null || minute == null) return null;

    return TimeOfDay(hour: hour, minute: minute);
  }

  /// Get end time for a weekday
  TimeOfDay? getWeekdayEndTime(String weekday) {
    if (!weekdays.contains(weekday)) return null;
    final daySchedule = _availabilitySchedule[weekday] as Map<String, dynamic>?;
    final endTimeStr = daySchedule?['end_time'] as String?;
    if (endTimeStr == null) return null;

    final parts = endTimeStr.split(':');
    if (parts.length != 2) return null;

    final hour = int.tryParse(parts[0]);
    final minute = int.tryParse(parts[1]);
    if (hour == null || minute == null) return null;

    return TimeOfDay(hour: hour, minute: minute);
  }

  /// Set all days as available
  void setAllDaysAvailable() {
    for (final weekday in weekdays) {
      updateWeekdayAvailability(weekday, true);
    }
  }

  /// Clear all schedules
  void clearAllSchedules() {
    for (final weekday in weekdays) {
      updateWeekdayAvailability(weekday, false);
    }
    _specialDates.clear();
    _notifyScheduleChanged();
  }

  /// Add special date
  void addSpecialDate(DateTime date,
      {bool isClosed = false, TimeOfDay? startTime, TimeOfDay? endTime}) {
    if (isClosed) {
      _specialDates[date] = {
        'closed': true,
      };
    } else if (startTime != null && endTime != null) {
      _specialDates[date] = {
        'closed': false,
        'start_time':
            '${startTime.hour.toString().padLeft(2, '0')}:${startTime.minute.toString().padLeft(2, '0')}',
        'end_time':
            '${endTime.hour.toString().padLeft(2, '0')}:${endTime.minute.toString().padLeft(2, '0')}',
      };
    }
    _notifyScheduleChanged();
  }

  /// Remove special date
  void removeSpecialDate(DateTime date) {
    _specialDates.remove(date);
    _notifyScheduleChanged();
  }

  /// Check if a date is a special date
  bool isSpecialDate(DateTime date) {
    return _specialDates.containsKey(date);
  }

  /// Check if a special date is closed
  bool isSpecialDateClosed(DateTime date) {
    final specialDate = _specialDates[date];
    return specialDate?['closed'] == true;
  }

  /// Get formatted schedule for API
  Map<String, dynamic> getFormattedSchedule() {
    final schedule = Map<String, dynamic>.from(_availabilitySchedule);

    // Add special dates
    if (_specialDates.isNotEmpty) {
      final specialDatesFormatted = <String, dynamic>{};
      _specialDates.forEach((date, data) {
        specialDatesFormatted[date.toIso8601String().split('T')[0]] = data;
      });
      schedule['special_dates'] = specialDatesFormatted;
    }

    return schedule;
  }

  /// Notify parent about schedule changes
  void _notifyScheduleChanged() {
    // This will be called by the parent widget to get updated schedule
    // The parent should listen to this controller's reactive state
  }

  /// Copy schedule from another day
  void copyScheduleFromDay(String fromWeekday, String toWeekday) {
    if (!weekdays.contains(fromWeekday) || !weekdays.contains(toWeekday))
      return;

    final fromSchedule =
        _availabilitySchedule[fromWeekday] as Map<String, dynamic>?;
    if (fromSchedule != null) {
      _availabilitySchedule[toWeekday] =
          Map<String, dynamic>.from(fromSchedule);
      _notifyScheduleChanged();
    }
  }

  /// Parse time string to TimeOfDay
  TimeOfDay? parseTimeOfDay(String? timeString) {
    if (timeString == null || timeString.isEmpty) return null;

    try {
      final parts = timeString.split(':');
      if (parts.length == 2) {
        final hour = int.parse(parts[0]);
        final minute = int.parse(parts[1]);
        return TimeOfDay(hour: hour, minute: minute);
      }
    } catch (e) {
      // Invalid time format
    }

    return null;
  }

  /// Get formatted time string
  String formatTime(TimeOfDay time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }
}
