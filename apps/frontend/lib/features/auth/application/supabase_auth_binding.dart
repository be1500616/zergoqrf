import 'package:get/get.dart';

import '../infrastructure/auth_repository_impl.dart';
import 'supabase_auth_controller.dart';

/// Dependency injection binding for Supabase authentication.
/// 
/// This binding sets up the simplified authentication system that
/// properly integrates with Supabase's built-in patterns.
class SupabaseAuthBinding extends Bindings {
  @override
  void dependencies() {
    // Register repository
    Get.lazyPut<AuthRepositoryImpl>(
      () => AuthRepositoryImpl(),
      fenix: true,
    );

    // Register the new simplified auth controller
    Get.put<SupabaseAuthController>(
      SupabaseAuthController(),
      permanent: true,
    );
  }
}
