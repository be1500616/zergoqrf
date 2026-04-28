# ZERGO QR Responsive System Documentation

## Overview

The ZERGO QR responsive system provides a comprehensive solution for building adaptive user interfaces that work seamlessly across mobile, tablet, and desktop platforms. Built following Clean Architecture principles, it integrates with the existing GetX state management and design system.

## Table of Contents

1. [Architecture](#architecture)
2. [Breakpoint System](#breakpoint-system)
3. [Core Components](#core-components)
4. [Usage Examples](#usage-examples)
5. [Integration with Existing Systems](#integration-with-existing-systems)
6. [Testing](#testing)
7. [Best Practices](#best-practices)

## Architecture

The responsive system follows a layered architecture:

```
lib/shared/responsive/
├── breakpoints.dart          # Breakpoint definitions and utilities
├── screen_size.dart          # Screen size detection and utilities
├── test_utils.dart           # Testing utilities and mock devices
├── widgets/
│   ├── adaptive_container.dart    # Responsive containers
│   ├── responsive_builder.dart    # Builder widgets
│   ├── responsive_grid.dart       # Grid layouts
│   ├── responsive_layout.dart     # Layout switching
│   └── index.dart                 # Widget exports
└── index.dart                # Main exports
```

## Breakpoint System

### Defined Breakpoints

The system uses five breakpoints following Material Design guidelines:

| Breakpoint | Range | Description | Use Case |
|------------|-------|-------------|----------|
| `mobile` | 0-427px | Small mobile devices | Single-column, touch-optimized |
| `mobileLarge` | 428-599px | Large mobile devices | Enhanced touch targets |
| `tablet` | 600-1023px | Tablet devices | Two-column, hybrid input |
| `desktop` | 1024-1439px | Desktop devices | Multi-column, pointer-optimized |
| `desktopXL` | 1440px+ | Large desktop | Maximum information density |

### Usage

```dart
import 'package:zergo_frontend/shared/responsive/index.dart';

// Get current breakpoint
final breakpoint = BreakpointConfig.getCurrentBreakpoint(context);

// Check specific breakpoint
if (BreakpointConfig.isBreakpoint(context, Breakpoint.mobile)) {
  // Mobile-specific logic
}

// Check minimum breakpoint
if (BreakpointConfig.isAtLeastBreakpoint(context, Breakpoint.tablet)) {
  // Tablet and above logic
}
```

## Core Components

### ResponsiveBuilder

Provides breakpoint context to child widgets:

```dart
ResponsiveBuilder(
  builder: (context, breakpoint) {
    switch (breakpoint) {
      case Breakpoint.mobile:
        return MobileLayout();
      case Breakpoint.tablet:
        return TabletLayout();
      case Breakpoint.desktop:
        return DesktopLayout();
      default:
        return DefaultLayout();
    }
  },
)
```

### ResponsiveLayout

Declarative layout switching:

```dart
ResponsiveLayout(
  mobile: MobileMenuLayout(),
  tablet: TabletMenuLayout(),
  desktop: DesktopMenuLayout(),
  fallback: DefaultMenuLayout(), // Optional
)
```

### ResponsiveGrid

Adaptive grid with automatic column calculation:

```dart
ResponsiveGrid(
  children: menuItems.map((item) => MenuItemCard(item: item)).toList(),
)
```

### AdaptiveContainer

Container with responsive properties:

```dart
AdaptiveContainer(
  child: MenuContent(),
  // Automatically adapts padding, margin, and constraints
)
```

### ScreenSize Utility

Comprehensive screen information:

```dart
final screenSize = ScreenSize.of(context);

// Breakpoint checks
if (screenSize.isMobile) { /* mobile logic */ }
if (screenSize.isTablet) { /* tablet logic */ }
if (screenSize.isDesktop) { /* desktop logic */ }

// Responsive value selection
final columns = screenSize.responsiveValue(
  mobile: 1,
  tablet: 2,
  desktop: 3,
);

// Platform detection
if (screenSize.isWeb) { /* web-specific logic */ }
if (screenSize.isMobilePlatform) { /* mobile platform logic */ }

// Orientation
if (screenSize.isLandscape) { /* landscape logic */ }
```

## Usage Examples

### Basic Responsive Widget

```dart
class ResponsiveMenuCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ResponsiveBuilder(
      builder: (context, breakpoint) {
        return AdaptiveCard(
          child: Column(
            children: [
              Text('Menu Item'),
              if (breakpoint != Breakpoint.mobile)
                Text('Additional details for larger screens'),
            ],
          ),
        );
      },
    );
  }
}
```

### Complex Responsive Layout

```dart
class ResponsiveMenuScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final screenSize = ScreenSize.of(context);
    
    return ResponsiveLayout(
      mobile: _buildMobileLayout(screenSize),
      tablet: _buildTabletLayout(screenSize),
      desktop: _buildDesktopLayout(screenSize),
    );
  }
  
  Widget _buildMobileLayout(ScreenSize screenSize) {
    return Column(
      children: [
        SearchBar(),
        Expanded(
          child: ListView(
            children: menuItems.map((item) => 
              MenuItemCard(item: item)
            ).toList(),
          ),
        ),
      ],
    );
  }
  
  Widget _buildTabletLayout(ScreenSize screenSize) {
    return Row(
      children: [
        SizedBox(
          width: 300,
          child: CategorySidebar(),
        ),
        Expanded(
          child: ResponsiveGrid(
            children: menuItems.map((item) => 
              MenuItemCard(item: item)
            ).toList(),
          ),
        ),
      ],
    );
  }
  
  Widget _buildDesktopLayout(ScreenSize screenSize) {
    return Row(
      children: [
        SizedBox(
          width: 280,
          child: NavigationSidebar(),
        ),
        Expanded(
          child: Column(
            children: [
              SearchAndFilters(),
              Expanded(
                child: ResponsiveGrid(
                  children: menuItems.map((item) => 
                    MenuItemCard(item: item)
                  ).toList(),
                ),
              ),
            ],
          ),
        ),
        SizedBox(
          width: 320,
          child: CartSidebar(),
        ),
      ],
    );
  }
}
```

## Integration with Existing Systems

### GetX Integration

The responsive system works seamlessly with GetX controllers:

```dart
class MenuController extends GetxController {
  final _screenSize = Rx<ScreenSize?>(null);
  
  void updateScreenSize(ScreenSize screenSize) {
    _screenSize.value = screenSize;
    // Trigger responsive updates
    update();
  }
  
  int get gridColumns => _screenSize.value?.gridColumns ?? 1;
}

// In widget
ResponsiveBuilder(
  builder: (context, breakpoint) {
    final controller = Get.find<MenuController>();
    controller.updateScreenSize(ScreenSize.of(context));
    
    return Obx(() => ResponsiveGrid(
      children: controller.menuItems.map((item) => 
        MenuItemCard(item: item)
      ).toList(),
    ));
  },
)
```

### Theme System Integration

The responsive system extends the existing AppSpacing system:

```dart
// Responsive spacing automatically applied
final spacing = AppSpacing.md * ScreenSize.of(context).spacingMultiplier;

// Or use ResponsiveSpacing directly
final responsiveSpacing = ResponsiveSpacing.getSpacing(
  AppSpacing.md, 
  MediaQuery.of(context).size.width
);
```

## Testing

### Using ResponsiveTestUtils

```dart
testWidgets('should show mobile layout on mobile screen', (tester) async {
  await tester.pumpWidget(
    ResponsiveTestUtils.wrapWithMediaQuery(
      child: MyResponsiveWidget(),
      deviceConfig: ResponsiveTestUtils.mobileDevice,
    ),
  );
  
  expect(find.byType(MobileLayout), findsOneWidget);
  expect(find.byType(DesktopLayout), findsNothing);
});

// Test across all devices
ResponsiveTestUtils.testAcrossDevices(
  'should render correctly',
  (tester, device) async {
    await tester.pumpWidget(
      ResponsiveTestUtils.wrapWithMediaQuery(
        child: MyResponsiveWidget(),
        deviceConfig: device,
      ),
    );
    
    expect(find.byType(MyResponsiveWidget), findsOneWidget);
  },
);

// Test across breakpoints
ResponsiveTestUtils.testAcrossBreakpoints(
  'should adapt to breakpoint',
  (tester, device, breakpoint) async {
    await tester.pumpWidget(
      ResponsiveTestUtils.wrapWithMediaQuery(
        child: MyResponsiveWidget(),
        deviceConfig: device,
      ),
    );
    
    // Verify breakpoint-specific behavior
    switch (breakpoint) {
      case Breakpoint.mobile:
        expect(find.byType(MobileLayout), findsOneWidget);
        break;
      case Breakpoint.desktop:
        expect(find.byType(DesktopLayout), findsOneWidget);
        break;
    }
  },
);
```

## Best Practices

### 1. Mobile-First Design

Always start with mobile layout and progressively enhance:

```dart
ResponsiveLayout(
  mobile: MobileLayout(),           // Required
  tablet: TabletLayout(),           // Enhanced
  desktop: DesktopLayout(),         // Most enhanced
)
```

### 2. Use Semantic Breakpoints

Focus on content and functionality rather than specific devices:

```dart
// Good: Content-based decisions
if (screenSize.isCompact) {
  return SingleColumnLayout();
} else {
  return MultiColumnLayout();
}

// Avoid: Device-specific decisions
if (screenSize.width == 375) { /* iPhone specific */ }
```

### 3. Consistent Spacing

Use the responsive spacing system:

```dart
// Good: Responsive spacing
AdaptiveContainer(
  child: content,
  // Automatically applies responsive padding
)

// Good: Manual responsive spacing
Padding(
  padding: EdgeInsets.all(
    AppSpacing.md * ScreenSize.of(context).spacingMultiplier
  ),
  child: content,
)
```

### 4. Performance Considerations

- Use `ResponsiveBuilder` sparingly to avoid unnecessary rebuilds
- Prefer `ResponsiveLayout` for simple layout switching
- Cache expensive calculations in controllers

### 5. Accessibility

The system automatically handles accessibility requirements:

- Minimum touch targets (44px) on mobile
- Appropriate spacing for different input methods
- Platform-specific interaction patterns

## Migration Guide

### From Existing Responsive Code

1. Replace manual breakpoint checks:
```dart
// Before
if (MediaQuery.of(context).size.width > 600) {
  return TabletLayout();
}

// After
if (ScreenSize.of(context).isTablet) {
  return TabletLayout();
}
```

2. Use responsive widgets:
```dart
// Before
Container(
  padding: EdgeInsets.all(16),
  child: content,
)

// After
AdaptiveContainer(
  child: content,
)
```

3. Leverage responsive utilities:
```dart
// Before
final columns = MediaQuery.of(context).size.width > 600 ? 2 : 1;

// After
final columns = ScreenSize.of(context).responsiveValue(
  mobile: 1,
  tablet: 2,
  desktop: 3,
);
```

This responsive system provides a solid foundation for building adaptive interfaces in the ZERGO QR application while maintaining consistency with existing patterns and ensuring excellent user experience across all devices.
