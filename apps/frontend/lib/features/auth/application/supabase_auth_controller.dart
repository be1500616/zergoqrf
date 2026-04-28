import 'dart:async';
import 'dart:developer' as developer;

import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:supabase_flutter/supabase_flutter.dart' as supabase;

import '../domain/auth_entity.dart';
import '../infrastructure/auth_repository_impl.dart';

/// Simplified authentication controller using Supabase's built-in patterns.
///
/// This controller eliminates manual token management and leverages Supabase's
/// automatic session handling, token refresh, and state management.
class SupabaseAuthController extends GetxController {
  final AuthRepositoryImpl _authRepository;
  final supabase.SupabaseClient _supabase;

  SupabaseAuthController({
    AuthRepositoryImpl? authRepository,
    supabase.SupabaseClient? supabaseClient,
  })  : _authRepository = authRepository ?? Get.find<AuthRepositoryImpl>(),
        _supabase = supabaseClient ?? supabase.Supabase.instance.client;

  // Text controllers for form fields (for backward compatibility with UI)
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  final phoneController =
      TextEditingController(text: '+91'); // Initialize with India country code
  final otpController = TextEditingController();
  final nameController = TextEditingController();
  final restaurantCodeController = TextEditingController();

  // Form keys for validation
  final staffLoginFormKey = GlobalKey<FormState>();
  final customerFormKey = GlobalKey<FormState>();
  final otpVerificationFormKey = GlobalKey<FormState>();
  final restaurantCodeFormKey = GlobalKey<FormState>();

  // Reactive state variables
  final Rx<AuthUser?> _currentUser = Rx<AuthUser?>(null);
  final RxBool _isLoading = false.obs;
  final RxBool _isAuthenticated = false.obs;
  final RxBool _isAnonymous = false.obs;
  final RxBool _isOtpSent = false.obs;
  final RxString _error = ''.obs;
  final Rx<AnonymousSession?> _anonymousSession = Rx<AnonymousSession?>(null);
  final RxBool isPasswordVisible = false.obs;

  // Reactive form validation observables
  final RxBool _canSignIn = false.obs;
  final RxBool _canSignUp = false.obs;
  final RxBool _canSendOtp = false.obs;
  final RxBool _canVerifyOtp = false.obs;

  // Getters for reactive state
  AuthUser? get currentUser => _currentUser.value;
  RxBool get isLoading => _isLoading;
  RxBool get isOtpSent => _isOtpSent;
  bool get isAuthenticated => _isAuthenticated.value;
  bool get isAnonymous => _isAnonymous.value;
  String get error => _error.value;
  AnonymousSession? get anonymousSession => _anonymousSession.value;

  // Reactive form validation getters
  RxBool get canSignIn => _canSignIn;
  RxBool get canSignUp => _canSignUp;
  RxBool get canSendOtp => _canSendOtp;
  RxBool get canVerifyOtp => _canVerifyOtp;

  // Backward compatibility aliases
  RxBool get canSendOTP => _canSendOtp;
  RxBool get canVerifyOTP => _canVerifyOtp;

  // Stream subscription for auth state changes
  StreamSubscription<supabase.AuthState>? _authSubscription;

  @override
  void onInit() {
    super.onInit();
    _initializeAuth();
  }

  @override
  void onClose() {
    // Dispose text controllers
    emailController.dispose();
    passwordController.dispose();
    phoneController.dispose();
    otpController.dispose();
    nameController.dispose();
    restaurantCodeController.dispose();

    // Cancel auth subscription
    _authSubscription?.cancel();
    super.onClose();
  }

  /// Initialize authentication and listen to auth state changes.
  void _initializeAuth() {
    // Setup text controller listeners for reactive form validation
    _setupFormValidationListeners();

    // Listen to Supabase auth state changes
    _authSubscription = _supabase.auth.onAuthStateChange.listen(
      (data) {
        _handleAuthStateChange(data.event, data.session);
      },
      onError: (error) {
        developer.log('Auth state change error: $error',
            name: 'AuthController');
        _setError('Authentication state error: ${error.toString()}');
      },
    );

    // Check initial session
    _checkInitialSession();
  }

  /// Setup listeners on text controllers to update reactive validation states.
  void _setupFormValidationListeners() {
    // Staff login form validation
    emailController.addListener(_updateCanSignIn);
    passwordController.addListener(_updateCanSignIn);
    passwordController.addListener(_updateCanSignUp);

    // Customer phone login validation
    phoneController.addListener(_updateCanSendOtp);
    phoneController.addListener(_updateCanVerifyOtp);

    // OTP verification validation
    otpController.addListener(_updateCanVerifyOtp);
  }

  /// Update canSignIn reactive state based on email and password.
  void _updateCanSignIn() {
    _canSignIn.value = emailController.text.trim().isNotEmpty &&
        passwordController.text.isNotEmpty;
  }

  /// Update canSignUp reactive state based on email and password length.
  void _updateCanSignUp() {
    _canSignUp.value = emailController.text.trim().isNotEmpty &&
        passwordController.text.length >= 8;
  }

  /// Update canSendOtp reactive state based on phone number.
  void _updateCanSendOtp() {
    _canSendOtp.value = phoneController.text.trim().isNotEmpty;
  }

  /// Update canVerifyOtp reactive state based on phone and OTP.
  void _updateCanVerifyOtp() {
    _canVerifyOtp.value = phoneController.text.trim().isNotEmpty &&
        otpController.text.trim().length == 6;
  }

  /// Check for existing session on app start.
  Future<void> _checkInitialSession() async {
    try {
      _setLoading(true);

      final session = _supabase.auth.currentSession;
      if (session != null) {
        await _handleAuthenticatedUser(session.user);
      } else {
        // Check for anonymous session in local storage
        await _checkAnonymousSession();
      }
    } catch (e) {
      developer.log('Initial session check error: $e', name: 'AuthController');
      _setError('Failed to restore session: ${e.toString()}');
    } finally {
      _setLoading(false);
    }
  }

  /// Handle auth state changes from Supabase.
  Future<void> _handleAuthStateChange(
      supabase.AuthChangeEvent event, supabase.Session? session) async {
    developer.log('Auth state changed: $event', name: 'AuthController');

    switch (event) {
      case supabase.AuthChangeEvent.signedIn:
        if (session?.user != null) {
          await _handleAuthenticatedUser(session!.user);
        }
        break;
      case supabase.AuthChangeEvent.signedOut:
        _handleSignOut();
        break;
      case supabase.AuthChangeEvent.tokenRefreshed:
        if (session?.user != null) {
          await _handleAuthenticatedUser(session!.user);
        }
        break;
      case supabase.AuthChangeEvent.userUpdated:
        if (session?.user != null) {
          await _handleAuthenticatedUser(session!.user);
        }
        break;
      case supabase.AuthChangeEvent.passwordRecovery:
        // Handle password recovery if needed
        break;
      case supabase.AuthChangeEvent.initialSession:
        // Handle initial session if needed
        break;
      case supabase.AuthChangeEvent.userDeleted:
        // Handle user deletion if needed
        break;
      case supabase.AuthChangeEvent.mfaChallengeVerified:
        // Handle MFA challenge verification if needed
        break;
    }
  }

  /// Handle authenticated user and create user context.
  Future<void> _handleAuthenticatedUser(supabase.User user) async {
    try {
      // Get user metadata
      final userMetadata = user.userMetadata ?? {};

      // Create AuthUser from Supabase user
      final authUser = AuthUser(
        id: user.id,
        email: user.email,
        phone: user.phone,
        name: userMetadata['name'] as String?,
        role: userMetadata['role'] as String? ?? 'customer',
        restaurantId: userMetadata['restaurant_id'] as String?,
        permissions: userMetadata['permissions'] as Map<String, dynamic>? ?? {},
        isActive: true,
        isAnonymous: false,
        createdAt:
            user.createdAt != null ? DateTime.tryParse(user.createdAt) : null,
      );

      _currentUser.value = authUser;
      _isAuthenticated.value = true;
      _isAnonymous.value = false;
      _anonymousSession.value = null;
      _clearError();

      developer.log('User authenticated: ${authUser.id} (${authUser.role})',
          name: 'AuthController');

      // Navigate based on user role
      _navigateAfterAuth(authUser);
    } catch (e) {
      developer.log('Error handling authenticated user: $e',
          name: 'AuthController');
      _setError('Failed to process user data: ${e.toString()}');
    }
  }

  /// Navigate to appropriate screen based on user role.
  void _navigateAfterAuth(AuthUser user) {
    // Only navigate if we're currently on the auth screen
    if (Get.currentRoute == '/auth') {
      switch (user.role) {
        case 'owner':
        case 'manager':
        case 'staff':
          // Navigate to dashboard for staff roles
          Get.offAllNamed('/dashboard');
          break;
        case 'customer':
          // Navigate to home for customers
          Get.offAllNamed('/home');
          break;
        default:
          // Default to home for unknown roles
          Get.offAllNamed('/home');
      }
    }
  }

  /// Handle sign out.
  void _handleSignOut() {
    _currentUser.value = null;
    _isAuthenticated.value = false;
    _isAnonymous.value = false;
    _anonymousSession.value = null;
    _clearError();

    developer.log('User signed out', name: 'AuthController');

    // Navigate to auth screen after sign out
    if (Get.currentRoute != '/auth') {
      Get.offAllNamed('/auth');
    }
  }

  /// Sign in with email and password.
  /// If parameters are not provided, uses text controllers.
  Future<bool> signInWithEmail([String? email, String? password]) async {
    try {
      _setLoading(true);
      _clearError();

      final emailToUse = email ?? emailController.text.trim();
      final passwordToUse = password ?? passwordController.text;

      final response = await _supabase.auth.signInWithPassword(
        email: emailToUse,
        password: passwordToUse,
      );

      if (response.user == null) {
        _setError('Invalid email or password');
        Get.snackbar(
          'Sign In Failed',
          'Invalid email or password. Please try again.',
          snackPosition: SnackPosition.TOP,
          backgroundColor: Get.theme.colorScheme.errorContainer,
          colorText: Get.theme.colorScheme.onErrorContainer,
          icon: Icon(
            Icons.error_outline,
            color: Get.theme.colorScheme.error,
          ),
        );
        return false;
      }

      // Show success message
      Get.snackbar(
        'Welcome Back!',
        'You have successfully signed in.',
        snackPosition: SnackPosition.TOP,
        backgroundColor: Get.theme.colorScheme.primaryContainer,
        colorText: Get.theme.colorScheme.onPrimaryContainer,
        icon: Icon(
          Icons.check_circle_outline,
          color: Get.theme.colorScheme.primary,
        ),
      );

      // User will be handled by auth state change listener
      return true;
    } catch (e) {
      developer.log('Email sign in error: $e', name: 'AuthController');
      final errorMessage = _parseAuthError(e.toString());
      _setError(errorMessage);
      Get.snackbar(
        'Sign In Failed',
        errorMessage,
        snackPosition: SnackPosition.TOP,
        backgroundColor: Get.theme.colorScheme.errorContainer,
        colorText: Get.theme.colorScheme.onErrorContainer,
        icon: Icon(
          Icons.error_outline,
          color: Get.theme.colorScheme.error,
        ),
      );
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Sign up with email and password.
  Future<bool> signUpWithEmail({
    required String email,
    required String password,
    String? name,
    String? role,
    String? restaurantId,
  }) async {
    try {
      _setLoading(true);
      _clearError();

      // Prepare user metadata
      final userData = <String, dynamic>{};
      if (name != null) userData['name'] = name;
      if (role != null) userData['role'] = role;
      if (restaurantId != null) userData['restaurant_id'] = restaurantId;

      final response = await _supabase.auth.signUp(
        email: email,
        password: password,
        data: userData,
      );

      if (response.user == null) {
        _setError('Failed to create account');
        return false;
      }

      // If session is null, email confirmation is required
      if (response.session == null) {
        Get.snackbar(
          'Account Created',
          'Please check your email to confirm your account',
          snackPosition: SnackPosition.TOP,
        );
      }

      return true;
    } catch (e) {
      developer.log('Email sign up error: $e', name: 'AuthController');
      _setError('Sign up failed: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Sign in with phone OTP.
  /// If phone parameter is not provided, uses phoneController.
  Future<bool> signInWithPhone([String? phone]) async {
    try {
      _setLoading(true);
      _clearError();

      final phoneToUse = phone ?? phoneController.text.trim();

      await _supabase.auth.signInWithOtp(phone: phoneToUse);

      _isOtpSent.value = true;

      Get.snackbar(
        'OTP Sent',
        'Please check your phone for the verification code',
        snackPosition: SnackPosition.TOP,
        backgroundColor: Get.theme.colorScheme.primaryContainer,
        colorText: Get.theme.colorScheme.onPrimaryContainer,
        icon: Icon(
          Icons.sms_outlined,
          color: Get.theme.colorScheme.primary,
        ),
      );

      return true;
    } catch (e) {
      developer.log('Phone sign in error: $e', name: 'AuthController');
      final errorMessage = _parseAuthError(e.toString());
      _setError(errorMessage);
      Get.snackbar(
        'Failed to Send OTP',
        errorMessage,
        snackPosition: SnackPosition.TOP,
        backgroundColor: Get.theme.colorScheme.errorContainer,
        colorText: Get.theme.colorScheme.onErrorContainer,
        icon: Icon(
          Icons.error_outline,
          color: Get.theme.colorScheme.error,
        ),
      );
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Verify phone OTP.
  Future<bool> verifyPhoneOtp({
    required String phone,
    required String token,
    String? name,
  }) async {
    try {
      _setLoading(true);
      _clearError();

      final response = await _supabase.auth.verifyOTP(
        phone: phone,
        token: token,
        type: supabase.OtpType.sms,
      );

      if (response.user == null) {
        _setError('Invalid or expired OTP');
        Get.snackbar(
          'Verification Failed',
          'Invalid or expired verification code. Please try again.',
          snackPosition: SnackPosition.TOP,
          backgroundColor: Get.theme.colorScheme.errorContainer,
          colorText: Get.theme.colorScheme.onErrorContainer,
          icon: Icon(
            Icons.error_outline,
            color: Get.theme.colorScheme.error,
          ),
        );
        return false;
      }

      // Update user metadata if name provided
      if (name != null && response.user!.userMetadata?['name'] == null) {
        await _supabase.auth.updateUser(
          supabase.UserAttributes(data: {'name': name}),
        );
      }

      // Show success message
      Get.snackbar(
        'Welcome!',
        'You have successfully signed in.',
        snackPosition: SnackPosition.TOP,
        backgroundColor: Get.theme.colorScheme.primaryContainer,
        colorText: Get.theme.colorScheme.onPrimaryContainer,
        icon: Icon(
          Icons.check_circle_outline,
          color: Get.theme.colorScheme.primary,
        ),
      );

      return true;
    } catch (e) {
      developer.log('Phone OTP verification error: $e', name: 'AuthController');
      final errorMessage = _parseAuthError(e.toString());
      _setError(errorMessage);
      Get.snackbar(
        'Verification Failed',
        errorMessage,
        snackPosition: SnackPosition.TOP,
        backgroundColor: Get.theme.colorScheme.errorContainer,
        colorText: Get.theme.colorScheme.onErrorContainer,
        icon: Icon(
          Icons.error_outline,
          color: Get.theme.colorScheme.error,
        ),
      );
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Create anonymous session for QR code users.
  Future<bool> createAnonymousSession({
    required String restaurantId,
    String? tableId,
  }) async {
    try {
      _setLoading(true);
      _clearError();

      final session = await _authRepository.createAnonymousSession(
        restaurantId,
        tableId ?? '',
      );

      _anonymousSession.value = session;
      _isAnonymous.value = true;
      _isAuthenticated.value = false;
      _currentUser.value = null;

      developer.log('Anonymous session created: ${session.sessionId}',
          name: 'AuthController');
      return true;
    } catch (e) {
      developer.log('Anonymous session creation error: $e',
          name: 'AuthController');
      _setError('Failed to create session: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Check for existing anonymous session.
  Future<void> _checkAnonymousSession() async {
    // This would typically check local storage for anonymous session
    // For now, we'll skip this implementation
  }

  /// Validate restaurant code and create anonymous session.
  Future<Map<String, dynamic>?> validateRestaurantCode([String? code]) async {
    try {
      _setLoading(true);
      _clearError();

      final codeToUse = code ?? restaurantCodeController.text.trim();

      // Call backend API to validate restaurant code
      final response = await _supabase.functions.invoke(
        'validate-restaurant-code',
        body: {'code': codeToUse},
      );

      if (response.status == 200 && response.data != null) {
        final data = response.data as Map<String, dynamic>;

        if (data['valid'] == true) {
          // Store session token
          final sessionToken = data['session_token'] as String?;
          final restaurant = data['restaurant'] as Map<String, dynamic>?;

          if (sessionToken != null && restaurant != null) {
            // Create anonymous session locally
            _anonymousSession.value = AnonymousSession(
              sessionId: sessionToken,
              sessionToken: sessionToken,
              restaurantId: restaurant['restaurant_id'] as String,
              tableId: '', // Will be set when user scans QR code at table
              expiresAt: DateTime.now().add(const Duration(hours: 24)),
            );
            _isAnonymous.value = true;
            _isAuthenticated.value = false;

            developer.log(
              'Restaurant code validated: ${restaurant['name']}',
              name: 'AuthController',
            );

            Get.snackbar(
              'Success',
              data['message'] ?? 'Restaurant code validated',
              snackPosition: SnackPosition.TOP,
            );

            return data;
          }
        }
      }

      _setError('Invalid restaurant code');
      return null;
    } catch (e) {
      developer.log('Restaurant code validation error: $e',
          name: 'AuthController');
      _setError('Failed to validate restaurant code: ${e.toString()}');
      return null;
    } finally {
      _setLoading(false);
    }
  }

  /// Sign out current user.
  Future<void> signOut() async {
    try {
      _setLoading(true);

      if (_isAuthenticated.value) {
        await _supabase.auth.signOut();
      }

      // Clear anonymous session
      _anonymousSession.value = null;

      // State will be handled by auth state change listener
    } catch (e) {
      developer.log('Sign out error: $e', name: 'AuthController');
      _setError('Sign out failed: ${e.toString()}');
    } finally {
      _setLoading(false);
    }
  }

  /// Check if user has specific role.
  bool hasRole(String role) {
    return currentUser?.hasRole(role) ?? false;
  }

  /// Check if user has any of the specified roles.
  bool hasAnyRole(List<String> roles) {
    return currentUser?.hasAnyRole(roles) ?? false;
  }

  /// Check if user has specific permission.
  bool hasPermission(String permission) {
    return currentUser?.hasPermission(permission) ?? false;
  }

  /// Check if user can access specific restaurant.
  bool canAccessRestaurant(String? restaurantId) {
    if (isAnonymous && anonymousSession != null) {
      return anonymousSession!.restaurantId == restaurantId;
    }
    return currentUser?.canAccessRestaurant(restaurantId) ?? false;
  }

  /// Get current access token (for API calls).
  String? get accessToken {
    return _supabase.auth.currentSession?.accessToken;
  }

  /// Get anonymous session token (for API calls).
  String? get sessionToken {
    return anonymousSession?.sessionToken;
  }

  // Wrapper methods for backward compatibility with UI
  /// Sign in using email and password from text controllers.
  Future<void> signInWithEmailFromControllers() async {
    await signInWithEmail(
      emailController.text.trim(),
      passwordController.text,
    );
  }

  /// Parse authentication error messages to user-friendly text.
  String _parseAuthError(String error) {
    if (error.contains('Invalid login credentials')) {
      return 'Invalid email or password. Please try again.';
    } else if (error.contains('Email not confirmed')) {
      return 'Please confirm your email address before signing in.';
    } else if (error.contains('User not found')) {
      return 'No account found with this email address.';
    } else if (error.contains('Invalid phone number')) {
      return 'Please enter a valid phone number.';
    } else if (error.contains('Invalid OTP')) {
      return 'Invalid verification code. Please try again.';
    } else if (error.contains('OTP expired')) {
      return 'Verification code has expired. Please request a new one.';
    } else if (error.contains('Network')) {
      return 'Network error. Please check your connection and try again.';
    } else if (error.contains('Too many requests')) {
      return 'Too many attempts. Please try again later.';
    } else {
      return 'An error occurred. Please try again.';
    }
  }

  /// Sign up using form data from text controllers.
  Future<void> signUpWithEmailFromControllers() async {
    await signUpWithEmail(
      email: emailController.text.trim(),
      password: passwordController.text,
      name: nameController.text.trim().isEmpty
          ? null
          : nameController.text.trim(),
    );
  }

  /// Send OTP using phone from text controller.
  Future<void> sendOTPFromController() async {
    await signInWithPhone(phoneController.text.trim());
  }

  /// Verify OTP using phone and OTP from text controllers.
  /// Alias for verifyPhoneOtp that uses text controllers.
  Future<void> verifyOtp() async {
    await verifyPhoneOtp(
      phone: phoneController.text.trim(),
      token: otpController.text.trim(),
      name: nameController.text.trim().isEmpty
          ? null
          : nameController.text.trim(),
    );
  }

  // Helper methods
  void _setLoading(bool loading) {
    _isLoading.value = loading;
  }

  void _setError(String error) {
    _error.value = error;
    if (error.isNotEmpty) {
      Get.snackbar(
        'Error',
        error,
        snackPosition: SnackPosition.TOP,
      );
    }
  }

  void _clearError() {
    _error.value = '';
  }

  /// Toggle password visibility for password input fields
  void togglePasswordVisibility() {
    isPasswordVisible.value = !isPasswordVisible.value;
  }
}
