# ZERGO QR - Story 2.1 Restaurant Onboarding Design Specification

**Comprehensive Restaurant Registration & Setup Experience**

---

## 📋 Executive Summary

This document defines the complete UI/UX design specification for restaurant onboarding and initial setup experience in the ZERGO QR platform. Building upon the established Material Design 3 + ZERGO brand system, this specification delivers a world-class onboarding experience that guides restaurant owners from initial registration through full platform activation with confidence, clarity, and professional polish.

## 🎯 Design Goals

- **Frictionless Registration**: Complete restaurant setup in under 15 minutes with intuitive step-by-step guidance
- **Professional Trust Building**: Enterprise-grade interface that establishes credibility and confidence
- **Contextual Help System**: Provide the right assistance at exactly the right moment
- **Mobile-First Excellence**: Seamless experience across all devices with touch-optimized interactions
- **Business Intelligence Integration**: Smart suggestions based on restaurant type and location
- **Error-Free Setup**: Comprehensive validation and clear error prevention throughout the process

---

## 🎨 Enhanced Visual Design System

### Onboarding-Specific Color Extensions

```yaml
# Onboarding Progress Colors
onboarding_progress:
  completed_step:
    background: "#E8F5E8" # success.50
    border: "#2E7D32" # success.600
    text: "#1B5E20" # success.800
    checkmark: "#4CAF50"

  active_step:
    background: "#E3F2FD" # primary.50
    border: "#1976D2" # primary.600
    text: "#0D47A1" # primary.900
    glow: "rgba(25, 118, 210, 0.2)"

  pending_step:
    background: "#F5F5F5" # neutral.100
    border: "#E0E0E0" # neutral.300
    text: "#757575" # neutral.600

# Input Field States
input_states:
  valid:
    border: "#2E7D32"
    background: "#E8F5E8"
    icon: "#4CAF50"

  invalid:
    border: "#D32F2F"
    background: "#FFEBEE"
    icon: "#F44336"

  focused:
    border: "#1976D2"
    background: "#FFFFFF"
    shadow: "0 0 0 4px rgba(25, 118, 210, 0.1)"

# Success Celebration Colors
celebration:
  primary: "#4CAF50"
  secondary: "#8BC34A"
  accent: "#FFD54F"
  confetti: ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"]
```

### Enhanced Typography for Onboarding

```yaml
# Onboarding-Specific Typography Scale
onboarding_typography:
  hero_title:
    size: 32px
    weight: 600
    line_height: 1.2
    letter_spacing: -0.5px
    color: "neutral.900"

  hero_subtitle:
    size: 18px
    weight: 400
    line_height: 1.5
    color: "neutral.600"

  step_title:
    size: 20px
    weight: 600
    line_height: 1.3
    color: "neutral.900"

  step_description:
    size: 16px
    weight: 400
    line_height: 1.5
    color: "neutral.600"

  form_label:
    size: 14px
    weight: 500
    line_height: 1.4
    color: "neutral.700"

  input_placeholder:
    size: 16px
    weight: 400
    line_height: 1.5
    color: "neutral.400"

  helper_text:
    size: 12px
    weight: 400
    line_height: 1.4
    color: "neutral.500"

  success_message:
    size: 14px
    weight: 500
    line_height: 1.4
    color: "success.700"

  error_message:
    size: 14px
    weight: 500
    line_height: 1.4
    color: "error.700"
```

---

## 📱 Comprehensive Onboarding Flow Design

### Step 1: Restaurant Information (Enhanced)

**Layout Strategy:** Centered card with full-width mobile adaptation

```yaml
step_1_restaurant_info:
  layout: "centered_card_with_progress"
  max_width: "640px"
  background: "gradient(primary.50 -> neutral.50)"

  header_section:
    hero_content:
      title: "Welcome to ZERGO QR! 🎉"
      subtitle: "Let's set up your restaurant in just a few minutes"
      illustration: "restaurant-welcome-illustration.svg"
      trust_indicators:
        - "✅ 10,000+ restaurants trust ZERGO"
        - "🔒 Bank-level security"
        - "⚡ Setup in under 15 minutes"

    step_progress:
      type: "connected_dots"
      steps: 4
      current_step: 1
      animation: "smooth_fill_progress"

  form_sections:
    restaurant_identity:
      title: "Tell us about your restaurant"
      description: "This information helps customers find and recognize your restaurant"

      fields:
        - restaurant_name:
            type: "enhanced_text_input"
            label: "Restaurant Name"
            placeholder: "Enter your restaurant name"
            validation: "real_time_duplicate_check"
            max_length: 50
            character_counter: true
            helper_text: "This appears on customer receipts and QR menus"
            icon: "storefront"
            focus_animation: "border_glow"

        - restaurant_type:
            type: "visual_selection_cards"
            label: "Restaurant Type"
            options:
              - value: "casual_dining"
                label: "Casual Dining"
                description: "Relaxed atmosphere, table service"
                icon: "🍽️"
                color: "primary"
              - value: "quick_service"
                label: "Quick Service"
                description: "Fast food, counter service"
                icon: "🍔"
                color: "warning"
              - value: "fine_dining"
                label: "Fine Dining"
                description: "Upscale experience, full service"
                icon: "🥂"
                color: "success"
              - value: "cafe"
                label: "Cafe"
                description: "Coffee shop, light meals"
                icon: "☕"
                color: "secondary"
            selection_animation: "scale_and_shadow"
            multi_select: false

    location_information:
      title: "Where are you located?"
      description: "Help customers find you and enable delivery options"

      fields:
        - restaurant_address:
            type: "smart_address_input"
            label: "Restaurant Address"
            placeholder: "Start typing your address..."
            google_maps_integration: true
            autocomplete: true
            validation: "address_format_check"
            map_preview: true
            helper_text: "Used for delivery radius and customer navigation"

        - contact_information:
            type: "two_column_responsive"
            fields:
              - phone:
                  type: "international_phone"
                  label: "Phone Number"
                  country_code: "+91"
                  validation: "phone_format"
                  format: "mobile_friendly"
              - email:
                  type: "enhanced_email"
                  label: "Restaurant Email"
                  validation: "real_time_email_check"
                  helper_text: "For order confirmations and business updates"

    cuisine_information:
      title: "What type of cuisine do you serve?"
      description: "Select all that apply to help customers discover your restaurant"

      fields:
        - primary_cuisine:
            type: "multi_select_with_search"
            label: "Primary Cuisines"
            options:
              - { value: "indian", label: "Indian", icon: "🍛" }
              - { value: "chinese", label: "Chinese", icon: "🥢" }
              - { value: "italian", label: "Italian", icon: "🍝" }
              - { value: "mexican", label: "Mexican", icon: "🌮" }
              - { value: "thai", label: "Thai", icon: "🍜" }
              - { value: "japanese", label: "Japanese", icon: "🍱" }
              - { value: "american", label: "American", icon: "🍔" }
              - { value: "mediterranean", label: "Mediterranean", icon: "🥗" }
              - { value: "french", label: "French", icon: "🥐" }
              - { value: "korean", label: "Korean", icon: "🍲" }
            max_selections: 3
            search_enabled: true
            visual_cards: true

        - dietary_focus:
            type: "badge_selection"
            label: "Dietary Focus (Optional)"
            options:
              - { value: "vegetarian", label: "Vegetarian-Friendly", color: "success" }
              - { value: "vegan", label: "Vegan Options", color: "success" }
              - { value: "gluten_free", label: "Gluten-Free", color: "warning" }
              - { value: "halal", label: "Halal", color: "info" }
              - { value: "organic", label: "Organic", color: "success" }
            multi_select: true
            optional: true
```

**Mobile Layout Adaptation:**
```yaml
mobile_adaptations:
  layout: "full_screen_scroll"
  form_columns: 1
  hero_section: "compact_with_progress_top"
  input_fields: "enhanced_touch_targets"
  visual_cards: "larger_tap_areas"
  keyboard_avoidance: "intelligent_scroll_adjustment"
```

### Step 2: Owner Account Setup (Security-Focused)

**Layout Strategy:** Security-emphasized design with trust indicators

```yaml
step_2_owner_account:
  layout: "centered_card_with_security_focus"
  max_width: "600px"
  background: "neutral.50"

  header_section:
    hero_content:
      title: "Create your owner account"
      subtitle: "This will be your admin access to manage everything"
      security_badge: "🔒 Bank-level security"
      trust_indicators:
        - "256-bit SSL encryption"
        - "GDPR compliant"
        - "PCI DSS certified"
        - "SOC 2 Type II certified"

    step_progress:
      type: "security_emphasized"
      current_step: 2

  form_sections:
    personal_information:
      title: "Your Personal Information"
      description: "Your account details for secure access"

      fields:
        - owner_name:
            type: "enhanced_text_input"
            label: "Your Full Name"
            placeholder: "Enter your full name"
            validation: "name_format_check"
            icon: "person"
            helper_text: "This will appear on business documents"

        - professional_title:
            type: "enhanced_text_input"
            label: "Professional Title"
            placeholder: "e.g., Owner, Manager, Chef"
            validation: "optional"
            helper_text: "Helps us personalize your experience"

    account_security:
      title: "Account Security"
      description: "Create a strong password to protect your business"

      fields:
        - email_address:
            type: "enhanced_email"
            label: "Email Address"
            placeholder: "your.email@restaurant.com"
            validation: "real_time_email_check"
            helper_text: "This will be your login username"
            availability_check: true

        - password:
            type: "password_with_strength_meter"
            label: "Password"
            placeholder: "Create a strong password"
            strength_meter:
              enabled: true
              requirements:
                - { type: "length", min: 8, message: "8+ characters" }
                - { type: "uppercase", required: true, message: "Uppercase letter" }
                - { type: "lowercase", required: true, message: "Lowercase letter" }
                - { type: "number", required: true, message: "Number" }
                - { type: "special", required: true, message: "Special character" }
            visibility_toggle: true
            helper_text: "Choose a strong password to protect your business"

        - confirm_password:
            type: "password_with_validation"
            label: "Confirm Password"
            validation: "password_match_check"
            match_target: "password"
            helper_text: "Re-enter your password to confirm"

    security_options:
      title: "Additional Security (Recommended)"
      description: "Add extra layers of protection for your account"

      fields:
        - two_factor_auth:
            type: "toggle_switch"
            label: "Enable Two-Factor Authentication"
            description: "Require code verification for new logins"
            default_value: true
            benefit_badge: "Recommended"

        - session_management:
            type: "radio_group"
            label: "Session Management"
            options:
              - value: "auto_logout"
                label: "Auto-logout after inactivity"
                description: "Secure option for shared devices"
              - value: "remember_me"
                label: "Remember this device"
                description: "Convenient for private devices"
            default_value: "remember_me"
```

### Step 3: Business Verification (Trust-Building)

**Layout Strategy:** Professional verification with clear privacy assurances

```yaml
step_3_business_verification:
  layout: "centered_card_with_trust_focus"
  max_width: "680px"
  background: "neutral.50"

  header_section:
    hero_content:
      title: "Verify your business"
      subtitle: "Help us keep the platform secure for everyone"
      trust_badge: "🛡️ Your information is secure and encrypted"
      privacy_note: "We only use your information for verification purposes"

    step_progress:
      current_step: 3
      completion_percentage: 75

  verification_sections:
    document_upload:
      title: "Business Document Upload"
      description: "Upload any business registration document to verify your restaurant"

      upload_area:
        type: "advanced_drag_drop"
        accepted_formats: ["PDF", "JPG", "JPEG", "PNG"]
        max_file_size: "10MB"
        max_files: 3
        drag_instructions: "Drag & drop files here or click to browse"
        camera_capture: true
        file_preview: true
        upload_progress: true
        validation: "document_quality_check"

      document_types:
        suggested:
          - "Business Registration Certificate"
          - "FSSAI License"
          - "GST Registration"
          - "Shop & Establishment License"
          - "Trade License"
          - "Partnership Deed"
          - "MOA/AOA"

    business_details:
      title: "Business Details (Optional but Recommended)"
      description: "Additional information helps us personalize your experience"

      fields:
        - registration_number:
            type: "enhanced_text_input"
            label: "Business Registration Number"
            placeholder: "GSTIN, CIN, or other registration"
            optional: true
            helper_text: "Helps with faster verification"
            format_examples:
              - "GSTIN: 27ABCDE1234F1ZV"
              - "CIN: U12345MH2023PTC123456"

        - business_type:
            type: "selection_dropdown"
            label: "Business Structure"
            options:
              - { value: "proprietorship", label: "Proprietorship" }
              - { value: "partnership", label: "Partnership" }
              - { value: "llp", label: "Limited Liability Partnership" }
              - { value: "private_limited", label: "Private Limited Company" }
              - { value: "public_limited", label: "Public Limited Company" }
            default_value: "proprietorship"

        - years_in_business:
            type: "selection_slider"
            label: "How long have you been in business?"
            min: 0
            max: 50
            step: 1
            value_display: "years"
            default_value: 2
            helper_text: "This helps us suggest relevant features"

        - estimated_monthly_revenue:
            type: "range_slider"
            label: "Estimated Monthly Revenue"
            ranges:
              - { min: 0, max: 50000, label: "Under ₹50K" }
              - { min: 50000, max: 200000, label: "₹50K - ₹2L" }
              - { min: 200000, max: 1000000, label: "₹2L - ₹10L" }
              - { min: 1000000, max: 10000000, label: "₹10L+" }
            optional: true
            helper_text: "Helps us suggest appropriate pricing plans"

    verification_summary:
      title: "Verification Status"
      real_time_updates: true

      status_indicators:
        - documents_uploaded:
            label: "Documents Uploaded"
            status: "pending"
            icon: "upload_file"
        - information_complete:
            label: "Information Complete"
            status: "pending"
            icon: "check_circle"
        - verification_in_progress:
            label: "Verification Progress"
            status: "pending"
            icon: "hourglass_top"
        - estimated_completion:
            label: "Estimated Completion"
            value: "2-24 hours"
            icon: "schedule"
```

### Step 4: Review & Launch (Excitement Building)

**Layout Strategy:** Celebration-focused review with clear next steps

```yaml
step_4_review_launch:
  layout: "centered_card_with_celebration"
  max_width: "720px"
  background: "gradient(success.50 -> primary.50)"

  header_section:
    hero_content:
      title: "🎉 You're all set to launch!"
      subtitle: "Review your information and start serving customers"
      celebration_animation: "confetti_burst"
      completion_badge: "Setup Complete"

    step_progress:
      type: "completion_emphasized"
      all_steps_completed: true
      completion_percentage: 100

  review_sections:
    restaurant_summary:
      title: "Restaurant Information"
      type: "editable_info_card"
      editable: true

      fields_displayed:
        - name: "Restaurant Name"
        - address: "Address"
        - phone: "Phone"
        - email: "Email"
        - cuisine: "Cuisine Type"
        - type: "Restaurant Type"
      edit_button: "✏️ Edit"

    owner_summary:
      title: "Owner Account"
      type: "editable_info_card"
      editable: true

      fields_displayed:
        - name: "Your Name"
        - email: "Email Address"
        - two_factor: "Two-Factor Authentication"
      edit_button: "✏️ Edit"

    business_summary:
      title: "Business Details"
      type: "info_card"

      fields_displayed:
        - verification_status: "Verification Status"
        - registration_number: "Registration Number"
        - business_type: "Business Structure"
        - years_in_business: "Years in Business"

    next_steps_preview:
      title: "What happens next?"
      type: "timeline_preview"
      animation: "sequential_appear"

      steps:
        - step: 1
          title: "Account Created Instantly"
          duration: "30 seconds"
          icon: "✅"
          description: "Your account is ready to use"
        - step: 2
          title: "Generate Your First QR Codes"
          duration: "2 minutes"
          icon: "📱"
          description: "Create QR codes for your tables"
        - step: 3
          title: "Set Up Your Menu"
          duration: "10 minutes"
          icon: "📋"
          description: "Add your menu items and pricing"
        - step: 4
          title: "Add Staff Members"
          duration: "5 minutes"
          icon: "👥"
          description: "Invite your team to join"
        - step: 5
          title: "Start Serving Customers!"
          duration: "Ready to go"
          icon: "🚀"
          description: "Your restaurant is live"

    launch_options:
      title: "Choose How to Start"
      type: "selection_cards"

      options:
        - quick_start:
            title: "Quick Start"
            description: "Generate QR codes and go live immediately"
            recommended: true
            icon: "⚡"
            next_action: "Generate QR Codes"

        - guided_setup:
            title: "Guided Setup"
            description: "Follow step-by-step tutorial with expert assistance"
            icon: "🧭"
            next_action: "Start Tutorial"

        - advanced_setup:
            title: "Advanced Setup"
            description: "Configure all features before going live"
            icon: "⚙️"
            next_action: "Advanced Configuration"
```

---

## 📱 Responsive Design Breakpoints

### Mobile-First Strategy (320px - 767px)

```yaml
mobile_onboarding:
  layout: "full_screen_cards"
  navigation: "bottom_progress_bar"
  input_fields: "enhanced_touch_targets_44px"
  keyboard_handling: "intelligent_scroll_adjustment"

  step_indicators:
    type: "horizontal_dots"
    position: "top"
    size: "large_touch_targets"

  form_layout:
    columns: 1
    field_spacing: "24px"
    section_spacing: "32px"
    button_height: "56px"
    text_size: "enhanced_readability"

  file_upload:
    camera_first: true
    drag_drop: "simplified"
    preview_size: "full_width"

  visual_elements:
    icons: "large_24px"
    illustrations: "optimized_for_mobile"
    animations: "performance_optimized"
```

### Tablet Enhancement (768px - 1023px)

```yaml
tablet_onboarding:
  layout: "centered_card_with_sidebar"
  max_width: "640px"

  step_indicators:
    type: "horizontal_steps_with_labels"
    position: "top"
    detailed_labels: true

  form_layout:
    columns: 2
    field_spacing: "20px"
    section_spacing: "40px"

  file_upload:
    drag_drop: "enhanced"
    preview_grid: "2x2"
    side_panel: "file_details"

  advanced_features:
    - real_time_validation
    - progress_indicators
    - contextual_help
    - keyboard_shortcuts
```

### Desktop Power-User (1024px+)

```yaml
desktop_onboarding:
  layout: "centered_card_with_wings"
  max_width: "640px"

  step_indicators:
    type: "connected_lines_with_progress"
    position: "top"
    interactive_states: true

  form_layout:
    columns: "responsive_2-3"
    field_spacing: "16px"
    section_spacing: "32px"

  file_upload:
    drag_drop: "advanced"
    preview_grid: "3x3"
    bulk_operations: true
    file_management: true

  professional_features:
    - auto_save_progress
    - keyboard_navigation
    - screen_reader_support
    - high_contrast_mode
    - multiple_language_support
```

---

## 🔄 Advanced Interaction Patterns

### Form Validation & Feedback

```yaml
validation_system:
  real_time_validation:
    debounce: "300ms"
    inline_feedback: true
    error_prevention: true
    success_indicators: true

  visual_feedback:
    valid_input:
      border_color: "success.600"
      background: "success.50"
      icon: "check_circle"
      animation: "fade_in_scale"

    invalid_input:
      border_color: "error.600"
      background: "error.50"
      icon: "error_outline"
      animation: "shake_then_fade"

    loading_state:
      border_color: "primary.600"
      background: "neutral.50"
      icon: "hourglass_empty"
      animation: "rotating"

  error_handling:
    prevention: true
    clear_messaging: true
    recovery_guidance: true
    contextual_help: true
```

### Progress Tracking

```yaml
progress_system:
  step_progress:
    visual_type: "connected_progress_bar"
    completion_animation: "smooth_fill"
    accessibility_labels: true
    keyboard_navigation: true

  auto_save:
    interval: "30_seconds"
    indication: "subtle_status_badge"
    recovery: "full_state_restore"

  completion_celebration:
    animation: "confetti_burst"
    sound_feedback: "subtle_success_chime"
    social_sharing: true
```

### File Upload Enhancement

```yaml
file_upload_system:
  drag_drop:
    active_zone: "highlighted_border"
    invalid_types: "red_border_with_shake"
    success_zone: "green_border_with_check"

  upload_progress:
    real_time_updates: true
    pause_resume: true
    cancel_capability: true
    retry_failed_uploads: true

  file_management:
    preview_generation: true
    bulk_operations: true
    file_organization: true
    cloud_backup: true
```

---

## ♿ Accessibility Implementation

### WCAG 2.1 AA Compliance

```yaml
accessibility_features:
  keyboard_navigation:
    tab_order: "logical_flow"
    focus_indicators: "high_contrast"
    skip_links: "to_main_content"
    shortcuts: "customizable"

  screen_reader_support:
    semantic_markup: "proper_html5"
    aria_labels: "all_interactive_elements"
    live_regions: "dynamic_updates"
    heading_structure: "hierarchical"

  visual_accessibility:
    color_contrast: "4.5:1_minimum"
    font_scaling: "up_to_200%"
    focus_management: "predictable"
    color_independence: "icons_plus_text"

  motor_accessibility:
    touch_targets: "44px_minimum"
    click_tolerance: "generous"
    alternative_inputs: "voice_control"
    timing_adjustments: "customizable"
```

### Multi-Language Support

```yaml
internationalization:
  supported_languages: ["English", "Hindi", "Spanish", "French", "German"]
  text_direction: "adaptive_ltr_rtl"
  date_formats: "localization_aware"
  number_formats: "locale_specific"
  currency_formats: "automatic_detection"
```

---

## 🎯 Success Metrics & KPIs

### Onboarding Performance

```yaml
success_metrics:
  completion_rates:
    overall_completion: "target: 85%"
    step_1_to_2: "target: 95%"
    step_2_to_3: "target: 90%"
    step_3_to_4: "target: 95%"
    launch_conversion: "target: 90%"

  time_metrics:
    total_setup_time: "target: <15_minutes"
    average_step_time: "target: <4_minutes"
    document_upload_time: "target: <2_minutes"
    verification_time: "target: <24_hours"

  user_satisfaction:
    ease_of_use: "target: 4.5/5"
    clarity: "target: 4.7/5"
    trust_level: "target: 4.8/5"
    recommendation_score: "target: 85%"

  technical_performance:
    page_load_time: "target: <2_seconds"
    form_response_time: "target: <300ms"
    file_upload_speed: "target: <5_seconds"
    mobile_performance: "target: 60fps"
```

### Business Impact

```yaml
business_metrics:
  customer_acquisition:
    setup_to_first_qr: "target: <30_minutes"
    setup_to_first_order: "target: <2_hours"
    setup_to_first_month_active: "target: 90%"

  operational_efficiency:
    staff_onboarding_time: "target: <10_minutes"
    menu_setup_time: "target: <15_minutes"
    qr_code_generation_time: "target: <2_minutes"

  user_retention:
    day_7_retention: "target: 80%"
    day_30_retention: "target: 70%"
    month_6_retention: "target: 60%"
```

---

## 🚀 Implementation Guidelines

### Flutter Implementation

```dart
// Enhanced Onboarding Step Indicator
class OnboardingStepIndicator extends StatelessWidget {
  final int currentStep;
  final int totalSteps;
  final List<String> stepTitles;

  const OnboardingStepIndicator({
    super.key,
    required this.currentStep,
    required this.totalSteps,
    required this.stepTitles,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
      child: Column(
        children: [
          // Progress bar
          LinearProgressIndicator(
            value: currentStep / totalSteps,
            backgroundColor: Colors.grey.shade300,
            valueColor: AlwaysStoppedAnimation<Color>(
              Colors.green,
            ),
          ),
          const SizedBox(height: 16),
          // Step dots
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: List.generate(totalSteps, (index) {
              final isCompleted = index < currentStep;
              final isActive = index == currentStep;

              return _buildStepDot(
                context,
                index,
                isCompleted,
                isActive,
              );
            }),
          ),
          const SizedBox(height: 8),
          // Step titles
          Text(
            stepTitles[currentStep],
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              color: Colors.blue.shade700,
              fontWeight: FontWeight.w600,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildStepDot(
    BuildContext context,
    int index,
    bool isCompleted,
    bool isActive,
  ) {
    return Column(
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: isCompleted
                ? Colors.green
                : isActive
                    ? Colors.blue
                    : Colors.grey.shade300,
            ),
          child: Icon(
            isCompleted ? Icons.check : Icons.circle,
            color: Colors.white,
            size: 16,
          ),
        ),
      ],
    );
  }
}
```

### Form Validation Component

```dart
class EnhancedFormField extends StatefulWidget {
  final String label;
  final String? hintText;
  final String? helperText;
  final String? errorText;
  final TextEditingController? controller;
  final bool required;
  final TextInputType? keyboardType;
  final String? Function(String?)? validator;
  final VoidCallback? onChanged;
  final Widget? prefixIcon;
  final bool showCharacterCounter;
  final int? maxLength;

  const EnhancedFormField({
    super.key,
    required this.label,
    this.hintText,
    this.helperText,
    this.errorText,
    this.controller,
    this.required = false,
    this.keyboardType,
    this.validator,
    this.onChanged,
    this.prefixIcon,
    this.showCharacterCounter = false,
    this.maxLength,
  });

  @override
  State<EnhancedFormField> createState() => _EnhancedFormFieldState();
}

class _EnhancedFormFieldState extends State<EnhancedFormField> {
  bool _hasFocus = false;
  bool _isValid = false;
  String? _currentError;

  @override
  Widget build(BuildContext context) {
    final hasError = _currentError != null;
    final fieldColor = hasError
        ? Colors.red
        : _hasFocus
            ? Colors.blue
            : Colors.grey.shade600;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Label
        Row(
          children: [
            Text(
              widget.label,
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                color: fieldColor,
                fontWeight: FontWeight.w500,
              ),
            ),
            if (widget.required)
              Text(
                ' *',
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                  color: Colors.red,
                ),
              ),
          ],
        ),
        const SizedBox(height: 8),
        // Text field
        TextFormField(
          controller: widget.controller,
          keyboardType: widget.keyboardType,
          maxLength: widget.maxLength,
          decoration: InputDecoration(
            hintText: widget.hintText,
            prefixIcon: widget.prefixIcon,
            suffixIcon: _isValid
                ? Icon(Icons.check_circle, color: Colors.green)
                : null,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: fieldColor,
                width: hasError ? 2 : 1,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: Colors.blue,
                width: 2,
              ),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: Colors.red,
                width: 2,
              ),
            ),
            filled: true,
            fillColor: hasError
                ? Colors.red.shade50
                : Colors.white,
            counterText: widget.showCharacterCounter ? null : '',
          ),
          validator: widget.validator,
          onChanged: (value) {
            setState(() {
              _currentError = widget.validator?.call(value);
              _isValid = _currentError == null && value.isNotEmpty;
            });
            widget.onChanged?.call(value);
          },
          onTap: () {
            setState(() {
              _hasFocus = true;
            });
          },
          onEditingComplete: () {
            setState(() {
              _hasFocus = false;
            });
          },
        ),
        // Helper text and error
        if (widget.helperText != null || _currentError != null)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Row(
              children: [
                if (_currentError != null)
                  Icon(
                    Icons.error_outline,
                    size: 16,
                    color: Colors.red,
                  ),
                if (_currentError != null)
                  const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    _currentError ?? widget.helperText!,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: _currentError != null
                          ? Colors.red.shade700
                          : Colors.grey.shade600,
                    ),
                  ),
                ),
              ],
            ),
          ),
        // Character counter
        if (widget.showCharacterCounter && widget.maxLength != null)
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Text(
              '${widget.controller?.text.length ?? 0}/${widget.maxLength}',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey.shade500,
              ),
              textAlign: TextAlign.right,
            ),
          ),
      ],
    );
  }
}
```

This comprehensive design specification provides everything needed to implement a world-class restaurant onboarding experience that converts effectively, builds trust, and sets users up for long-term success with the ZERGO QR platform.