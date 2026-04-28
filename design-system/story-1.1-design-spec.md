# ZERGO QR - Story 1.1 UI/UX Design System

## Design Requirements Analysis Completed

Refer to story-1.5-menu-management-design-spec.md for the comprehensive menu management design system.

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

- **Conversion Optimization**: Minimize drop-off rates through intuitive, step-by-step guidance
- **Professional Trust**: Establish credibility through polished, enterprise-grade UI
- **Mobile-First Excellence**: Ensure seamless experience across all device sizes
- **Accessibility Leadership**: WCAG 2.1 AA compliance with inclusive design principles
- **Brand Consistency**: Align with ZERGO's identity while following Material Design 3

---

## 🎨 Visual Design System

### Color Palette (Material Design 3 + ZERGO Brand)

```yaml
# Primary Colors (ZERGO Brand)
primary:
  50: "#E3F2FD" # Light blue background
  100: "#BBDEFB" # Subtle highlights
  600: "#1976D2" # Primary CTA buttons
  700: "#1565C0" # Hover states
  900: "#0D47A1" # Strong emphasis

# Semantic Colors
success:
  50: "#E8F5E8" # Success backgrounds
  600: "#2E7D32" # Success text/icons

warning:
  50: "#FFF8E1" # Warning backgrounds
  600: "#F57C00" # Warning text/icons

error:
  50: "#FFEBEE" # Error backgrounds
  600: "#D32F2F" # Error text/icons

# Neutral Palette
neutral:
  50: "#FAFAFA" # Page backgrounds
  100: "#F5F5F5" # Card backgrounds
  200: "#EEEEEE" # Borders, dividers
  400: "#BDBDBD" # Placeholder text
  600: "#757575" # Secondary text
  900: "#212121" # Primary text
```

### Typography Scale (Material Design 3)

```yaml
# Display (Hero sections)
display-large: 57px, -0.25px, 400
display-medium: 45px, 0px, 400
display-small: 36px, 0px, 400

# Headings
headline-large: 32px, 0px, 400
headline-medium: 28px, 0px, 400
headline-small: 24px, 0px, 400

# Titles
title-large: 22px, 0px, 400
title-medium: 16px, 0.15px, 500
title-small: 14px, 0.1px, 500

# Body Text
body-large: 16px, 0.5px, 400
body-medium: 14px, 0.25px, 400
body-small: 12px, 0.4px, 400

# Labels
label-large: 14px, 0.1px, 500
label-medium: 12px, 0.5px, 500
label-small: 11px, 0.5px, 500
```

### Spacing System (8dp Grid)

```yaml
spacing:
  xs: 4px # Tight spacing
  sm: 8px # Base unit
  md: 16px # Standard spacing
  lg: 24px # Section spacing
  xl: 32px # Large gaps
  xxl: 48px # Hero spacing
  xxxl: 64px # Page-level spacing
```

### Elevation & Shadow System

```yaml
elevation:
  0: none # Flat surfaces
  1: 0 1px 2px rgba(0,0,0,0.12) # Cards at rest
  2: 0 1px 5px rgba(0,0,0,0.12) # Cards on hover
  3: 0 1px 8px rgba(0,0,0,0.12) # Modals, dropdowns
  4: 0 2px 10px rgba(0,0,0,0.12) # FABs, app bars
  5: 0 4px 15px rgba(0,0,0,0.12) # Navigation drawers
```

---

## 📱 Component Specifications

### 1. Progressive Registration Wizard

**Current Issues Identified:**

- Basic linear stepper lacks visual hierarchy
- No contextual help or guidance
- Missing validation feedback patterns
- Form fields don't follow Material Design 3 principles

**Enhanced Design:**

```yaml
RegistrationWizard:
  layout: "centered-card"
  max_width: 640px
  background: "gradient(neutral.50 -> primary.50)"

  step_indicator:
    type: "horizontal-pills"
    active_color: "primary.600"
    completed_color: "success.600"
    pending_color: "neutral.400"
    animation: "slide-progress"

  navigation:
    position: "sticky-bottom"
    elevation: 2
    background: "white"
    padding: "lg"
```

**Step 1: Restaurant Information (Enhanced)**

```yaml
RestaurantInfoStep:
  hero_section:
    title: "Tell us about your restaurant"
    subtitle: "We'll help you get set up in just a few minutes"
    illustration: 'restaurant-setup.svg'

  form_sections:
    - basic_info:
        fields:
          - name:
              type: 'text'
              label: 'Restaurant Name'
              required: true
              validation: 'real-time'
              help_text: 'This will appear on customer receipts and QR menus'
              max_length: 50

          - description:
              type: 'textarea'
              label: 'Brief Description'
              max_length: 160
              help_text: 'Help customers know what to expect (optional)'
              counter: true

    - location_info:
        title: "Where are you located?"
        fields:
          - address:
              type: 'address_input'
              label: 'Restaurant Address'
              autocomplete: true
              help_text: 'We\'ll use this for delivery integrations'

    - contact_info:
        title: "How can customers reach you?"
        layout: 'two-column-responsive'
        fields:
          - phone:
              type: 'phone'
              label: 'Phone Number'
              country_code: '+91'
              validation: 'international'

          - email:
              type: 'email'
              label: 'Restaurant Email'
              validation: 'real-time'

    - cuisine_info:
        title: "What type of cuisine do you serve?"
        layout: 'visual-cards'
        fields:
          - cuisine_type:
              type: 'single_select_cards'
              options:
                - {value: 'indian', label: 'Indian', icon: '🍛'}
                - {value: 'chinese', label: 'Chinese', icon: '🥢'}
                - {value: 'italian', label: 'Italian', icon: '🍝'}
                # ... more options with visual icons

          - dining_style:
              type: 'single_select_cards'
              options:
                - {value: 'casual', label: 'Casual Dining', description: 'Relaxed atmosphere, table service'}
                - {value: 'fine', label: 'Fine Dining', description: 'Upscale experience, full service'}
                # ... more options
```

**Step 2: Owner Information (Security-Focused)**

```yaml
OwnerInfoStep:
  hero_section:
    title: "Create your owner account"
    subtitle: "This will be your admin access to manage everything"
    security_badge: "🔒 Bank-level security"

  form_sections:
    - personal_info:
        fields:
          - owner_name:
              type: "text"
              label: "Your Full Name"
              required: true
              autocomplete: "name"

    - account_security:
        title: "Account Security"
        fields:
          - email:
              type: "email"
              label: "Email Address"
              required: true
              validation: "real-time"
              help_text: "This will be your login username"

          - password:
              type: "password_with_strength"
              label: "Password"
              required: true
              strength_meter: true
              requirements:
                - min_length: 8
                - uppercase: true
                - lowercase: true
                - number: true
                - special: true
              help_text: "Choose a strong password to protect your business"

          - confirm_password:
              type: "password"
              label: "Confirm Password"
              required: true
              validation: "matches_password"
```

**Step 3: Business Verification (Trust-Building)**

```yaml
BusinessVerificationStep:
  hero_section:
    title: "Verify your business"
    subtitle: "Help us keep the platform secure for everyone"
    trust_indicators:
      - "✅ 256-bit SSL encryption"
      - "✅ GDPR compliant"
      - "✅ PCI DSS certified"

  verification_options:
    - document_upload:
        title: "Business Documents"
        description: "Upload any business registration document"
        accepted_formats: ["PDF", "JPG", "PNG"]
        max_size: "10MB"
        drag_drop: true
        camera_capture: true # Mobile

    - business_details:
        fields:
          - business_registration_number:
              type: "text"
              label: "Registration Number (optional)"
              help_text: "GST, CIN, or other business registration"

          - years_in_business:
              type: "select"
              label: "Years in Business"
              options: ["New Business", "1-2 years", "3-5 years", "5+ years"]
```

**Step 4: Review & Launch (Excitement Building)**

```yaml
ReviewStep:
  hero_section:
    title: "You're almost ready! 🎉"
    subtitle: "Review your information and launch your digital restaurant"

  review_sections:
    - restaurant_summary:
        type: "info_card"
        editable: true

    - owner_summary:
        type: "info_card"
        editable: true

    - next_steps_preview:
        title: "What happens next?"
        timeline:
          - {
              step: 1,
              title: "Account created instantly",
              duration: "30 seconds",
            }
          - {
              step: 2,
              title: "Generate your first QR codes",
              duration: "2 minutes",
            }
          - { step: 3, title: "Set up your menu", duration: "10 minutes" }
          - {
              step: 4,
              title: "Start serving customers!",
              duration: "Ready to go",
            }
```

### 2. Modern SaaS Dashboard

**Enhanced Dashboard Layout:**

```yaml
RestaurantDashboard:
  layout: "sidebar-main-content"

  header:
    height: 64px
    background: "white"
    elevation: 1
    elements:
      - logo: { position: "left", size: "medium" }
      - breadcrumbs: { position: "center" }
      - user_menu: { position: "right" }
      - notifications: { position: "right", badge: true }

  sidebar:
    width: 256px
    background: "neutral.900"
    theme: "dark"
    navigation:
      - { icon: "dashboard", label: "Dashboard", route: "/dashboard" }
      - { icon: "qr_code", label: "QR Codes", route: "/qr-codes" }
      - { icon: "restaurant_menu", label: "Menu", route: "/menu" }
      - { icon: "people", label: "Staff", route: "/staff" }
      - { icon: "analytics", label: "Analytics", route: "/analytics" }
      - { icon: "settings", label: "Settings", route: "/settings" }

  main_content:
    padding: "xxl"

    welcome_section:
      greeting: "Good morning, [Owner Name]! ☀️"
      restaurant_status: "online | offline | setup_needed"
      quick_stats: ["today_orders", "active_tables", "online_customers"]

    overview_cards:
      layout: "responsive_grid"
      cards:
        - today_performance:
            title: "Today's Performance"
            metrics:
              - { label: "Orders", value: "23", change: "+15%" }
              - { label: "Revenue", value: "₹2,340", change: "+8%" }
              - { label: "Customers", value: "45", change: "+12%" }
            chart_type: "sparkline"

        - active_tables:
            title: "Table Status"
            visual: "table_map"
            summary: "3 occupied, 7 available"

        - recent_orders:
            title: "Recent Orders"
            list_type: "timeline"
            max_items: 5

        - qr_performance:
            title: "QR Code Scans"
            metrics:
              - { label: "Today", value: "67" }
              - { label: "This Week", value: "342" }
            chart_type: "mini_bar"
```

### 3. Advanced Settings Interface

**5-Tab Settings Design:**

```yaml
SettingsInterface:
  layout: "tab_navigation"

  tab_bar:
    style: "pills" # Instead of underline
    position: "top_sticky"
    background: "white"
    elevation: 1

  tabs:
    - general:
        icon: "settings"
        label: "General"
        sections:
          - restaurant_profile:
              title: "Restaurant Profile"
              description: "Basic information about your restaurant"
              fields: [...] # Enhanced versions of existing fields

          - location_settings:
              title: "Location & Contact"
              features:
                - google_maps_integration: true
                - delivery_radius_selector: true
                - multiple_locations_support: false # Future feature

    - hours:
        icon: "schedule"
        label: "Hours"
        layout: "visual_weekly_calendar"
        features:
          - drag_to_set_hours: true
          - special_hours_overlay: true # Holidays, events
          - timezone_support: true
          - break_times: true

    - financial:
        icon: "payments"
        label: "Financial"
        sections:
          - pricing_currency:
              default_currency: "INR"
              decimal_places: 2

          - taxes_charges:
              gst_rate: { type: "percentage", default: 18 }
              service_charge: { type: "percentage", optional: true }
              delivery_fee: { type: "amount", optional: true }

          - payment_methods:
              cash: { enabled: true, default: true }
              upi: { enabled: true, qr_code: "auto_generate" }
              cards: { enabled: false, requires_gateway: true }

    - operations:
        icon: "business"
        label: "Operations"
        sections:
          - service_model:
              type: "radio_cards"
              options:
                - self_service: "Customers order and pay themselves"
                - staff_assisted: "Staff take orders, customers pay"
                - full_service: "Staff handle everything"

          - order_management:
              auto_accept_orders: { type: "toggle", default: false }
              order_preparation_time:
                { type: "duration", default: "15 minutes" }
              max_orders_per_hour: { type: "number", optional: true }

          - notifications:
              new_order_sound: { type: "toggle", default: true }
              email_notifications: { type: "toggle", default: true }
              sms_notifications: { type: "toggle", default: false }

    - branding:
        icon: "palette"
        label: "Branding"
        sections:
          - logo_management:
              upload_area: "drag_drop_with_preview"
              formats: ["PNG", "JPG", "SVG"]
              recommendations: "Square format, 512x512px minimum"

          - color_theme:
              primary_color: "color_picker_with_presets"
              secondary_color: "color_picker_with_presets"
              accent_color: "color_picker_with_presets"
              preview: "live_menu_preview"

          - menu_styling:
              font_family: "dropdown_with_preview"
              header_style: "style_selector"
              card_style: "style_selector"
```

---

## 📋 Responsive Design Breakpoints

```yaml
breakpoints:
  mobile: "320px - 767px"
  tablet: "768px - 1023px"
  desktop: "1024px - 1439px"
  large_desktop: "1440px+"

responsive_behavior:
  registration_wizard:
    mobile: "single_column, full_screen"
    tablet: "centered_card, 600px_max_width"
    desktop: "centered_card, 640px_max_width"

  dashboard:
    mobile: "bottom_navigation, collapsible_sidebar"
    tablet: "side_navigation, overlay_sidebar"
    desktop: "side_navigation, persistent_sidebar"

  settings:
    mobile: "accordion_tabs, single_column"
    tablet: "horizontal_tabs, two_column_forms"
    desktop: "horizontal_tabs, three_column_layout"
```

---

## ♿ Accessibility Specifications

```yaml
accessibility_features:
  keyboard_navigation:
    - tab_order: "logical_flow"
    - focus_indicators: "high_contrast_outline"
    - skip_links: "main_content, navigation"

  screen_reader_support:
    - alt_text: "all_images_and_icons"
    - aria_labels: "all_interactive_elements"
    - semantic_markup: "proper_heading_hierarchy"

  visual_accessibility:
    - color_contrast: "WCAG_AA_compliant"
    - font_scaling: "up_to_200_percent"
    - color_independence: "no_color_only_information"

  motor_accessibility:
    - touch_targets: "minimum_44px"
    - click_tolerance: "generous_margins"
    - alternative_inputs: "voice_control_support"
```

---

## 🎭 Micro-Interactions & Animations

```yaml
animations:
  duration_scale:
    instant: "0ms"
    fast: "150ms"
    normal: "250ms"
    slow: "400ms"

  easing_curves:
    standard: "cubic-bezier(0.4, 0.0, 0.2, 1)"
    decelerate: "cubic-bezier(0.0, 0.0, 0.2, 1)"
    accelerate: "cubic-bezier(0.4, 0.0, 1, 1)"

  interactive_feedback:
    button_press:
      scale: "0.98"
      duration: "fast"
      easing: "standard"

    card_hover:
      elevation: "level_2"
      duration: "normal"
      easing: "decelerate"

    form_field_focus:
      border_color: "primary.600"
      border_width: "2px"
      duration: "fast"

  state_transitions:
    step_progression:
      type: "slide_left"
      duration: "normal"
      stagger: "50ms"

    loading_states:
      skeleton: "shimmer_effect"
      spinner: "circular_progress"

    success_feedback:
      checkmark: "scale_bounce"
      color_change: "success.600"
      duration: "slow"
```

---

## 🚨 Error Handling & Empty States

```yaml
error_handling:
  form_validation:
    real_time: true
    error_position: "below_field"
    error_color: "error.600"
    error_icon: "warning_amber"

  network_errors:
    toast_notification: true
    retry_button: true
    offline_indicator: true

  empty_states:
    illustration: "custom_svg"
    heading: "encouraging_tone"
    action_button: "primary_cta"

example_empty_states:
  no_staff_members:
    illustration: "team-illustration.svg"
    title: "Build your team"
    description: "Add staff members to help manage your restaurant"
    action: "Add First Team Member"

  no_menu_items:
    illustration: "menu-illustration.svg"
    title: "Your menu awaits"
    description: "Start building your digital menu to attract customers"
    action: "Add Menu Items"
```

---

## 🔧 Implementation Notes

### Flutter/Material Design 3 Integration

```yaml
flutter_implementation:
  theme_data:
    use_material_3: true
    color_scheme: "custom_zergo_scheme"
    typography: "material_2022"

  custom_widgets:
    - ZergoCard: "elevated_card_with_padding"
    - ZergoButton: "material_3_button_with_custom_colors"
    - ZergoTextField: "outlined_field_with_validation"
    - ZergoStepIndicator: "custom_progress_indicator"

  animation_library:
    - flutter_animate: "^4.5.0"
    - rive: "^0.12.0" # For complex illustrations
```

### Development Priorities

1. **Phase 1**: Enhanced Registration Wizard
2. **Phase 2**: Improved Dashboard Layout
3. **Phase 3**: Advanced Settings Interface
4. **Phase 4**: Micro-interactions & Polish
5. **Phase 5**: Accessibility Audit & Improvements

---

## 📊 Success Metrics

```yaml
success_metrics:
  conversion_rates:
    registration_completion: "target: >85%"
    step_1_to_2: "target: >95%"
    step_2_to_3: "target: >90%"
    step_3_to_4: "target: >95%"

  usability_metrics:
    time_to_complete_registration: "target: <5 minutes"
    settings_task_completion: "target: >90%"
    mobile_usability_score: "target: >4.5/5"

  accessibility_metrics:
    wcag_compliance_score: "target: 100%"
    keyboard_navigation_success: "target: 100%"
    screen_reader_compatibility: "target: 100%"
```

---

## 🎨 Design Assets Needed

```yaml
design_assets:
  illustrations:
    - restaurant_setup_hero.svg
    - business_verification.svg
    - success_celebration.svg
    - empty_state_team.svg
    - empty_state_menu.svg

  icons:
    - cuisine_type_icons: ["🍛", "🥢", "🍝", "🌮", "🍜", "🍱", "🍔", "🥗"]
    - dining_style_icons: [custom svg icons for each style]

  animations:
    - loading_spinner.json (Lottie)
    - success_checkmark.json (Lottie)
    - step_transition.riv (Rive)
```

This comprehensive design system provides a roadmap for creating a world-class restaurant registration experience that rivals the best SaaS onboarding flows in the industry while maintaining accessibility and mobile-first principles.

---

## 🔧 Flutter Component Implementation Guide

### Enhanced Registration Step Indicator

```dart
class ZergoStepIndicator extends StatelessWidget {
  final int currentStep;
  final int totalSteps;
  final List<String> stepLabels;

  const ZergoStepIndicator({
    super.key,
    required this.currentStep,
    required this.totalSteps,
    required this.stepLabels,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
      child: Row(
        children: List.generate(totalSteps, (index) {
          final isCompleted = index < currentStep;
          final isActive = index == currentStep;

          return Expanded(
            child: Row(
              children: [
                _buildStepCircle(context, index, isCompleted, isActive),
                if (index < totalSteps - 1)
                  Expanded(
                    child: _buildStepConnector(context, isCompleted),
                  ),
              ],
            ),
          );
        }),
      ),
    );
  }

  Widget _buildStepCircle(BuildContext context, int index, bool isCompleted, bool isActive) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Column(
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: isCompleted
              ? const Color(0xFF2E7D32) // success.600
              : isActive
                ? colorScheme.primary
                : const Color(0xFFBDBDBD), // neutral.400
            boxShadow: isActive ? [
              BoxShadow(
                color: colorScheme.primary.withOpacity(0.3),
                blurRadius: 8,
                spreadRadius: 2,
              )
            ] : null,
          ),
          child: Icon(
            isCompleted ? Icons.check : Icons.circle,
            color: Colors.white,
            size: 16,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          stepLabels[index],
          style: theme.textTheme.labelSmall?.copyWith(
            color: isActive ? colorScheme.primary : const Color(0xFF757575),
            fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildStepConnector(BuildContext context, bool isCompleted) {
    return Container(
      height: 2,
      margin: const EdgeInsets.only(bottom: 24),
      decoration: BoxDecoration(
        color: isCompleted
          ? const Color(0xFF2E7D32)
          : const Color(0xFFEEEEEE),
        borderRadius: BorderRadius.circular(1),
      ),
    );
  }
}
```

### Enhanced Form Field Component

```dart
class ZergoTextField extends StatefulWidget {
  final String label;
  final String? hintText;
  final String? helpText;
  final String? initialValue;
  final bool required;
  final int maxLines;
  final int? maxLength;
  final TextInputType? keyboardType;
  final String? Function(String?)? validator;
  final void Function(String)? onChanged;
  final Widget? prefixIcon;
  final Widget? suffixIcon;
  final bool showCounter;

  const ZergoTextField({
    super.key,
    required this.label,
    this.hintText,
    this.helpText,
    this.initialValue,
    this.required = false,
    this.maxLines = 1,
    this.maxLength,
    this.keyboardType,
    this.validator,
    this.onChanged,
    this.prefixIcon,
    this.suffixIcon,
    this.showCounter = false,
  });

  @override
  State<ZergoTextField> createState() => _ZergoTextFieldState();
}

class _ZergoTextFieldState extends State<ZergoTextField> {
  late final TextEditingController _controller;
  String? _errorText;
  bool _hasFocus = false;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.initialValue);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Label with required indicator
        if (widget.label.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: RichText(
              text: TextSpan(
                text: widget.label,
                style: theme.textTheme.labelLarge?.copyWith(
                  color: const Color(0xFF212121),
                ),
                children: widget.required ? [
                  TextSpan(
                    text: ' *',
                    style: TextStyle(color: colorScheme.error),
                  ),
                ] : null,
              ),
            ),
          ),

        // Text field
        Focus(
          onFocusChange: (hasFocus) {
            setState(() {
              _hasFocus = hasFocus;
            });
          },
          child: TextFormField(
            controller: _controller,
            maxLines: widget.maxLines,
            maxLength: widget.maxLength,
            keyboardType: widget.keyboardType,
            decoration: InputDecoration(
              hintText: widget.hintText,
              prefixIcon: widget.prefixIcon,
              suffixIcon: widget.suffixIcon,
              filled: true,
              fillColor: Colors.white,
              counterText: widget.showCounter ? null : '',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Color(0xFFEEEEEE)),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Color(0xFFEEEEEE)),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: colorScheme.primary, width: 2),
              ),
              errorBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: colorScheme.error),
              ),
              focusedErrorBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: colorScheme.error, width: 2),
              ),
            ),
            validator: widget.validator,
            onChanged: (value) {
              if (widget.validator != null) {
                final error = widget.validator!(value);
                setState(() {
                  _errorText = error;
                });
              }
              widget.onChanged?.call(value);
            },
          ),
        ),

        // Help text and error
        if (widget.helpText != null || _errorText != null)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (_errorText != null)
                  Icon(
                    Icons.error_outline,
                    size: 16,
                    color: colorScheme.error,
                  ),
                if (_errorText != null)
                  const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    _errorText ?? widget.helpText!,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: _errorText != null
                        ? colorScheme.error
                        : const Color(0xFF757575),
                    ),
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
```

### Card-Based Selection Component

```dart
class ZergoSelectionCard<T> extends StatelessWidget {
  final T value;
  final T? groupValue;
  final String title;
  final String? description;
  final String? emoji;
  final Widget? icon;
  final void Function(T?)? onChanged;

  const ZergoSelectionCard({
    super.key,
    required this.value,
    required this.groupValue,
    required this.title,
    this.description,
    this.emoji,
    this.icon,
    this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isSelected = value == groupValue;

    return GestureDetector(
      onTap: () => onChanged?.call(value),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isSelected ? colorScheme.primaryContainer : Colors.white,
          border: Border.all(
            color: isSelected
              ? colorScheme.primary
              : const Color(0xFFEEEEEE),
            width: isSelected ? 2 : 1,
          ),
          borderRadius: BorderRadius.circular(12),
          boxShadow: isSelected ? [
            BoxShadow(
              color: colorScheme.primary.withOpacity(0.1),
              blurRadius: 8,
              spreadRadius: 0,
              offset: const Offset(0, 2),
            ),
          ] : null,
        ),
        child: Row(
          children: [
            // Icon or emoji
            if (emoji != null)
              Text(
                emoji!,
                style: const TextStyle(fontSize: 24),
              ),
            if (icon != null)
              icon!,
            if (emoji != null || icon != null)
              const SizedBox(width: 12),

            // Content
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: theme.textTheme.titleMedium?.copyWith(
                      color: isSelected
                        ? colorScheme.onPrimaryContainer
                        : const Color(0xFF212121),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  if (description != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      description!,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: isSelected
                          ? colorScheme.onPrimaryContainer.withOpacity(0.8)
                          : const Color(0xFF757575),
                      ),
                    ),
                  ],
                ],
              ),
            ),

            // Selection indicator
            AnimatedScale(
              scale: isSelected ? 1.0 : 0.0,
              duration: const Duration(milliseconds: 150),
              child: Icon(
                Icons.check_circle,
                color: colorScheme.primary,
                size: 24,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

### Enhanced Dashboard Overview Card

```dart
class ZergoDashboardCard extends StatelessWidget {
  final String title;
  final String? subtitle;
  final List<DashboardMetric> metrics;
  final Widget? chart;
  final List<DashboardAction>? actions;
  final bool isLoading;

  const ZergoDashboardCard({
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
    final theme = Theme.of(context);

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: Color(0xFFEEEEEE)),
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
                        style: theme.textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      if (subtitle != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          subtitle!,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: const Color(0xFF757575),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),

                // Actions dropdown
                if (actions != null)
                  PopupMenuButton<DashboardAction>(
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

            const SizedBox(height: 20),

            // Content
            if (isLoading)
              const _LoadingSkeleton()
            else ...[
              // Metrics
              if (metrics.isNotEmpty)
                _buildMetricsRow(context, metrics),

              // Chart
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

  Widget _buildMetricsRow(BuildContext context, List<DashboardMetric> metrics) {
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
                  color: const Color(0xFF757575),
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
                          ? const Color(0xFFE8F5E8)
                          : const Color(0xFFFFEBEE),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        metric.change!,
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: metric.isPositiveChange
                            ? const Color(0xFF2E7D32)
                            : const Color(0xFFD32F2F),
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
}

class DashboardMetric {
  final String label;
  final String value;
  final String? change;
  final bool isPositiveChange;

  const DashboardMetric({
    required this.label,
    required this.value,
    this.change,
    this.isPositiveChange = true,
  });
}

class DashboardAction {
  final String label;
  final VoidCallback onTap;

  const DashboardAction({
    required this.label,
    required this.onTap,
  });
}

class _LoadingSkeleton extends StatelessWidget {
  const _LoadingSkeleton();

  @override
  Widget build(BuildContext context) {
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
                    color: const Color(0xFFF5F5F5),
                    borderRadius: BorderRadius.circular(6),
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  height: 24,
                  width: 80,
                  decoration: BoxDecoration(
                    color: const Color(0xFFF5F5F5),
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
```

## 📱 Mobile-First Implementation Examples

### Responsive Layout Helper

```dart
class ResponsiveLayout extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;

  const ResponsiveLayout({
    super.key,
    required this.mobile,
    this.tablet,
    this.desktop,
  });

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;

    if (screenWidth >= 1024 && desktop != null) {
      return desktop!;
    } else if (screenWidth >= 768 && tablet != null) {
      return tablet!;
    } else {
      return mobile;
    }
  }
}
```

---

## 🎨 UI Mockup Specifications

### Registration Flow Screens

**Screen 1: Welcome & Restaurant Info**

```
┌─────────────────────────────────────────┐
│ ← Back              ZERGO QR     Skip → │
├─────────────────────────────────────────┤
│                                         │
│        🏪 Restaurant Setup              │
│                                         │
│  ● ────── ○ ────── ○ ────── ○          │
│  Info   Owner   Details  Review         │
│                                         │
│   Tell us about your restaurant         │
│   We'll help you get set up in just     │
│   a few minutes                         │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Restaurant Name *                   │ │
│ │ [Your restaurant name here______]   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Brief Description                   │ │
│ │ [Help customers know what to...___] │ │
│ │ [________________________       ] │ │
│ │ [________________________       ] │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ What type of cuisine do you serve?      │
│                                         │
│ [🍛 Indian  ] [🥢 Chinese ] [🍝 Italian] │
│ [🌮 Mexican ] [🍜 Thai    ] [🍱 Japanese]│
│                                         │
│ ┌─────────────────┬─────────────────────┐│
│ │ [  Previous   ] │ [     Next →     ] ││
│ └─────────────────┴─────────────────────┘│
└─────────────────────────────────────────┘
```

**Screen 2: Owner Account Setup**

```
┌─────────────────────────────────────────┐
│ ← Back              ZERGO QR            │
├─────────────────────────────────────────┤
│                                         │
│        🔒 Create Your Account           │
│                                         │
│  ● ────── ● ────── ○ ────── ○          │
│  Info   Owner   Details  Review         │
│                                         │
│   This will be your admin access       │
│   🛡️ Bank-level security                │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Your Full Name *                    │ │
│ │ [John Smith___________________]     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Email Address * (Login username)    │ │
│ │ [john@restaurant.com__________] ✓   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Password *                          │ │
│ │ [●●●●●●●●●●●●●●●●●●●●●●●●●] 👁️     │ │
│ │ ████████████████░░░░ Strong         │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ✅ 8+ characters  ✅ Uppercase          │
│ ✅ Lowercase     ✅ Number              │
│ ✅ Special char                         │
│                                         │
│ ┌─────────────────┬─────────────────────┐│
│ │ [  ← Previous ] │ [     Next →     ] ││
│ └─────────────────┴─────────────────────┘│
└─────────────────────────────────────────┘
```

**Screen 3: Business Verification**

```
┌─────────────────────────────────────────┐
│ ← Back              ZERGO QR            │
├─────────────────────────────────────────┤
│                                         │
│        📋 Verify Your Business          │
│                                         │
│  ● ────── ● ────── ● ────── ○          │
│  Info   Owner   Details  Review         │
│                                         │
│   Help us keep the platform secure     │
│   ✅ 256-bit SSL  ✅ GDPR ✅ PCI DSS    │
│                                         │
│ Upload Business Documents               │
│ ┌─────────────────────────────────────┐ │
│ │ 📎 Drag & drop files here           │ │
│ │                                     │ │
│ │         📄 📸                       │ │
│ │    or choose files                  │ │
│ │                                     │ │
│ │ PDF, JPG, PNG • Max 10MB            │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Business Details (Optional)             │
│ ┌─────────────────────────────────────┐ │
│ │ Registration Number                 │ │
│ │ [GST, CIN, or other registration] │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Years in Business                   │ │
│ │ [3-5 years ▼               ]      │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────┬─────────────────────┐│
│ │ [  ← Previous ] │ [     Next →     ] ││
│ └─────────────────┴─────────────────────┘│
└─────────────────────────────────────────┘
```

**Screen 4: Review & Launch**

```
┌─────────────────────────────────────────┐
│ ← Back              ZERGO QR            │
├─────────────────────────────────────────┤
│                                         │
│        🎉 You're almost ready!          │
│                                         │
│  ● ────── ● ────── ● ────── ●          │
│  Info   Owner   Details  Review         │
│                                         │
│   Review your information and launch    │
│   your digital restaurant               │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 🏪 Spice Garden Restaurant      ✏️ │ │
│ │ 📍 Mumbai, Maharashtra             │ │
│ │ 🍛 Indian • Casual Dining          │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 👤 John Smith (Owner)           ✏️ │ │
│ │ 📧 john@spicegarden.com            │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ What happens next?                      │
│ 1⃣ Account created instantly (30s)      │
│ 2⃣ Generate QR codes (2 min)            │
│ 3⃣ Set up your menu (10 min)           │
│ 4⃣ Start serving customers! 🚀          │
│                                         │
│ ┌─────────────────┬─────────────────────┐│
│ │ [  ← Previous ] │ [🚀 Launch Setup!] ││
│ └─────────────────┴─────────────────────┘│
└─────────────────────────────────────────┘
```

### Dashboard Layout Mockup

**Main Dashboard Screen**

```
┌─────────────────────────────────────────┐
│ ☰ ZERGO QR          🔔 👤 John Smith    │
├─────────────────────────────────────────┤
│ 📊 Dashboard                            │
│ 📋 QR Codes                            │
│ 🍽️ Menu                                │
│ 👥 Staff                               │
│ 📈 Analytics                           │
│ ⚙️ Settings                            │
├─────────────────────────────────────────┤
│ Good morning, John! ☀️                  │
│ Spice Garden Restaurant                 │
│                                         │
│ ┌─────────┬─────────┬─────────┬───────┐ │
│ │Today's Performance         │ Status │ │
│ ├─────────┼─────────┼─────────┤       │ │
│ │Orders   │Revenue  │Customers│ 🟢    │ │
│ │   23    │ ₹2,340  │   45    │Online │ │
│ │  +15%   │   +8%   │  +12%   │       │ │
│ └─────────┴─────────┴─────────┴───────┘ │
│                                         │
│ ┌─────────────────┬─────────────────────┐ │
│ │ Table Status    │ QR Code Scans      │ │
│ │                 │                    │ │
│ │ [T1][T2][T3]    │      67            │ │
│ │ [T4][T5][T6]    │     Today          │ │
│ │ [T7][T8][T9]    │                    │ │
│ │                 │     342            │ │
│ │ 3 occupied      │   This Week        │ │
│ │ 7 available     │ ▅▆▇█▆▅▄           │ │
│ └─────────────────┴─────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Quick Actions                       │ │
│ │                                     │ │
│ │ [📋 View Menu] [🔗 Generate QR]     │ │
│ │ [👥 Add Staff] [📊 View Analytics]  │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Settings Interface Mockup

**Tabbed Settings Layout**

```
┌─────────────────────────────────────────┐
│ ← Settings           ZERGO QR           │
├─────────────────────────────────────────┤
│ [General] [Hours] [Financial] [Operations] [Branding]
├─────────────────────────────────────────┤
│ Restaurant Profile                      │
│ Basic information about your restaurant │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Restaurant Name                     │ │
│ │ [Spice Garden Restaurant_______]    │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Description                         │ │
│ │ [Authentic Indian cuisine with___] │ │
│ │ [traditional recipes and modern__] │ │
│ │ [presentation__________________ ] │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Location & Contact                      │
│ ┌─────────────────┬─────────────────────┐ │
│ │ Phone Number    │ Email Address      │ │
│ │ [+91 98765___]  │ [contact@spice___] │ │
│ └─────────────────┴─────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 📍 Restaurant Address               │ │
│ │ [123 MG Road, Bandra West_______] │ │
│ │ [Mumbai, Maharashtra 400050_____] │ │
│ │                    [🗺️ View Map] │ │
│ └─────────────────────────────────────┘ │
│                                         │
│               [💾 Save Changes]          │
└─────────────────────────────────────────┘
```

---

## 🔄 Interaction Patterns & Micro-animations

### Form Validation States

```yaml
validation_feedback:
  on_focus:
    - border_color: primary.600
    - border_width: 2px
    - animation: smooth_border_transition (150ms)

  on_valid_input:
    - show_checkmark: right_side_icon
    - border_color: success.600
    - animation: scale_bounce (200ms)

  on_error:
    - border_color: error.600
    - shake_animation: 3_oscillations (300ms)
    - error_message: slide_down (150ms)
    - error_icon: warning_outline

  on_typing:
    - real_time_validation: debounced (500ms)
    - character_counter: animate_on_change
    - password_strength: live_update
```

### Step Transitions

```yaml
step_progression:
  forward_transition:
    - current_step: slide_out_left (250ms)
    - new_step: slide_in_right (250ms)
    - step_indicator: progress_fill_animation (300ms)
    - page_background: subtle_color_shift (400ms)

  backward_transition:
    - current_step: slide_out_right (250ms)
    - new_step: slide_in_left (250ms)
    - step_indicator: progress_unfill (200ms)

  completion_celebration:
    - success_checkmark: scale_bounce (500ms)
    - confetti_animation: particle_system (2000ms)
    - success_message: fade_in_scale (300ms)
```

### Button Interactions

```yaml
button_states:
  rest_state:
    - elevation: 0
    - background: primary.600
    - text_color: white

  hover_state: # Desktop
    - elevation: 2
    - background: primary.700
    - animation: elevation_rise (150ms)

  pressed_state:
    - scale: 0.98
    - elevation: 0
    - animation: press_feedback (100ms)

  loading_state:
    - spinner: circular_progress
    - text: fade_out (200ms)
    - disable_interaction: true

  success_state:
    - background: success.600
    - icon: checkmark_scale_in
    - haptic_feedback: light_impact
```

### Card Hover Effects

```yaml
card_interactions:
  selection_cards:
    rest_state:
      - elevation: 0
      - border: neutral.200
      - scale: 1.0

    hover_state:
      - elevation: 1
      - border: primary.300
      - scale: 1.02
      - animation: lift_and_glow (200ms)

    selected_state:
      - elevation: 2
      - border: primary.600 (2px)
      - background: primary.50
      - checkmark: scale_bounce_in

  dashboard_cards:
    hover_state:
      - elevation: 4
      - animation: smooth_lift (250ms)
      - metrics: subtle_highlight
```

---

## ♿ Enhanced Accessibility Features

### Screen Reader Optimization

```yaml
semantic_markup:
  registration_wizard:
    - step_indicator:
        role: "progressbar"
        aria_valuenow: current_step
        aria_valuemax: total_steps
        aria_label: "Registration progress, step {current} of {total}"

    - form_sections:
        role: "group"
        aria_labelledby: section_heading_id

    - required_fields:
        aria_required: "true"
        aria_describedby: "field_help_text error_message"

    - error_messages:
        role: "alert"
        aria_live: "polite"

  dashboard:
    - metric_cards:
        role: "region"
        aria_label: "{metric_name} is {value} with {change} change"

    - interactive_elements:
        aria_expanded: true/false
        aria_controls: related_element_id
```

### Keyboard Navigation

```yaml
keyboard_support:
  tab_order:
    - registration_flow: logical_form_progression
    - dashboard: left_to_right_top_to_bottom
    - settings: tab_navigation_first_then_content

  custom_shortcuts:
    - "Ctrl/Cmd + Enter": submit_current_step
    - "Escape": close_modal_or_go_back
    - "Arrow Keys": navigate_between_options
    - "Space": select_current_option
    - "Enter": activate_current_button

  focus_management:
    - trap_focus: within_modals_and_dropdowns
    - restore_focus: after_modal_close
    - skip_links: to_main_content
    - visible_focus_indicators: high_contrast_outline
```

### Visual Accessibility

```yaml
color_contrast:
  text_on_background:
    - body_text: 7:1 (AAA)
    - headings: 7:1 (AAA)
    - secondary_text: 4.5:1 (AA)

  interactive_elements:
    - buttons: 4.5:1 (AA)
    - links: 4.5:1 (AA)
    - form_controls: 3:1 (AA)

  state_indicators:
    - error_states: 4.5:1 (AA)
    - success_states: 4.5:1 (AA)
    - warning_states: 4.5:1 (AA)

font_scaling:
  support_range: 100% to 200%
  layout_behavior: graceful_reflow
  text_truncation: avoid_information_loss

color_blindness:
  not_color_only: use_icons_and_patterns
  error_indicators: combine_color_with_symbols
  status_indicators: use_shapes_and_text
```

---

## 📊 Performance Optimization

### Loading States & Skeleton Screens

```yaml
loading_strategies:
  registration_form:
    - initial_load: show_skeleton_form
    - step_transition: crossfade_with_shimmer
    - image_upload: progress_bar_with_preview

  dashboard:
    - metric_cards: skeleton_with_animation
    - charts: placeholder_shapes
    - recent_activity: skeleton_list_items

  settings:
    - form_data: shimmer_text_blocks
    - image_previews: skeleton_rectangles
```

### Progressive Loading

```yaml
progressive_enhancement:
  critical_path: 1. basic_layout_and_structure
    2. primary_text_content
    3. form_inputs_and_buttons
    4. secondary_ui_elements
    5. animations_and_polish

  lazy_loading:
    - non_critical_images: intersection_observer
    - charts_and_graphs: viewport_based
    - secondary_form_sections: on_demand
```

This comprehensive design specification provides everything needed to implement a world-class restaurant registration and management experience that rivals the best SaaS platforms while maintaining the Flutter/Material Design 3 foundation already established in your codebase.

```

```
