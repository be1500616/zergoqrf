# AI UI Generation Prompts for Restaurant Onboarding & Dashboard

This document contains optimized prompts for AI code generation tools (v0.dev, Lovable, Cursor, etc.) to implement Flutter UI components based on the comprehensive design specifications.

## Quick Start Prompts

### 1. Complete Restaurant Onboarding Wizard
```
Create a complete 4-step restaurant onboarding wizard in Flutter with Material Design 3.

Requirements:
- 4-step progressive wizard with business details, restaurant info, staff management, and review
- Responsive design supporting mobile (320px+), tablet (768px+), desktop (1024px+)
- Form validation with real-time feedback
- Smooth step transitions with slide animations
- Auto-save draft functionality
- Professional restaurant industry theme

Color Scheme:
- Primary: #2E7D32 (Material Green 700)
- Secondary: #1565C0 (Material Blue 700)
- Surface: #FFFFFF with subtle elevation
- Error: #D32F2F (Material Red 700)

Use FormFlowWidget with enhanced form validation, responsive step layouts, and industry-specific input components.

Include:
- Business details step with company structure selection
- Restaurant info step with cuisine type and operating hours
- Staff management step with role-based invitations
- Review step with editable summary and confirmation

Use GetX for state management and implement proper error handling with loading states.
```

### 2. Restaurant Dashboard with Real-time Metrics
```
Create a comprehensive restaurant dashboard in Flutter with real-time metrics and management features.

Requirements:
- Responsive grid layout adapting to all screen sizes
- Real-time sales metrics and analytics
- Table status management with visual indicators
- Staff activity monitoring
- Quick action buttons for common tasks
- Order status tracking with live updates
- Revenue charts and daily summaries

Layout Structure:
- Desktop: 3-column grid (metrics/tables/staff)
- Tablet: 2-column layout (metrics+tables/staff)
- Mobile: Single column with expandable sections

Key Components:
- MetricsOverviewCards (revenue, orders, customers, ratings)
- TableManagementGrid (visual table status)
- StaffActivityList (team performance)
- RecentOrdersWidget (live order tracking)
- QuickActionsPanel (common tasks)

Use Material Design 3 with #2E7D32 primary color, smooth animations, and proper loading states.

Implement with GetX, real-time data simulation, and refresh functionality.
```

## Detailed Component Prompts

### 3. Enhanced Form Validation Components
```
Create Flutter form validation components for restaurant onboarding with Material Design 3.

Features needed:
- Real-time field validation with visual feedback
- Industry-specific input masks (phone, business registration)
- Progressive form strength indicator
- Auto-save draft functionality
- Smart field suggestions (cuisine types, restaurant types)
- Multi-language error messages

Components to build:
1. EnhancedTextFormField with validation styling
2. BusinessRegistrationInput with company type selector
3. OperatingHoursPicker with day-based scheduling
4. CuisineTypeSelector with popular suggestions
5. FormProgressIndicator showing completion percentage

Use InputValidationMixin for consistent validation logic and implement proper accessibility with semantic labels.

Color coding: Green for valid, Red for errors, Orange for warnings, Blue for info.
```

### 4. Responsive Table Management Interface
```
Create a responsive table management interface for restaurants with visual status indicators.

Requirements:
- Dynamic table grid based on restaurant layout
- Color-coded table status (available/occupied/needs-cleaning)
- Drag-and-drop table repositioning
- Quick table actions (assign staff, merge tables, split tables)
- Real-time status updates
- Mobile-optimized table cards

Table Status Colors:
- Available: #4CAF50 (Green)
- Occupied: #FF9800 (Orange)
- Needs Cleaning: #2196F3 (Blue)
- Reserved: #9C27B0 (Purple)
- Out of Service: #9E9E9E (Grey)

Components:
- TableGridView (desktop/tablet)
- TableListView (mobile)
- TableStatusCard with quick actions
- TableLayoutEditor for floor plan management

Implement with GetX, smooth animations, and gesture controls for mobile devices.
```

### 5. Staff Management Dashboard
```
Create a staff management dashboard for restaurants with role-based access and performance tracking.

Features:
- Staff directory with roles and contact info
- Performance metrics (orders handled, ratings, hours worked)
- Schedule management with shift assignments
- Permission management by role (owner/manager/staff)
- Activity timeline and notifications
- Quick staff actions (send message, assign table)

Layout:
- Desktop: 3-column layout (directory/metrics/schedule)
- Tablet: 2-column with collapsible sections
- Mobile: Tabbed interface with bottom navigation

Components:
- StaffDirectoryCard with avatar and status
- PerformanceMetricsWidget with charts
- ShiftSchedulerView with calendar view
- RolePermissionManager with toggle switches
- ActivityFeed with real-time updates

Use Material Design 3, implement search/filter functionality, and add loading states.
```

## Technical Implementation Prompts

### 6. State Management with GetX
```
Implement GetX state management for restaurant dashboard with reactive controllers.

Required Controllers:
1. RestaurantController - restaurant data and settings
2. DashboardController - metrics and analytics
3. TableController - table status management
4. StaffController - staff data and schedules
5. OrderController - order tracking and updates

Features:
- Reactive UI updates with Obx widgets
- Real-time data simulation for development
- Error handling with retry mechanisms
- Loading states and skeleton screens
- Data caching and offline support
- Pagination for large datasets

Controller Structure:
```dart
class RestaurantController extends GetxController {
  final restaurant = Rx<Restaurant?>(null);
  final isLoading = false.obs;
  final error = Rx<String?>(null);

  Future<void> loadRestaurant() async {
    try {
      isLoading.value = true;
      error.value = null;
      // Load restaurant data
    } catch (e) {
      error.value = e.toString();
    } finally {
      isLoading.value = false;
    }
  }
}
```

Use proper dependency injection and implement controller lifecycle management.
```

### 7. Responsive Layout System
```
Create a responsive layout system for restaurant interfaces using Flutter's responsive utilities.

Breakpoint System:
- Mobile: 320px - 767px
- Tablet: 768px - 1023px
- Desktop: 1024px - 1439px
- Large Desktop: 1440px+

Components:
1. ResponsiveBuilder with breakpoint detection
2. AdaptiveLayout for screen-specific widgets
3. ResponsiveGrid with column management
4. ResponsiveContainer with max-width constraints
5. ResponsiveNavigation with mobile-first approach

Implementation:
```dart
class ResponsiveBuilder extends StatelessWidget {
  final Widget Function(BuildContext context, ScreenSize screenSize) builder;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final screenSize = ScreenSize.fromWidth(constraints.maxWidth);
        return builder(context, screenSize);
      },
    );
  }
}
```

Use MediaQuery, LayoutBuilder, and OrientationBuilder for optimal responsive behavior.
```

### 8. Animation and Micro-interactions
```
Implement smooth animations and micro-interactions for restaurant dashboard using Flutter's animation system.

Required Animations:
- Page transitions with slide/fade effects
- Metric counter animations (count up from 0)
- Table status change transitions
- Loading skeleton screens with shimmer effects
- Button press feedback with scale/ripple
- Card hover states with elevation changes
- Chart data animations with easing curves

Animation Controllers:
1. DashboardMetricsAnimation for counter animations
2. TableStatusAnimation for state transitions
3. ChartAnimation for data visualization
4. LoadingAnimation for skeleton screens

Example Implementation:
```dart
class MetricCounterAnimation extends StatefulWidget {
  final int targetValue;
  final Duration duration;

  @override
  _MetricCounterAnimationState createState() => _MetricCounterAnimationState();
}

class _MetricCounterAnimationState extends State<MetricCounterAnimation>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );
    _animation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic),
    );
    _controller.forward();
  }
}
```

Use Curves.easeOutCubic for natural motion and implement proper animation disposal.
```

## Theme and Styling Prompts

### 9. Material Design 3 Theme Implementation
```
Create a Material Design 3 theme for restaurant management application with industry-specific customization.

Theme Requirements:
- Primary Color: #2E7D32 (Material Green 700)
- Secondary Color: #1565C0 (Material Blue 700)
- Surface Colors: White and grey tones with subtle elevation
- Typography: SF Pro / Roboto with clear hierarchy
- Border Radius: 12px for cards, 8px for buttons
- Elevation: 0-8dp with proper shadow layers

Component Themes:
- ElevatedButton with rounded corners and color variants
- Card with subtle borders and hover states
- TextField with floating labels and validation styling
- DataTable with striped rows and hover highlighting
- NavigationBar with active/inactive states

Implementation:
```dart
ThemeData restaurantTheme = ThemeData(
  useMaterial3: true,
  colorScheme: ColorScheme.fromSeed(
    seedColor: Color(0xFF2E7D32),
    brightness: Brightness.light,
  ),
  cardTheme: CardTheme(
    elevation: 2,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(12),
    ),
  ),
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
    ),
  ),
);
```

Include dark theme variant and ensure proper contrast ratios for accessibility.
```

### 10. Industry-Specific Iconography
```
Create a comprehensive icon system for restaurant management with custom SVG icons and Material Icons integration.

Icon Categories:
1. Restaurant Operations: table, chair, menu, order, bill
2. Staff Management: chef, waiter, manager, schedule
3. Analytics: chart, graph, metric, trend
4. Status Indicators: available, occupied, cleaning, reserved

Custom Icons Needed:
- Table status icons (2D top view of tables)
- Cuisine type icons (pizza, burger, pasta, etc.)
- Staff role icons with different colors
- Performance metric icons with trend arrows

Implementation:
```dart
class RestaurantIcons {
  static const IconData tableAvailable = Icons.table_restaurant;
  static const IconData tableOccupied = Icons.table_restaurant;
  static const IconData tableNeedsCleaning = Icons.cleaning_services;

  static Widget tableStatusIcon(TableStatus status) {
    IconData iconData;
    Color color;

    switch (status) {
      case TableStatus.available:
        iconData = Icons.table_restaurant;
        color = Colors.green;
        break;
      case TableStatus.occupied:
        iconData = Icons.table_restaurant;
        color = Colors.orange;
        break;
      // ... other cases
    }

    return Icon(iconData, color: color, size: 24);
  }
}
```

Use consistent sizing (16px, 24px, 32px) and maintain visual hierarchy.
```

## Data Integration Prompts

### 11. API Integration with Supabase
```
Implement Supabase backend integration for restaurant management system with real-time data synchronization.

Required Services:
1. RestaurantService - restaurant data CRUD operations
2. TableService - table status management
3. StaffService - staff data and authentication
4. OrderService - order tracking and updates
5. AnalyticsService - metrics and reporting

Integration Features:
- Real-time subscriptions for table status updates
- Offline data caching with synchronization
- Error handling with retry mechanisms
- Data validation and type safety
- Authentication state management

Example Implementation:
```dart
class RestaurantService {
  final SupabaseClient _supabase;

  RestaurantService(this._supabase);

  Future<List<TableData>> getTables(String restaurantId) async {
    try {
      final response = await _supabase
          .from('tables')
          .select('*')
          .eq('restaurant_id', restaurantId)
          .order('table_number');

      return response.map((json) => TableData.fromJson(json)).toList();
    } catch (e) {
      throw RestaurantException('Failed to load tables: $e');
    }
  }

  Stream<List<TableData>> watchTables(String restaurantId) {
    return _supabase
        .from('tables')
        .stream(primaryKey: ['id'])
        .eq('restaurant_id', restaurantId)
        .map((data) => data.map((json) => TableData.fromJson(json)).toList());
  }
}
```

Implement proper error types, loading states, and data transformation layers.
```

### 12. Real-time Data Simulation
```
Create a real-time data simulation system for development and testing of restaurant dashboard.

Simulation Features:
- Realistic table status changes
- Dynamic order creation and updates
- Staff activity simulation
- Revenue metric fluctuations
- Customer rating updates
- Performance indicators

Simulation Components:
1. TableStatusSimulator for table state changes
2. OrderSimulator for order lifecycle
3. RevenueSimulator for financial metrics
4. StaffActivitySimulator for staff movements

Implementation:
```dart
class DashboardDataSimulator {
  final Random _random = Random();
  Timer? _timer;

  void startSimulation() {
    _timer = Timer.periodic(Duration(seconds: 5), (timer) {
      _simulateTableStatusChange();
      _simulateNewOrder();
      _simulateRevenueUpdate();
    });
  }

  void _simulateTableStatusChange() {
    final tables = Get.find<TableController>().tables;
    if (tables.isNotEmpty) {
      final randomTable = tables[_random.nextInt(tables.length)];
      final newStatus = _getRandomTableStatus(randomTable.status);

      Get.find<TableController>().updateTableStatus(
        randomTable.id,
        newStatus,
      );
    }
  }
}
```

Use realistic timing intervals and data patterns for accurate development testing.
```

## Testing and Quality Assurance Prompts

### 13. Widget Testing Implementation
```
Create comprehensive widget tests for restaurant dashboard components using Flutter's testing framework.

Test Coverage Required:
- Form validation with various input scenarios
- Responsive layout behavior across screen sizes
- Button interactions and state changes
- Data loading and error states
- Accessibility compliance with semantic labels

Test Structure:
```dart
void main() {
  group('RestaurantOnboardingWidget', () {
    testWidgets('displays all 4 steps correctly', (tester) async {
      await tester.pumpWidget(
        GetMaterialApp(
          home: RestaurantOnboardingWidget(),
        ),
      );

      // Verify step indicators
      expect(find.text('Business Details'), findsOneWidget);
      expect(find.text('Restaurant Info'), findsOneWidget);
      expect(find.text('Staff Management'), findsOneWidget);
      expect(find.text('Review'), findsOneWidget);
    });

    testWidgets('validates required fields', (tester) async {
      await tester.pumpWidget(
        GetMaterialApp(
          home: RestaurantOnboardingWidget(),
        ),
      );

      // Test form validation
      await tester.tap(find.text('Continue'));
      await tester.pump();

      expect(find.text('Business name is required'), findsOneWidget);
    });
  });
}
```

Use golden tests for visual regression testing and mock providers for consistent test data.
```

### 14. Performance Optimization
```
Implement performance optimizations for restaurant dashboard with large datasets and real-time updates.

Optimization Strategies:
1. Lazy loading for data tables and lists
2. Image caching for restaurant photos and avatars
3. Efficient widget rebuilding with const constructors
4. Memory management for real-time streams
5. Background data synchronization

Performance Components:
- LazyListView for large data sets
- ImageCacheManager for photo handling
- StreamManager for real-time subscriptions
- MemoryOptimizer for widget disposal

Implementation:
```dart
class OptimizedTableGridView extends StatelessWidget {
  final List<TableData> tables;

  const OptimizedTableGridView({Key? key, required this.tables}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: _getCrossAxisCount(context),
        childAspectRatio: 1.0,
      ),
      itemCount: tables.length,
      itemBuilder: (context, index) {
        return const TableCard(
          key: ValueKey('table-card'),
        );
      },
    );
  }

  int _getCrossAxisCount(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    if (screenWidth >= 1200) return 6;
    if (screenWidth >= 800) return 4;
    if (screenWidth >= 600) return 3;
    return 2;
  }
}
```

Use Flutter DevTools for performance profiling and optimize rebuild cycles.
```

## Usage Instructions

### How to Use These Prompts

1. **Select the appropriate prompt** based on the component you want to build
2. **Copy the entire prompt** into your AI code generation tool
3. **Customize if needed** - adjust colors, spacing, or specific requirements
4. **Generate the code** - the AI will create Flutter code following Material Design 3
5. **Review and integrate** - test the generated code and integrate into your project

### Best Practices

- **Test generated code** thoroughly before production use
- **Adapt to your project structure** and naming conventions
- **Verify responsive behavior** across different screen sizes
- **Check accessibility compliance** with semantic labels
- **Validate API integration** with your actual backend endpoints

### Customization Tips

- **Colors**: Adjust primary/secondary colors in the theme prompts
- **Typography**: Modify font families and sizes in theme implementation
- **Spacing**: Tweak padding and margins in layout prompts
- **Animations**: Adjust duration and curves in animation prompts
- **Data Models**: Update data structures to match your API responses

These prompts are optimized for generating production-ready Flutter code that follows Material Design 3 guidelines and implements the comprehensive restaurant management system specified in the design documentation.