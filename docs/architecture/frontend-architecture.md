# Frontend Architecture

## Component Architecture

### Component Organization
```

lib/
├── core/
│ ├── services/ # API clients and business logic
│ ├── models/ # Data models and DTOs
│ ├── constants/ # App constants and enums
│ ├── theme/ # Material Design theme
│ └── utils/ # Helper functions
├── features/
│ ├── auth/
│ │ ├── controllers/ # GetX controllers
│ │ ├── views/ # UI screens
│ │ ├── widgets/ # Feature-specific widgets
│ │ └── bindings.dart # Dependency injection
│ ├── menu/
│ │ ├── controllers/
│ │ ├── views/
│ │ ├── widgets/
│ │ └── bindings.dart
│ ├── ordering/
│ └── admin/
├── shared/
│ ├── widgets/ # Reusable UI components
│ ├── extensions/ # Dart extensions
│ └── validators/ # Form validation
└── main.dart

````

### Component Template
```typescript
// GetX Controller Pattern
class MenuController extends GetxController {
  final ApiService _apiService = Get.find<ApiService>();
  final AuthController _authController = Get.find<AuthController>();

  // Reactive state
  final Rx<Menu?> menu = Rx<Menu?>(null);
  final RxList<OrderItem> cartItems = <OrderItem>[].obs;
  final RxBool isLoading = false.obs;
  final RxString error = ''.obs;

  @override
  void onInit() {
    super.onInit();
    loadMenu();

    // Listen to auth changes
    ever(_authController.currentTable, (_) => loadMenu());
  }

  Future<void> loadMenu() async {
    try {
      isLoading.value = true;
      error.value = '';

      final result = await _apiService.getMenuByQRToken(
        _authController.currentTable.value?.qrToken ?? ''
      );

      menu.value = result;
    } catch (e) {
      error.value = e.toString();
      Get.snackbar('Error', 'Failed to load menu');
    } finally {
      isLoading.value = false;
    }
  }

  void addToCart(MenuItem item, int quantity) {
    final existingIndex = cartItems.indexWhere(
      (cartItem) => cartItem.menuItemId == item.id
    );

    if (existingIndex >= 0) {
      cartItems[existingIndex] = cartItems[existingIndex].copyWith(
        quantity: cartItems[existingIndex].quantity + quantity
      );
    } else {
      cartItems.add(OrderItem.fromMenuItem(item, quantity));
    }
  }

  @override
  void onClose() {
    // Cleanup subscriptions
    super.onClose();
  }
}
````

## State Management Architecture

### State Structure

```typescript
// Global App State with GetX
class AppController extends GetxController {
  // Authentication state
  final Rx<User?> currentUser = Rx<User?>(null);
  final Rx<Restaurant?> currentRestaurant = Rx<Restaurant?>(null);
  final Rx<Table?> currentTable = Rx<Table?>(null);

  // UI state
  final RxBool isDarkMode = false.obs;
  final RxString currentLanguage = 'en'.obs;
  final RxBool isOnline = true.obs;

  // Real-time connections
  final Rx<RealtimeChannel?> orderChannel = Rx<RealtimeChannel?>(null);

  @override
  void onInit() {
    super.onInit();
    initializeApp();
    setupRealtimeSubscriptions();
  }

  void setupRealtimeSubscriptions() {
    // Subscribe to order updates for current restaurant
    ever(currentRestaurant, (Restaurant? restaurant) {
      if (restaurant != null) {
        orderChannel.value = Supabase.instance.client
          .channel('orders:restaurant_id=eq.${restaurant.id}')
          .onPostgresChanges(
            event: PostgresChangeEvent.all,
            schema: 'public',
            table: 'orders',
            callback: (payload) {
              // Update local state
              _handleOrderUpdate(payload);
            },
          )
          .subscribe();
      }
    });
  }
}
```

### State Management Patterns

- **Reactive UI Updates**: Obx widgets for minimal rebuilds at component level
- **Global State**: AppController for authentication and restaurant context
- **Feature State**: Feature-specific controllers with lifecycle management
- **Dependency Injection**: GetX bindings for service and controller registration
- **Error Handling**: Centralized error handling with user-friendly messages
- **Offline Support**: Local storage with sync on reconnection

## Routing Architecture

### Route Organization

```
Routes Configuration:
/                          → Splash screen (auth check)
/login                     → Authentication screen
/qr-scan                   → QR code scanner
/menu/:restaurantSlug/:tableId → Public menu access
/cart                      → Order cart
/checkout                  → Payment screen
/order-tracking/:orderId   → Order status
/admin                     → Restaurant admin (protected)
/admin/orders              → Order management
/admin/menu                → Menu management
/admin/analytics           → Analytics dashboard
```

### Protected Route Pattern

```typescript
// Route Guard Implementation
class AuthMiddleware extends GetMiddleware {
  @override
  RouteSettings? redirect(String? route) {
    final AuthController authController = Get.find<AuthController>();

    // Check if user is authenticated for protected routes
    if (_isProtectedRoute(route) && !authController.isAuthenticated) {
      return const RouteSettings(name: '/login');
    }

    // Check restaurant admin permissions
    if (_isAdminRoute(route) && !authController.isRestaurantAdmin) {
      return const RouteSettings(name: '/unauthorized');
    }

    return null;
  }

  bool _isProtectedRoute(String? route) {
    return route?.startsWith('/admin') ?? false;
  }

  bool _isAdminRoute(String? route) {
    return route?.startsWith('/admin') ?? false;
  }
}

// GoRouter Configuration
final appRouter = GoRouter(
  initialLocation: '/',
  redirect: (context, state) {
    final authController = Get.find<AuthController>();
    final currentLocation = state.uri.path;

    // Handle authentication redirects
    if (!authController.isAuthenticated && _requiresAuth(currentLocation)) {
      return '/login';
    }

    return null;
  },
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const SplashScreen(),
    ),
    GoRoute(
      path: '/menu/:restaurantSlug/:tableId',
      builder: (context, state) {
        final restaurantSlug = state.params['restaurantSlug']!;
        final tableId = state.params['tableId']!;
        return MenuScreen(
          restaurantSlug: restaurantSlug,
          tableId: tableId,
        );
      },
    ),
    ShellRoute(
      builder: (context, state, child) => AdminShell(child: child),
      routes: [
        GoRoute(
          path: '/admin/orders',
          builder: (context, state) => const OrderManagementScreen(),
        ),
        GoRoute(
          path: '/admin/menu',
          builder: (context, state) => const MenuManagementScreen(),
        ),
      ],
    ),
  ],
);
```

## Frontend Services Layer

### API Client Setup

```typescript
class ApiService extends GetxService {
  late final Dio _dio;
  final SupabaseClient _supabase = Supabase.instance.client;

  @override
  void onInit() {
    super.onInit();
    _dio = Dio(BaseOptions(
      baseUrl: 'https://api.zergoqrf.com/v1',
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
    ));

    // Add interceptors
    _dio.interceptors.add(AuthInterceptor());
    _dio.interceptors.add(LoggingInterceptor());
    _dio.interceptors.add(ErrorInterceptor());
  }

  // Generic API methods
  Future<T> get<T>(String path, {Map<String, dynamic>? queryParameters}) async {
    try {
      final response = await _dio.get(path, queryParameters: queryParameters);
      return response.data as T;
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<T> post<T>(String path, {dynamic data}) async {
    try {
      final response = await _dio.post(path, data: data);
      return response.data as T;
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }
}
```

### Service Example

```typescript
class OrderService extends GetxService {
  final ApiService _apiService = Get.find<ApiService>();
  final SupabaseClient _supabase = Supabase.instance.client;

  Future<Order> createOrder(CreateOrderRequest request) async {
    try {
      // Create order via API
      final response = await _apiService.post<Map<String, dynamic>>(
        '/orders',
        data: request.toJson(),
      );

      // Return typed order
      return Order.fromJson(response);
    } catch (e) {
      throw OrderException('Failed to create order: $e');
    }
  }

  Stream<List<Order>> getRestaurantOrdersStream(String restaurantId) {
    return _supabase
        .from('orders')
        .stream(primaryKey: ['id'])
        .eq('restaurant_id', restaurantId)
        .order('created_at', ascending: false)
        .map((data) => data.map((json) => Order.fromJson(json)).toList());
  }

  Future<void> updateOrderStatus(String orderId, OrderStatus status) async {
    try {
      await _apiService.patch(
        '/orders/$orderId',
        data: {'status': status.name},
      );
    } catch (e) {
      throw OrderException('Failed to update order status: $e');
    }
  }
}
```
