import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Controller for managing app theme mode (light/dark)
/// Persists user preference and provides smooth theme switching
class ThemeController extends GetxController {
  static const String _themeModeKey = 'theme_mode';

  final Rx<ThemeMode> _themeMode = ThemeMode.light.obs;
  ThemeMode get themeMode => _themeMode.value;

  final RxBool _isDarkMode = false.obs;
  bool get isDarkMode => _isDarkMode.value;

  @override
  void onInit() {
    super.onInit();
    _loadThemeMode();
  }

  /// Load saved theme mode from shared preferences
  Future<void> _loadThemeMode() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedMode = prefs.getString(_themeModeKey);

      if (savedMode != null) {
        _themeMode.value = ThemeMode.values.firstWhere(
          (mode) => mode.toString() == savedMode,
          orElse: () => ThemeMode.system,
        );
      }

      // Update dark mode flag based on current brightness
      _updateDarkModeFlag();
    } catch (e) {
      debugPrint('Error loading theme mode: $e');
    }
  }

  /// Save theme mode to shared preferences
  Future<void> _saveThemeMode(ThemeMode mode) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_themeModeKey, mode.toString());
    } catch (e) {
      debugPrint('Error saving theme mode: $e');
    }
  }

  /// Update the dark mode flag based on current theme mode and system brightness
  void _updateDarkModeFlag() {
    final brightness =
        WidgetsBinding.instance.platformDispatcher.platformBrightness;

    if (_themeMode.value == ThemeMode.dark) {
      _isDarkMode.value = true;
    } else if (_themeMode.value == ThemeMode.light) {
      _isDarkMode.value = false;
    } else {
      // ThemeMode.system
      _isDarkMode.value = brightness == Brightness.dark;
    }
  }

  /// Toggle between light and dark mode
  Future<void> toggleTheme() async {
    if (_themeMode.value == ThemeMode.light) {
      await setThemeMode(ThemeMode.dark);
    } else {
      await setThemeMode(ThemeMode.light);
    }
  }

  /// Set specific theme mode
  Future<void> setThemeMode(ThemeMode mode) async {
    _themeMode.value = mode;
    _updateDarkModeFlag();
    await _saveThemeMode(mode);

    // Update GetX theme
    Get.changeThemeMode(mode);
  }

  /// Get icon for current theme mode
  IconData get themeIcon {
    if (_themeMode.value == ThemeMode.dark || _isDarkMode.value) {
      return Icons.dark_mode;
    } else {
      return Icons.light_mode;
    }
  }

  /// Get tooltip text for theme toggle button
  String get themeTooltip {
    if (_themeMode.value == ThemeMode.dark || _isDarkMode.value) {
      return 'Switch to Light Mode';
    } else {
      return 'Switch to Dark Mode';
    }
  }
}
