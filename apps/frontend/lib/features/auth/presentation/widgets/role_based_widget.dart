import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:zergo_frontend/features/auth/application/supabase_auth_controller.dart';

class RoleBasedWidget extends GetView<SupabaseAuthController> {
  final List<String>? allowedRoles;
  final List<String>? requiredPermissions;
  final String? requiredRestaurantId;
  final Widget child;
  final Widget? fallback;

  const RoleBasedWidget({
    super.key,
    this.allowedRoles,
    this.requiredPermissions,
    this.requiredRestaurantId,
    required this.child,
    this.fallback,
  });

  @override
  Widget build(BuildContext context) {
    return Obx(() {
      final user = controller.currentUser;

      // If no user is authenticated, don't show anything
      if (user == null) {
        return fallback ?? const SizedBox.shrink();
      }

      // Check role requirements
      if (allowedRoles != null && !user.hasAnyRole(allowedRoles!)) {
        return fallback ?? const SizedBox.shrink();
      }

      // Check permission requirements
      if (requiredPermissions != null) {
        final hasAllPermissions = requiredPermissions!.every(
          (permission) => user.hasPermission(permission),
        );
        if (!hasAllPermissions) {
          return fallback ?? const SizedBox.shrink();
        }
      }

      // Check restaurant access
      if (requiredRestaurantId != null &&
          !user.canAccessRestaurant(requiredRestaurantId)) {
        return fallback ?? const SizedBox.shrink();
      }

      return child;
    });
  }
}

class PermissionBasedWidget extends GetView<SupabaseAuthController> {
  final String permission;
  final Widget child;
  final Widget? fallback;

  const PermissionBasedWidget({
    super.key,
    required this.permission,
    required this.child,
    this.fallback,
  });

  @override
  Widget build(BuildContext context) {
    return Obx(() {
      final user = controller.currentUser;

      if (user == null || !user.hasPermission(permission)) {
        return fallback ?? const SizedBox.shrink();
      }

      return child;
    });
  }
}

class AuthenticatedWidget extends GetView<SupabaseAuthController> {
  final Widget child;
  final Widget? fallback;

  const AuthenticatedWidget({
    super.key,
    required this.child,
    this.fallback,
  });

  @override
  Widget build(BuildContext context) {
    return Obx(() {
      if (controller.isAuthenticated) {
        return child;
      } else {
        return fallback ?? const SizedBox.shrink();
      }
    });
  }
}
