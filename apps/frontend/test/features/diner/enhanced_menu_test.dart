import 'package:flutter/material.dart' hide MenuController;
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';

import 'package:zergo_frontend/features/diner/domain/entities/menu_item.dart';
import 'package:zergo_frontend/features/diner/domain/entities/menu_category.dart';
import 'package:zergo_frontend/features/diner/domain/entities/menu_structure.dart';
import 'package:zergo_frontend/features/diner/domain/entities/restaurant_branding.dart';
import 'package:zergo_frontend/features/diner/domain/entities/dietary_indicator.dart';
import 'package:zergo_frontend/features/diner/domain/entities/item_status.dart';
import 'package:zergo_frontend/features/diner/application/use_cases/fetch_menu.dart';
import 'package:zergo_frontend/features/diner/application/controllers/menu_controller.dart';
import 'package:zergo_frontend/features/diner/domain/entities/search_result.dart';
import 'package:zergo_frontend/features/diner/application/controllers/cart_controller.dart';
import 'package:zergo_frontend/features/diner/presentation/screens/enhanced_diner_menu_screen.dart';
import 'package:zergo_frontend/features/diner/application/services/cart_service.dart';

import 'enhanced_menu_test.mocks.dart';

@GenerateMocks([FetchMenuUseCase, CartService])
void main() {
  group('Enhanced Diner Menu Tests', () {
    late MockFetchMenuUseCase mockFetchMenuUseCase;
    late MenuController menuController;
    late CartController cartController;
    late MockCartService mockCartService;

    setUp(() {
      mockFetchMenuUseCase = MockFetchMenuUseCase();
      mockCartService = MockCartService();
      menuController = MenuController(mockFetchMenuUseCase);
      cartController = CartController(mockCartService);
      
      // Register controllers with GetX
      Get.put<MenuController>(menuController);
      Get.put<CartController>(cartController);
    });

    tearDown(() {
      Get.reset();
    });

    group('Domain Entities', () {
      test('RestaurantBranding should parse from JSON correctly', () {
        final json = {
          'id': 'test-id',
          'name': 'Test Restaurant',
          'code': 'TEST123',
          'logo_url': 'https://example.com/logo.png',
          'primary_color': '#FF6B35',
          'secondary_color': '#2C3E50',
          'accent_color': '#F39C12',
          'description': 'A test restaurant',
          'cuisine_type': 'Italian',
          'phone': '+1234567890',
          'address': '123 Test St',
        };

        final branding = RestaurantBranding.fromJson(json);

        expect(branding.id, equals('test-id'));
        expect(branding.name, equals('Test Restaurant'));
        expect(branding.code, equals('TEST123'));
        expect(branding.logoUrl, equals('https://example.com/logo.png'));
        expect(branding.primaryColor, equals('#FF6B35'));
        expect(branding.cuisineType, equals('Italian'));
      });

      test('MenuCategory should parse from JSON correctly', () {
        final json = {
          'id': 'category-id',
          'name': 'Appetizers',
          'description': 'Start your meal right',
          'sort_order': 1,
          'item_count': 5,
        };

        final category = MenuCategory.fromJson(json);

        expect(category.id, equals('category-id'));
        expect(category.name, equals('Appetizers'));
        expect(category.description, equals('Start your meal right'));
        expect(category.sortOrder, equals(1));
        expect(category.itemCount, equals(5));
      });

      test('DinerMenuItem should parse from JSON with dietary indicators', () {
        final json = {
          'id': 'item-id',
          'category_id': 'category-id',
          'name': 'Veggie Burger',
          'description': 'Plant-based burger',
          'base_price': 12.99,
          'image_url': 'https://example.com/burger.jpg',
          'gallery_images': ['https://example.com/burger1.jpg'],
          'status': 'available',
          'dietary_indicators': ['vegetarian', 'dairy_free'],
          'allergen_info': ['soy'],
          'preparation_time': 15,
          'sort_order': 1,
          'is_featured': true,
        };

        final item = DinerMenuItem.fromJson(json);

        expect(item.id, equals('item-id'));
        expect(item.name, equals('Veggie Burger'));
        expect(item.basePrice, equals(12.99));
        expect(item.priceCents, equals(1299)); // Backward compatibility
        expect(item.status, equals(ItemStatus.available));
        expect(item.isAvailable, isTrue);
        expect(item.isFeatured, isTrue);
        expect(item.dietaryIndicators, contains(DietaryIndicator.vegetarian));
        expect(item.dietaryIndicators, contains(DietaryIndicator.dairyFree));
        expect(item.allergenInfo, contains('soy'));
        expect(item.preparationTime, equals(15));
      });

      test('DietaryIndicator enum should work correctly', () {
        expect(DietaryIndicator.vegetarian.value, equals('vegetarian'));
        expect(DietaryIndicator.vegetarian.icon, equals('🥬'));
        expect(DietaryIndicator.vegetarian.displayName, equals('Vegetarian'));

        expect(DietaryIndicator.fromValue('vegan'), equals(DietaryIndicator.vegan));
        expect(DietaryIndicator.fromValue('invalid'), isNull);

        final indicators = DietaryIndicator.fromValueList(['vegetarian', 'vegan', 'invalid']);
        expect(indicators.length, equals(2));
        expect(indicators, contains(DietaryIndicator.vegetarian));
        expect(indicators, contains(DietaryIndicator.vegan));
      });
    });

    group('MenuController', () {
      test('should load menu structure successfully', () async {
        // Arrange
        final mockRestaurant = RestaurantBranding(
          id: 'test-id',
          name: 'Test Restaurant',
          code: 'TEST123',
        );

        final mockCategories = [
          MenuCategory(id: 'cat1', name: 'Appetizers', itemCount: 3),
          MenuCategory(id: 'cat2', name: 'Main Courses', itemCount: 5),
        ];

        final mockItems = [
          DinerMenuItem(
            id: 'item1',
            categoryId: 'cat1',
            name: 'Caesar Salad',
            basePrice: 8.99,
          ),
          DinerMenuItem(
            id: 'item2',
            categoryId: 'cat2',
            name: 'Grilled Chicken',
            basePrice: 15.99,
            isFeatured: true,
          ),
        ];

        final mockMenuStructure = MenuStructure(
          restaurant: mockRestaurant,
          categories: mockCategories,
          items: mockItems,
          lastUpdated: DateTime.now(),
        );

        when(mockFetchMenuUseCase.getMenuStructure('TEST123'))
            .thenAnswer((_) async => mockMenuStructure);

        // Act
        await menuController.loadMenu('TEST123');

        // Assert
        expect(menuController.isLoading, isFalse);
        expect(menuController.error, isNull);
        expect(menuController.menuStructure, isNotNull);
        expect(menuController.restaurant?.name, equals('Test Restaurant'));
        expect(menuController.categories.length, equals(2));
        expect(menuController.allItems.length, equals(2));
        expect(menuController.featuredItems.length, equals(1));
        expect(menuController.selectedCategory?.id, equals('cat1')); // First category selected
      });

      test('should handle menu loading error', () async {
        // Arrange
        when(mockFetchMenuUseCase.getMenuStructure('INVALID'))
            .thenThrow(Exception('Restaurant not found'));

        // Act
        await menuController.loadMenu('INVALID');

        // Assert
        expect(menuController.isLoading, isFalse);
        expect(menuController.error, isNotNull);
        expect(menuController.error, contains('Restaurant not found'));
        expect(menuController.menuStructure, isNull);
      });

      test('should filter items by selected category', () async {
        // Arrange - load menu first
        final mockMenuStructure = _createMockMenuStructure();
        when(mockFetchMenuUseCase.getMenuStructure('TEST123'))
            .thenAnswer((_) async => mockMenuStructure);
        await menuController.loadMenu('TEST123');

        // Act
        final category2 = menuController.categories.firstWhere((c) => c.id == 'cat2');
        menuController.selectCategory(category2);

        // Assert
        expect(menuController.selectedCategory?.id, equals('cat2'));
        expect(menuController.displayedItems.length, equals(1));
        expect(menuController.displayedItems.first.categoryId, equals('cat2'));
      });

      test('should search menu items', () async {
        // Arrange
        final mockSearchResult = MenuSearchResult(
          items: [
            DinerMenuItem(
              id: 'item1',
              categoryId: 'cat1',
              name: 'Caesar Salad',
              basePrice: 8.99,
            ),
          ],
          totalCount: 1,
          searchQuery: 'caesar',
        );

        when(mockFetchMenuUseCase.searchMenuItems('TEST123', 'caesar'))
            .thenAnswer((_) async => mockSearchResult);

        // Load menu first
        final mockMenuStructure = _createMockMenuStructure();
        when(mockFetchMenuUseCase.getMenuStructure('TEST123'))
            .thenAnswer((_) async => mockMenuStructure);
        await menuController.loadMenu('TEST123');

        // Act
        await menuController.searchItems('caesar');

        // Assert
        expect(menuController.isSearchMode, isTrue);
        expect(menuController.searchQuery, equals('caesar'));
        expect(menuController.hasSearchResults, isTrue);
        expect(menuController.displayedItems.length, equals(1));
        expect(menuController.displayedItems.first.name, equals('Caesar Salad'));
      });

      test('should clear search and return to category view', () async {
        // Arrange - load menu and perform search first
        final mockMenuStructure = _createMockMenuStructure();
        when(mockFetchMenuUseCase.getMenuStructure('TEST123'))
            .thenAnswer((_) async => mockMenuStructure);
        await menuController.loadMenu('TEST123');

        final mockSearchResult = MenuSearchResult(
          items: [DinerMenuItem(id: 'item1', categoryId: 'cat1', name: 'Test', basePrice: 1.0)],
          totalCount: 1,
          searchQuery: 'test',
        );
        when(mockFetchMenuUseCase.searchMenuItems('TEST123', 'test'))
            .thenAnswer((_) async => mockSearchResult);
        await menuController.searchItems('test');

        // Act
        menuController.clearSearch();

        // Assert
        expect(menuController.isSearchMode, isFalse);
        expect(menuController.searchQuery, isEmpty);
        expect(menuController.searchResults, isNull);
        expect(menuController.displayedItems.length, equals(1)); // Back to selected category
      });
    });

    group('CartController', () {
      test('should add items to cart', () {
        // Arrange
        final item = DinerMenuItem(
          id: 'item1',
          categoryId: 'cat1',
          name: 'Test Item',
          basePrice: 10.0,
        );

        // Act
        cartController.addItem(item);
        cartController.addItem(item);

        // Assert
        expect(cartController.totalItems, equals(2));
        expect(cartController.getItemQuantity('item1'), equals(2));
      });

      test('should remove items from cart', () {
        // Arrange
        final item = DinerMenuItem(
          id: 'item1',
          categoryId: 'cat1',
          name: 'Test Item',
          basePrice: 10.0,
        );
        cartController.addItem(item);
        cartController.addItem(item);

        // Act
        cartController.removeItem('item1');

        // Assert
        expect(cartController.totalItems, equals(1));
        expect(cartController.getItemQuantity('item1'), equals(1));
      });

      test('should clear cart', () {
        // Arrange
        final item = DinerMenuItem(
          id: 'item1',
          categoryId: 'cat1',
          name: 'Test Item',
          basePrice: 10.0,
        );
        cartController.addItem(item);

        // Act
        cartController.clearCart();

        // Assert
        expect(cartController.totalItems, equals(0));
        expect(cartController.getItemQuantity('item1'), equals(0));
      });
    });

    group('Widget Tests', () {
      testWidgets('EnhancedDinerMenuScreen should show loading initially', (WidgetTester tester) async {
        // Arrange
        when(mockFetchMenuUseCase.getMenuStructure('TEST123'))
            .thenAnswer((_) async {
          await Future.delayed(const Duration(seconds: 1));
          return _createMockMenuStructure();
        });

        // Act
        await tester.pumpWidget(
          GetMaterialApp(
            home: const EnhancedDinerMenuScreen(restaurantCode: 'TEST123'),
          ),
        );

        // Assert
        expect(find.text('Loading menu...'), findsOneWidget);
        expect(find.byType(CircularProgressIndicator), findsOneWidget);
      });

      testWidgets('EnhancedDinerMenuScreen should show error state', (WidgetTester tester) async {
        // Arrange
        when(mockFetchMenuUseCase.getMenuStructure('INVALID'))
            .thenThrow(Exception('Restaurant not found'));

        // Act
        await tester.pumpWidget(
          GetMaterialApp(
            home: const EnhancedDinerMenuScreen(restaurantCode: 'INVALID'),
          ),
        );

        await tester.pumpAndSettle();

        // Assert
        expect(find.text('Oops! Something went wrong'), findsOneWidget);
        expect(find.text('Try Again'), findsOneWidget);
      });
    });
  });
}

MenuStructure _createMockMenuStructure() {
  return MenuStructure(
    restaurant: const RestaurantBranding(
      id: 'test-id',
      name: 'Test Restaurant',
      code: 'TEST123',
    ),
    categories: const [
      MenuCategory(id: 'cat1', name: 'Appetizers', itemCount: 1),
      MenuCategory(id: 'cat2', name: 'Main Courses', itemCount: 1),
    ],
    items: const [
      DinerMenuItem(
        id: 'item1',
        categoryId: 'cat1',
        name: 'Caesar Salad',
        basePrice: 8.99,
      ),
      DinerMenuItem(
        id: 'item2',
        categoryId: 'cat2',
        name: 'Grilled Chicken',
        basePrice: 15.99,
        isFeatured: true,
      ),
    ],
    lastUpdated: DateTime.now(),
  );
}
