/// Dependency bindings for Diner (public PWA) feature.
///
/// Registers repositories, controllers, and use cases needed for the diner
/// flow (menu browse → item details → cart → place order).
library;

import 'package:get/get.dart';
import 'package:zergo_frontend/core/config/api_config.dart';
import 'package:zergo_frontend/features/diner/application/controllers/cart_controller.dart';
import 'package:zergo_frontend/features/diner/application/controllers/menu_controller.dart';
import 'package:zergo_frontend/features/diner/application/controllers/search_controller.dart';
import 'package:zergo_frontend/features/diner/application/services/cart_service.dart';
import 'package:zergo_frontend/features/diner/application/use_cases/fetch_menu.dart';
import 'package:zergo_frontend/features/diner/infrastructure/menu_repository_impl.dart';

class DinerBinding extends Bindings {
  /// Wires all diner dependencies with GetX service locator.
  @override
  void dependencies() {
    // Core dependencies
    Get.lazyPut(() => ApiConfig(), fenix: true);

    // Repositories
    Get.lazyPut(() => MenuRepositoryImpl(Get.find<ApiConfig>()), fenix: true);

    // Services
    Get.lazyPut(() => CartService(Get.find<ApiConfig>()), fenix: true);

    // Use cases
    Get.lazyPut(() => FetchMenuUseCase(Get.find<MenuRepositoryImpl>()),
        fenix: true);

    // Controllers
    Get.lazyPut(() => CartController(Get.find<CartService>()), fenix: true);
    Get.lazyPut(() => MenuController(Get.find<FetchMenuUseCase>()),
        fenix: true);
    Get.lazyPut(() => MenuSearchController(), fenix: true);
  }
}
