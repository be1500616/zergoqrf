# ZERGO QR - Story 2.2 Restaurant Dashboard Design Specification

**Comprehensive Restaurant Management Dashboard Interface**

---

## 📋 Executive Summary

This document defines the complete UI/UX design specification for the restaurant dashboard interface in the ZERGO QR platform. Building upon the established Material Design 3 + ZERGO brand system and responsive architecture, this specification delivers an enterprise-grade dashboard that provides real-time business insights, efficient operational management, and intuitive navigation for restaurant owners and staff.

## 🎯 Design Goals

- **Real-Time Business Intelligence**: Live data updates with actionable insights within 2 seconds
- **Operational Efficiency**: Complete frequent management tasks in 3 clicks or less
- **Mobile-First Operations**: Full functionality available on mobile for floor operations
- **Multi-Location Management**: Seamless switching and comparative analytics for multiple restaurants
- **Proactive Issue Detection**: Early warning system for operational problems and opportunities
- **Staff Empowerment**: Role-based access with clear responsibilities and training support

---

## 🎨 Enhanced Dashboard Visual Design System

### Dashboard-Specific Color Extensions

```yaml
# Dashboard Status Colors
dashboard_status:
  online:
    background: "#E8F5E8" # success.50
    border: "#2E7D32" # success.600
    text: "#1B5E20" # success.800
    pulse: "success.200"

  offline:
    background: "#FFF3E0" # warning.50
    border: "#F57C00" # warning.600
    text: "#E65100" # warning.800

  setup_needed:
    background: "#F3E5F5" # secondary.50
    border: "#9C27B0" # secondary.600
    text: "#6A1B9A" # secondary.800

  maintenance:
    background: "#E3F2FD" # info.50
    border: "#1976D2" # info.600
    text: "#0D47A1" # info.800

# Performance Indicator Colors
performance_indicators:
  excellent: "#4CAF50" # success
  good: "#8BC34A" # success.light
  average: "#FFC107" # warning
  poor: "#FF5722" # error
  critical: "#D32F2F" # error.dark

# Order Status Colors
order_status:
  new:
    background: "#E3F2FD"
    border: "#1976D2"
    text: "#1565C0"

  preparing:
    background: "#FFF8E1"
    border: "#F57C00"
    text: "#F57C00"

  ready:
    background: "#E8F5E8"
    border: "#4CAF50"
    text: "#2E7D32"

  completed:
    background: "#F3E5F5"
    border: "#9C27B0"
    text: "#7B1FA2"

  cancelled:
    background: "#FFEBEE"
    border: "#F44336"
    text: "#D32F2F"

# Table Status Colors
table_status:
  available:
    background: "#E8F5E8"
    border: "#2E7D32"
    icon: "table_restaurant"

  occupied:
    background: "#FFF8E1"
    border: "#F57C00"
    icon: "table_bar"

  reserved:
    background: "#E3F2FD"
    border: "#1976D2"
    icon: "table_restaurant_reserved"

  cleaning:
    background: "#F3E5F5"
    border: "#9C27B0"
    icon: "cleaning_services"

# Alert and Notification Colors
notifications:
  urgent:
    background: "#FFEBEE"
    border: "#D32F2F"
    icon: "warning"
    animation: "pulse"

  important:
    background: "#FFF3E0"
    border: "#F57C00"
    icon: "priority_high"
    animation: "fade_in"

  informational:
    background: "#E3F2FD"
    border: "#1976D2"
    icon: "info"
    animation: "slide_in"

  success:
    background: "#E8F5E8"
    border: "#2E7D32"
    icon: "check_circle"
    animation: "bounce_in"
```

### Dashboard Typography Scale

```yaml
# Dashboard-Specific Typography
dashboard_typography:
  welcome_message:
    size: 28px
    weight: 600
    line_height: 1.2
    color: "neutral.900"

  metric_value:
    size: 32px
    weight: 700
    line_height: 1.0
    color: "neutral.900"

  metric_label:
    size: 14px
    weight: 500
    line_height: 1.4
    color: "neutral.600"

  metric_change:
    size: 12px
    weight: 600
    line_height: 1.3
    color: "neutral.700"

  card_title:
    size: 18px
    weight: 600
    line_height: 1.3
    color: "neutral.900"

  card_subtitle:
    size: 14px
    weight: 400
    line_height: 1.4
    color: "neutral.600"

  section_header:
    size: 20px
    weight: 600
    line_height: 1.3
    color: "neutral.900"

  navigation_label:
    size: 14px
    weight: 500
    line_height: 1.3
    color: "neutral.700"

  status_badge:
    size: 12px
    weight: 600
    line_height: 1.2
    text_transform: "uppercase"
```

---

## 📱 Comprehensive Dashboard Layout Design

### Main Dashboard Structure

**Layout Strategy:** Adaptive sidebar + main content area with responsive breakpoints

```yaml
dashboard_layout:
  header:
    height: "64px"
    background: "white"
    elevation: 1
    elements:
      - logo: { position: "left", size: "medium" }
      - breadcrumbs: { position: "center" }
      - notifications: { position: "right", badge: true }
      - user_menu: { position: "right", avatar: true }
      - restaurant_switcher: { position: "right", dropdown: true }

  sidebar:
    width: "280px_desktop"
    background: "neutral.900"
    navigation_type: "collapsible"
    main_sections:
      - dashboard: { icon: "dashboard", label: "Dashboard" }
      - orders: { icon: "receipt_long", label: "Orders" }
      - menu: { icon: "restaurant_menu", label: "Menu" }
      - qr_codes: { icon: "qr_code", label: "QR Codes" }
      - staff: { icon: "people", label: "Staff" }
      - tables: { icon: "table_restaurant", label: "Tables" }
      - analytics: { icon: "analytics", label: "Analytics" }
      - settings: { icon: "settings", label: "Settings" }

  main_content:
    padding: "24px"
    max_width: "1400px"
    background: "neutral.50"

    sections:
      - welcome_banner: { height: "120px", animated: true }
      - key_metrics_row: { height: "180px" }
      - quick_actions: { height: "140px" }
      - recent_activity: { height: "300px" }
      - table_status: { height: "200px" }
      - upcoming_reminders: { height: "160px" }
```

### Welcome Banner Component

```yaml
welcome_banner:
  layout: "responsive_card_with_gradient"
  background: "gradient(primary.50 -> success.50)"
  border_radius: "16px"
  padding: "24px"

  content:
    greeting:
      type: "dynamic_based_on_time"
      formats:
        morning: "Good morning, {name}! ☀️"
        afternoon: "Good afternoon, {name}! 🌤"
        evening: "Good evening, {name}! 🌙"
      style: "headline_large"

    restaurant_info:
      name: "{restaurant_name}"
      status: "online | offline | setup_needed"
      status_indicator: "colored_dot"

    today_summary:
      type: "metrics_highlights"
      items:
        - label: "Today's Orders"
          value: "{order_count}"
          change: "{order_change_percent}"
        - label: "Revenue"
          value: "₹{revenue_amount}"
          change: "{revenue_change_percent}"
        - label: "Customers"
          value: "{customer_count}"
          change: "{customer_change_percent}"

    quick_actions:
      type: "floating_action_buttons"
      primary: "View Today's Performance"
      secondary: "Generate QR Code"
```

### Key Metrics Row

```yaml
metrics_row:
  layout: "responsive_grid_4_cards"
  card_height: "160px"
  animation: "staggered_appear"

  cards:
    - today_performance:
        title: "Today's Performance"
        primary_metric:
          label: "Revenue"
          value: "₹2,340"
          change: "+8%"
          trend: "up"
        secondary_metrics:
          - { label: "Orders", value: "23", change: "+15%" }
          - { label: "Customers", value: "45", change: "+12%" }
        mini_chart: "revenue_sparkline"
        quick_action: "View Details"

    - table_status:
        title: "Table Status"
        visual: "interactive_table_map"
        summary: "3 occupied, 7 available"
        capacity_utilization: "30%"
        table_breakdown:
          - total: 10
          - occupied: 3
          - available: 7
          - reserved: 0
        quick_action: "View Floor Plan"

    - recent_orders:
        title: "Recent Orders"
        type: "timeline_list"
        max_items: 5
        status_distribution:
          new: 2
          preparing: 3
          ready: 1
          completed: 2
        quick_action: "View All Orders"

    - qr_performance:
        title: "QR Code Performance"
        metrics:
          - { label: "Today", value: "67", change: "+12%" }
          - { label: "This Week", value: "342", change: "+18%" }
        mini_chart: "scans_bar_chart"
        quick_action: "QR Analytics"
```

### Quick Actions Section

```yaml
quick_actions:
  layout: "responsive_grid_2x2"
  card_height: "120px"
  border_radius: "12px"
  hover_elevation: 2

  actions:
    - view_menu:
      title: "View Menu"
      icon: "restaurant_menu"
      color: "primary"
      description: "Check menu items and pricing"
      hotkey: "Ctrl+M"

    - generate_qr:
      title: "Generate QR"
      icon: "qr_code_2"
      color: "success"
      description: "Create new QR codes"
      hotkey: "Ctrl+Q"

    - add_staff:
      title: "Add Staff"
      icon: "person_add"
      color: "secondary"
      description: "Invite team members"
      hotkey: "Ctrl+S"

    - view_analytics:
      title: "Analytics"
      icon: "insights"
      color: "info"
      description: "Business insights"
      hotkey: "Ctrl+A"

    - manage_tables:
      title: "Tables"
      icon: "table_restaurant"
      color: "warning"
      description: "Table management"
      hotkey: "Ctrl+T"

    - process_orders:
      title: "Orders"
      icon: "receipt_long"
      color: "error"
      description: "Order queue"
      hotkey: "Ctrl+O"
```

### Real-Time Updates System

```yaml
real_time_updates:
  websockets:
    connection: "persistent"
    channels: ["orders", "tables", "metrics", "notifications"]
    heartbeat: "30_seconds"
    reconnection: "automatic"

  update_types:
    - new_order:
      type: "notification_banner"
      priority: "high"
      auto_action: "sound + visual"
      timeout: "5_seconds"

    - table_status_change:
      type: "status_update"
      component: "table_map"
      animation: "smooth_transition"

    - metric_update:
      type: "number_animation"
      components: ["metric_cards", "charts"]
      duration: "500ms"

    - staff_activity:
      type: "activity_feed"
      component: "recent_activity"
      real_time: true
```

---

## 📱 Responsive Dashboard Breakpoints

### Mobile Dashboard (320px - 767px)

```yaml
mobile_dashboard:
  layout: "bottom_navigation + scrollable_content"
  header: "compact_with_menu_toggle"
  sidebar: "drawer_overlay"

  adaptations:
    - metrics: "stacked_cards"
    - tables: "simplified_list"
    - actions: "floating_buttons"
    - charts: "touch_optimized"

  navigation:
    type: "bottom_tab_bar"
    items: [
      { icon: "dashboard", label: "Dashboard" },
      { icon: "receipt_long", label: "Orders" },
      { icon: "restaurant_menu", label: "Menu" },
      { icon: "settings", label: "Settings" }
    ]

  interactions:
    - touch_targets: "44px_minimum"
    - gestures: "swipe_navigation"
    - keyboard: "minimized"
```

### Tablet Dashboard (768px - 1023px)

```yaml
tablet_dashboard:
  layout: "persistent_sidebar + scrollable_content"
  header: "full_width"
  sidebar: "collapsible_drawer"

  adaptations:
    - metrics: "2x2_grid"
    - tables: "enhanced_list"
    - actions: "inline_buttons"
    - charts: "responsive_sizing"

  navigation:
    type: "side_navigation"
    width: "240px"
    collapsible: true

  interactions:
    - touch_targets: "48px"
    - gestures: "supported"
    - keyboard: "full_support"
```

### Desktop Dashboard (1024px+)

```yaml
desktop_dashboard:
  layout: "persistent_sidebar + fluid_content"
  header: "full_width"
  sidebar: "fixed_280px"

  adaptations:
    - metrics: "4_column_grid"
    - tables: "interactive_floor_plan"
    - actions: "toolbar_buttons"
    - charts: "full_sized"

  navigation:
    type: "side_navigation"
    width: "280px"
    expandable: true

  interactions:
    - touch_targets: "standard"
    - gestures: "supported"
    - keyboard: "full_support_with_shortcuts"
    - mouse: "advanced_hover_states"
```

---

## 🔄 Advanced Dashboard Interactions

### Real-Time Order Management

```yaml
order_management:
  order_queue:
    layout: "kanban_board"
    columns: ["New", "Preparing", "Ready", "Completed"]
    drag_drop: "enabled"
    auto_refresh: "5_seconds"

  order_card:
    content:
      - order_number: "visible"
      - customer_info: "name + table"
      - items_summary: "item count + total"
      - time_elapsed: "relative_timestamp"
      - priority: "color_coded"

    actions:
      - accept_order: "primary_button"
      - view_details: "secondary_button"
      - mark_ready: "tertiary_button"
      - complete_order: "success_button"

    status_transitions:
      new -> preparing: "automatic"
      preparing -> ready: "manual"
      ready -> completed: "manual"
      any -> cancelled: "manual"

  notifications:
    new_order:
      type: "sound + visual"
      priority: "high"
      auto_dismiss: "10_seconds"

    order_ready:
      type: "visual"
      priority: "medium"
      auto_dismiss: "30_seconds"

    order_delayed:
      type: "alert"
      priority: "high"
      persistent: true
```

### Table Management Interface

```yaml
table_management:
  floor_plan:
    layout: "interactive_map"
    zoom_levels: ["overview", "normal", "detailed"]
    drag_drop: "enabled"

  table_widget:
    states:
      available:
        color: "success"
        icon: "table_restaurant"
        actions: ["assign", "qr_code"]

      occupied:
        color: "warning"
        icon: "table_bar"
        actions: ["view_order", "clear"]

      reserved:
        color: "info"
        icon: "table_restaurant_reserved"
        actions: ["check_in", "cancel"]

      cleaning:
        color: "secondary"
        icon: "cleaning_services"
        actions: ["mark_ready"]

    interactions:
      - tap: "view_details"
      - long_press: "action_menu"
      - drag: "reposition"
      - swipe: "quick_action"

  reservation_management:
    timeline: "upcoming_reservations"
    conflicts: "automatic_detection"
    notifications: "advance_alerts"
```

### Staff Management Dashboard

```yaml
staff_management:
  team_overview:
    layout: "grid_with_roles"
    roles: ["manager", "chefs", "service_staff", "cleaning"]

  staff_card:
    information:
      - photo: "profile_picture"
      - name: "full_name"
      - role: "position"
      - status: "online/offline/break"
      - performance: "rating_metrics"

    actions:
      - contact: "phone/messaging"
      - schedule: "view/modify"
      - permissions: "manage"
      - analytics: "view_performance"

  scheduling:
    layout: "weekly_calendar"
    shift_types: ["morning", "afternoon", "evening"]
    coverage: "visual_gaps"
    conflicts: "highlight_detection"
    notifications: "reminders"
```

---

## ♿ Accessibility & Performance

### Dashboard Accessibility

```yaml
accessibility_features:
  keyboard_navigation:
    tab_order: "logical"
    skip_links: "to_main_sections"
    focus_management: "predictable"
    shortcuts: "customizable"

  screen_reader:
    semantic_structure: "proper_html5"
    aria_labels: "all_interactive_elements"
    live_regions: "dynamic_updates"
    announcements: "important_changes"

  visual_accessibility:
    color_contrast: "enhanced_for_data"
    high_contrast_mode: "supported"
    font_scaling: "up_to_200%"
    motion_reduction: "user_controlled"

  cognitive_accessibility:
    clear_hierarchy: "visual_importance"
    consistent_patterns: "familiar_ui"
    error_prevention: "validation_feedback"
    help_system: "contextual_assistance"
```

### Performance Optimization

```yaml
performance_optimizations:
  loading_strategy:
    - skeleton_screens: "fast_perception"
    - progressive_loading: "content_priority"
    - lazy_loading: "below_fold"
    - virtual_scrolling: "large_datasets"

  data_optimization:
    - caching: "intelligent"
    - compression: "enabled"
    - delta_updates: "websocket"
    - background_sync: "automatic"

  rendering_optimization:
    - widget_reuse: "efficient"
    - animation_performance: "60fps_target"
    - memory_management: "garbage_collection"
    - battery_optimization: "power_efficient"
```

---

## 🎯 Success Metrics

### Dashboard Performance Metrics

```yaml
success_metrics:
  usability:
    task_completion_time: "target: <3_clicks"
    error_prevention: "target: 95%"
    learnability: "target: <5_minutes"
    satisfaction: "target: 4.5/5"

  performance:
    load_time: "target: <2_seconds"
    refresh_time: "target: <500ms"
    animation_fps: "target: 60fps"
    memory_usage: "target: <200MB"

  business_impact:
    daily_active_users: "target: >90%"
    time_to_first_action: "target: <30_seconds"
    issue_detection_time: "target: <5_minutes"
    customer_satisfaction: "target: >4.0/5"
```

---

## 🚀 Implementation Guidelines

### Flutter Dashboard Components

```dart
// Enhanced Dashboard Metric Card
class DashboardMetricCard extends StatelessWidget {
  final String title;
  final String? subtitle;
  final List<MetricData> metrics;
  final Widget? chart;
  final List<QuickAction>? actions;
  final bool isLoading;

  const DashboardMetricCard({
    super.key,
    required this.title,
    this.subtitle,
    required this.metrics,
    this.chart,
    this.actions,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: Colors.grey.shade300,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      if (subtitle != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          subtitle,
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: Colors.grey.shade600,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
                if (actions != null)
                  PopupMenuButton<QuickAction>(
                    icon: const Icon(Icons.more_vert),
                    itemBuilder: (context) => actions!
                        .map((action) => PopupMenuItem(
                          value: action,
                          child: Text(action.label),
                        ))
                        .toList(),
                    onSelected: (action) => action.onTap(),
                  ),
              ],
            ),

            const SizedBox(height: 16),

            // Content
            if (isLoading)
              _buildLoadingSkeleton()
            else ...[
              // Metrics
              _buildMetricsRow(context),

              // Chart (if provided)
              if (chart != null) ...[
                const SizedBox(height: 16),
                SizedBox(
                  height: 120,
                  child: chart!,
                ),
              ],
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildMetricsRow(BuildContext context) {
    final theme = Theme.of(context);

    return Row(
      children: metrics.map((metric) {
        return Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                metric.label,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: Colors.grey.shade600,
                ),
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  Text(
                    metric.value,
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  if (metric.change != null) ...[
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: metric.isPositiveChange
                            ? Colors.green.shade100
                            : Colors.red.shade100,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        metric.change!,
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: metric.isPositiveChange
                            ? Colors.green.shade700
                            : Colors.red.shade700,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildLoadingSkeleton() {
    return Column(
      children: [
        Row(
          children: List.generate(3, (index) => Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  height: 12,
                  width: 60,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(6),
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  height: 24,
                  width: 80,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ],
            ),
          )),
        ),
      ],
    );
  }
}

class MetricData {
  final String label;
  final String value;
  final String? change;
  final bool isPositiveChange;

  const MetricData({
    required this.label,
    required this.value,
    this.change,
    this.isPositiveChange = true,
  });
}

class QuickAction {
  final String label;
  final VoidCallback onTap;

  const QuickAction({
    required this.label,
    required this.onTap,
  });
}
```

This comprehensive dashboard design specification provides everything needed to implement a world-class restaurant management interface that delivers real-time insights, operational efficiency, and excellent user experience across all device types.

The specification includes detailed layouts, component designs, responsive strategies, and implementation guidelines that will help developers create a dashboard that restaurant owners and staff will love to use daily.