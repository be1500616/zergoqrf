# ZERGO QR - Story 1.2 UI/UX Design System

**Table Management & Floor Plan Interface**

---

## 📋 Executive Summary

This document extends the ZERGO QR design system for Story 1.2 (Table Management System), creating an enterprise-grade SaaS interface for restaurant floor plan management. Following the established Material Design 3 + ZERGO brand system from Story 1.1, this specification provides comprehensive UI/UX guidelines for interactive table layout editors, real-time status dashboards, and mobile-optimized staff interfaces that rival the quality of leading tech companies like Stripe, Linear, and Notion.

## 🎯 Design Goals

- **Operational Efficiency**: Streamline table management with intuitive drag-and-drop interfaces
- **Real-time Visibility**: Provide instant table status updates across all devices
- **Mobile Excellence**: Optimize for restaurant staff using mobile devices on the floor
- **Scalable Architecture**: Support restaurants from single-floor cafes to multi-level establishments
- **Data-Driven Insights**: Enable performance tracking and analytics integration
- **Accessibility First**: Ensure WCAG 2.1 AA compliance for all user interactions

---

## 🎨 Visual Design System (Inherited + Extended)

### Extended Color Palette for Table Management

```yaml
# Table Status Colors (extending ZERGO palette)
table_status:
  available:
    background: "#E8F5E8" # success.50
    border: "#2E7D32" # success.600
    icon: "#1B5E20" # success.800

  occupied:
    background: "#FFEBEE" # error.50
    border: "#D32F2F" # error.600
    icon: "#B71C1C" # error.800

  reserved:
    background: "#FFF8E1" # warning.50
    border: "#F57C00" # warning.600
    icon: "#E65100" # warning.800

  cleaning:
    background: "#F3E5F5" # purple.50
    border: "#9C27B0" # purple.600
    icon: "#6A1B9A" # purple.800

# Floor Plan Canvas Colors
canvas:
  background: "#FAFAFA" # neutral.50
  grid_lines: "#EEEEEE" # neutral.200
  grid_dots: "#E0E0E0" # neutral.300
  selection_box: "#1976D2" # primary.600
  drop_zone: "#E3F2FD" # primary.50

# Interactive Elements
interactions:
  drag_handle: "#757575" # neutral.600
  resize_handle: "#1976D2" # primary.600
  hover_overlay: "rgba(25, 118, 210, 0.08)"
  active_overlay: "rgba(25, 118, 210, 0.12)"
```

### Table Shape & Size Standards

```yaml
table_shapes:
  round:
    default_radius: 24px
    min_radius: 16px
    max_radius: 48px

  square:
    default_size: 48px
    min_size: 32px
    max_size: 80px

  rectangular:
    default_width: 64px
    default_height: 32px
    min_width: 48px
    max_width: 120px
    min_height: 24px
    max_height: 48px

table_capacity_indicators:
  small: "1-2 people" # 16px icon
  medium: "3-4 people" # 20px icon
  large: "5-8 people" # 24px icon
  xlarge: "8+ people" # 28px icon
```

---

## 📱 Responsive Layout Specifications

### Mobile Layout (320px - 767px)

```yaml
mobile_layout:
  navigation:
    type: "bottom_tab_bar"
    height: 64px
    tabs: ["Floor Plan", "Status", "Analytics"]

  floor_plan_view:
    canvas_mode: "full_screen_modal"
    zoom_controls: "floating_action_buttons"
    table_info: "bottom_sheet_on_tap"
    edit_mode: "toggle_button_in_header"

  table_list_view:
    layout: "card_list"
    card_height: 80px
    quick_actions: ["Reserve", "Clean", "Available"]
    search_bar: "sticky_top"

  status_dashboard:
    layout: "single_column_cards"
    metrics: "horizontal_scroll_cards"
    table_grid: "responsive_grid_2_columns"
```

### Tablet Layout (768px - 1023px)

```yaml
tablet_layout:
  navigation:
    type: "persistent_sidebar"
    width: 240px
    collapsed_width: 64px

  main_content:
    layout: "two_panel"
    left_panel: "floor_plan_canvas"
    right_panel: "table_details_and_controls"
    panel_ratio: "70:30"

  floor_plan_canvas:
    zoom_controls: "corner_overlay"
    table_toolbar: "floating_toolbar"
    property_inspector: "side_panel_overlay"

  multi_floor:
    tab_style: "horizontal_tabs"
    position: "above_canvas"
```

### Desktop Layout (1024px+)

```yaml
desktop_layout:
  navigation:
    type: "persistent_sidebar_with_secondary"
    primary_width: 240px
    secondary_width: 320px

  main_workspace:
    layout: "three_panel"
    left_panel: "navigation_and_tools"
    center_panel: "floor_plan_canvas"
    right_panel: "properties_and_status"
    panel_ratios: "20:60:20"

  advanced_features:
    multi_floor_tabs: "vertical_tab_stack"
    bulk_operations: "context_toolbar"
    analytics_overlay: "expandable_bottom_panel"
```

---

## 🏗️ Core Component Specifications

### 1. Interactive Floor Plan Canvas

```yaml
FloorPlanCanvas:
  component_type: "custom_painter_widget"

  canvas_properties:
    background_color: "canvas.background"
    grid_enabled: true
    grid_size: 16px # 2x base spacing unit
    snap_to_grid: true
    zoom_range: "25% to 400%"
    pan_enabled: true

  interaction_modes:
    view_mode:
      - pan_and_zoom: true
      - table_selection: "single_tap"
      - context_menu: "long_press"

    edit_mode:
      - drag_drop_enabled: true
      - resize_handles: "corner_and_edge"
      - multi_selection: "ctrl_click"
      - bulk_operations: true

  table_rendering:
    default_style:
      border_width: 2px
      border_radius: 8px # For square/rectangular tables
      shadow_elevation: 1

    status_indicators:
      position: "top_right_corner"
      size: 12px
      animation: "pulse_for_updates"

    capacity_labels:
      position: "center"
      font_size: 12px
      font_weight: "600"
      color: "neutral.700"
```

### 2. Table Status Indicator Component

```yaml
TableStatusIndicator:
  component_type: "stateful_widget"

  visual_states:
    available:
      color: "table_status.available.background"
      icon: "Icons.check_circle"
      animation: "none"

    occupied:
      color: "table_status.occupied.background"
      icon: "Icons.people"
      animation: "subtle_pulse"
      duration_display: true

    reserved:
      color: "table_status.reserved.background"
      icon: "Icons.schedule"
      animation: "breathing"
      countdown_timer: true

    cleaning:
      color: "table_status.cleaning.background"
      icon: "Icons.cleaning_services"
      animation: "rotating_slow"

  interaction_behavior:
    tap_action: "show_quick_actions_menu"
    long_press: "show_detailed_status"
    swipe_actions:
      left: "change_status"
      right: "view_history"
```

---

## 📊 Success Metrics & KPIs

### User Experience Metrics

```yaml
ux_metrics:
  task_completion_rate: "target: >95%"
  average_task_time: "target: <30_seconds"
  error_rate: "target: <2%"
  user_satisfaction_score: "target: >4.5/5"

performance_metrics:
  canvas_render_time: "target: <100ms"
  real_time_update_latency: "target: <500ms"
  drag_drop_responsiveness: "target: <16ms"
  mobile_scroll_performance: "target: 60fps"

business_metrics:
  table_turnover_rate: "improve by 15%"
  order_processing_time: "reduce by 20%"
  staff_efficiency: "improve by 25%"
  customer_satisfaction: "improve by 10%"
```

This comprehensive design specification provides everything needed to implement a world-class table management system that maintains consistency with the established ZERGO QR design system while delivering enterprise-grade functionality for restaurant table management, floor plan visualization, and real-time status tracking.

---

## 🎨 Extended Visual Design System

### Menu-Specific Color Extensions

```yaml
# Menu Item Status Colors (extending ZERGO palette)
menu_status:
  available:
    background: "#E8F5E8" # success.50
    border: "#2E7D32" # success.600
    text: "#1B5E20" # success.800

  unavailable:
    background: "#FFEBEE" # error.50
    border: "#D32F2F" # error.600
    text: "#B71C1C" # error.800

  seasonal:
    background: "#FFF8E1" # warning.50
    border: "#F57C00" # warning.600
    text: "#E65100" # warning.800

  featured:
    background: "#E8EAF6" # indigo.50
    border: "#3F51B5" # indigo.600
    text: "#283593" # indigo.800

# Dietary Indicator Colors
dietary_indicators:
  vegetarian:
    background: "#E8F5E8"
    border: "#4CAF50"
    icon_color: "#2E7D32"

  vegan:
    background: "#F1F8E9"
    border: "#8BC34A"
    icon_color: "#558B2F"

  gluten_free:
    background: "#FFF3E0"
    border: "#FF9800"
    icon_color: "#F57C00"

  spicy:
    background: "#FFEBEE"
    border: "#F44336"
    icon_color: "#D32F2F"

# Menu Editor Interface Colors
editor_interface:
  canvas_background: "#FAFAFA" # neutral.50
  category_separator: "#E0E0E0" # neutral.300
  drag_indicator: "#BDBDBD" # neutral.400
  drop_zone_active: "#E3F2FD" # primary.50
  drop_zone_border: "#1976D2" # primary.600
  preview_overlay: "rgba(25, 118, 210, 0.08)"
```

### Typography Enhancements for Menu Content

```yaml
# Menu-Specific Typography Scale
menu_typography:
  category_title:
    size: 20px
    weight: 600
    line_height: 1.2
    letter_spacing: 0.15px

  subcategory_title:
    size: 16px
    weight: 500
    line_height: 1.3
    letter_spacing: 0.1px

  item_name:
    size: 16px
    weight: 500
    line_height: 1.4
    letter_spacing: 0.1px

  item_description:
    size: 14px
    weight: 400
    line_height: 1.5
    letter_spacing: 0.25px
    color: "neutral.600"

  price_primary:
    size: 16px
    weight: 600
    line_height: 1.2
    color: "primary.700"

  price_secondary:
    size: 14px
    weight: 400
    line_height: 1.2
    color: "neutral.600"
    text_decoration: "line-through"

  addon_label:
    size: 12px
    weight: 500
    line_height: 1.3
    letter_spacing: 0.4px
    color: "neutral.700"
```

---

## 📱 Comprehensive Responsive Layout Strategy

### Mobile-First Menu Editor (320px - 767px)

```yaml
mobile_layout:
  navigation:
    type: "bottom_tab_bar_with_fab"
    height: 64px
    tabs: ["Structure", "Items", "Preview", "Publish"]
    fab_action: "add_item_or_category"

  menu_structure_editor:
    layout: "accordion_tree_view"
    category_cards: "full_width_with_expand"
    drag_handles: "large_touch_targets_44px"
    reordering: "long_press_then_drag"

  item_editor:
    layout: "full_screen_modal"
    sections: "collapsible_accordion"
    image_upload: "camera_first_gallery_second"
    form_fields: "single_column_stack"

  menu_preview:
    layout: "customer_perspective_mobile"
    navigation: "swipe_between_categories"
    zoom_controls: "pinch_to_zoom"

  publishing_workflow:
    layout: "stepper_bottom_sheet"
    version_comparison: "swipe_between_versions"
    publish_confirmation: "full_screen_modal"
```

### Tablet Split-View Interface (768px - 1023px)

```yaml
tablet_layout:
  main_interface:
    layout: "three_panel_adaptive"
    left_panel: "menu_structure_tree" # 280px
    center_panel: "item_editor_or_preview" # flexible
    right_panel: "properties_inspector" # 320px

  menu_structure_panel:
    header: "category_management_toolbar"
    content: "hierarchical_tree_with_drag_drop"
    footer: "add_category_quick_actions"

  item_editor_panel:
    header: "item_toolbar_with_save_status"
    content: "tabbed_form_sections"
    tabs: ["Details", "Pricing", "Add-ons", "Availability"]

  preview_panel:
    toggle_mode: "split_screen_or_full_preview"
    device_simulation: "mobile_frame_overlay"
    real_time_sync: "live_updates_as_typing"

  drag_drop_behavior:
    cross_panel: "drag_from_tree_to_editor"
    visual_feedback: "insertion_lines_and_highlights"
    snap_zones: "magnetic_drop_areas"
```

### Desktop Power-User Interface (1024px+)

```yaml
desktop_layout:
  workspace_layout:
    type: "flexible_multi_panel_dock"
    panels:
      - navigation: "collapsible_sidebar_240px"
      - structure: "menu_tree_panel_320px"
      - editor: "main_content_flexible"
      - preview: "live_preview_400px"
      - inspector: "properties_panel_280px"

  advanced_features:
    bulk_operations: "multi_select_with_actions_toolbar"
    batch_editing: "spreadsheet_style_inline_editing"
    keyboard_shortcuts: "full_productivity_shortcuts"
    multi_window: "detached_panels_support"

  menu_structure_visualization:
    type: "interactive_hierarchy_diagram"
    zoom_levels: "overview_to_detail"
    visual_connections: "category_item_relationships"

  professional_editing_tools:
    rich_text_editor: "WYSIWYG_with_markdown_support"
    image_management: "drag_drop_with_crop_resize"
    bulk_import: "CSV_Excel_import_wizard"
    template_system: "save_and_reuse_menu_templates"
```

---

## 🏗️ Core Component Specifications

### 1. Hierarchical Menu Structure Editor

```yaml
MenuStructureEditor:
  component_type: "interactive_tree_view"

  tree_node_types:
    category:
      visual_style: "folder_icon_with_expand_collapse"
      drag_handle: "visible_on_hover_or_mobile"
      actions: ["edit", "add_subcategory", "add_item", "delete"]

    subcategory:
      visual_style: "nested_folder_with_indent"
      max_nesting_depth: 3
      inheritance: "availability_schedules_from_parent"

    menu_item:
      visual_style: "document_icon_with_status_indicator"
      quick_preview: "hover_tooltip_with_image"
      batch_operations: "multi_select_checkbox"

  interaction_patterns:
    expand_collapse:
      animation: "smooth_height_transition_300ms"
      state_persistence: "remember_expanded_state"
      keyboard: "space_or_enter_to_toggle"

    drag_and_drop:
      visual_feedback: "blue_insertion_lines"
      valid_drop_zones: "highlight_compatible_targets"
      invalid_drops: "red_outline_with_shake"
      auto_scroll: "when_dragging_near_edges"

    contextual_actions:
      right_click_menu: "context_appropriate_options"
      touch_long_press: "action_sheet_on_mobile"
      keyboard_shortcuts: "delete_copy_paste_support"
```

### 2. Advanced Menu Item Editor

```yaml
MenuItemEditor:
  component_type: "tabbed_form_interface"

  basic_details_tab:
    layout: "two_column_responsive"
    sections:
      - item_identity:
          fields:
            - name:
                type: "text_input_with_counter"
                max_length: 60
                required: true
                validation: "real_time_duplicate_check"

            - description:
                type: "rich_text_editor"
                max_length: 200
                formatting: ["bold", "italic", "line_breaks"]
                preview: "live_character_formatting"

            - category_assignment:
                type: "hierarchical_dropdown"
                create_new: "inline_category_creation"
                multiple: false

      - visual_presentation:
          fields:
            - primary_image:
                type: "image_upload_with_crop"
                aspect_ratio: "16:9"
                max_size: "5MB"
                formats: ["JPG", "PNG", "WebP"]
                ai_optimization: "auto_compress_and_optimize"

            - gallery_images:
                type: "multiple_image_upload"
                max_count: 5
                drag_reorder: true

  pricing_variants_tab:
    layout: "dynamic_form_builder"
    sections:
      - base_pricing:
          fields:
            - default_price:
                type: "currency_input"
                currency: "INR"
                validation: "minimum_value_required"

            - discount_price:
                type: "currency_input"
                conditional: "show_if_promotion_enabled"

      - size_variants:
          type: "repeatable_section"
          fields:
            - size_name: "text_input" # Small, Medium, Large
            - price_adjustment: "currency_delta" # +₹50, -₹20
            - description: "short_text" # "Serves 1-2 people"

      - pricing_tiers:
          type: "multi_tier_pricing"
          tiers: ["Dine-in", "Takeaway", "Delivery"]
          inheritance: "base_price_with_adjustments"

  customization_addons_tab:
    layout: "grouped_sections"
    sections:
      - addon_categories:
          type: "nested_addon_groups"
          examples: ["Toppings", "Sides", "Drinks", "Spice Level"]
          fields:
            - category_name: "text_input"
            - selection_type: "single_or_multiple"
            - required: "boolean_toggle"
            - max_selections: "number_input"

      - individual_addons:
          type: "addon_item_builder"
          fields:
            - addon_name: "text_input"
            - price_adjustment: "currency_input"
            - availability: "conditional_logic"
            - dietary_restrictions: "checkbox_group"

  availability_scheduling_tab:
    layout: "calendar_based_interface"
    sections:
      - regular_availability:
          type: "weekly_schedule_editor"
          granularity: "hourly_blocks"
          templates: ["All Day", "Lunch Only", "Dinner Only"]

      - special_schedules:
          type: "date_range_editor"
          use_cases: ["Seasonal Items", "Limited Time", "Holiday Specials"]

      - inventory_tracking:
          fields:
            - daily_limit: "number_input_with_warning_threshold"
            - sold_out_behavior: "hide_or_show_unavailable"

  dietary_allergen_tab:
    layout: "icon_based_selection"
    sections:
      - dietary_indicators:
          type: "visual_checkbox_grid"
          options:
            - { id: "veg", label: "Vegetarian", icon: "🥗", color: "success" }
            - { id: "vegan", label: "Vegan", icon: "🌱", color: "success" }
            - { id: "gf", label: "Gluten Free", icon: "🌾", color: "warning" }
            - { id: "keto", label: "Keto", icon: "🥑", color: "info" }
            - { id: "spicy", label: "Spicy", icon: "🌶️", color: "error" }

      - allergen_information:
          type: "searchable_multi_select"
          categories: ["Nuts", "Dairy", "Eggs", "Soy", "Shellfish"]
          custom_allergens: "add_custom_allergen_option"

      - nutritional_info:
          type: "optional_detailed_section"
          fields: ["calories", "protein", "carbs", "fat", "fiber"]
          units: "metric_with_imperial_conversion"
```

### 3. Real-Time Menu Preview System

```yaml
MenuPreviewSystem:
  component_type: "live_preview_container"

  preview_modes:
    customer_mobile_view:
      device_frame: "iPhone_or_Android_chrome"
      viewport_size: "375x667"
      interaction: "scroll_and_tap_simulation"

    customer_tablet_view:
      device_frame: "iPad_safari"
      viewport_size: "768x1024"
      layout: "tablet_optimized_grid"

    qr_code_experience:
      simulation: "full_customer_journey"
      steps: ["QR_scan", "menu_load", "browsing", "ordering"]

  real_time_sync:
    update_trigger: "debounced_500ms"
    sync_indicators: "subtle_flash_on_change"
    error_handling: "graceful_fallback_to_cached"

  preview_interactions:
    category_navigation: "smooth_scroll_to_section"
    item_details: "modal_or_expandable_card"
    add_to_cart: "animated_cart_icon_feedback"

  performance_optimization:
    lazy_loading: "images_load_on_scroll"
    virtual_scrolling: "large_menu_performance"
    caching: "intelligent_preview_cache"
```

### 4. Professional Publishing Workflow

```yaml
PublishingWorkflowSystem:
  component_type: "multi_step_wizard"

  draft_management:
    auto_save: "every_30_seconds"
    version_naming: "auto_timestamp_with_custom_labels"
    change_tracking: "granular_field_level_changes"

  pre_publish_validation:
    checks:
      - missing_required_fields: "highlight_incomplete_items"
      - image_optimization: "compress_oversized_images"
      - pricing_consistency: "validate_all_variants"
      - accessibility_audit: "check_alt_text_and_contrast"

  version_comparison:
    layout: "side_by_side_diff_view"
    change_indicators: "green_additions_red_removals"
    summary_report: "count_of_changes_by_type"

  publishing_options:
    immediate_publish:
      confirmation: "are_you_sure_modal"
      propagation: "instant_qr_code_updates"

    scheduled_publish:
      datetime_picker: "timezone_aware"
      recurring_schedules: "daily_weekly_monthly"
      preview_scheduling: "calendar_view"

  rollback_system:
    version_history: "timeline_view_with_thumbnails"
    one_click_rollback: "restore_previous_version"
    selective_rollback: "cherry_pick_changes"
    emergency_rollback: "instant_revert_option"
```

### 5. Advanced Menu Analytics Dashboard

```yaml
MenuAnalyticsDashboard:
  component_type: "modular_dashboard"

  performance_metrics:
    layout: "responsive_card_grid"
    metrics:
      - most_popular_items:
          visualization: "horizontal_bar_chart"
          time_range: "daily_weekly_monthly"

      - category_performance:
          visualization: "donut_chart_with_center_total"
          interaction: "drill_down_to_items"

      - pricing_analysis:
          visualization: "scatter_plot_price_vs_popularity"
          insights: "suggested_price_optimizations"

  customer_behavior:
    sections:
      - browsing_patterns:
          heatmap: "menu_section_attention_map"
          flow_analysis: "category_to_category_movement"

      - search_insights:
          top_searches: "word_cloud_or_list"
          failed_searches: "improvement_suggestions"

  real_time_monitoring:
    live_updates: "websocket_based"
    alerts: "unusual_patterns_or_outages"
    export_options: ["PDF", "Excel", "CSV"]
```

---

## 🎭 Detailed UI Mockups

### Desktop Menu Editor - Main Interface

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ ☰ ZERGO QR      Menu Management                    🔔 👤 John Smith    [💾 Auto-saved] │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│ ┌───────────┬─────────────────────┬─────────────────────────┬─────────────────────┐ │
│ │📋Structure│   🍽️ Item Editor     │     📱 Live Preview      │   ⚙️ Properties    │ │
│ │           │                     │                         │                     │ │
│ │ 📂 Starters│ ┌─────────────────┐ │ ┌─────────────────────┐ │ Selected Item:      │ │
│ │   🥗 Salads │ │ Item Details    │ │ │  📱 Customer View  │ │ Paneer Tikka        │ │
│ │   🍤 Appetizers│ ├─────────────────┤ │ │ ┌─────────────────┐ │ │ ┌─────────────────┐ │
│ │             │ │ Name*           │ │ │ │🔥 Popular Items │ │ │ │ Status: ●Available│ │
│ │ 📂 Mains    │ │[Paneer Tikka___]│ │ │ │ 🍛 Paneer Tikka│ │ │ │ Category: Starters│ │
│ │   🍛 Curries│ │                 │ │ │ │ ₹280      ⭐4.8│ │ │ │ Price: ₹280      │ │
│ │   🍝 Pasta  │ │ Description     │ │ │ │ Tender cottage │ │ │ └─────────────────┘ │
│ │   🥘 Biryani│ │ [Tender cottage │ │ │ │ cheese cubes...│ │ │                     │ │
│ │             │ │  cheese cubes __| │ │ │ │ 🥗 Add-ons     │ │ │ Quick Actions:      │ │
│ │ 📂 Desserts │ │  marinated in __|│ │ │ │ □ Extra Mint   │ │ │ [📷 Upload Image]   │ │
│ │   🍰 Cakes  │ │  spices and ___]│ │ │ │ □ Spicy Level  │ │ │ [🔄 Duplicate]      │ │
│ │   🍦 Ice Cream│ │                 │ │ │ │ [Add to Cart]  │ │ │ [🗑️ Delete]        │ │
│ │             │ │ 📸 Images       │ │ │ └─────────────────┘ │ │                     │ │
│ │ [+ Category]│ │ [Upload/Camera] │ │ │                     │ │ Dietary Info:       │ │
│ └───────────┴─┤ 💰 Pricing      │ │ │     QR Code View    │ │ ✅ Vegetarian       │ │
│               │ Base: [₹280___] │ │ │ Real-time updates   │ │ ❌ Vegan           │ │
│ Bulk Actions: │ Variants:       │ │ │ as you type         │ │ ❌ Gluten Free     │ │
│ [📤 Export]   │ □ Half: ₹180    │ │ │                     │ │ ⚠️ Contains: Dairy │ │
│ [📥 Import]   │ □ Full: ₹280    │ │ └─────────────────────┘ └─────────────────────┘ │
│ [🏷️ Bulk Edit]│ ☑ Jumbo: ₹380   │ │                                                │ │
└───────────────┴─────────────────┴─────────────────────────────────────────────────┘ │
                                                                                     │
│ ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│ │ Publishing Status: 📝 Draft (Last saved: 2 min ago)     [🔍 Preview] [📤 Publish]│ │
│ └─────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Mobile Menu Editor - Category Structure

```
┌─────────────────────────────┐
│ ← Menu    Structure    ⋯    │
├─────────────────────────────┤
│ 🔍 [Search menu items...]   │
├─────────────────────────────┤
│                             │
│ ┌─📂 Starters (8 items)───┐ │
│ │ 🟢 Available  ⚡ Featured│ │
│ │ ⋮                      │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─📂 Mains (12 items)─────┐ │
│ │ 🟢 Available            │ │
│ │ ⋮                      │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─📂 Desserts (6 items)───┐ │
│ │ 🟡 Some Unavailable     │ │
│ │ ⋮                      │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─📂 Beverages (15 items)─┐ │
│ │ 🟢 Available            │ │
│ │ ⋮                      │ │
│ └─────────────────────────┘ │
│                             │
│ [+ Add Category]            │
│                             │
├─────────────────────────────┤
│[📋Structure][🍽️Items][📱Preview][📤Publish]
│                       +     │
└─────────────────────────────┘
```

### Tablet Split-View - Item Details

```
┌─────────────────────────────────────────────────────────────────┐
│ ← Menu Management                         📱 Preview    🔔 👤   │
├───────────────────────┬─────────────────────────────────────────┤
│ 📂 Menu Structure     │ Paneer Tikka - Item Details            │
│                       │                                         │
│ 🥗 Starters           │ [Details] [Pricing] [Add-ons] [Schedule]│
│ ├─ Paneer Tikka ●     │                                         │
│ ├─ Veg Spring Rolls   │ ┌─────────────────────────────────────┐ │
│ ├─ Stuffed Mushrooms  │ │ Item Name *                         │ │
│ └─ Crispy Corn        │ │ [Paneer Tikka___________________]   │ │
│                       │ └─────────────────────────────────────┘ │
│ 🍛 Mains              │                                         │
│ ├─ Butter Chicken     │ ┌─────────────────────────────────────┐ │
│ ├─ Dal Makhani        │ │ Description                         │ │
│ ├─ Palak Paneer       │ │ [Tender cottage cheese cubes____]  │ │
│ └─ Biryani            │ │ [marinated in aromatic spices___]  │ │
│                       │ │ [and grilled to perfection______]  │ │
│ 🍰 Desserts           │ └─────────────────────────────────────┘ │
│                       │                                         │
│ [+ Add Category]      │ ┌─────────────────┬─────────────────────┐ │
│                       │ │ 📸 Primary Image│ Category            │ │
│ Quick Actions:        │ │ ┌─────────────┐ │ [Starters ▼]       │ │
│ [🔄 Reorder Items]    │ │ │   🖼️ Upload │ │                     │ │
│ [📤 Export Menu]      │ │ │    Image    │ │ Dietary Tags:       │ │
│ [📥 Import Items]     │ │ │             │ │ ☑️ Vegetarian       │ │
│ [👀 Preview All]      │ │ └─────────────┘ │ ☑️ Gluten Free     │ │
│                       │ │ [Upload] [📷]   │ ☑️ Spicy           │ │
└───────────────────────┴─┴─────────────────┴─────────────────────┘ │
                                                                   │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 💾 Auto-saved • Last published: 2 hours ago  [📤 Publish] │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Publishing Workflow - Version Control

```
┌─────────────────────────────┐
│ ← Back    Publish Menu      │
├─────────────────────────────┤
│ Step 2 of 3: Review Changes │
│ ●──●──○                     │
│                             │
│ 📊 Changes Summary:         │
│ ┌─────────────────────────┐ │
│ │ ✅ 3 items added        │ │
│ │ ✏️ 5 items modified     │ │
│ │ ❌ 1 item removed       │ │
│ │ 💰 8 prices updated     │ │
│ └─────────────────────────┘ │
│                             │
│ 🔍 Detailed Changes:        │
│                             │
│ ┌─Paneer Tikka──────────────┐│
│ │ ✏️ Modified              ││
│ │ Price: ₹250 → ₹280      ││
│ │ Added: Gluten Free tag  ││
│ └─────────────────────────┘│
│                            │
│ ┌─Chocolate Lava Cake─────┐ │
│ │ ✅ Added                 │ │
│ │ Category: Desserts       │ │
│ │ Price: ₹180              │ │
│ └─────────────────────────┘ │
│                             │
│ ⏰ Publishing Options:      │
│ ○ Publish Now               │
│ ● Schedule for Later        │
│   📅 Date: Tomorrow         │
│   🕐 Time: 12:00 PM         │
│                             │
│ ┌─────────────────────────┐ │
│ │ [◀ Previous]  [Next ▶] │ │
│ └─────────────────────────┘ │
├─────────────────────────────┤
│          Cancel             │
└─────────────────────────────┘
```

---

## 🔄 Advanced Interaction Patterns

### Drag & Drop Menu Organization

```yaml
drag_drop_system:
  visual_feedback:
    drag_start:
      - lift_animation: "scale(1.05) with shadow"
      - opacity_reduction: "to 0.9"
      - cursor_change: "grabbing_hand"

    drag_progress:
      - insertion_indicator: "blue_line_at_drop_position"
      - invalid_zones: "red_outline_with_shake"
      - auto_scroll: "when_near_container_edges"
      - magnetic_snapping: "snap_to_valid_positions"

    drop_completion:
      - success_animation: "gentle_settle_bounce"
      - hierarchy_reflow: "smooth_reorganization"
      - save_indication: "auto_save_spinner"

  interaction_types:
    category_reordering:
      - drag_handle: "visible_grip_icon"
      - constraints: "maintain_logical_hierarchy"

    item_movement:
      - cross_category: "allowed_with_confirmation"
      - position_memory: "remember_preferred_order"

    bulk_operations:
      - multi_select: "ctrl_click_or_checkboxes"
      - group_drag: "drag_multiple_items_together"
```

### Real-Time Collaborative Editing

```yaml
collaborative_features:
  multi_user_editing:
    conflict_resolution: "last_writer_wins_with_warnings"
    user_presence: "colored_cursors_and_avatars"
    edit_locks: "temporary_field_locking"

  change_notifications:
    real_time_updates: "smooth_fade_in_animations"
    conflict_indicators: "yellow_highlight_with_warning"
    sync_status: "connection_indicator_in_header"

  version_control:
    auto_branching: "create_versions_on_major_changes"
    merge_capabilities: "intelligent_change_merging"
    rollback_safety: "prevent_rollback_conflicts"
```

### Smart Content Assistance

```yaml
ai_powered_features:
  content_suggestions:
    description_enhancement: "AI_powered_description_improvements"
    pricing_recommendations: "market_analysis_based_pricing"
    category_organization: "suggest_optimal_menu_structure"

  image_optimization:
    auto_cropping: "smart_crop_for_best_presentation"
    compression: "maintain_quality_reduce_size"
    alt_text_generation: "accessibility_focused_descriptions"

  menu_analysis:
    performance_insights: "highlight_underperforming_items"
    seasonal_suggestions: "recommend_seasonal_additions"
    competitive_analysis: "benchmark_against_similar_restaurants"
```

---

## ♿ Comprehensive Accessibility Implementation

### Keyboard Navigation for Menu Management

```yaml
keyboard_shortcuts:
  global_shortcuts:
    "Ctrl/Cmd + S": "save_current_changes"
    "Ctrl/Cmd + Z": "undo_last_action"
    "Ctrl/Cmd + Y": "redo_last_action"
    "Ctrl/Cmd + F": "search_menu_items"
    "Ctrl/Cmd + N": "create_new_item"

  structure_navigation:
    "Arrow Keys": "navigate_menu_tree"
    "Enter": "expand_collapse_or_edit"
    "Space": "select_multiple_items"
    "Delete": "remove_selected_items"
    "F2": "rename_selected_item"

  editor_shortcuts:
    "Tab": "move_to_next_field"
    "Shift + Tab": "move_to_previous_field"
    "Ctrl/Cmd + Enter": "save_and_continue"
    "Escape": "cancel_current_edit"

screen_reader_optimizations:
  menu_structure_announcements:
    format: "{item_type}: {name}, {status}, {position} of {total}"
    example: "Menu Item: Paneer Tikka, Available, 3 of 8 in Starters"

  editing_context:
    field_labels: "clear_descriptive_labels"
    form_structure: "logical_fieldset_grouping"
    validation_feedback: "immediate_error_announcements"

  progress_feedback:
    save_status: "auto_save_progress_announcements"
    publishing_status: "step_by_step_progress_updates"
    bulk_operations: "completion_percentage_updates"
```

### Visual Accessibility Features

```yaml
visual_accessibility:
  high_contrast_support:
    color_combinations: "WCAG_AAA_compliant"
    icon_visibility: "outline_versions_for_contrast"
    focus_indicators: "extra_thick_focus_rings"

  customizable_display:
    font_scaling: "up_to_200_percent_support"
    compact_vs_comfortable: "density_options"
    color_theme_options: "high_contrast_dark_light"

  status_communication:
    not_color_only: "icons_plus_text_labels"
    pattern_coding: "different_patterns_for_status"
    redundant_encoding: "multiple_visual_cues"
```

---

## 🚀 Performance Optimization Strategy

### Large Menu Support

```yaml
performance_optimizations:
  virtualization:
    menu_tree: "render_only_visible_nodes"
    item_lists: "virtual_scrolling_for_hundreds_of_items"
    image_loading: "lazy_load_with_intersection_observer"

  caching_strategy:
    menu_structure: "cache_full_structure_locally"
    images: "progressive_loading_with_thumbnails"
    search_index: "client_side_search_optimization"

  real_time_efficiency:
    debounced_updates: "batch_rapid_changes"
    selective_rendering: "update_only_changed_components"
    connection_pooling: "efficient_websocket_usage"
```

### Mobile Performance

```yaml
mobile_optimizations:
  touch_responsiveness:
    tap_delays: "eliminate_300ms_click_delay"
    scroll_performance: "60fps_smooth_scrolling"
    gesture_handling: "efficient_touch_event_processing"

  memory_management:
    image_sizing: "serve_appropriate_resolution"
    component_cleanup: "proper_widget_disposal"
    cache_limits: "prevent_memory_bloat"

  offline_capabilities:
    draft_storage: "local_storage_for_unsaved_changes"
    image_caching: "cache_recently_uploaded_images"
    graceful_degradation: "work_without_internet"
```

---

## 📊 Success Metrics & KPIs

### User Experience Metrics

```yaml
ux_metrics:
  menu_creation_efficiency:
    new_item_creation_time: "target: <2_minutes"
    category_organization_time: "target: <30_seconds"
    bulk_operations_completion: "target: >90%"

  publishing_workflow:
    draft_to_publish_time: "target: <5_minutes"
    version_rollback_success: "target: >95%"
    scheduled_publish_accuracy: "target: >99%"

  mobile_usability:
    touch_target_accessibility: "target: 100%"
    one_handed_operation_success: "target: >85%"
    offline_functionality: "target: >90%"

performance_metrics:
  loading_times:
    menu_editor_initialization: "target: <2_seconds"
    image_upload_processing: "target: <5_seconds"
    real_time_preview_sync: "target: <500ms"

  scalability:
    large_menu_performance: "target: 60fps_with_500_items"
    concurrent_editing: "target: 10_simultaneous_users"

business_impact:
  menu_update_frequency: "increase by 200%"
  customer_engagement: "improve menu browsing by 40%"
  operational_efficiency: "reduce menu management time by 60%"
```

This comprehensive design specification provides everything needed to implement a world-class menu management system that maintains consistency with the established ZERGO QR design system while delivering enterprise-grade functionality for restaurant menu creation, organization, and publishing workflows.

## 🎯 Design Goals

- **Operational Efficiency**: Streamline table management with intuitive drag-and-drop interfaces
- **Real-time Visibility**: Provide instant table status updates across all devices
- **Mobile Excellence**: Optimize for restaurant staff using mobile devices on the floor
- **Scalable Architecture**: Support restaurants from single-floor cafes to multi-level establishments
- **Data-Driven Insights**: Enable performance tracking and analytics integration
- **Accessibility First**: Ensure WCAG 2.1 AA compliance for all user interactions

---

## 🎨 Visual Design System (Inherited + Extended)

### Extended Color Palette for Table Management

```yaml
# Table Status Colors (extending ZERGO palette)
table_status:
  available:
    background: "#E8F5E8" # success.50
    border: "#2E7D32" # success.600
    icon: "#1B5E20" # success.800

  occupied:
    background: "#FFEBEE" # error.50
    border: "#D32F2F" # error.600
    icon: "#B71C1C" # error.800

  reserved:
    background: "#FFF8E1" # warning.50
    border: "#F57C00" # warning.600
    icon: "#E65100" # warning.800

  cleaning:
    background: "#F3E5F5" # purple.50
    border: "#9C27B0" # purple.600
    icon: "#6A1B9A" # purple.800

# Floor Plan Canvas Colors
canvas:
  background: "#FAFAFA" # neutral.50
  grid_lines: "#EEEEEE" # neutral.200
  grid_dots: "#E0E0E0" # neutral.300
  selection_box: "#1976D2" # primary.600
  drop_zone: "#E3F2FD" # primary.50

# Interactive Elements
interactions:
  drag_handle: "#757575" # neutral.600
  resize_handle: "#1976D2" # primary.600
  hover_overlay: "rgba(25, 118, 210, 0.08)"
  active_overlay: "rgba(25, 118, 210, 0.12)"
```

### Table Shape & Size Standards

```yaml
table_shapes:
  round:
    default_radius: 24px
    min_radius: 16px
    max_radius: 48px

  square:
    default_size: 48px
    min_size: 32px
    max_size: 80px

  rectangular:
    default_width: 64px
    default_height: 32px
    min_width: 48px
    max_width: 120px
    min_height: 24px
    max_height: 48px

table_capacity_indicators:
  small: "1-2 people" # 16px icon
  medium: "3-4 people" # 20px icon
  large: "5-8 people" # 24px icon
  xlarge: "8+ people" # 28px icon
```

---

## 📱 Responsive Layout Specifications

### Mobile Layout (320px - 767px)

```yaml
mobile_layout:
  navigation:
    type: "bottom_tab_bar"
    height: 64px
    tabs: ["Floor Plan", "Status", "Analytics"]

  floor_plan_view:
    canvas_mode: "full_screen_modal"
    zoom_controls: "floating_action_buttons"
    table_info: "bottom_sheet_on_tap"
    edit_mode: "toggle_button_in_header"

  table_list_view:
    layout: "card_list"
    card_height: 80px
    quick_actions: ["Reserve", "Clean", "Available"]
    search_bar: "sticky_top"

  status_dashboard:
    layout: "single_column_cards"
    metrics: "horizontal_scroll_cards"
    table_grid: "responsive_grid_2_columns"
```

### Tablet Layout (768px - 1023px)

```yaml
tablet_layout:
  navigation:
    type: "persistent_sidebar"
    width: 240px
    collapsed_width: 64px

  main_content:
    layout: "two_panel"
    left_panel: "floor_plan_canvas"
    right_panel: "table_details_and_controls"
    panel_ratio: "70:30"

  floor_plan_canvas:
    zoom_controls: "corner_overlay"
    table_toolbar: "floating_toolbar"
    property_inspector: "side_panel_overlay"

  multi_floor:
    tab_style: "horizontal_tabs"
    position: "above_canvas"
```

### Desktop Layout (1024px+)

```yaml
desktop_layout:
  navigation:
    type: "persistent_sidebar_with_secondary"
    primary_width: 240px
    secondary_width: 320px

  main_workspace:
    layout: "three_panel"
    left_panel: "navigation_and_tools"
    center_panel: "floor_plan_canvas"
    right_panel: "properties_and_status"
    panel_ratios: "20:60:20"

  advanced_features:
    multi_floor_tabs: "vertical_tab_stack"
    bulk_operations: "context_toolbar"
    analytics_overlay: "expandable_bottom_panel"
```

---

## 🏗️ Core Component Specifications

### 1. Interactive Floor Plan Canvas

```yaml
FloorPlanCanvas:
  component_type: "custom_painter_widget"

  canvas_properties:
    background_color: "canvas.background"
    grid_enabled: true
    grid_size: 16px # 2x base spacing unit
    snap_to_grid: true
    zoom_range: "25% to 400%"
    pan_enabled: true

  interaction_modes:
    view_mode:
      - pan_and_zoom: true
      - table_selection: "single_tap"
      - context_menu: "long_press"

    edit_mode:
      - drag_drop_enabled: true
      - resize_handles: "corner_and_edge"
      - multi_selection: "ctrl_click"
      - bulk_operations: true

  table_rendering:
    default_style:
      border_width: 2px
      border_radius: 8px # For square/rectangular tables
      shadow_elevation: 1

    status_indicators:
      position: "top_right_corner"
      size: 12px
      animation: "pulse_for_updates"

    capacity_labels:
      position: "center"
      font_size: 12px
      font_weight: "600"
      color: "neutral.700"
```

### 2. Table Status Indicator Component

```yaml
TableStatusIndicator:
  component_type: "stateful_widget"

  visual_states:
    available:
      color: "table_status.available.background"
      icon: "Icons.check_circle"
      animation: "none"

    occupied:
      color: "table_status.occupied.background"
      icon: "Icons.people"
      animation: "subtle_pulse"
      duration_display: true

    reserved:
      color: "table_status.reserved.background"
      icon: "Icons.schedule"
      animation: "breathing"
      countdown_timer: true

    cleaning:
      color: "table_status.cleaning.background"
      icon: "Icons.cleaning_services"
      animation: "rotating_slow"

  interaction_behavior:
    tap_action: "show_quick_actions_menu"
    long_press: "show_detailed_status"
    swipe_actions:
      left: "change_status"
      right: "view_history"
```

### 3. Table Configuration Modal

```yaml
TableConfigModal:
  component_type: "modal_bottom_sheet" # Mobile
  component_type_tablet: "dialog_overlay" # Tablet/Desktop

  sections:
    basic_info:
      title: "Table Details"
      fields:
        - table_number:
            type: "text_field"
            validation: "required|unique_per_restaurant"

        - capacity:
            type: "stepper_input"
            min_value: 1
            max_value: 20

        - shape:
            type: "visual_selector"
            options: ["round", "square", "rectangular"]

    positioning:
      title: "Position & Size"
      fields:
        - coordinates:
            type: "coordinate_input"
            read_only: true # Set via drag-drop

        - dimensions:
            type: "size_input"
            constraints: "based_on_shape"

        - rotation:
            type: "rotation_slider"
            range: "0° to 360°"

    categorization:
      title: "Table Type"
      fields:
        - category:
            type: "dropdown_select"
            options: ["Regular", "VIP", "Outdoor", "Bar", "Counter"]

        - special_requirements:
            type: "multi_select_chips"
            options: ["High Chair", "Wheelchair Accessible", "Window View"]
```

### 4. Real-Time Status Dashboard

```yaml
StatusDashboard:
  component_type: "stream_builder_widget"

  header_metrics:
    layout: "horizontal_cards"
    metrics:
      - total_tables:
          value: "count"
          trend: "none"

      - occupancy_rate:
          value: "percentage"
          trend: "hourly_comparison"
          color: "dynamic_based_on_value"

      - average_turnaround:
          value: "duration"
          trend: "daily_average"

      - revenue_per_table:
          value: "currency"
          trend: "weekly_comparison"

  status_filters:
    type: "filter_chips"
    options:
      - "All Tables"
      - "Available"
      - "Occupied"
      - "Reserved"
      - "Cleaning"
    default_selected: "All Tables"

  table_grid:
    layout: "responsive_grid"
    item_component: "TableStatusCard"
    sort_options:
      - "Table Number"
      - "Status"
      - "Occupancy Duration"
      - "Last Updated"

  real_time_updates:
    connection: "supabase_realtime"
    animation: "smooth_state_transitions"
    sound_alerts: "configurable"
    push_notifications: "status_changes"
```

### 5. Multi-Floor Navigation

```yaml
FloorNavigation:
  component_type: "tab_bar_with_overflow"

  floor_tabs:
    style: "material_3_tabs"
    scrollable: true
    indicator: "rounded_rectangle"

    tab_content:
      - floor_name: "editable_on_double_tap"
      - table_count: "live_count_badge"
      - status_indicator: "colored_dot"

  floor_management:
    add_floor_button:
      position: "trailing"
      icon: "Icons.add"
      action: "show_create_floor_dialog"

    floor_options_menu:
      trigger: "long_press_tab"
      actions:
        - "Rename Floor"
        - "Duplicate Layout"
        - "Delete Floor"
        - "Floor Settings"

  floor_switching:
    animation: "slide_transition"
    preserve_zoom_level: true
    preserve_pan_position: false # Reset to center
```

---

## 🎭 UI Mockups & Wireframes

### Desktop Floor Plan Editor

```
┌─────────────────────────────────────────────────────────────────┐
│ ☰ ZERGO QR    Table Management             🔔 👤 John Smith    │
├───────────────────┬─────────────────────────────┬───────────────┤
│ 📊 Dashboard      │ Ground Floor ▼ Main Hall ▼  │ Table T-001   │
│ 📋 QR Codes      │ ┌─┬─────────────────────────┐ │ ●●●●○ (4/5)   │
│ 🍽️ Menu          │ │+│ 🔍 100% ⊞ ⊟ 📐 ↻       │ │ Available     │
│ 👥 Staff         │ ├─┴─────────────────────────┤ │ ┌───────────┐ │
│ 📈 Analytics     │ │ ┌─[T1]─┐    ┌─[T3]─┐     │ │ │ Capacity  │ │
│ 🏢 Tables ●      │ │ │ ●●○○ │    │ ●●●● │     │ │ │ [4] people│ │
│ ⚙️ Settings      │ │ │ 2/4  │    │ 4/4  │     │ │ └───────────┘ │
│                  │ │ └──────┘    └──────┘     │ │ ┌───────────┐ │
│ Floor Plans:     │ │    ┌[T2]┐     ┌[T4]─┐    │ │ │ Shape     │ │
│ ▶ Ground Floor   │ │    │●●●○│     │●●●●○│    │ │ │ ⬜ Square  │ │
│   First Floor    │ │    │3/4│     │4/5 │    │ │ └───────────┘ │
│   Terrace        │ │    └────┘     └─────┘    │ │ ┌───────────┐ │
│                  │ │         ┌─[T5]──┐       │ │ │ Status    │ │
│ Quick Actions:   │ │         │ ●●○○○ │       │ │ │ Available │ │
│ [Add Table]      │ │         │  2/5  │       │ │ │ [Change]  │ │
│ [Import Layout]  │ │         └───────┘       │ │ └───────────┘ │
│ [Export QR]      │ └─────────────────────────┘ │ [Save Changes]│
└───────────────────┴─────────────────────────────┴───────────────┘
```

### Mobile Table Status View

```
┌─────────────────────────────┐
│ ← Back    Table Status      │
├─────────────────────────────┤
│                             │
│ ┌─────┬─────┬─────┬─────┐    │
│ │ All │ ●12 │ ●4  │ ●1  │    │
│ │ 20  │ Avl │ Ocp │ Rsv │    │
│ └─────┴─────┴─────┴─────┘    │
│                             │
│ 🔍 [Search tables...]       │
│                             │
│ ┌─T1──────────────────────┐  │
│ │ 🟢 Available       2/4  │  │
│ │ Last cleaned: 2h ago    │  │
│ │ [Reserve] [Clean] [...] │  │
│ └─────────────────────────┘  │
│                             │
│ ┌─T2──────────────────────┐  │
│ │ 🔴 Occupied        3/4  │  │
│ │ Duration: 45 min        │  │
│ │ Order: #1234 (₹890)     │  │
│ │ [Check Order] [Clean]   │  │
│ └─────────────────────────┘  │
│                             │
│ ┌─T3──────────────────────┐  │
│ │ 🟡 Reserved        4/4  │  │
│ │ Reserved for: 7:30 PM   │  │
│ │ Customer: John Smith    │  │
│ │ [Cancel] [Modify]       │  │
│ └─────────────────────────┘  │
├─────────────────────────────┤
│ [📊 Floor Plan] [📋 Status] │
│ [📈 Analytics]              │
└─────────────────────────────┘
```

### Tablet Split-Screen Layout

```
┌─────────────────────────────────────────────────────────────┐
│ ☰ ZERGO QR         Table Management              🔔 👤    │
├─────────────────────────────────┬───────────────────────────┤
│ Ground Floor | First Floor      │ Live Status Dashboard     │
│ ┌─────────────────────────────┐ │ ┌───────┬───────┬───────┐ │
│ │ [🔍] [📐] [⊞] [↻] [💾]     │ │ │ 15/20 │ 2.1h  │ ₹125  │ │
│ │ ┌─[T1]─┐  ┌─[T2]─┐  [T3]   │ │ │ Occup │ Avg   │ /Table│ │
│ │ │ ●●○○ │  │ ●●●● │   ●     │ │ └───────┴───────┴───────┘ │
│ │ │ 2/4  │  │ 4/4  │   1     │ │                           │
│ │ └──────┘  └──────┘         │ │ Recent Activity:          │
│ │     ┌[T4]─┐    ┌[T5]─┐     │ │ ┌─────────────────────────┐ │
│ │     │●●●○ │    │●●○○ │     │ │ │ T7 → Available (2min)   │ │
│ │     │3/4 │    │2/4  │     │ │ │ T3 → Occupied (5min)    │ │
│ │     └─────┘    └─────┘     │ │ │ T12→ Reserved (8min)    │ │
│ │        ┌─[T6]──────┐       │ │ └─────────────────────────┘ │
│ │        │   ●●●●●   │       │ │                           │
│ │        │    5/6    │       │ │ Quick Actions:            │
│ │        └───────────┘       │ │ [🟢 Set Available]        │
│ └─────────────────────────────┘ │ [🔴 Mark Occupied]        │
│                                 │ [🟡 Reserve Table]        │
│ Selected: Table T1              │ [🧹 Start Cleaning]       │
│ Capacity: 4 people              │                           │
│ Status: Available               │ [View All Tables]         │
│ [Edit Details] [View History]   │                           │
└─────────────────────────────────┴───────────────────────────┘
```

---

## 🔄 Interaction Patterns & Micro-Animations

### Drag & Drop Behavior

```yaml
drag_drop_interactions:
  table_selection:
    visual_feedback:
      - selection_ring: "2px solid primary.600"
      - elevation_increase: "0 to 4"
      - scale_transform: "1.0 to 1.05"

  drag_initiation:
    trigger: "long_press_200ms"
    visual_changes:
      - lift_animation: "scale(1.1) with elevation"
      - opacity_reduction: "1.0 to 0.8"
      - cursor_change: "grabbing"

  drag_progress:
    grid_snapping:
      - snap_threshold: "8px"
      - snap_animation: "smooth_ease_300ms"
      - visual_guides: "dotted_alignment_lines"

    collision_detection:
      - invalid_drop_zone: "red_outline_shake"
      - valid_drop_zone: "green_outline_pulse"
      - overlap_warning: "yellow_outline_flash"

  drop_completion:
    success_feedback:
      - position_confirm: "gentle_bounce_200ms"
      - shadow_settle: "elevation_ease_out"
      - state_save: "auto_save_indicator"

    failure_feedback:
      - return_to_origin: "elastic_bounce_400ms"
      - error_indication: "red_flash_100ms"
```

### Status Change Animations

```yaml
status_transitions:
  available_to_occupied:
    duration: 300ms
    sequence:
      - color_transition: "success.50 to error.50"
      - icon_morph: "check_circle to people"
      - scale_pulse: "1.0 to 1.2 to 1.0"
      - duration_timer_start: "fade_in_from_bottom"

  occupied_to_available:
    duration: 250ms
    sequence:
      - celebration_burst: "subtle_particle_effect"
      - color_transition: "error.50 to success.50"
      - icon_morph: "people to check_circle"
      - counter_reset: "slide_out_right"

  reserved_notification:
    trigger: "15_minutes_before"
    animation:
      - attention_pulse: "3_cycles_over_5_seconds"
      - color_intensify: "warning.50 to warning.100"
      - icon_bounce: "subtle_vertical_movement"

  cleaning_rotation:
    duration: 2000ms # 2 seconds per rotation
    animation: "continuous_slow_spin"
    easing: "linear"
```

### Real-Time Update Feedback

```yaml
realtime_updates:
  new_table_added:
    animation: "scale_in_from_center"
    duration: 400ms
    highlight: "primary_glow_2_seconds"

  table_status_changed:
    animation: "color_morph_with_icon_change"
    duration: 300ms
    sound: "subtle_notification_chime"

  table_removed:
    animation: "scale_out_to_center"
    duration: 300ms
    follow_up: "layout_reflow_smooth"

  connection_lost:
    visual_indicator: "grayscale_overlay"
    message: "Connection lost - trying to reconnect..."
    retry_animation: "pulsing_reconnect_icon"

  connection_restored:
    visual_indicator: "color_restoration_wave"
    message: "Connected - syncing latest changes..."
    sync_animation: "spinning_refresh_icon"
```

---

## ♿ Advanced Accessibility Features

### Keyboard Navigation for Table Management

```yaml
keyboard_support:
  floor_plan_navigation:
    arrow_keys: "move_between_tables"
    tab_key: "focus_next_interactive_element"
    shift_tab: "focus_previous_element"
    enter: "select_table_or_activate"
    space: "toggle_table_selection"
    escape: "clear_selection_or_exit_mode"

  table_manipulation:
    ctrl_arrow_keys: "move_selected_table_1px"
    shift_arrow_keys: "move_selected_table_10px"
    plus_minus: "resize_table"
    ctrl_c: "copy_table_properties"
    ctrl_v: "paste_table_properties"
    delete: "remove_selected_table"

  floor_switching:
    ctrl_tab: "switch_to_next_floor"
    ctrl_shift_tab: "switch_to_previous_floor"
    ctrl_1_9: "switch_to_floor_by_number"

screen_reader_support:
  table_announcements:
    format: "{table_number}, {status}, {occupancy}, {duration}"
    example: "Table 5, occupied, 3 out of 4 seats, 45 minutes"

  status_change_announcements:
    format: "Table {number} changed from {old_status} to {new_status}"
    live_region: "polite" # Don't interrupt current speech

  canvas_navigation:
    spatial_description: "Floor plan with {count} tables arranged in {layout}"
    position_feedback: "Table {number} at position {x}, {y}"
```

### Visual Accessibility Enhancements

```yaml
visual_accessibility:
  high_contrast_mode:
    table_borders: "3px solid black"
    status_colors: "adjusted_for_contrast_ratio_7_1"
    text_labels: "bold_weight_increased_size"
    background: "pure_white_or_pure_black"

  color_blind_support:
    status_patterns:
      available: "solid_fill + checkmark_icon"
      occupied: "diagonal_stripes + people_icon"
      reserved: "dotted_pattern + clock_icon"
      cleaning: "crosshatch + cleaning_icon"

  low_vision_support:
    zoom_levels: "up_to_400_percent"
    text_scaling: "respects_system_font_size"
    focus_indicators: "extra_thick_outlines"
    button_sizes: "minimum_44px_touch_targets"
```

---

## 🚀 Performance Optimization Strategies

### Real-Time Data Management

```yaml
performance_optimizations:
  real_time_updates:
    throttling: "max_10_updates_per_second"
    batching: "combine_multiple_status_changes"
    selective_updates: "only_affected_tables_rerender"

  canvas_rendering:
    virtualization: "render_only_visible_tables"
    canvas_caching: "cache_static_elements"
    animation_optimization: "use_gpu_acceleration"

  mobile_optimizations:
    touch_debouncing: "prevent_accidental_multiple_taps"
    gesture_recognition: "efficient_pan_zoom_detection"
    memory_management: "dispose_off_screen_widgets"

  data_loading:
    progressive_loading: "essential_data_first"
    background_sync: "update_non_critical_data_later"
    offline_support: "cache_last_known_state"
```

### Large Restaurant Support

```yaml
scalability_patterns:
  table_virtualization:
    visible_area_rendering: "render_only_viewport_tables"
    lazy_loading: "load_floor_data_on_demand"
    pagination: "chunk_large_table_lists"

  search_optimization:
    indexed_search: "fast_table_number_lookup"
    filtered_views: "pre_computed_status_groups"
    autocomplete: "debounced_search_suggestions"

  memory_management:
    floor_unloading: "unload_inactive_floor_data"
    image_optimization: "compressed_floor_plan_backgrounds"
    widget_pooling: "reuse_table_widgets"
```

---

## 🔧 Flutter Implementation Specifications

### Core Widget Architecture

```dart
// Main Table Management Screen Structure
class TableManagementScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ResponsiveLayout(
      mobile: MobileTableManagementView(),
      tablet: TabletTableManagementView(),
      desktop: DesktopTableManagementView(),
    );
  }
}

// Floor Plan Canvas Widget
class FloorPlanCanvas extends StatefulWidget {
  final List<Table> tables;
  final Function(Table) onTableTap;
  final Function(Table, Offset) onTableMoved;
  final bool editMode;

  @override
  _FloorPlanCanvasState createState() => _FloorPlanCanvasState();
}

class _FloorPlanCanvasState extends State<FloorPlanCanvas>
    with TickerProviderStateMixin {

  late AnimationController _statusAnimationController;
  late AnimationController _dragAnimationController;
  TransformationController _transformController = TransformationController();

  @override
  Widget build(BuildContext context) {
    return InteractiveViewer(
      transformationController: _transformController,
      minScale: 0.25,
      maxScale: 4.0,
      child: CustomPaint(
        painter: FloorPlanPainter(
          tables: widget.tables,
          gridEnabled: true,
          selectedTable: selectedTable,
        ),
        child: GestureDetector(
          onTapUp: _handleTapUp,
          onPanStart: _handlePanStart,
          onPanUpdate: _handlePanUpdate,
          onPanEnd: _handlePanEnd,
          child: Container(
            width: 1200, // Canvas size
            height: 800,
          ),
        ),
      ),
    );
  }
}
```

### Custom Painter for Floor Plan

```dart
class FloorPlanPainter extends CustomPainter {
  final List<Table> tables;
  final bool gridEnabled;
  final Table? selectedTable;

  @override
  void paint(Canvas canvas, Size size) {
    // Draw grid background
    if (gridEnabled) {
      _drawGrid(canvas, size);
    }

    // Draw tables
    for (final table in tables) {
      _drawTable(canvas, table);
      _drawTableStatus(canvas, table);
      _drawCapacityIndicator(canvas, table);
    }

    // Draw selection indicator
    if (selectedTable != null) {
      _drawSelectionRing(canvas, selectedTable!);
    }
  }

  void _drawTable(Canvas canvas, Table table) {
    final paint = Paint()
      ..color = _getTableColor(table.status)
      ..style = PaintingStyle.fill;

    final borderPaint = Paint()
      ..color = _getTableBorderColor(table.status)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    final rect = Rect.fromCenter(
      center: Offset(table.position.x, table.position.y),
      width: table.dimensions.width,
      height: table.dimensions.height,
    );

    // Draw based on table shape
    switch (table.shape) {
      case TableShape.round:
        canvas.drawCircle(rect.center, rect.width / 2, paint);
        canvas.drawCircle(rect.center, rect.width / 2, borderPaint);
        break;
      case TableShape.square:
      case TableShape.rectangular:
        final roundedRect = RRect.fromRectAndRadius(rect, Radius.circular(8));
        canvas.drawRRect(roundedRect, paint);
        canvas.drawRRect(roundedRect, borderPaint);
        break;
    }
  }

  void _drawTableStatus(Canvas canvas, Table table) {
    final statusIconPaint = Paint()..color = _getStatusIconColor(table.status);

    final iconRect = Rect.fromCenter(
      center: Offset(
        table.position.x + table.dimensions.width / 2 - 8,
        table.position.y - table.dimensions.height / 2 + 8,
      ),
      width: 16,
      height: 16,
    );

    // Draw status icon based on table status
    _drawStatusIcon(canvas, table.status, iconRect, statusIconPaint);
  }
}
```

### Real-Time Status Updates

```dart
class TableStatusController extends GetxController {
  final _tableRepository = Get.find<TableRepository>();
  final RxList<Table> tables = <Table>[].obs;
  final Rx<Table?> selectedTable = Rx<Table?>(null);

  late StreamSubscription _realtimeSubscription;

  @override
  void onInit() {
    super.onInit();
    _setupRealtimeUpdates();
    loadTables();
  }

  void _setupRealtimeUpdates() {
    _realtimeSubscription = _tableRepository
        .getRealtimeUpdates()
        .listen((update) {
      _handleRealtimeUpdate(update);
    });
  }

  void _handleRealtimeUpdate(TableUpdate update) {
    switch (update.type) {
      case UpdateType.statusChange:
        _updateTableStatus(update.tableId, update.newStatus);
        _showStatusChangeAnimation(update.tableId);
        break;
      case UpdateType.tableAdded:
        _addNewTable(update.table!);
        break;
      case UpdateType.tableRemoved:
        _removeTable(update.tableId);
        break;
    }
  }

  void _updateTableStatus(String tableId, TableStatus newStatus) {
    final tableIndex = tables.indexWhere((t) => t.id == tableId);
    if (tableIndex >= 0) {
      final updatedTable = tables[tableIndex].copyWith(status: newStatus);
      tables[tableIndex] = updatedTable;

      // Trigger status change animation
      _triggerStatusAnimation(tableId, newStatus);
    }
  }
}
```

### Touch-Optimized Mobile Components

```dart
class MobileTableStatusCard extends StatelessWidget {
  final Table table;
  final VoidCallback? onTap;
  final Function(TableStatus)? onStatusChange;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Row(
            children: [
              // Status indicator
              Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  color: _getStatusColor(table.status),
                  shape: BoxShape.circle,
                ),
              ),
              SizedBox(width: 12),

              // Table info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Table ${table.tableNumber}',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      _getStatusDescription(table),
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),

              // Capacity indicator
              Container(
                padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  '${table.currentOccupancy}/${table.capacity}',
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),

              // Quick actions
              if (onStatusChange != null)
                PopupMenuButton<TableStatus>(
                  icon: Icon(Icons.more_vert),
                  itemBuilder: (context) => _buildQuickActions(),
                  onSelected: onStatusChange,
                ),
            ],
          ),
        ),
      ),
    );
  }
}
```

---

## 📊 Implementation Roadmap

### Phase 1: Core Canvas & Basic Table Management (Week 1-2)

```yaml
phase_1_deliverables:
  - interactive_floor_plan_canvas
  - basic_table_crud_operations
  - simple_drag_drop_functionality
  - mobile_responsive_layout
  - table_status_indicators
```

### Phase 2: Real-Time Updates & Advanced Features (Week 3-4)

```yaml
phase_2_deliverables:
  - supabase_realtime_integration
  - status_change_animations
  - multi_floor_support
  - table_configuration_modals
  - search_and_filtering
```

### Phase 3: Analytics & Performance Optimization (Week 5-6)

```yaml
phase_3_deliverables:
  - performance_metrics_dashboard
  - large_restaurant_optimizations
  - offline_support
  - accessibility_enhancements
  - comprehensive_testing
```

---

## 🎯 Success Metrics & KPIs

### User Experience Metrics

```yaml
ux_metrics:
  task_completion_rate: "target: >95%"
  average_task_time: "target: <30_seconds"
  error_rate: "target: <2%"
  user_satisfaction_score: "target: >4.5/5"

performance_metrics:
  canvas_render_time: "target: <100ms"
  real_time_update_latency: "target: <500ms"
  drag_drop_responsiveness: "target: <16ms"
  mobile_scroll_performance: "target: 60fps"

business_metrics:
  table_turnover_rate: "improve by 15%"
  order_processing_time: "reduce by 20%"
  staff_efficiency: "improve by 25%"
  customer_satisfaction: "improve by 10%"
```

This comprehensive design specification provides everything needed to implement a world-class table management system that maintains consistency with the Story 1.1 design system while delivering the enterprise-grade functionality expected by restaurant operators. The design balances operational efficiency with visual appeal, ensuring that staff can quickly manage table statuses while providing customers with a seamless dining experience.
