import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../application/controllers/search_controller.dart';

/// Enhanced search bar widget for menu items.
class MenuSearchBar extends GetView<MenuSearchController> {
  const MenuSearchBar({
    super.key,
    required this.onSearch,
    required this.onClear,
  });

  final Function(String) onSearch;
  final VoidCallback onClear;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Container(
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: colorScheme.outline),
      ),
      child: TextField(
        controller: controller.textController,
        focusNode: controller.focusNode,
        onChanged: (value) {
          controller.onSearchChanged(value);
          onSearch(value);
        },
        onSubmitted: (value) {
          controller.onSearchSubmitted(value);
          onSearch(value);
        },
        decoration: InputDecoration(
          hintText: 'Search menu items...',
          hintStyle: TextStyle(color: colorScheme.onSurfaceVariant),
          prefixIcon: Icon(Icons.search, color: colorScheme.onSurfaceVariant),
          suffixIcon: Obx(() => controller.hasText
              ? IconButton(
                  icon: Icon(Icons.clear, color: colorScheme.onSurfaceVariant),
                  onPressed: () {
                    controller.clearSearch();
                    onClear();
                  },
                )
              : const SizedBox.shrink()),
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 12,
          ),
        ),
      ),
    );
  }
}
