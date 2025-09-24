import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:go_router/go_router.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:zergo_frontend/features/auth/application/auth_binding.dart';
import 'package:zergo_frontend/features/auth/presentation/auth_screen.dart';
import 'package:zergo_frontend/features/restaurants/restaurants.dart';

import 'core/supabase_init.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await initSupabase();
  runApp(const ZergoApp());
}

final _router = GoRouter(
  initialLocation: '/auth',
  routes: [
    GoRoute(
      path: '/home',
      builder: (context, state) => const HomeScreen(),
    ),
    GoRoute(
      path: '/auth',
      builder: (context, state) {
        AuthBinding().dependencies();
        return const AuthScreen();
      },
    ),
    GoRoute(
      path: '/restaurant/register',
      builder: (context, state) {
        RestaurantBinding().dependencies();
        return const RestaurantRegistrationScreen();
      },
    ),
    GoRoute(
      path: '/dashboard',
      builder: (context, state) {
        RestaurantBinding().dependencies();
        return const RestaurantDashboardScreen();
      },
    ),
    GoRoute(
      path: '/restaurant/settings',
      builder: (context, state) {
        RestaurantBinding().dependencies();
        return const RestaurantSettingsScreen();
      },
    ),
    GoRoute(
      path: '/restaurant/staff',
      builder: (context, state) {
        RestaurantBinding().dependencies();
        return const StaffManagementScreen();
      },
    ),
  ],
);

class ZergoApp extends StatelessWidget {
  const ZergoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp.router(
      title: 'ZERGO QR',
      routeInformationParser: _router.routeInformationParser,
      routeInformationProvider: _router.routeInformationProvider,
      routerDelegate: _router.routerDelegate,
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ZERGO QR')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('Welcome to ZERGO QR'),
            ElevatedButton(
              onPressed: () async {
                final session = Supabase.instance.client.auth.currentSession;
                final email = session == null
                    ? 'Not signed in'
                    : (session.user.email ?? 'Unknown');
                Get.snackbar('Session', email);
              },
              child: const Text('Check session'),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => Get.toNamed('/restaurant/register'),
              child: const Text('Register Restaurant'),
            ),
          ],
        ),
      ),
    );
  }
}

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Restaurant Dashboard')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('Restaurant Dashboard'),
            Text('Welcome to your restaurant management dashboard!'),
          ],
        ),
      ),
    );
  }
}
