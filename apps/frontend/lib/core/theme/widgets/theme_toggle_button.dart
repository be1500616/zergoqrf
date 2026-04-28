import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:get/get.dart';

import '../theme_controller.dart';

/// A beautiful animated toggle button for switching between light and dark themes
class ThemeToggleButton extends StatelessWidget {
  const ThemeToggleButton({
    super.key,
    this.size = 24.0,
    this.padding = const EdgeInsets.all(12.0),
  });

  final double size;
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    final themeController = Get.find<ThemeController>();
    final theme = Theme.of(context);

    return Obx(() {
      final isDark = themeController.isDarkMode;

      return Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => themeController.toggleTheme(),
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: padding,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: theme.colorScheme.outline.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: AnimatedSwitcher(
              duration: 300.ms,
              transitionBuilder: (child, animation) {
                return RotationTransition(
                  turns: animation,
                  child: FadeTransition(
                    opacity: animation,
                    child: child,
                  ),
                );
              },
              child: Icon(
                isDark ? Icons.dark_mode : Icons.light_mode,
                key: ValueKey(isDark),
                size: size,
                color: isDark
                    ? theme.colorScheme.primary
                    : theme.colorScheme.secondary,
              ),
            ),
          ),
        ),
      )
          .animate(
            onPlay: (controller) => controller.repeat(reverse: true),
          )
          .shimmer(
            delay: 3000.ms,
            duration: 1500.ms,
            color: theme.colorScheme.primary.withOpacity(0.1),
          );
    });
  }
}

/// Icon-only version for AppBar or compact spaces
class ThemeToggleIconButton extends StatelessWidget {
  const ThemeToggleIconButton({super.key});

  @override
  Widget build(BuildContext context) {
    final themeController = Get.find<ThemeController>();
    final theme = Theme.of(context);

    return Obx(() {
      final isDark = themeController.isDarkMode;

      return Tooltip(
        message: themeController.themeTooltip,
        child: IconButton(
          onPressed: () => themeController.toggleTheme(),
          icon: AnimatedSwitcher(
            duration: 300.ms,
            transitionBuilder: (child, animation) {
              return RotationTransition(
                turns: animation,
                child: ScaleTransition(
                  scale: animation,
                  child: child,
                ),
              );
            },
            child: Icon(
              isDark ? Icons.dark_mode : Icons.light_mode,
              key: ValueKey(isDark),
              color: isDark
                  ? theme.colorScheme.primary
                  : theme.colorScheme.secondary,
            ),
          ),
        ),
      );
    });
  }
}

/// Segmented button version with labels
class ThemeToggleSegmented extends StatelessWidget {
  const ThemeToggleSegmented({super.key});

  @override
  Widget build(BuildContext context) {
    final themeController = Get.find<ThemeController>();
    final theme = Theme.of(context);

    return Obx(() {
      final themeMode = themeController.themeMode;

      return SegmentedButton<ThemeMode>(
        segments: [
          const ButtonSegment(
            value: ThemeMode.light,
            icon: Icon(Icons.light_mode),
            label: Text('Light'),
          ),
          const ButtonSegment(
            value: ThemeMode.system,
            icon: Icon(Icons.brightness_auto),
            label: Text('Auto'),
          ),
          const ButtonSegment(
            value: ThemeMode.dark,
            icon: Icon(Icons.dark_mode),
            label: Text('Dark'),
          ),
        ],
        selected: {themeMode},
        onSelectionChanged: (Set<ThemeMode> selection) {
          themeController.setThemeMode(selection.first);
        },
        style: ButtonStyle(
          backgroundColor: WidgetStateProperty.resolveWith((states) {
            if (states.contains(WidgetState.selected)) {
              return theme.colorScheme.primaryContainer;
            }
            return theme.colorScheme.surface;
          }),
          foregroundColor: WidgetStateProperty.resolveWith((states) {
            if (states.contains(WidgetState.selected)) {
              return theme.colorScheme.onPrimaryContainer;
            }
            return theme.colorScheme.onSurface;
          }),
        ),
      );
    });
  }
}
