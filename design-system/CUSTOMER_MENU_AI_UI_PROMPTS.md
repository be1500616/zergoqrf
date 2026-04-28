# AI UI Generation Prompts - Customer-Facing Menu Interface

**Optimized prompts for implementing the ZERGO QR customer menu interface in Flutter**

---

## 🚀 Quick Start Prompts

### 1. Complete Customer Ordering System
```
Create a complete customer-facing restaurant ordering system in Flutter with Material Design 3.

Requirements:
- Mobile-first design (320px-767px) with responsive tablet support (768px+)
- 3-second load time goal with skeleton screens and progressive loading
- 2-minute order completion flow for first-time users
- Full WCAG 2.1 AA accessibility compliance
- Multi-restaurant brand adaptation (colors, fonts, logos)

Core Screens:
1. Restaurant Landing - Welcome screen with table info
2. Menu Categories - Visual category grid with search
3. Menu Items Grid - Item cards with images and quick add
4. Item Details Modal - Full product information with customization
5. Shopping Cart - Order review with real-time updates
6. Payment Processing - Multiple payment methods with security
7. Order Confirmation - Receipt with real-time tracking

Key Features:
- Real-time cart updates with haptic feedback
- Image lazy loading with blur-up effect
- Swipe gestures for item removal
- Offline mode with cached menu data
- Pull-to-refresh functionality
- Progressive Web App (PWA) support

Color System:
- Primary background: #FFFFFF
- Surface: #FAFAFA
- Accent (CTAs): #2E7D32 (ZERGO green)
- Price highlight: #1565C0
- Success: #4CAF50
- Error: #F44336

Use GetX for state management, implement proper error handling, and ensure 60fps animations throughout.
```

### 2. Restaurant Landing Page with Brand Adaptation
```
Create a Flutter restaurant landing page that adapts to any restaurant's branding while maintaining ZERGO design standards.

Requirements:
- Dynamic brand colors injection (primary, secondary, accent)
- Restaurant logo integration with fallback handling
- Hero image gallery with restaurant's signature dishes
- Welcome message with table number display
- Quick stats: rating, cuisine type, estimated wait time
- Auto-advance to menu after 3 seconds unless user interacts

Layout Structure:
- Safe area padding for notches and rounded corners
- Flexible space for restaurant hero image (16:9 aspect ratio)
- Bottom section with restaurant information and CTAs
- Floating action button for quick menu access

Components:
- HeroImageGallery with swipe gestures
- RestaurantInfoCard with dynamic branding
- QuickActionButtons for "View Menu" and "Call Waiter"
- TableIndicator showing current table number
- TrustBadges for security and verification

Animation Requirements:
- Smooth fade-in animations (300ms, ease-out-cubic)
- Parallax effect on hero image scroll
- Auto-advance countdown animation
- Button press feedback with scale animations

Use MediaQuery for safe areas, implement proper image caching, and support dark mode adaptation.
```

### 3. Interactive Menu Grid with Performance Optimization
```
Create a high-performance menu items grid in Flutter optimized for restaurant browsing with 100+ menu items.

Requirements:
- 2-column responsive grid (adaptive to screen size)
- Item cards with high-quality images and lazy loading
- Real-time search and filtering functionality
- Quick add buttons with haptic feedback
- Infinite scroll with loading indicators
- Skeleton screen placeholders for loading states

Grid Layout:
- Cross-axis count: 2 (mobile), 3 (tablet), 4 (desktop)
- Child aspect ratio: 0.8 (portrait cards)
- Cross-axis spacing: 12px, Main-axis spacing: 16px
- Padding: 16px edges

Item Card Components:
- NetworkImage with placeholder and error handling
- Item title (18px, 500 weight)
- Price (16px, 600 weight, accent color)
- Dietary indicators (vegetarian, spicy, etc.)
- Quick add button (40px circular, fixed position)
- Badge system for popular/recommended items

Performance Features:
- Image caching with cached_network_image
- Lazy loading beyond visible items
- Debounced search input (300ms delay)
- Efficient list view with ListView.builder
- Memory optimization for large menus

Interaction Patterns:
- Card press animation with scale and elevation changes
- Quick add button with bounce animation
- Haptic feedback on add to cart
- Swipe-to-dismiss for filtering
- Pull-to-refresh with custom indicator

Implement with GetX for state management, ensure 60fps scroll performance, and add comprehensive error handling.
```

---

## 📱 Component-Specific Prompts

### 4. Item Details Modal with Customization
```
Create a full-screen item details modal in Flutter for restaurant menu items with extensive customization options.

Requirements:
- Full-screen modal with swipe-to-dismiss gesture
- Image gallery with pinch-to-zoom functionality
- Detailed item information with ingredients and allergens
- Dynamic customization options based on item type
- Real-time price calculation with modifications
- Add to cart functionality with quantity selection

Modal Structure:
- Custom app bar with transparent background
- Hero image gallery with smooth transitions
- Scrollable content area with item details
- Fixed bottom action bar with price and add button

Content Sections:
- Item name and description (typography hierarchy)
- Dietary indicators and allergen warnings
- Ingredients list with expandable details
- Customization options grouped by type
- Nutritional information (expandable)

Customization System:
- Single choice options (radio buttons)
- Multiple choice options (checkboxes)
- Text inputs for special instructions
- Quantity selectors with +/- buttons
- Price impact display for each option

Implementation Details:
- PageView for image gallery
- ExpansionTile for collapsible sections
- Custom radio/checkbox components
- Real-time price calculation with GetX
- Smooth animations and transitions

Use Hero animations for image transitions, implement proper modal dismissal handling, and ensure accessibility with semantic labels.
```

### 5. Shopping Cart with Real-time Updates
```
Create a Flutter shopping cart interface for restaurant orders with real-time updates and smooth animations.

Requirements:
- List of ordered items with images and details
- Quantity controls with increment/decrement buttons
- Swipe-to-remove gesture with undo option
- Real-time subtotal calculation
- Special instructions text area
- Promotional code input with validation
- Clear checkout button with order summary

Cart Item Layout:
- Item image (60x60px) on the left
- Item details in center (name, customizations)
- Price and quantity controls on right
- Swipe gesture area for remove action

Quantity Controls:
- Circular buttons (32px) with +/- icons
- Quantity display in center
- Haptic feedback on quantity change
- Animation on quantity update
- Min/max quantity validation

Interactive Features:
- Swipe left to reveal remove button
- Pull-to-refresh for cart updates
- Animated item additions/removals
- Real-time price calculations
- Undo functionality for removed items

Visual Design:
- Card-based layout with subtle shadows
- Smooth slide animations for item changes
- Color changes for price updates
- Loading states for cart operations
- Empty cart state with call-to-action

Implement with GetX reactive programming, add comprehensive error handling, and ensure smooth 60fps animations.
```

### 6. Payment Processing Interface
```
Create a secure and user-friendly payment processing interface in Flutter for restaurant orders.

Requirements:
- Multiple payment methods (credit card, digital wallets, cash)
- Tip calculator with preset percentages
- Order summary review before payment
- Secure payment form with validation
- Processing animation with status updates
- Success confirmation with receipt

Payment Options:
- Credit/debit card input with format masking
- Digital wallet integration (Apple Pay, Google Pay)
- Cash on collection option
- Split payment functionality
- Save card for future orders (secure storage)

Security Features:
- PCI DSS compliant form design
- Card number masking and validation
- CVV input with secure keyboard
- Security badges and trust indicators
- SSL/TLS connection indicators

Tip Calculator:
- Preset percentages (15%, 18%, 20%, 25%)
- Custom tip amount input
- Real-time total calculation
- Tip suggestions based on service type
- Option for no tip

Processing Flow:
- Loading animation during payment processing
- Status updates (processing, confirming, completed)
- Error handling with retry options
- Timeout management
- Success confirmation with receipt display

Use secure form validation, implement proper error handling, and ensure accessibility for all payment methods.
```

---

## 🎨 Theme and Styling Prompts

### 7. Adaptive Restaurant Theme System
```
Create a Flutter theme system that adapts to any restaurant's branding while maintaining ZERGO design consistency.

Requirements:
- Dynamic color scheme injection from restaurant data
- Flexible typography system with restaurant fonts
- Adaptive component styling
- Dark mode support with automatic switching
- Brand consistency across all screens

Theme Structure:
```dart
class RestaurantTheme {
  final Color primaryBrand;
  final Color secondaryBrand;
  final String logoUrl;
  final String primaryFont;
  final String secondaryFont;

  ThemeData toLightTheme() {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryBrand,
        brightness: Brightness.light,
      ),
      // Restaurant-specific customizations
    );
  }

  ThemeData toDarkTheme() {
    // Dark mode adaptation with brand colors
  }
}
```

Dynamic Components:
- Brand-colored buttons with proper contrast
- Adaptive card colors and elevations
- Restaurant-specific accent colors
- Consistent typography with custom fonts
- Flexible spacing system

Color Adaptation:
- Extract brand colors from logo
- Generate complementary color palettes
- Ensure WCAG contrast compliance
- Support light and dark themes
- Handle invalid color inputs gracefully

Implementation:
- Theme extension for custom restaurant properties
- Color utility functions for brand adaptation
- Font loading with fallback mechanisms
- Dynamic theme switching with animations
- Persistent theme preferences

Use ThemeExtension for custom properties, implement proper color contrast validation, and ensure smooth theme transitions.
```

### 8. High-Performance Image System
```
Create a Flutter image loading system optimized for restaurant food photography with performance and visual appeal.

Requirements:
- Progressive JPEG loading with blur-up effect
- Lazy loading for below-fold images
- Image caching with memory management
- Fallback images for network failures
- Zoom functionality for detailed viewing
- WebP format support with fallbacks

Image Loading Strategy:
- Low-quality image placeholders (LQIP)
- Progressive loading with fade-in effect
- Memory-efficient caching with LRU eviction
- Background preloading for next images
- Offline support with cached images

Performance Features:
- CachedNetworkImage for network images
- Custom image loader with retry logic
- Memory monitoring and cleanup
- Image compression and optimization
- Bandwidth-adaptive loading

Visual Enhancements:
- Blur-up effect for smooth loading
- Fade-in animations (400ms, ease-out)
- Placeholder images with branding
- Error images with retry options
- Hero animations for detailed view

Implementation Details:
```dart
class OptimizedNetworkImage extends StatelessWidget {
  final String imageUrl;
  final double? width;
  final double? height;
  final BoxFit fit;

  @override
  Widget build(BuildContext context) {
    return CachedNetworkImage(
      imageUrl: imageUrl,
      placeholder: (context, url) => ImagePlaceholder(),
      errorWidget: (context, url, error) => ImageErrorWidget(),
      memCacheWidth: width?.toInt(),
      memCacheHeight: height?.toInt(),
      fadeInDuration: Duration(milliseconds: 400),
    );
  }
}
```

Use cached_network_image package, implement proper memory management, and add comprehensive error handling.
```

---

## ⚡ Performance and Optimization Prompts

### 9. State Management with GetX Architecture
```
Implement a comprehensive GetX state management architecture for the customer restaurant ordering system.

Required Controllers:
- RestaurantController - restaurant data and theme management
- MenuController - menu items, categories, and search
- CartController - cart operations and calculations
- OrderController - order processing and tracking
- PaymentController - payment processing and validation
- UserController - customer information and preferences

Controller Architecture:
```dart
class RestaurantController extends GetxController {
  final restaurant = Rx<Restaurant?>(null);
  final theme = Rx<RestaurantTheme?>(null);
  final isLoading = false.obs;
  final error = Rx<String?>(null);

  @override
  void onInit() {
    super.onInit();
    loadRestaurantData();
  }

  Future<void> loadRestaurantData() async {
    try {
      isLoading.value = true;
      error.value = null;
      // Load restaurant data from API
      restaurant.value = await apiService.getRestaurant();
      theme.value = RestaurantTheme.fromRestaurant(restaurant.value!);
    } catch (e) {
      error.value = e.toString();
    } finally {
      isLoading.value = false;
    }
  }
}
```

Cart Controller Features:
- Reactive cart items list
- Real-time price calculations
- Quantity management
- Customization handling
- Local storage persistence

Menu Controller Features:
- Search functionality with debouncing
- Category filtering
- Item availability management
- Offline caching
- Real-time updates

Performance Optimizations:
- Lazy loading for large datasets
- Efficient list rendering with ListView.builder
- Memory management for image caching
- Debounced user inputs
- Reactive UI updates with minimal rebuilds

Use GetX reactive programming, implement proper error handling, and ensure efficient memory usage.
```

### 10. Animation and Micro-interactions System
```
Create a comprehensive animation and micro-interaction system for Flutter that enhances the restaurant ordering experience.

Animation Controllers:
- PageTransitionController for screen transitions
- CartAnimationController for cart operations
- ButtonPressController for touch feedback
- LoadingAnimationController for various loading states
- SuccessAnimationController for completion feedback

Key Animations:
- Page transitions with slide and fade effects
- Item add to cart with bounce animation
- Button press feedback with scale effects
- Loading skeletons with shimmer effects
- Success checkmarks with draw animations

Implementation Example:
```dart
class CartAddAnimation extends StatefulWidget {
  final Widget child;
  final VoidCallback onComplete;

  @override
  _CartAddAnimationState createState() => _CartAddAnimationState();
}

class _CartAddAnimationState extends State<CardAddAnimation>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 600),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: 0.8,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.elasticOut,
    ));

    _controller.forward().then((_) => widget.onComplete());
  }
}
```

Micro-interactions:
- Haptic feedback on touch events
- Button state changes with color transitions
- Card lift effects on hover/press
- Smooth scrolling with physics simulation
- Loading progress indicators

Performance Considerations:
- Use AnimationBuilder for optimal performance
- Avoid animating expensive widgets
- Implement proper disposal of animation controllers
- Use hardware acceleration where possible
- Respect reduced motion preferences

Use Flutter's animation system efficiently, implement proper disposal patterns, and ensure 60fps performance.
```

---

## 🔐 Security and Trust Prompts

### 11. Secure Payment Form Implementation
```
Create a secure payment form in Flutter that meets PCI DSS requirements and builds user trust.

Security Requirements:
- PCI DSS compliant form design
- Secure data transmission with HTTPS
- Card number masking and validation
- CVV input with secure keyboard
- No sensitive data storage on device

Form Components:
- Card number input with automatic formatting
- Expiry date with MM/YY validation
- CVV input with masked display
- Cardholder name input
- Save card option (with user consent)

Security Features:
- Real-time card number validation
- Luhn algorithm implementation
- Expiry date validation
- Secure keyboard for sensitive inputs
- Session timeout for inactive forms

Trust Indicators:
- SSL certificate badges
- PCI compliance indicators
- Security seals and badges
- Privacy policy links
- Secure payment icons

Implementation Example:
```dart
class SecurePaymentForm extends StatefulWidget {
  @override
  _SecurePaymentFormState createState() => _SecurePaymentFormState();
}

class _SecurePaymentFormState extends State<SecurePaymentForm> {
  final _formKey = GlobalKey<FormState>();
  final _cardNumberController = TextEditingController();
  final _expiryController = TextEditingController();
  final _cvvController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        children: [
          CardNumberInput(
            controller: _cardNumberController,
            validator: CardNumberValidator.validate,
          ),
          ExpiryInput(
            controller: _expiryController,
            validator: ExpiryValidator.validate,
          ),
          CVVInput(
            controller: _cvvController,
            validator: CVVValidator.validate,
          ),
        ],
      ),
    );
  }
}
```

Use secure input methods, implement proper validation, and ensure PCI compliance throughout.
```

### 12. Offline Mode and Error Handling
```
Implement comprehensive offline mode and error handling for the restaurant ordering system.

Offline Features:
- Cached menu data for offline browsing
- Offline cart management
- Sync when connection restored
- Graceful degradation of features
- Clear offline indicators

Error Handling Strategy:
- Network error detection and recovery
- Retry mechanisms with exponential backoff
- User-friendly error messages
- Fallback options for critical features
- Error reporting and analytics

Implementation Pattern:
```dart
class NetworkAwareWidget extends StatelessWidget {
  final Widget onlineChild;
  final Widget offlineChild;

  @override
  Widget build(BuildContext context) {
    return Obx(() {
      final connectivity = Get.find<ConnectivityController>().status;

      if (connectivity == ConnectivityStatus.online) {
        return onlineChild;
      } else {
        return offlineChild;
      }
    });
  }
}

class ErrorBoundary extends StatelessWidget {
  final Widget child;
  final String fallbackMessage;

  @override
  Widget build(BuildContext context) {
    return ErrorWidget.builder(
      (FlutterErrorDetails error) {
        return ErrorDisplay(
          message: fallbackMessage,
          onRetry: () => _retryOperation(),
        );
      },
      child: child,
    );
  }
}
```

Error Recovery Features:
- Automatic retry for failed requests
- User-initiated retry options
- Cached data fallbacks
- Graceful service degradation
- Clear communication about issues

Use connectivity_plus for network detection, implement proper caching strategies, and ensure robust error recovery.
```

---

## 📱 Responsive Design Prompts

### 13. Multi-Device Adaptive Layout
```
Create a responsive Flutter layout system that adapts seamlessly across different device sizes and orientations.

Breakpoint System:
- Mobile Small: 320px - 374px (iPhone SE)
- Mobile: 375px - 767px (iPhone, Android phones)
- Tablet: 768px - 1023px (iPad, Android tablets)
- Desktop: 1024px - 1439px (Small laptops)
- Wide: 1440px+ (Large desktop)

Adaptive Components:
- Responsive grid layouts
- Adaptive navigation patterns
- Flexible typography scaling
- Touch-optimized interactions
- Device-specific features

Implementation Example:
```dart
class ResponsiveLayout extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth >= 1024 && desktop != null) {
          return desktop!;
        } else if (constraints.maxWidth >= 768 && tablet != null) {
          return tablet!;
        } else {
          return mobile;
        }
      },
    );
  }
}

class AdaptiveGrid extends StatelessWidget {
  final List<Widget> children;
  final double spacing;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final crossAxisCount = _getCrossAxisCount(constraints.maxWidth);
        final childAspectRatio = _getChildAspectRatio(constraints.maxWidth);

        return GridView.builder(
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: crossAxisCount,
            childAspectRatio: childAspectRatio,
            crossAxisSpacing: spacing,
            mainAxisSpacing: spacing,
          ),
          itemCount: children.length,
          itemBuilder: (context, index) => children[index],
        );
      },
    );
  }

  int _getCrossAxisCount(double width) {
    if (width >= 1024) return 4;
    if (width >= 768) return 3;
    return 2;
  }

  double _getChildAspectRatio(double width) {
    if (width >= 768) return 1.2;
    return 0.8;
  }
}
```

Use MediaQuery for device detection, implement proper breakpoint handling, and ensure consistent experience across devices.
```

### 14. Accessibility-First Implementation
```
Implement comprehensive accessibility features in Flutter to ensure WCAG 2.1 AA compliance for all users.

Accessibility Features:
- Semantic labeling for all interactive elements
- Screen reader support with proper announcements
- Keyboard navigation for all functionality
- High contrast mode support
- Font size scaling support
- Reduced motion preferences

Implementation Examples:
```dart
class AccessibleMenuItem extends StatelessWidget {
  final String name;
  final String description;
  final double price;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: '$name, $description, ${price.toStringAsFixed(2)} dollars',
      hint: 'Double tap to add to cart',
      child: GestureDetector(
        onTap: onTap,
        child: ItemCard(
          name: name,
          description: description,
          price: price,
        ),
      ),
    );
  }
}

class AccessibleForm extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Focus(
      autofocus: true,
      child: SingleChildScrollView(
        child: Column(
          children: [
            AccessibleTextField(
              label: 'Name',
              hint: 'Enter your full name',
              semanticLabel: 'Full name field',
            ),
            AccessibleButton(
              label: 'Submit Order',
              onPressed: _submitOrder,
              semanticLabel: 'Submit order button',
            ),
          ],
        ),
      ),
    );
  }
}
```

Testing Strategy:
- Automated testing with flutter_test
- Manual testing with screen readers
- Keyboard navigation testing
- Color contrast validation
- Font scaling testing

Use Semantics widgets for screen readers, implement proper focus management, and ensure keyboard accessibility.
```

---

## 🎯 Usage Instructions

### How to Use These Prompts

1. **Select appropriate prompt** based on the component you want to build
2. **Copy entire prompt** into your AI code generation tool
3. **Customize as needed** - adjust colors, spacing, or specific requirements
4. **Generate code** - AI will create Flutter code following Material Design 3
5. **Review and integrate** - test generated code and integrate into your project

### Best Practices

- **Test thoroughly** before production deployment
- **Adapt to project structure** and naming conventions
- **Verify responsive behavior** across different screen sizes
- **Check accessibility compliance** with semantic labels
- **Validate API integration** with actual backend endpoints

### Customization Tips

- **Colors**: Adjust primary/secondary colors for different restaurant brands
- **Typography**: Modify font families and sizes for brand consistency
- **Animations**: Adjust duration and curves for performance optimization
- **Layout**: Tweak spacing and margins for different content types
- **Performance**: Optimize image loading and caching strategies

These prompts are optimized for generating production-ready Flutter code that implements a world-class customer-facing restaurant ordering system with enterprise-grade quality, performance, and accessibility.

---

## 🚀 Implementation Priority

### Phase 1: Core Experience (Week 1-2)
1. Restaurant Landing Page
2. Menu Categories Grid
3. Menu Items with Quick Add
4. Basic Shopping Cart

### Phase 2: Enhanced Features (Week 3-4)
5. Item Details Modal
6. Customization Options
7. Payment Processing
8. Order Confirmation

### Phase 3: Advanced Features (Week 5-6)
9. Offline Mode Support
10. Advanced Filtering
11. Multi-language Support
12. Analytics Integration

Each prompt is designed to generate production-ready code that can be immediately integrated into your ZERGO QR application.