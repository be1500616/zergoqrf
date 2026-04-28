import 'package:get/get.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter/material.dart';

import '../../features/auth/application/supabase_auth_controller.dart';

/// Route guard for authentication and authorization.
/// 
/// This guard ensures that users are properly authenticated and authorized
/// before accessing protected routes.
class AuthGuard {
  static final SupabaseAuthController _authController = Get.find<SupabaseAuthController>();

  /// Check if user is authenticated.
  static bool isAuthenticated() {
    return _authController.isAuthenticated || _authController.isAnonymous;
  }

  /// Check if user has required role.
  static bool hasRole(String role) {
    return _authController.hasRole(role);
  }

  /// Check if user has any of the required roles.
  static bool hasAnyRole(List<String> roles) {
    return _authController.hasAnyRole(roles);
  }

  /// Check if user has required permission.
  static bool hasPermission(String permission) {
    return _authController.hasPermission(permission);
  }

  /// Check if user can access restaurant.
  static bool canAccessRestaurant(String? restaurantId) {
    return _authController.canAccessRestaurant(restaurantId);
  }

  /// Redirect to login if not authenticated.
  static String? redirectToLogin(BuildContext context, GoRouterState state) {
    if (!isAuthenticated()) {
      return '/auth';
    }
    return null;
  }

  /// Redirect based on role requirements.
  static String? requireRole(
    BuildContext context,
    GoRouterState state,
    String requiredRole,
  ) {
    if (!isAuthenticated()) {
      return '/auth';
    }
    
    if (!hasRole(requiredRole)) {
      return '/unauthorized';
    }
    
    return null;
  }

  /// Redirect based on multiple role requirements.
  static String? requireAnyRole(
    BuildContext context,
    GoRouterState state,
    List<String> requiredRoles,
  ) {
    if (!isAuthenticated()) {
      return '/auth';
    }
    
    if (!hasAnyRole(requiredRoles)) {
      return '/unauthorized';
    }
    
    return null;
  }

  /// Redirect based on permission requirements.
  static String? requirePermission(
    BuildContext context,
    GoRouterState state,
    String requiredPermission,
  ) {
    if (!isAuthenticated()) {
      return '/auth';
    }
    
    if (!hasPermission(requiredPermission)) {
      return '/unauthorized';
    }
    
    return null;
  }

  /// Redirect based on restaurant access.
  static String? requireRestaurantAccess(
    BuildContext context,
    GoRouterState state,
    String? restaurantId,
  ) {
    if (!isAuthenticated()) {
      return '/auth';
    }
    
    if (!canAccessRestaurant(restaurantId)) {
      return '/unauthorized';
    }
    
    return null;
  }
}

/// Route guard middleware for GoRouter.
class RouteGuardMiddleware {
  /// Create a redirect function for authentication.
  static String? Function(BuildContext, GoRouterState) authenticated() {
    return AuthGuard.redirectToLogin;
  }

  /// Create a redirect function for role-based access.
  static String? Function(BuildContext, GoRouterState) requireRole(String role) {
    return (context, state) => AuthGuard.requireRole(context, state, role);
  }

  /// Create a redirect function for multiple roles.
  static String? Function(BuildContext, GoRouterState) requireAnyRole(List<String> roles) {
    return (context, state) => AuthGuard.requireAnyRole(context, state, roles);
  }

  /// Create a redirect function for permission-based access.
  static String? Function(BuildContext, GoRouterState) requirePermission(String permission) {
    return (context, state) => AuthGuard.requirePermission(context, state, permission);
  }

  /// Create a redirect function for restaurant access.
  static String? Function(BuildContext, GoRouterState) requireRestaurantAccess(String? restaurantId) {
    return (context, state) => AuthGuard.requireRestaurantAccess(context, state, restaurantId);
  }
}

/// Widget for displaying unauthorized access message.
class UnauthorizedScreen extends StatelessWidget {
  const UnauthorizedScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Access Denied'),
      ),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.lock_outline,
              size: 64,
              color: Colors.grey,
            ),
            SizedBox(height: 16),
            Text(
              'Access Denied',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 8),
            Text(
              'You do not have permission to access this resource.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey,
              ),
            ),
            SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}
