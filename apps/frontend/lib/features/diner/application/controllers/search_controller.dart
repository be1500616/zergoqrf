/// Search controller for diner menu search functionality.
///
/// This controller manages search state and provides reactive search capabilities
/// for the diner menu experience.
library;

import 'package:flutter/material.dart';
import 'package:get/get.dart';

class MenuSearchController extends GetxController {
  /// Text editing controller for search input
  final TextEditingController textController = TextEditingController();

  /// Focus node for search input
  final FocusNode focusNode = FocusNode();

  /// Current search query
  final RxString searchQuery = ''.obs;

  /// Whether search has text
  bool get hasText => searchQuery.value.isNotEmpty;

  @override
  void onInit() {
    super.onInit();

    // Listen to text changes
    textController.addListener(() {
      searchQuery.value = textController.text;
    });
  }

  @override
  void onClose() {
    textController.dispose();
    focusNode.dispose();
    super.onClose();
  }

  /// Clear search input
  void clearSearch() {
    textController.clear();
    searchQuery.value = '';
  }

  /// Handle search submission
  void onSearchSubmitted(String query) {
    searchQuery.value = query;
    focusNode.unfocus();
  }

  /// Handle search text changes
  void onSearchChanged(String query) {
    searchQuery.value = query;
  }
}
