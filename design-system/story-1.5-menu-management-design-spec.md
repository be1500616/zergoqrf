# ZERGO QR - Story 1.5 UI/UX Design System

**Menu Creation & Management Interface**

---

## 📋 Executive Summary

This document defines the comprehensive UI/UX design system for Story 1.5 (Menu Creation & Management), building upon the established Material Design 3 + ZERGO brand system from Stories 1.1 and 1.2. The specification delivers enterprise-grade menu management interfaces that rival leading SaaS platforms like Stripe, Linear, and Notion, with advanced features including hierarchical menu organization, real-time preview capabilities, professional publishing workflows, and comprehensive version control.

## 🎯 Design Goals

- **Professional Menu Creation**: Intuitive drag-and-drop menu builder with visual hierarchy management
- **Enterprise Publishing Workflow**: Draft/live versioning with scheduled updates and rollback capabilities
- **Multi-Device Excellence**: Responsive design optimized for mobile editing, tablet split-views, and desktop power-user workflows
- **Real-Time Collaboration**: Live preview functionality with instant updates across all QR codes
- **Accessibility Leadership**: WCAG 2.1 AA compliance with inclusive design for all restaurant staff
- **Performance at Scale**: Optimized for large menus with hundreds of items and complex categorization

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

---

## 🎭 Detailed Implementation Notes

### Flutter Widget Architecture

The menu management system should be implemented using a modular Flutter architecture:

- `MenuManagementController` - State management with GetX
- `MenuStructureTree` - Hierarchical category/item display
- `MenuItemEditor` - Tabbed form interface
- `LivePreviewPanel` - Real-time customer view simulation
- `PublishingWorkflow` - Version control and publishing wizard

### Key Technical Requirements

- Real-time synchronization using Supabase WebSockets
- Image optimization and CDN delivery
- Offline draft editing capabilities
- Professional drag-and-drop interface
- Comprehensive accessibility support

This specification provides the foundation for implementing a world-class menu management system that maintains consistency with the established ZERGO QR design system while delivering enterprise-grade functionality for restaurant menu creation, organization, and publishing workflows.
