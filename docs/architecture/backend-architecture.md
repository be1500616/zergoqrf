# Backend Architecture

## Service Architecture

### Function Organization (FastAPI Structure)

```
app/
├── core/
│   ├── config.py          # Configuration management
│   ├── database.py        # Supabase client setup
│   ├── security.py        # Authentication & authorization
│   └── exceptions.py      # Custom exception classes
├── features/
│   ├── auth/
│   │   ├── router.py      # Authentication endpoints
│   │   ├── service.py     # Business logic
│   │   ├── models.py      # Pydantic models
│   │   └── dependencies.py # Route dependencies
│   ├── restaurants/
│   ├── orders/
│   ├── menu/
│   └── payments/
├── services/
│   ├── whatsapp_service.py
│   ├── payment_service.py
│   └── notification_service.py
├── middleware/
│   ├── cors.py
│   ├── logging.py
│   └── error_handler.py
└── main.py
```

### Controller Template (FastAPI Router)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.security import get_current_restaurant
from app.features.orders.service import OrderService
from app.features.orders.models import OrderCreate, OrderResponse, OrderUpdate
from app.core.database import get_supabase_client

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    order_service: OrderService = Depends(),
    supabase = Depends(get_supabase_client)
):
    """Create a new order with payment processing"""
    try:
        # Validate menu items exist and are available
        await order_service.validate_order_items(order_data.items)

        # Calculate total with taxes
        total_amount = await order_service.calculate_total(order_data.items)

        # Create order in database
        order = await order_service.create_order(
            order_data,
            total_amount=total_amount
        )

        # Send notifications
        await order_service.send_notifications(order)

        return OrderResponse.from_order(order)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order"
        )

@router.get("/restaurant/{restaurant_id}", response_model=List[OrderResponse])
async def get_restaurant_orders(
    restaurant_id: str,
    status_filter: Optional[str] = None,
    current_restaurant = Depends(get_current_restaurant),
    order_service: OrderService = Depends()
):
    """Get orders for a restaurant with optional status filtering"""
    # Ensure user can only access their restaurant's orders
    if current_restaurant.id != restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to restaurant orders"
        )

    orders = await order_service.get_restaurant_orders(
        restaurant_id,
        status_filter
    )

    return [OrderResponse.from_order(order) for order in orders]

@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    status_update: OrderUpdate,
    current_restaurant = Depends(get_current_restaurant),
    order_service: OrderService = Depends()
):
    """Update order status with real-time notifications"""
    # Verify order belongs to current restaurant
    order = await order_service.get_order(order_id)
    if order.restaurant_id != current_restaurant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to order"
        )

    # Update status
    updated_order = await order_service.update_status(
        order_id,
        status_update.status
    )

    # Send real-time updates
    await order_service.broadcast_status_update(updated_order)

    return OrderResponse.from_order(updated_order)
```

## Database Architecture

### Data Access Layer

```python
from typing import List, Optional
from supabase import Client
from app.core.database import get_supabase_client
from app.features.orders.models import Order, OrderCreate, OrderStatus

class OrderRepository:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def create_order(self, order_data: OrderCreate, total_amount: float) -> Order:
        """Create new order with RLS policy enforcement"""
        result = self.supabase.table('orders').insert({
            'restaurant_id': order_data.restaurant_id,
            'table_id': order_data.table_id,
            'customer_id': order_data.customer_id,
            'items': order_data.items,
            'total_amount': total_amount,
            'status': 'pending',
            'payment_status': 'pending',
            'special_instructions': order_data.special_instructions,
            'estimated_prep_time': await self._calculate_prep_time(order_data.items)
        }).execute()

        return Order(**result.data[0])

    async def get_restaurant_orders(
        self,
        restaurant_id: str,
        status_filter: Optional[str] = None
    ) -> List[Order]:
        """Get orders for restaurant with optional filtering"""
        query = self.supabase.table('orders').select('*').eq('restaurant_id', restaurant_id)

        if status_filter:
            query = query.eq('status', status_filter)

        result = query.order('created_at', desc=True).execute()
        return [Order(**row) for row in result.data]

    async def update_order_status(self, order_id: str, status: OrderStatus) -> Order:
        """Update order status with optimistic locking"""
        result = self.supabase.table('orders').update({
            'status': status.value,
            'updated_at': 'NOW()'
        }).eq('id', order_id).execute()

        if not result.data:
            raise ValueError(f"Order {order_id} not found")

        return Order(**result.data[0])

    async def _calculate_prep_time(self, items: List[dict]) -> int:
        """Calculate estimated preparation time based on items"""
        # Business logic for prep time calculation
        base_time = 15  # 15 minutes base
        item_time = len(items) * 3  # 3 minutes per item
        return min(base_time + item_time, 45)  # Max 45 minutes
```

## Responsive Cross-Platform Design Architecture

## Design Philosophy for Multi-Platform Applications

ZergoQRF implements a **Responsive-First, Platform-Adaptive** design strategy that ensures optimal user experience across mobile phones, tablets, web browsers, and desktop applications. The approach balances consistency with platform-specific conventions to create a unified brand experience while respecting each platform's unique interaction patterns.

### Core Design Principles

1. **Content-First Responsive Design**: UI adapts to content and screen real estate, not fixed breakpoints
2. **Progressive Enhancement**: Core functionality works on all platforms, enhanced features activate based on capabilities
3. **Platform Convention Respect**: Follows Material Design on Android, Human Interface Guidelines on iOS, web accessibility standards
4. **Touch-First with Keyboard Support**: Optimized for touch interactions with comprehensive keyboard navigation
5. **Performance-Conscious Responsive**: Efficient rendering across different device capabilities

## Flutter Responsive Design Framework

### Adaptive Layout System

```dart
// Core responsive layout foundation
class ResponsiveLayout extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;
  final Widget? web;

  const ResponsiveLayout({
    Key? key,
    required this.mobile,
    this.tablet,
    this.desktop,
    this.web,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final platform = Theme.of(context).platform;

    // Platform-specific overrides
    if (kIsWeb && web != null) {
      return web!;
    }

    // Responsive breakpoints with platform considerations
    if (screenWidth >= BreakpointConfig.desktop) {
      return desktop ?? tablet ?? mobile;
    } else if (screenWidth >= BreakpointConfig.tablet) {
      return tablet ?? mobile;
    } else {
      return mobile;
    }
  }
}

// Advanced responsive breakpoint configuration
class BreakpointConfig {
  // Mobile-first breakpoints
  static const double mobile = 0;
  static const double mobileLarge = 428;    // iPhone 14 Pro Max
  static const double tablet = 768;         // iPad Mini
  static const double tabletLarge = 1024;   // iPad Pro
  static const double desktop = 1200;       // Small desktop
  static const double desktopLarge = 1440;  // Large desktop
  static const double desktopXL = 1920;     // Ultra-wide screens

  // Platform-specific adjustments
  static double getAdjustedBreakpoint(double breakpoint, TargetPlatform platform) {
    switch (platform) {
      case TargetPlatform.iOS:
        // iOS tends to have different aspect ratios
        return breakpoint * 0.95;
      case TargetPlatform.android:
        return breakpoint;
      case TargetPlatform.fuchsia:
      case TargetPlatform.linux:
      case TargetPlatform.macOS:
      case TargetPlatform.windows:
        // Desktop platforms need more generous breakpoints
        return breakpoint * 1.1;
    }
  }
}

// Screen size utility class
class ScreenSize {
  final BuildContext context;
  late final MediaQueryData _mediaQuery;
  late final Size _size;

  ScreenSize(this.context) {
    _mediaQuery = MediaQuery.of(context);
    _size = _mediaQuery.size;
  }

  // Screen dimensions
  double get width => _size.width;
  double get height => _size.height;
  double get aspectRatio => _size.aspectRatio;

  // Responsive helpers
  bool get isMobile => width < BreakpointConfig.tablet;
  bool get isTablet => width >= BreakpointConfig.tablet && width < BreakpointConfig.desktop;
  bool get isDesktop => width >= BreakpointConfig.desktop;
  bool get isWeb => kIsWeb;

  // Platform-specific checks
  bool get isIOS => Theme.of(context).platform == TargetPlatform.iOS;
  bool get isAndroid => Theme.of(context).platform == TargetPlatform.android;
  bool get isMacOS => Theme.of(context).platform == TargetPlatform.macOS;
  bool get isWindows => Theme.of(context).platform == TargetPlatform.windows;

  // Orientation
  bool get isLandscape => _mediaQuery.orientation == Orientation.landscape;
  bool get isPortrait => _mediaQuery.orientation == Orientation.portrait;

  // Safe areas and insets
  EdgeInsets get safeAreaPadding => _mediaQuery.padding;
  EdgeInsets get viewInsets => _mediaQuery.viewInsets;

  // Density and scaling
  double get devicePixelRatio => _mediaQuery.devicePixelRatio;
  double get textScaleFactor => _mediaQuery.textScaleFactor;

  // Responsive value selection
  T responsiveValue<T>({
    required T mobile,
    T? tablet,
    T? desktop,
    T? web,
  }) {
    if (isWeb && web != null) return web;
    if (isDesktop && desktop != null) return desktop;
    if (isTablet && tablet != null) return tablet;
    return mobile;
  }
}
```

### Adaptive Component Architecture

```dart
// Adaptive menu layout for different screen sizes
class AdaptiveMenuLayout extends StatelessWidget {
  final Menu menu;
  final Function(MenuItem) onItemTap;

  const AdaptiveMenuLayout({
    Key? key,
    required this.menu,
    required this.onItemTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final screenSize = ScreenSize(context);

    return ResponsiveLayout(
      mobile: _buildMobileLayout(context, screenSize),
      tablet: _buildTabletLayout(context, screenSize),
      desktop: _buildDesktopLayout(context, screenSize),
      web: _buildWebLayout(context, screenSize),
    );
  }

  // Mobile: Single-column scrollable list
  Widget _buildMobileLayout(BuildContext context, ScreenSize screenSize) {
    return CustomScrollView(
      slivers: [
        // Sticky app bar
        SliverAppBar(
          expandedHeight: screenSize.responsiveValue(
            mobile: 120.0,
            tablet: 160.0,
          ),
          pinned: true,
          flexibleSpace: FlexibleSpaceBar(
            title: Text('Menu'),
            background: _buildHeroImage(),
          ),
        ),

        // Menu categories as tabs
        SliverPersistentHeader(
          pinned: true,
          delegate: _CategoryTabDelegate(
            categories: menu.categories,
            height: 60.0,
          ),
        ),

        // Menu items
        ...menu.categories.map((category) =>
          SliverList(
            delegate: SliverChildListDelegate([
              _buildCategoryHeader(category),
              ...category.items.map((item) =>
                _buildMobileMenuItem(item, screenSize)
              ),
            ]),
          ),
        ),
      ],
    );
  }

  // Tablet: Two-column layout with sidebar
  Widget _buildTabletLayout(BuildContext context, ScreenSize screenSize) {
    return Row(
      children: [
        // Category sidebar
        Container(
          width: screenSize.responsiveValue(
            tablet: 280.0,
            desktop: 320.0,
          ),
          child: _buildCategorySidebar(),
        ),

        // Main content area
        Expanded(
          child: _buildItemGrid(
            crossAxisCount: screenSize.isLandscape ? 3 : 2,
            childAspectRatio: 0.8,
          ),
        ),
      ],
    );
  }

  // Desktop: Three-panel layout
  Widget _buildDesktopLayout(BuildContext context, ScreenSize screenSize) {
    return Row(
      children: [
        // Navigation panel
        Container(
          width: 280.0,
          child: _buildNavigationPanel(),
        ),

        // Main content
        Expanded(
          flex: 2,
          child: _buildItemGrid(
            crossAxisCount: screenSize.responsiveValue(
              desktop: 3,
              desktopLarge: 4,
            ),
            childAspectRatio: 0.75,
          ),
        ),

        // Cart/order summary panel
        Container(
          width: 360.0,
          child: _buildCartPanel(),
        ),
      ],
    );
  }

  // Web: Responsive grid with dynamic columns
  Widget _buildWebLayout(BuildContext context, ScreenSize screenSize) {
    return Column(
      children: [
        // Web-specific navigation
        _buildWebNavigation(),

        // Hero section
        _buildWebHeroSection(screenSize),

        // Responsive grid
        Expanded(
          child: GridView.builder(
            padding: EdgeInsets.all(screenSize.responsiveValue(
              mobile: 16.0,
              tablet: 24.0,
              desktop: 32.0,
            )),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: screenSize.responsiveValue(
                mobile: 1,
                tablet: 2,
                desktop: 3,
                desktopLarge: 4,
                desktopXL: 5,
              ),
              crossAxisSpacing: 16.0,
              mainAxisSpacing: 16.0,
              childAspectRatio: 0.8,
            ),
            itemCount: menu.items.length,
            itemBuilder: (context, index) {
              return _buildWebMenuItem(menu.items[index], screenSize);
            },
          ),
        ),
      ],
    );
  }

  // Platform-specific menu item cards
  Widget _buildMobileMenuItem(MenuItem item, ScreenSize screenSize) {
    return Card(
      margin: EdgeInsets.symmetric(
        horizontal: 16.0,
        vertical: 8.0,
      ),
      child: ListTile(
        contentPadding: EdgeInsets.all(16.0),
        leading: _buildItemImage(item, size: 60.0),
        title: Text(
          item.name,
          style: Theme.of(context).textTheme.titleMedium,
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              item.description,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            SizedBox(height: 8.0),
            Text(
              '₹${item.price}',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                color: Theme.of(context).colorScheme.primary,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        trailing: _buildAddButton(item, compact: true),
        onTap: () => onItemTap(item),
      ),
    );
  }

  Widget _buildWebMenuItem(MenuItem item, ScreenSize screenSize) {
    return Card(
      elevation: 4.0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Image with aspect ratio
          Expanded(
            flex: 3,
            child: ClipRRect(
              borderRadius: BorderRadius.vertical(
                top: Radius.circular(8.0),
              ),
              child: _buildItemImage(
                item,
                fit: BoxFit.cover,
              ),
            ),
          ),

          // Content section
          Expanded(
            flex: 2,
            child: Padding(
              padding: EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.name,
                    style: Theme.of(context).textTheme.titleMedium,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  SizedBox(height: 4.0),
                  Text(
                    item.description,
                    style: Theme.of(context).textTheme.bodySmall,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  Spacer(),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '₹${item.price}',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          color: Theme.of(context).colorScheme.primary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      _buildAddButton(item, compact: false),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
```

### Platform-Specific Optimizations

```dart
// Platform-adaptive UI components
class PlatformAdaptiveScaffold extends StatelessWidget {
  final String title;
  final Widget body;
  final List<Widget>? actions;
  final Widget? floatingActionButton;
  final Widget? drawer;

  const PlatformAdaptiveScaffold({
    Key? key,
    required this.title,
    required this.body,
    this.actions,
    this.floatingActionButton,
    this.drawer,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final screenSize = ScreenSize(context);

    // Web-specific layout
    if (screenSize.isWeb && screenSize.isDesktop) {
      return _buildWebDesktopLayout(context, screenSize);
    }

    // Mobile/tablet layout
    return Scaffold(
      appBar: _buildPlatformAppBar(context, screenSize),
      body: body,
      drawer: drawer,
      floatingActionButton: _buildAdaptiveFAB(context, screenSize),
      bottomNavigationBar: _buildAdaptiveBottomNav(context, screenSize),
    );
  }

  PreferredSizeWidget _buildPlatformAppBar(BuildContext context, ScreenSize screenSize) {
    // iOS-style navigation bar
    if (screenSize.isIOS && !screenSize.isTablet) {
      return CupertinoNavigationBar(
        middle: Text(title),
        trailing: actions != null
          ? Row(
              mainAxisSize: MainAxisSize.min,
              children: actions!,
            )
          : null,
      );
    }

    // Material Design app bar
    return AppBar(
      title: Text(title),
      actions: actions,
      centerTitle: screenSize.isIOS,
      elevation: screenSize.isWeb ? 1.0 : null,
      backgroundColor: screenSize.isWeb
        ? Theme.of(context).colorScheme.surface
        : null,
    );
  }

  Widget _buildWebDesktopLayout(BuildContext context, ScreenSize screenSize) {
    return Column(
      children: [
        // Web app bar
        Container(
          height: 64.0,
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            border: Border(
              bottom: BorderSide(
                color: Theme.of(context).dividerColor,
                width: 1.0,
              ),
            ),
          ),
          child: Row(
            children: [
              SizedBox(width: 24.0),
              Text(
                title,
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              Spacer(),
              if (actions != null) ...actions!,
              SizedBox(width: 24.0),
            ],
          ),
        ),

        // Main content area
        Expanded(
          child: Row(
            children: [
              // Side navigation
              if (drawer != null)
                Container(
                  width: 280.0,
                  decoration: BoxDecoration(
                    border: Border(
                      right: BorderSide(
                        color: Theme.of(context).dividerColor,
                        width: 1.0,
                      ),
                    ),
                  ),
                  child: drawer,
                ),

              // Body content
              Expanded(child: body),
            ],
          ),
        ),
      ],
    );
  }

  Widget? _buildAdaptiveFAB(BuildContext context, ScreenSize screenSize) {
    if (floatingActionButton == null) return null;

    // Hide FAB on desktop/web layouts
    if (screenSize.isDesktop || screenSize.isWeb) {
      return null;
    }

    return floatingActionButton;
  }

  Widget? _buildAdaptiveBottomNav(BuildContext context, ScreenSize screenSize) {
    // Don't show bottom nav on desktop/web
    if (screenSize.isDesktop || screenSize.isWeb) {
      return null;
    }

    // Return platform-specific bottom navigation
    return _buildBottomNavigationBar(context, screenSize);
  }
}

// Adaptive input components
class AdaptiveTextField extends StatelessWidget {
  final String label;
  final String? hint;
  final TextEditingController? controller;
  final TextInputType? keyboardType;
  final bool obscureText;
  final String? Function(String?)? validator;
  final Function(String)? onChanged;

  const AdaptiveTextField({
    Key? key,
    required this.label,
    this.hint,
    this.controller,
    this.keyboardType,
    this.obscureText = false,
    this.validator,
    this.onChanged,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final screenSize = ScreenSize(context);

    // Web-optimized text field
    if (screenSize.isWeb) {
      return _buildWebTextField(context, screenSize);
    }

    // iOS-style text field
    if (screenSize.isIOS) {
      return _buildCupertinoTextField(context, screenSize);
    }

    // Material Design text field
    return _buildMaterialTextField(context, screenSize);
  }

  Widget _buildWebTextField(BuildContext context, ScreenSize screenSize) {
    return Container(
      constraints: BoxConstraints(
        maxWidth: screenSize.responsiveValue(
          mobile: double.infinity,
          tablet: 400.0,
          desktop: 480.0,
        ),
      ),
      child: TextFormField(
        controller: controller,
        keyboardType: keyboardType,
        obscureText: obscureText,
        validator: validator,
        onChanged: onChanged,
        style: TextStyle(
          fontSize: 16.0, // Prevent zoom on iOS Safari
        ),
        decoration: InputDecoration(
          labelText: label,
          hintText: hint,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8.0),
          ),
          filled: true,
          fillColor: Theme.of(context).colorScheme.surface,
          contentPadding: EdgeInsets.symmetric(
            horizontal: 16.0,
            vertical: 16.0,
          ),
        ),
      ),
    );
  }

  Widget _buildCupertinoTextField(BuildContext context, ScreenSize screenSize) {
    return CupertinoTextFormFieldRow(
      controller: controller,
      keyboardType: keyboardType,
      obscureText: obscureText,
      validator: validator,
      onChanged: onChanged,
      prefix: Text(label),
      placeholder: hint,
      padding: EdgeInsets.symmetric(
        horizontal: 16.0,
        vertical: 12.0,
      ),
    );
  }

  Widget _buildMaterialTextField(BuildContext context, ScreenSize screenSize) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      obscureText: obscureText,
      validator: validator,
      onChanged: onChanged,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        border: OutlineInputBorder(),
        contentPadding: EdgeInsets.symmetric(
          horizontal: 16.0,
          vertical: 16.0,
        ),
      ),
    );
  }
}
```

## Responsive Typography and Spacing System

```dart
// Adaptive typography system
class ResponsiveTypography {
  static TextTheme getAdaptiveTextTheme(BuildContext context) {
    final screenSize = ScreenSize(context);
    final baseTheme = Theme.of(context).textTheme;

    // Scale factors based on screen size
    final scaleFactor = screenSize.responsiveValue(
      mobile: 1.0,
      tablet: 1.1,
      desktop: 1.2,
    );

    return TextTheme(
      displayLarge: baseTheme.displayLarge?.copyWith(
        fontSize: (baseTheme.displayLarge?.fontSize ?? 57) * scaleFactor,
        height: screenSize.responsiveValue(
          mobile: 1.2,
          tablet: 1.3,
          desktop: 1.4,
        ),
      ),
      headlineMedium: baseTheme.headlineMedium?.copyWith(
        fontSize: (baseTheme.headlineMedium?.fontSize ?? 28) * scaleFactor,
      ),
      titleLarge: baseTheme.titleLarge?.copyWith(
        fontSize: (baseTheme.titleLarge?.fontSize ?? 22) * scaleFactor,
      ),
      bodyLarge: baseTheme.bodyLarge?.copyWith(
        fontSize: screenSize.responsiveValue(
          mobile: 16.0,
          tablet: 17.0,
          desktop: 18.0,
        ),
        height: 1.5, // Better reading experience
      ),
      bodyMedium: baseTheme.bodyMedium?.copyWith(
        fontSize: screenSize.responsiveValue(
          mobile: 14.0,
          tablet: 15.0,
          desktop: 16.0,
        ),
      ),
      labelLarge: baseTheme.labelLarge?.copyWith(
        fontSize: screenSize.responsiveValue(
          mobile: 14.0,
          tablet: 15.0,
          desktop: 16.0,
        ),
      ),
    );
  }
}

// Adaptive spacing system
class ResponsiveSpacing {
  static const double _baseUnit = 8.0;

  static double xs(BuildContext context) => _getSpacing(context, 0.5); // 4dp
  static double sm(BuildContext context) => _getSpacing(context, 1);   // 8dp
  static double md(BuildContext context) => _getSpacing(context, 2);   // 16dp
  static double lg(BuildContext context) => _getSpacing(context, 3);   // 24dp
  static double xl(BuildContext context) => _getSpacing(context, 4);   // 32dp
  static double xxl(BuildContext context) => _getSpacing(context, 6);  // 48dp

  static double _getSpacing(BuildContext context, double multiplier) {
    final screenSize = ScreenSize(context);
    final scaleFactor = screenSize.responsiveValue(
      mobile: 1.0,
      tablet: 1.2,
      desktop: 1.4,
    );

    return _baseUnit * multiplier * scaleFactor;
  }

  // Semantic spacing methods
  static EdgeInsets contentPadding(BuildContext context) {
    final screenSize = ScreenSize(context);
    return EdgeInsets.all(
      screenSize.responsiveValue(
        mobile: 16.0,
        tablet: 24.0,
        desktop: 32.0,
      ),
    );
  }

  static EdgeInsets sectionPadding(BuildContext context) {
    final screenSize = ScreenSize(context);
    return EdgeInsets.symmetric(
      horizontal: screenSize.responsiveValue(
        mobile: 16.0,
        tablet: 32.0,
        desktop: 48.0,
      ),
      vertical: screenSize.responsiveValue(
        mobile: 24.0,
        tablet: 32.0,
        desktop: 40.0,
      ),
    );
  }
}
```

## Advanced Responsive Patterns

### Adaptive Navigation Patterns

```dart
// Adaptive navigation controller
class AdaptiveNavigationController extends GetxController {
  final RxInt _selectedIndex = 0.obs;
  final RxBool _isRailCollapsed = false.obs;

  int get selectedIndex => _selectedIndex.value;
  bool get isRailCollapsed => _isRailCollapsed.value;

  void selectTab(int index) {
    _selectedIndex.value = index;
  }

  void toggleRail() {
    _isRailCollapsed.value = !_isRailCollapsed.value;
  }
}

// Adaptive navigation widget
class AdaptiveNavigation extends StatelessWidget {
  final List<NavigationDestination> destinations;
  final List<Widget> pages;
  final AdaptiveNavigationController controller;

  const AdaptiveNavigation({
    Key? key,
    required this.destinations,
    required this.pages,
    required this.controller,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final screenSize = ScreenSize(context);

    return Scaffold(
      body: Obx(() {
        // Desktop: Navigation rail + content
        if (screenSize.isDesktop) {
          return Row(
            children: [
              NavigationRail(
                selectedIndex: controller.selectedIndex,
                onDestinationSelected: controller.selectTab,
                extended: !controller.isRailCollapsed,
                leading: IconButton(
                  icon: Icon(Icons.menu),
                  onPressed: controller.toggleRail,
                ),
                destinations: destinations.map((dest) =>
                  NavigationRailDestination(
                    icon: dest.icon,
                    label: Text(dest.label),
                    selectedIcon: dest.selectedIcon,
                  ),
                ).toList(),
              ),
              Expanded(
                child: pages[controller.selectedIndex],
              ),
            ],
          );
        }

        // Tablet: Navigation drawer + content
        if (screenSize.isTablet) {
          return Row(
            children: [
              NavigationDrawer(
                selectedIndex: controller.selectedIndex,
                onDestinationSelected: controller.selectTab,
                children: [
                  DrawerHeader(
                    child: Text('ZergoQRF'),
                  ),
                  ...destinations.map((dest) =>
                    NavigationDrawerDestination(
                      icon: dest.icon,
                      label: Text(dest.label),
                      selectedIcon: dest.selectedIcon,
                    ),
                  ),
                ],
              ),
              Expanded(
                child: pages[controller.selectedIndex],
              ),
            ],
          );
        }

        // Mobile: Bottom navigation + content
        return Column(
          children: [
            Expanded(
              child: pages[controller.selectedIndex],
            ),
            NavigationBar(
              selectedIndex: controller.selectedIndex,
              onDestinationSelected: controller.selectTab,
              destinations: destinations,
            ),
          ],
        );
      }),
    );
  }
}
```

### Responsive Image Handling

```dart
// Adaptive image widget with responsive sizing
class AdaptiveImage extends StatelessWidget {
  final String imageUrl;
  final String? alt;
  final BoxFit? fit;
  final double? aspectRatio;

  const AdaptiveImage({
    Key? key,
    required this.imageUrl,
    this.alt,
    this.fit,
    this.aspectRatio,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final screenSize = ScreenSize(context);

    // Generate responsive image URL based on screen size
    final optimizedUrl = _generateResponsiveUrl(screenSize);

    return AspectRatio(
      aspectRatio: aspectRatio ?? _getDefaultAspectRatio(screenSize),
      child: CachedNetworkImage(
        imageUrl: optimizedUrl,
        fit: fit ?? BoxFit.cover,
        placeholder: (context, url) => _buildPlaceholder(screenSize),
        errorWidget: (context, url, error) => _buildErrorWidget(screenSize),
        semanticLabel: alt,
        memCacheWidth: _getCacheWidth(screenSize),
        memCacheHeight: _getCacheHeight(screenSize),
      ),
    );
  }

  String _generateResponsiveUrl(ScreenSize screenSize) {
    final width = screenSize.responsiveValue(
      mobile: 400,
      tablet: 600,
      desktop: 800,
    );

    final height = (width / (aspectRatio ?? 1.0)).round();

    // Use Supabase image transformations
    return '$imageUrl?width=$width&height=$height&resize=cover&format=webp&quality=80';
  }

  double _getDefaultAspectRatio(ScreenSize screenSize) {
    return screenSize.responsiveValue(
      mobile: 16 / 9,
      tablet: 4 / 3,
      desktop: 3 / 2,
    );
  }

  int _getCacheWidth(ScreenSize screenSize) {
    return screenSize.responsiveValue(
      mobile: 400,
      tablet: 600,
      desktop: 800,
    );
  }

  int _getCacheHeight(ScreenSize screenSize) {
    final width = _getCacheWidth(screenSize);
    return (width / (aspectRatio ?? _getDefaultAspectRatio(screenSize))).round();
  }
}
```

## Platform-Specific User Experience Optimizations

### iOS-Specific Optimizations

```dart
// iOS-specific behaviors and interactions
class IOSOptimizations {
  static Widget buildIOSScrollBehavior({
    required Widget child,
    required BuildContext context,
  }) {
    return ScrollConfiguration(
      behavior: IOSScrollBehavior(),
      child: child,
    );
  }

  static Widget buildIOSModalBottomSheet({
    required Widget child,
    required BuildContext context,
  }) {
    return CupertinoModalPopup(
      child: Container(
        decoration: BoxDecoration(
          color: CupertinoTheme.of(context).scaffoldBackgroundColor,
          borderRadius: BorderRadius.vertical(
            top: Radius.circular(12.0),
          ),
        ),
        child: SafeArea(child: child),
      ),
    );
  }

  static void showIOSActionSheet({
    required BuildContext context,
    required List<CupertinoActionSheetAction> actions,
    String? title,
    String? message,
  }) {
    showCupertinoModalPopup(
      context: context,
      builder: (context) => CupertinoActionSheet(
        title: title != null ? Text(title) : null,
        message: message != null ? Text(message) : null,
        actions: actions,
        cancelButton: CupertinoActionSheetAction(
          onPressed: () => Navigator.pop(context),
          child: Text('Cancel'),
        ),
      ),
    );
  }
}

class IOSScrollBehavior extends ScrollBehavior {
  @override
  Widget buildOverscrollIndicator(
    BuildContext context,
    Widget child,
    ScrollableDetails details,
  ) {
    // iOS doesn't show overscroll indicators
    return child;
  }

  @override
  ScrollPhysics getScrollPhysics(BuildContext context) {
    return BouncingScrollPhysics();
  }
}
```

### Web-Specific Optimizations

```dart
// Web-specific performance and UX optimizations
class WebOptimizations {
  static void setupWebOptimizations() {
    // Disable context menu on web
    if (kIsWeb) {
      BrowserContextMenu.disableContextMenu();
    }
  }

  static Widget buildWebScrollbar({
    required Widget child,
    ScrollController? controller,
  }) {
    if (!kIsWeb) return child;

    return Scrollbar(
      controller: controller,
      thumbVisibility: true,
      trackVisibility: true,
      child: child,
    );
  }

  static void setupWebHotkeys(BuildContext context) {
    if (!kIsWeb) return;

    // Add keyboard shortcuts for web
    final shortcuts = <LogicalKeySet, Intent>{
      LogicalKeySet(LogicalKeyboardKey.control, LogicalKeyboardKey.keyF):
        const SearchIntent(),
      LogicalKeySet(LogicalKeyboardKey.escape):
        const EscapeIntent(),
    };

    final actions = <Type, Action<Intent>>{
      SearchIntent: CallbackAction<SearchIntent>(
        onInvoke: (intent) {
          // Show search dialog
          return null;
        },
      ),
      EscapeIntent: CallbackAction<EscapeIntent>(
        onInvoke: (intent) {
          // Close current dialog/modal
          Navigator.maybePop(context);
          return null;
        },
      ),
    };

    Shortcuts(
      shortcuts: shortcuts,
      child: Actions(
        actions: actions,
        child: Focus(
          autofocus: true,
          child: Container(), // Your app content
        ),
      ),
    );
  }
}

class SearchIntent extends Intent {}
class EscapeIntent extends Intent {}
```

## Testing Responsive Design

```dart
// Responsive design testing utilities
class ResponsiveTestUtils {
  static Widget wrapWithScreenSize({
    required Widget child,
    required Size size,
    double devicePixelRatio = 1.0,
  }) {
    return MediaQuery(
      data: MediaQueryData(
        size: size,
        devicePixelRatio: devicePixelRatio,
        textScaleFactor: 1.0,
      ),
      child: MaterialApp(
        home: child,
      ),
    );
  }

  static const Size mobileSize = Size(375, 667);   // iPhone SE
  static const Size tabletSize = Size(768, 1024);  // iPad
  static const Size desktopSize = Size(1440, 900); // Desktop
}

// Example responsive widget tests
void main() {
  group('AdaptiveMenuLayout Responsive Tests', () {
    testWidgets('displays mobile layout on small screens', (tester) async {
      await tester.pumpWidget(
        ResponsiveTestUtils.wrapWithScreenSize(
          size: ResponsiveTestUtils.mobileSize,
          child: AdaptiveMenuLayout(
            menu: TestDataFactory.createMenu(),
            onItemTap: (item) {},
          ),
        ),
      );

      // Verify mobile-specific widgets are present
      expect(find.byType(SliverAppBar), findsOneWidget);
      expect(find.byType(ListTile), findsWidgets);
      expect(find.byType(GridView), findsNothing);
    });

    testWidgets('displays tablet layout on medium screens', (tester) async {
      await tester.pumpWidget(
        ResponsiveTestUtils.wrapWithScreenSize(
          size: ResponsiveTestUtils.tabletSize,
          child: AdaptiveMenuLayout(
            menu: TestDataFactory.createMenu(),
            onItemTap: (item) {},
          ),
        ),
      );

      // Verify tablet-specific widgets are present
      expect(find.byType(Row), findsOneWidget); // Sidebar + content
      expect(find.byType(GridView), findsOneWidget);
    });

    testWidgets('displays desktop layout on large screens', (tester) async {
      await tester.pumpWidget(
        ResponsiveTestUtils.wrapWithScreenSize(
          size: ResponsiveTestUtils.desktopSize,
          child: AdaptiveMenuLayout(
            menu: TestDataFactory.createMenu(),
            onItemTap: (item) {},
          ),
        ),
      );

      // Verify desktop-specific widgets are present
      expect(find.byType(Row), findsOneWidget); // Three-panel layout
      expect(find.byType(GridView), findsOneWidget);
    });
  });
}
```

This comprehensive responsive design architecture ensures that ZergoQRF provides an optimal user experience across all platforms while maintaining consistency in branding and core functionality. The adaptive approach respects platform conventions while leveraging Flutter's cross-platform capabilities for maximum code reuse and maintainability.
