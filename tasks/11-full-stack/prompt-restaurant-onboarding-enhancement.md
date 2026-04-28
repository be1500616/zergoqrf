# Task: Enhance ZERGO QR Restaurant Onboarding with Modern SaaS Design & Code Optimization

## Context
You are working on the ZERGO QR restaurant ordering platform's restaurant onboarding system. The current registration flow (`apps/frontend/lib/features/restaurants/presentation/restaurant_registration_screen.dart`) needs to be redesigned with a modern, professional SaaS aesthetic while eliminating code duplication and creating reusable components.

## Current Issues Identified

### Code Duplication Problems:
1. **Form Field Patterns:** Similar text editing patterns repeated across steps
2. **Validation Logic:** Duplicated validation approaches in different widgets
3. **Debounce Patterns:** Similar async validation implementations
4. **UI Components:** Repeated card layouts and button patterns
5. **State Management:** Similar reactive patterns across step widgets

### UX/UI Issues:
1. **Linear Flow:** Restrictive step-by-step process
2. **Visual Appeal:** Basic Material Design without modern aesthetics
3. **Trust Building:** Missing professional validation elements
4. **Mobile Experience:** Not optimized for mobile onboarding
5. **Progress Feedback:** Limited sense of achievement and progress

## Design Requirements

### Overall Architecture: Component-Based Design

**Core Principle:** Create a reusable onboarding framework that can be adapted for different user types (restaurants, staff, customers).

**File Structure:**
```
lib/shared/onboarding/
├── widgets/
│   ├── onboarding_step_base.dart          # Base class for all steps
│   ├── responsive_form_layout.dart       # Responsive form container
│   ├── validation_field.dart             # Self-validating form field
│   ├── progress_indicator.dart           # Enhanced progress tracking
│   └── trust_indicators.dart             # Professional trust elements
├── components/
│   ├── animated_input_field.dart         # Animated text input
│   ├── availability_checker.dart         # Reusable availability validation
│   ├── password_strength_meter.dart      # Password strength indicator
│   ├── image_upload_widget.dart          # Image upload with preview
│   └── business_hours_selector.dart      # Interactive hours selection
├── mixins/
│   ├── validation_mixin.dart             # Common validation logic
│   ├── animation_mixin.dart              # Shared animation patterns
│   └── debounce_mixin.dart               # Reusable debounce functionality
└── utils/
    ├── form_validator.dart               # Centralized validation rules
    ├── onboarding_animator.dart          # Shared animation controllers
    └── responsive_helper.dart            # Responsive design utilities
```

### Enhanced Registration Flow Architecture

**New Approach:** Tab-based + Linear Hybrid
- **Desktop:** Side-by-side with tab navigation and visual progress
- **Mobile:** Stacked with swipeable cards and bottom navigation
- **Smart Progress:** Auto-save and resume from any section
- **Quick Start:** Option to fill minimum info and complete later

### Modern Visual Design System

**Layout Structure:**
- **Desktop (> 1024px):** 40/60 split (visual panel + form)
- **Tablet (768px - 1024px):** 30/70 split with collapsible visual
- **Mobile (< 768px):** Full-width with slide-up panels

**Visual Panel Enhancement:**
```dart
// Create reusable visual panel component
class RestaurantOnboardingVisual extends StatelessWidget {
  final OnboardingStep currentStep;
  final double completionPercentage;

  // Features:
  // - Dynamic content based on current step
  // - Progress animation with percentage
  // - Trust indicators (security badges, testimonials)
  // - Feature highlights with icons
  // - Professional restaurant imagery
}
```

**Form Panel Enhancement:**
```dart
// Create reusable form container
class ResponsiveOnboardingForm extends StatelessWidget {
  final List<OnboardingStep> steps;
  final int currentStepIndex;
  final Function(int) onStepChanged;

  // Features:
  // - Adaptive layout for different screen sizes
  // - Tab navigation for desktop
  // - Swipe gestures for mobile
  // - Auto-save functionality
  // - Progress persistence
}
```

## Component Library: Reusable Onboarding Elements

### 1. Base Step Class
```dart
abstract class OnboardingStepBase extends StatefulWidget {
  // Common interface for all onboarding steps
  // Shared validation logic
  // Common animation patterns
  // Auto-save functionality
}
```

### 2. Self-Validating Form Fields
```dart
class ValidationField<T> extends StatefulWidget {
  final String label;
  final T? initialValue;
  final Validator<T>? validator;
  final AsyncValidator<T>? asyncValidator;
  final ValueChanged<T>? onChanged;
  final Widget? suffixIcon;
  final String? helperText;
  final bool required;

  // Features:
  // - Built-in validation with visual feedback
  // - Async validation with loading states
  // - Debounced validation for performance
  // - Accessibility support
  // - Consistent styling
}
```

### 3. Enhanced Progress System
```dart
class OnboardingProgressIndicator extends StatelessWidget {
  final List<OnboardingStep> steps;
  final int currentStep;
  final Map<int, bool> stepCompletion;
  final Function(int)? onStepTapped;

  // Features:
  // - Visual progress with completion percentage
  // - Clickable steps for navigation
  // - Animated transitions
  // - Mobile-friendly touch targets
  // - Achievement celebrations
}
```

### 4. Trust Building Components
```dart
class TrustIndicators extends StatelessWidget {
  // Security badges
  // Customer testimonials
  // Statistics (restaurants served, orders processed)
  // Professional certifications
  // Social proof elements
}
```

## Enhanced Onboarding Steps

### Step 1: Restaurant Profile (Enhanced)
**Current:** `restaurant_info_step.dart`
**Improvements:**
- Use `ValidationField` components for all inputs
- Implement image upload with logo preview
- Add restaurant type selection with visual cards
- Include location autocomplete
- Real-time name availability with improved UX
- Cuisine type multi-select with chips
- Professional photo gallery upload

### Step 2: Owner Information (Streamlined)
**Current:** `owner_info_step.dart`
**Improvements:**
- Social login options (Google, Microsoft)
- Progressive profiling (basic info first, details later)
- Password strength meter with visual feedback
- Phone verification with international formatting
- Document upload with drag-and-drop
- Digital signature capability

### Step 3: Business Configuration (Simplified)
**Current:** `business_details_step.dart`
**Improvements:**
- Template-based setup (quick start options)
- Interactive business hours selector
- Service model selection with icons
- Payment setup wizard
- Staff invitation system
- QR code generation preview

### Step 4: Launch Preparation (New)
**Features:**
- Menu import wizard (CSV, PDF, manual)
- Table layout designer
- Staff role assignment
- Test order simulation
- Launch checklist
- Marketing materials generator

## Code Optimization Strategies

### 1. Mixin-Based Shared Functionality
```dart
mixin ValidationMixin<T extends StatefulWidget> on State<T> {
  // Common validation patterns
  // Error message display
  // Form state management
}

mixin DebounceMixin<T extends StatefulWidget> on State<T> {
  // Reusable debounce functionality
  // Timer management
  // Performance optimization
}

mixin AnimationMixin<T extends StatefulWidget> on State<T> {
  // Shared animation controllers
  // Common transition patterns
  // Performance optimization
}
```

### 2. Controller Composition
```dart
class OnboardingController extends GetxController {
  late final RegistrationController registration;
  late final ValidationController validation;
  late final AnimationController animation;
  late final ProgressController progress;

  // Coordinated state management
  // Cross-step validation
  // Auto-save functionality
}
```

### 3. Theme Integration
```dart
class OnboardingTheme {
  // Consistent styling across all onboarding flows
  // Restaurant-specific color palette
  // Typography system
  // Spacing constants
  // Animation definitions
}
```

## Implementation Guidelines

### Responsive Design Requirements
- **Mobile First:** Design for mobile, enhance for desktop
- **Touch Targets:** Minimum 44dp for all interactive elements
- **Keyboard Navigation:** Full keyboard support
- **Screen Reader Support:** Semantic HTML and ARIA labels
- **High Contrast:** Support for high contrast mode

### Performance Optimization
- **Lazy Loading:** Load step content on demand
- **Image Optimization:** WebP format, progressive loading
- **Animation Performance:** 60fps target, GPU acceleration
- **State Management:** Efficient reactive patterns
- **Memory Management:** Proper disposal of controllers

### Accessibility Standards
- **WCAG AA Compliance:** 4.5:1 contrast ratio minimum
- **Keyboard Accessibility:** Full keyboard navigation
- **Screen Reader Support:** Proper labels and announcements
- **Focus Management:** Logical focus flow
- **Error Prevention:** Clear error messages and recovery

### Testing Strategy
- **Unit Tests:** All validation logic and utilities
- **Widget Tests:** Component rendering and interactions
- **Integration Tests:** Complete onboarding flow
- **Accessibility Tests:** Screen reader and keyboard navigation
- **Performance Tests:** Load times and animation performance

## Deliverables

### Phase 1: Foundation Components (Week 1)
1. **Base Architecture:**
   - `OnboardingStepBase` abstract class
   - `ValidationField` reusable component
   - `ResponsiveFormLayout` container
   - Shared mixins for validation and animation

2. **Theme System:**
   - `OnboardingTheme` for consistent styling
   - Restaurant-specific color palette
   - Typography and spacing system
   - Animation definitions

3. **Progress System:**
   - Enhanced progress indicator
   - Step completion tracking
   - Achievement celebrations
   - Mobile-friendly navigation

### Phase 2: Step Enhancements (Week 2)
1. **Restaurant Profile Step:**
   - Implement with new component system
   - Add image upload functionality
   - Enhanced validation and UX
   - Mobile optimization

2. **Owner Information Step:**
   - Social login integration
   - Password strength meter
   - Document upload system
   - Progressive profiling

### Phase 3: Advanced Features (Week 3)
1. **Business Configuration:**
   - Template-based setup
   - Interactive selectors
   - Payment integration
   - Staff management

2. **Launch Preparation:**
   - Menu import wizard
   - Table layout designer
   - Test order simulation
   - Marketing materials

### Phase 4: Polish & Testing (Week 4)
1. **Animation & Transitions:**
   - Smooth step transitions
   - Micro-interactions
   - Loading states
   - Error recovery

2. **Testing & Optimization:**
   - Complete test suite
   - Performance optimization
   - Accessibility validation
   - Cross-browser testing

## Success Metrics

### Code Quality Metrics
- **Code Duplication Reduction:** 70% reduction in duplicated code
- **Component Reusability:** 80% of UI components reusable
- **Test Coverage:** 90%+ test coverage for new components
- **Performance:** < 2 second load time for onboarding flow

### User Experience Metrics
- **Completion Rate:** Increase from 60% to 85%
- **Time to Complete:** Reduce from 15 minutes to 8 minutes
- **Error Rate:** Reduce form errors by 50%
- **User Satisfaction:** 4.5+ star rating

### Business Impact Metrics
- **Setup Time:** Reduce restaurant setup time by 60%
- **Support Tickets:** Reduce onboarding support tickets by 40%
- **Feature Adoption:** Increase advanced feature usage by 30%
- **Retention:** Improve 30-day retention by 25%

## Implementation Checklist

### Pre-Development
- [ ] Review existing codebase for patterns to extract
- [ ] Design component architecture
- [ ] Define validation rules and patterns
- [ ] Create design system specifications
- [ ] Set up testing framework

### Development
- [ ] Implement base classes and mixins
- [ ] Create reusable form components
- [ ] Build responsive layout system
- [ ] Develop animation framework
- [ ] Integrate theme system

### Integration
- [ ] Refactor existing steps to use new components
- [ ] Implement new onboarding features
- [ ] Add responsive design
- [ ] Integrate with existing controllers
- [ ] Add error handling and recovery

### Testing
- [ ] Unit tests for all components
- [ ] Widget tests for UI interactions
- [ ] Integration tests for complete flow
- [ ] Accessibility testing
- [ ] Performance testing

### Deployment
- [ ] Code review and optimization
- [ ] Documentation updates
- [ ] Migration strategy
- [ ] Monitoring setup
- [ ] Rollback plan

## Maintenance & Future Development

### Component Maintenance
- Regular updates to design system
- Performance monitoring
- Bug fixes and improvements
- New feature additions

### Extensibility
- Support for new user types
- Additional onboarding flows
- Internationalization support
- Advanced customization options

### Analytics & Improvement
- User behavior tracking
- A/B testing framework
- Performance monitoring
- Feedback collection system

---

This comprehensive prompt focuses on creating a modern, professional restaurant onboarding experience while eliminating code duplication through a well-architected component system. The approach emphasizes reusability, maintainability, and exceptional user experience following modern SaaS design patterns.