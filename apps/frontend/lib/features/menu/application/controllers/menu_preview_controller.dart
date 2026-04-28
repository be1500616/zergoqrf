/// Menu preview controller for managing preview options and device selection.
///
/// This controller replaces the StatefulWidget pattern in MenuPreviewTab
/// with GetX reactive state management.

import 'package:get/get.dart';

class MenuPreviewController extends GetxController {
  // Observable state
  final _selectedDevice = 'mobile'.obs;
  final _showPrices = true.obs;
  final _showDescriptions = true.obs;
  
  // Getters
  String get selectedDevice => _selectedDevice.value;
  bool get showPrices => _showPrices.value;
  bool get showDescriptions => _showDescriptions.value;
  
  /// Update selected device for preview
  void updateSelectedDevice(String device) {
    if (device == 'mobile' || device == 'tablet') {
      _selectedDevice.value = device;
    }
  }
  
  /// Toggle price visibility in preview
  void togglePrices(bool show) {
    _showPrices.value = show;
  }
  
  /// Toggle description visibility in preview
  void toggleDescriptions(bool show) {
    _showDescriptions.value = show;
  }
  
  /// Get device width for preview container
  double getDeviceWidth() {
    return selectedDevice == 'mobile' ? 375 : 768;
  }
  
  /// Reset preview options to defaults
  void resetToDefaults() {
    _selectedDevice.value = 'mobile';
    _showPrices.value = true;
    _showDescriptions.value = true;
  }
}
