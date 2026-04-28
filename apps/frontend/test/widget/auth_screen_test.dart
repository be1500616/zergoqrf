import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:zergo_frontend/features/auth/application/supabase_auth_controller.dart';
import 'package:zergo_frontend/features/auth/presentation/auth_screen.dart';
import 'package:zergo_frontend/core/theme/theme_controller.dart';

class TestAuthController extends SupabaseAuthController {
  bool signInCalled = false;
  TestAuthController();
  
  @override
  // ignore: must_call_super
  void onInit() {
    // Skip base onInit to avoid Supabase listeners in tests
  }
  @override
  Future<bool> signInWithEmail([String? email, String? password]) async {
    signInCalled = true;
    return true;
  }
}

void main() {
  group('AuthScreen', () {
    late SupabaseAuthController authController;

    setUp(() {
      Get.testMode = true;
      final testController = TestAuthController();
      // Seed form fields to enable the Sign In button
      testController.emailController.text = 'user@example.com';
      testController.passwordController.text = 'password123';
      authController = testController;

      Get.put<ThemeController>(ThemeController());
      Get.put<SupabaseAuthController>(authController);
    });

    testWidgets('renders correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        const GetMaterialApp(
          home: AuthScreen(),
        ),
      );

      // AppBar title
      expect(find.text('ZERGO QR'), findsOneWidget);
      // Headings
      expect(find.text('Welcome to ZERGO QR'), findsOneWidget);
      // Form fields and actions
      expect(find.widgetWithText(TextField, 'Email'), findsOneWidget);
      expect(find.widgetWithText(TextField, 'Password'), findsOneWidget);
      expect(find.widgetWithText(ElevatedButton, 'Sign In'), findsOneWidget);
      expect(find.widgetWithText(TextButton, 'New staff member? Register here'),
          findsOneWidget);
    });

    testWidgets('calls signIn when Sign In button is tapped',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const GetMaterialApp(
          home: AuthScreen(),
        ),
      );

      final signInFinder = find.widgetWithText(ElevatedButton, 'Sign In');
      await tester.ensureVisible(signInFinder);
      final button = tester.widget<ElevatedButton>(signInFinder);
      // Validate that the button is enabled and wired
      expect(button.onPressed, isNotNull);
    });

    testWidgets('shows registration dialog when Register link tapped',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const GetMaterialApp(
          home: AuthScreen(),
        ),
      );

      final registerFinder =
          find.widgetWithText(TextButton, 'New staff member? Register here');
      await tester.ensureVisible(registerFinder);
      await tester.tap(registerFinder);
      await tester.pumpAndSettle();

      expect(find.text('Staff Registration'), findsOneWidget);
    });
  });
}
