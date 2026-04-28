import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:mocktail/mocktail.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:zergo_frontend/features/auth/application/supabase_auth_controller.dart';
import 'package:zergo_frontend/features/auth/domain/auth_entity.dart' as domain;
import 'package:zergo_frontend/features/auth/infrastructure/auth_repository_impl.dart';

class MockSupabaseClient extends Mock implements SupabaseClient {}

class MockGoTrueClient extends Mock implements GoTrueClient {}

class MockUser extends Mock implements User {}

class MockSession extends Mock implements Session {}

class MockAuthRepositoryImpl extends Mock implements AuthRepositoryImpl {}

void main() {
  group('SupabaseAuthController', () {
    late SupabaseAuthController authController;
    late MockSupabaseClient mockSupabaseClient;
    late MockGoTrueClient mockGoTrueClient;
    late MockAuthRepositoryImpl mockAuthRepository;

    setUpAll(() {
      Get.testMode = true;
      registerFallbackValue(OtpType.sms);
    });

    setUp(() {
      mockSupabaseClient = MockSupabaseClient();
      mockGoTrueClient = MockGoTrueClient();
      mockAuthRepository = MockAuthRepositoryImpl();

      Get.reset();

      // Setup default mocks
      when(() => mockSupabaseClient.auth).thenReturn(mockGoTrueClient);
      when(() => mockGoTrueClient.currentUser).thenReturn(null);
      when(() => mockGoTrueClient.currentSession).thenReturn(null);
      when(() => mockGoTrueClient.onAuthStateChange)
          .thenAnswer((_) => const Stream.empty());

      authController = SupabaseAuthController(
        supabaseClient: mockSupabaseClient,
        authRepository: mockAuthRepository,
      );
    });

    test('initial values are correct', () {
      expect(authController.isLoading.value, false);
      expect(authController.isAuthenticated, false);
      expect(authController.currentUser, null);
    });

    test('form validation works correctly', () {
      authController.emailController.text = 'invalid-email';
      expect(authController.canSignIn.value, false);

      authController.emailController.text = 'valid@example.com';
      authController.passwordController.text = 'password123';
      expect(authController.canSignIn.value, true);

      authController.passwordController.text = 'short';
      expect(authController.canSignUp.value, false);

      authController.passwordController.text = 'longenoughpassword';
      expect(authController.canSignUp.value, true);
    });

    test('signInWithEmail success', () async {
      final mockUser = MockUser();
      final mockSession = MockSession();

      when(() => mockUser.id).thenReturn('user-id');
      when(() => mockUser.email).thenReturn('test@example.com');
      when(() => mockSession.accessToken).thenReturn('access-token');
      when(() => mockSession.refreshToken).thenReturn('refresh-token');
      when(() => mockSession.expiresAt).thenReturn(
          DateTime.now().add(const Duration(hours: 1)).millisecondsSinceEpoch ~/
              1000);

      final authResponse = AuthResponse(
        session: mockSession,
        user: mockUser,
      );

      when(() => mockGoTrueClient.signInWithPassword(
            email: any(named: 'email'),
            password: any(named: 'password'),
          )).thenAnswer((_) async => authResponse);

      authController.emailController.text = 'test@example.com';
      authController.passwordController.text = 'password123';

      await authController.signInWithEmail();

      expect(authController.isLoading.value, false);
      verify(() => mockGoTrueClient.signInWithPassword(
            email: 'test@example.com',
            password: 'password123',
          )).called(1);
    });

    test('signInWithPhone sends OTP', () async {
      when(() => mockGoTrueClient.signInWithOtp(
            phone: any(named: 'phone'),
          )).thenAnswer((_) async {});

      authController.phoneController.text = '+1234567890';

      await authController.signInWithPhone('+1234567890');

      expect(authController.isOtpSent.value, true);
      expect(authController.isLoading.value, false);
      verify(() => mockGoTrueClient.signInWithOtp(
            phone: '+1234567890',
          )).called(1);
    });

    test('verifyOtp success', () async {
      final mockUser = MockUser();
      final mockSession = MockSession();

      when(() => mockUser.id).thenReturn('user-id');
      when(() => mockUser.phone).thenReturn('+1234567890');
      when(() => mockSession.accessToken).thenReturn('access-token');
      when(() => mockSession.refreshToken).thenReturn('refresh-token');
      when(() => mockSession.expiresAt).thenReturn(
          DateTime.now().add(const Duration(hours: 1)).millisecondsSinceEpoch ~/
              1000);

      final authResponse = AuthResponse(
        session: mockSession,
        user: mockUser,
      );

      when(() => mockGoTrueClient.verifyOTP(
            phone: any(named: 'phone'),
            token: any(named: 'token'),
            type: any(named: 'type'),
          )).thenAnswer((_) async => authResponse);

      authController.phoneController.text = '+1234567890';
      authController.otpController.text = '123456';

      await authController.verifyPhoneOtp(
        phone: '+1234567890',
        token: '123456',
      );

      expect(authController.isLoading.value, false);
      verify(() => mockGoTrueClient.verifyOTP(
            phone: '+1234567890',
            token: '123456',
            type: OtpType.sms,
          )).called(1);
    });

    test('signOut clears user state', () async {
      when(() => mockGoTrueClient.signOut()).thenAnswer((_) async {});

      await authController.signOut();

      verify(() => mockGoTrueClient.signOut()).called(1);
    });

    test('createAnonymousSession success', () async {
      final anonymousSession = domain.AnonymousSession(
        sessionId: 'session-id',
        sessionToken: 'session-token',
        restaurantId: 'restaurant-id',
        tableId: 'table-id',
        expiresAt: DateTime.now().add(const Duration(hours: 24)),
      );

      when(() => mockAuthRepository.createAnonymousSession(any(), any()))
          .thenAnswer((_) async => anonymousSession);

      await authController.createAnonymousSession(
        restaurantId: 'restaurant-id',
        tableId: 'table-id',
      );

      expect(authController.isAnonymous, true);
      expect(authController.anonymousSession?.restaurantId, 'restaurant-id');
    });
  });
}
